import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import User

bearer_scheme = HTTPBearer(auto_error=False)

_jwks_client: PyJWKClient | None = None


def _get_jwks_client() -> PyJWKClient:
    """Supabase now signs new sessions with an asymmetric key (ES256) rather than
    the old shared HS256 secret (see project Settings > API > JWT Signing Keys).
    Verifying against the project's JWKS endpoint works for both the new and the
    legacy key without hardcoding which one is currently active."""
    global _jwks_client
    if _jwks_client is None:
        if not settings.supabase_url:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "SUPABASE_URL is not configured")
        jwks_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
        _jwks_client = PyJWKClient(jwks_url)
    return _jwks_client


def _decode_supabase_jwt(token: str) -> dict:
    try:
        signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
        return jwt.decode(token, signing_key.key, algorithms=["ES256", "RS256"], audience="authenticated")
    except jwt.PyJWTError as jwks_error:
        # Fallback for older projects still fully on the legacy shared JWT secret.
        if settings.supabase_jwt_secret:
            try:
                return jwt.decode(token, settings.supabase_jwt_secret, algorithms=["HS256"], audience="authenticated")
            except jwt.PyJWTError as legacy_error:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Invalid session token: {legacy_error}")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Invalid session token: {jwks_error}")


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Equivalent of the old protectedProcedure: requires a valid Supabase session JWT."""
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Please login (10001)")
    payload = _decode_supabase_jwt(credentials.credentials)
    supabase_uid = payload.get("sub")
    if not supabase_uid:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Please login (10001)")

    user = db.query(User).filter(User.supabase_uid == supabase_uid).first()
    if user is None:
        # First request after Supabase sign-up/sign-in: mirror upsertUser() from db.ts
        user = User(
            supabase_uid=supabase_uid,
            email=payload.get("email"),
            name=(payload.get("user_metadata") or {}).get("full_name"),
            login_method=(payload.get("app_metadata") or {}).get("provider", "email"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    """Equivalent of publicProcedure with ctx.user — returns None instead of raising."""
    if credentials is None:
        return None
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
