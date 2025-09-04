import logging
from typing import Any, List, Optional

from bson import ObjectId
from common.mongo_infrastructure import infra
from common.repositories.base_repository import BaseRepository

from app.schemas.user import User

logger = logging.getLogger(__name__)


class AuthRepository(BaseRepository[User]):
    def __init__(self):
        self.db = infra.mongo_config.get_database_connection()
        self.collection = self.db.users

    async def find_by_id(self, entity_id: Any) -> Optional[User]:
        try:
            if isinstance(entity_id, str):
                entity_id = ObjectId(entity_id)
            user_doc = await self.collection.find_one({"_id": entity_id})
            if user_doc:
                user_doc["id"] = str(user_doc.pop("_id"))
                return User(**user_doc)
            return None
        except Exception as e:
            logger.error(f"Error finding user by id: {e}")
            raise

    async def get_all(self, **filters) -> List[User]:
        try:
            users = []
            cursor = await self.collection.find().to_list(length=None)
            for user_doc in cursor:
                user_doc["id"] = str(user_doc.pop("_id"))
                users.append(User(**user_doc))
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            raise

    async def delete(self, entity_id: Any) -> bool:
        try:
            if isinstance(entity_id, str):
                entity_id = ObjectId(entity_id)
            result = await self.collection.delete_one({"_id": entity_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise

    async def update(self, entity_id: Any, entity: User) -> Optional[User]:
        try:
            if isinstance(entity_id, str):
                entity_id = ObjectId(entity_id)
            user_dict = entity.model_dump()

            result = await self.collection.update_one(
                {"_id": entity_id}, {"$set": user_dict}
            )
            return (
                await self.find_by_id(entity_id) if result.modified_count > 0 else None
            )
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise

    async def get_user_by_username(self, username: str) -> Optional[User]:
        try:
            user_doc = await self.collection.find_one({"username": username})
            if user_doc:
                user_doc["id"] = str(user_doc.pop("_id"))
                return User(**user_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            raise

    async def create_user(self, user: User) -> User:
        try:
            user_dict = user.model_dump(exclude={"id"})

            result = await self.collection.insert_one(user_dict)

            user_dict["id"] = str(result.inserted_id)
            return User(**user_dict)
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
