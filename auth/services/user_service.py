import logging
from typing import List, Optional

from auth.repositories.auth_repository import AuthRepository
from auth.schemas.user import User

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self):
        self.auth_repository = AuthRepository()

    async def get_all_users(self) -> List[User]:
        logger.info("Fetching all users from the database")

        try:
            users = await self.auth_repository.get_all()
            logger.info(f"Users fetched successfully: {len(users)} users")

            return users

        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            raise

    async def get_user(self, username: str) -> Optional[User]:
        logger.info(f"Fetching user by username: {username}")

        try:
            user = await self.auth_repository.get_user_by_username(username)

            if user:
                logger.info(f"User found: {user.username}")
            else:
                logger.warning(f"User not found: {username}")
            return user

        except Exception as e:
            logger.error(f"Error fetching user by username: {e}")
            raise

    async def update_user(self, username: str, updated_user: User) -> User:
        logger.info(f"Updating user by username: {username}")

        try:
            user = await self.auth_repository.get_user_by_username(username)

            if not user:
                raise ValueError("User not found")

            updated_result = await self.auth_repository.update(user.id, updated_user)
            logger.info(f"User {username} updated successfully")

            return updated_result
        except Exception as e:
            logger.error(f"Error in update_user: {e}")
            raise

    async def delete_user(self, username: str) -> None:
        logger.info(f"Deleting user by username: {username}")

        try:
            user = await self.auth_repository.get_user_by_username(username)

            if not user:
                raise ValueError("User not found")

            await self.auth_repository.delete(user.id)
            logger.info(f"User {username} deleted successfully")
        except Exception as e:
            logger.error(f"Error in delete_user: {e}")
            raise
