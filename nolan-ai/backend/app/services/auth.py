"""Verifies Supabase-issued Google-login JWTs.

Newer Supabase projects sign access tokens asymmetrically (ES256, key
type ECC P-256) rather than with a single shared HS256 secret — the
project's JWT Keys page exposes signing keys, not a static secret, and
the public half is published at SUPABASE_URL/auth/v1/.well-known/jwks.json.
PyJWKClient fetches and caches that JWKS and picks the right key by the
token's `kid`, so key rotation (standby keys, previously-used keys still
valid until their tokens expire) is handled without any code changes here.

The frontend sends the access token as `Authorization: Bearer <token>`
on every request; this dependency verifies it and exposes the
authenticated user to route handlers. No local users table — Supabase
IS the user store. Single-user today, but every protected route already
depends on a real identity, so adding per-user data scoping later is a
column addition, not a redesign.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

_bearer = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    id: str
    email: str | None


@lru_cache(maxsize=1)
def _jwks_client() -> jwt.PyJWKClient:
    jwks_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    return jwt.PyJWKClient(jwks_url, cache_keys=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser:
    if not settings.supabase_url:
        raise HTTPException(
            503,
            "Auth not configured — set SUPABASE_URL once the Supabase "
            "project exists (Setup Dependencies in HANDOFF.md).",
        )
    if credentials is None:
        raise HTTPException(401, "Missing bearer token — please log in.")

    try:
        signing_key = _jwks_client().get_signing_key_from_jwt(credentials.credentials)
        payload = jwt.decode(
            credentials.credentials,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(401, f"Invalid or expired session: {exc}") from exc

    return CurrentUser(id=payload["sub"], email=payload.get("email"))
