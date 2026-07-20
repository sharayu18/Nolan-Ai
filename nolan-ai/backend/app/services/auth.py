"""Verifies Supabase-issued Google-login JWTs.

Supabase Auth (Google OAuth) issues a standard HS256 JWT signed with the
project's JWT secret. The frontend sends it as `Authorization: Bearer
<token>` on every request; this dependency verifies it and exposes the
authenticated user to route handlers. No local users table — Supabase
IS the user store. Single-user today, but every protected route already
depends on a real identity, so adding per-user data scoping later is a
column addition, not a redesign.
"""
from __future__ import annotations

from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

_bearer = HTTPBearer(auto_error=False)


class AuthNotConfiguredError(RuntimeError):
    pass


@dataclass
class CurrentUser:
    id: str
    email: str | None


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser:
    if not settings.supabase_jwt_secret:
        raise HTTPException(
            503,
            "Auth not configured — set SUPABASE_JWT_SECRET once the Supabase "
            "project exists (Setup Dependencies in HANDOFF.md).",
        )
    if credentials is None:
        raise HTTPException(401, "Missing bearer token — please log in.")

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(401, f"Invalid or expired session: {exc}") from exc

    return CurrentUser(id=payload["sub"], email=payload.get("email"))
