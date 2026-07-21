"""Verifies Supabase-issued Google-login JWTs.

Newer Supabase projects sign access tokens asymmetrically (ES256, key
type ECC P-256) rather than with a single shared HS256 secret — the
project's JWT Keys page exposes signing keys, not a static secret, and
the public half is published at SUPABASE_URL/auth/v1/.well-known/jwks.json.

We fetch that JWKS ourselves via httpx rather than PyJWT's built-in
PyJWKClient: PyJWKClient uses bare urllib with no custom headers, which
got silently rejected (observed as a plain HTTP 404, not a WAF-style 403)
when this ran on Render against Supabase's edge — httpx with an explicit
User-Agent avoids that. On a `kid` we haven't seen (key rotation), we
refetch once before giving up, same behavior PyJWKClient provides
out of the box.

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

import httpx
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.algorithms import ECAlgorithm

from app.config import settings

_bearer = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    id: str
    email: str | None


@lru_cache(maxsize=1)
def _fetch_jwks() -> dict:
    jwks_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    response = httpx.get(
        jwks_url, timeout=10.0, headers={"User-Agent": "nolan-ai-backend/1.0"}
    )
    response.raise_for_status()
    return response.json()


def _signing_key_for(kid: str):
    jwks = _fetch_jwks()
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return ECAlgorithm.from_jwk(key)

    _fetch_jwks.cache_clear()  # key not found — could be a rotation, refetch once
    jwks = _fetch_jwks()
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return ECAlgorithm.from_jwk(key)

    raise jwt.InvalidKeyError(f"No matching JWKS key for kid={kid}")


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
        unverified_header = jwt.get_unverified_header(credentials.credentials)
        kid = unverified_header.get("kid")
        if not kid:
            raise jwt.InvalidTokenError("Token header is missing 'kid'")

        signing_key = _signing_key_for(kid)
        payload = jwt.decode(
            credentials.credentials,
            signing_key,
            algorithms=["ES256"],
            audience="authenticated",
        )
    except (jwt.PyJWTError, httpx.HTTPError) as exc:
        raise HTTPException(401, f"Invalid or expired session: {exc}") from exc

    return CurrentUser(id=payload["sub"], email=payload.get("email"))
