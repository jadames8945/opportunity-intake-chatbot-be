import logging
from typing import List, Dict

from app.agent.chat_history_agent import ChatHistoryAgent
from app.config.conversation_store import get_or_create_conversation_store
from app.models.chat_history import ChatHistory
from app.repository.chat_history_repository import ChatHistoryRepository
from app.schemas.chat_history_request import ChatHistoryRequest

logger = logging.getLogger(__name__)


class ChatHistoryService:
    def __init__(self):
        self.agent = ChatHistoryAgent()
        self.repository = ChatHistoryRepository()

    def get_chat_history(self, session_id: str) -> List[Dict[str, str]]:
        logger.info(f"Getting chat history for session: {session_id}")
        
        try:
            conversation_store = get_or_create_conversation_store(session_id)
            messages = conversation_store.get_last_n_messages(10)
            logger.info(f"Retrieved {len(messages)} messages for session {session_id}")
            return messages
        except Exception as e:
            logger.error(f"Failed to get chat history for session {session_id}: {e}")
            return []

    def generate_title_stream(self, chat_history: List[Dict[str, str]]):
        return self.agent.get_chat_history_title_stream(chat_history)

    def save_to_mongodb(self, title: str, chat_history: List[Dict[str, str]]) -> bool:
        return self.repository.save_chat_history(title, chat_history)

    def get_chat_history_from_database(self, session_id: str, chat_title: str) -> List[Dict[str, str]]:
        logger.info(f"Loading chat history from database for session {session_id}, title: {chat_title}")
        chat_history_response: ChatHistory | None = self.repository.get_chat_history_by_title(chat_title)
        if chat_history_response is None:
            logger.error(f"Chat history not found for title: {chat_title}")
            raise Exception("Chat history not found")

        chat_history = chat_history_response.chat_history
        logger.info(f"Found {len(chat_history)} messages in database for title: {chat_title}")

        conversation_store = get_or_create_conversation_store(session_id)
        conversation_store.clear_history()

        if chat_history and len(chat_history) > 0:
            logger.info(f"Populating conversation store with {len(chat_history)} messages")

            conversation_store.set_messages(chat_history)
        else:
            logger.warning("No chat history found to populate conversation store")

        return chat_history

    def get_all_chat_histories(self) -> List[Dict[str, any]]:
        return self.repository.get_all_chat_histories()

    def delete_chat_history(self, request: ChatHistoryRequest, ) -> Dict[str, any]:
        conversation_store = get_or_create_conversation_store(request.session_id)
        conversation_store.clear_history()

        return self.repository.delete_chat_history(title=request.chat_title)
