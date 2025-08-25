import logging
from datetime import datetime
from typing import List, Dict

from app.infrastructure import infra
from app.models.chat_history import ChatHistory

logger = logging.getLogger(__name__)


class ChatHistoryRepository:
    def __init__(self):
        self.db = infra.mongo_client.get_database_connection()
        self.collection = self.db.chat_histories

    def save_chat_history(self, title: str, chat_history: List[Dict[str, str]], username: str) -> bool:
        try:
            document = {
                "username": username,
                "title": title,
                "chat_history": chat_history,
                "created_at": datetime.utcnow()
            }

            result = self.collection.insert_one(document)
            logger.info(f"Saved chat history with ID: {result.inserted_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save chat history: {e}")
            return False

    def get_chat_history_by_title(self, title: str, username: str) -> ChatHistory | None:
        try:
            result: Dict = self.collection.find_one({"username": username, "title": title})

            return ChatHistory(**result)

        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            return None

    def get_all_chat_histories(self, username: str) -> List[Dict]:
        try:
            cursor = (self.collection
                      .find({"username": username})
                      .sort("created_at", -1))

            chat_histories = []

            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                chat_histories.append(doc)

            return chat_histories
        except Exception as e:
            logger.error(f"Failed to get chat histories: {e}")
            return []

    def delete_chat_history(self, title: str, username: str):
        try:
            self.collection.delete_one({"username": username, "title": title})

            return {"status": "success"}
        except Exception as e:
            logger.error(f"Failed to delete chat history: {e}")
            return {"status": "error"}
