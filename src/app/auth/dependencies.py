from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.models import User
from app.auth.permissions import flatten_permissions
from app.auth.token import InvalidTokenError, validate_token

security = HTTPBearer(auto_error=False)


def get_public_key() -> str:
    from app.config import Settings

    return Settings().public_key


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    public_key: str = Depends(get_public_key),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        payload = validate_token(credentials.credentials, public_key)
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
