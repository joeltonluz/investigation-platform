from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwks import JWKSFetcher, validate_token_with_jwks
from app.auth.models import User
from app.auth.permissions import flatten_permissions
from app.auth.token import InvalidTokenError, validate_token
from app.config import Settings

security = HTTPBearer(auto_error=False)

_fetcher: JWKSFetcher | None = None


def get_public_key() -> str:
    return Settings().public_key


@lru_cache
def get_settings() -> Settings:
    return Settings()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    settings: Settings = Depends(get_settings),
    public_key: str = Depends(get_public_key),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        if settings.auth_mode == "mock":
            payload = validate_token(credentials.credentials, public_key)
        else:
            global _fetcher
            if _fetcher is None:
                _fetcher = JWKSFetcher(settings.keycloak_jwks_url)
            payload = await validate_token_with_jwks(
                credentials.credentials, _fetcher, settings.keycloak_issuer
            )
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    permissions = flatten_permissions(payload.get("resource_access", {}))
    return User(
        user_id=payload.get("sub", ""),
        app_client_id=payload.get("azp", ""),
        permissions=permissions,
    )


def require_permission(permission: str):
    async def _check(user: User = Depends(get_current_user)) -> None:
        if permission not in user.permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return _check
