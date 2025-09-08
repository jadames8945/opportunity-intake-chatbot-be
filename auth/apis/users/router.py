from typing import List

from fastapi import APIRouter, Depends, HTTPException

from auth.dependencies.auth_dependencies import get_current_user
from auth.schemas.user import User
from auth.services.user_service import UserService

users_router = APIRouter(
    prefix="/users",
    tags=["users"],
)


def get_users_service():
    return UserService()


@users_router.get("/", response_model=List[User])
async def get_all_users(
    user_service: UserService = Depends(get_users_service),
    current_user: User = Depends(get_current_user),
) -> List[User]:
    try:
        users = await user_service.get_all_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@users_router.get("/{username}", response_model=User)
async def get_user(
    username: str,
    user_service: UserService = Depends(get_users_service),
    current_user: User = Depends(get_current_user),
) -> User:
    try:
        user = await user_service.get_user(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@users_router.put("/{username}", response_model=User)
async def update_user(
    username: str,
    user_obj: User,
    user_service: UserService = Depends(get_users_service),
    current_user: User = Depends(get_current_user),
) -> User:
    try:
        updated_user = await user_service.update_user(username, user_obj)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"Unable to update user: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@users_router.delete("/{username}", response_model=dict)
async def delete_user(
    username: str,
    user_service: UserService = Depends(get_users_service),
    current_user: User = Depends(get_current_user),
) -> dict:
    try:
        await user_service.delete_user(username)
        return {"detail": "User deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@users_router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)) -> User:
    return current_user
