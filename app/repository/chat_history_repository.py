import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from app.infrastructure import infra
from app.models.chat_history import ChatHistory

logger = logging.getLogger(__name__)


class ChatHistoryRepository:
    def __init__(self) -> None:
        self.db = infra.mongo_client.get_database_connection()
        self.collection = self.db.chat_histories

    async def save_chat_history(
        self, title: str, chat_history: List[Dict[str, str]], username: str
    ) -> Optional[str]:
        try:
            document = {
                "session_id": str(uuid.uuid4()),
                "username": username,
                "title": title,
                "chat_history": chat_history,
                "created_at": datetime.utcnow(),
            }

            result = await self.collection.insert_one(document=document)
            logger.info(f"Saved chat history with ID: {result.inserted_id}")
            return str(result.inserted_id)

        except Exception as e:
            logger.error(f"Failed to save chat history: {e}")
            return None

    async def get_chat_history_by_title(
        self, title: str, username: str
    ) -> Optional[ChatHistory]:
        try:
            result: Dict = await self.collection.find_one(
                filter={"username": username, "title": title}
            )

            return ChatHistory(**result)

        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            return None

    async def update_chat_history(
        self, chat_id: str, messages: List[Dict[str, str]], username: str
    ) -> bool:
        try:
            from bson import ObjectId

            result = await self.collection.update_one(
                {"_id": ObjectId(chat_id), "username": username},
                {
                    "$set": {
                        "chat_history": messages,
                        "updated_at": datetime.utcnow(),
                    }
                },
            )

            if result.modified_count > 0:
                logger.info(f"Updated chat history for chat_id: {chat_id}")
                return True
            else:
                logger.warning(
                    f"No chat history found to update for chat_id: {chat_id}"
                )
                return False

        except Exception as e:
            logger.error(f"Failed to update chat history: {e}")
            return False

    async def get_all_chat_histories(self, username: str) -> List[Dict[str, Any]]:
        try:
            cursor = self.collection.find(filter={"username": username}).sort(
                "created_at", -1
            )

            chat_histories = []

            docs = await cursor.to_list(length=None)
            for doc in docs:
                doc["_id"] = str(doc["_id"])
                chat_histories.append(doc)

            return chat_histories
        except Exception as e:
            logger.error(f"Failed to get chat histories: {e}")
            return []

    async def delete_chat_history(self, title: str, username: str) -> Dict[str, str]:
        try:
            await self.collection.delete_one(
                filter={"username": username, "title": title}
            )

            return {"status": "success"}
        except Exception as e:
            logger.error(f"Failed to delete chat history: {e}")
            return {"status": "error"}
