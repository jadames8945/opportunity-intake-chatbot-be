import logging
from typing import Optional

import httpx
from fastapi import HTTPException

from auth.repositories.auth_repository import AuthRepository
from auth.schemas.user import User
from auth.services.token_service import TokenService

logger = logging.getLogger(__name__)


class MicrosoftAuthService:
    def __init__(self):
        self.auth_repository = AuthRepository()
        self.token_service = TokenService()

    async def validate_microsoft_token(self, access_token: str) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://graph.microsoft.com/v1.0/me",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=401, detail="Invalid Microsoft token"
                    )
        except Exception as e:
            logger.error(f"Microsoft token validation failed: {str(e)}")
            raise HTTPException(
                status_code=401, detail=f"Token validation failed: {str(e)}"
            )

    async def get_or_create_user_from_microsoft(self, user_info: dict) -> User:
        email = user_info.get("mail") or user_info.get("userPrincipalName")
        if not email:
            raise HTTPException(
                status_code=400, detail="No email found in Microsoft user info"
            )

        username = email.split("@")[0]
        display_name = user_info.get("displayName", username)
        first_name = user_info.get("givenName", display_name.split(" ")[0])
        last_name = user_info.get(
            "surname", display_name.split(" ")[-1] if " " in display_name else ""
        )

        try:
            existing_user = await self.auth_repository.get_user_by_username(username)
            if existing_user:
                return existing_user
        except:
            existing_user = None

        if not existing_user:
            new_user = User(
                username=username,
                password="",
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            existing_user = await self.auth_repository.create_user(new_user)

        return existing_user

    def create_jwt_token(self, user: User) -> str:
        return self.token_service.create_access_token(data={"username": user.username})
