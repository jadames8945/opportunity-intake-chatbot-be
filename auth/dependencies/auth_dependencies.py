from auth.schemas.user import User
from auth.services.auth_service import AuthService
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(AuthService),
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    Use this to protect endpoints that require authentication.
    """
    token = credentials.credentials

    username = auth_service.token_service.verify_token(token)

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await auth_service.auth_repository.get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_username(current_user: User = Depends(get_current_user)) -> str:
    """
    Dependency to get just the username from the authenticated user.
    """
    return current_user.username
