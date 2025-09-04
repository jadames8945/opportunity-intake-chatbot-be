import json
import logging
from datetime import datetime
from typing import Dict, List

from common.redis_infrastructure import infra

logger = logging.getLogger(__name__)


class ConversationStore:
    def __init__(self, session_id: str = None, user_id: str = None):
        self.session_id = session_id or "default"
        self.user_id = user_id
        logger.info(f"ConversationStore initialized for session: {self.session_id}")

    def _get_messages(self) -> List[Dict[str, str]]:
        messages_json = infra.redis_client.get(f"conversation:{self.session_id}")
        return json.loads(messages_json) if messages_json else []

    def _set_messages(self, messages: List[Dict[str, str]]):
        infra.redis_client.set(f"conversation:{self.session_id}", json.dumps(messages))

    def add_message(self, content: str, role: str = "user", user_id: str = None):
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        messages = self._get_messages()
        messages.append(message)
        self._set_messages(messages)
        logger.info(f"Added {role} message to conversation store for session {self.session_id}: {content[:50]}...")

    def add_conversation_turn(self, user_input: str, assistant_response: str, user_id: str = None):
        self.add_message(user_input, "user", user_id)
        self.add_message(assistant_response, "assistant", user_id)
        logger.info(f"Added conversation turn to store for session {self.session_id}: user + assistant messages")

    def get_last_n_messages(self, n: int = 10) -> List[Dict[str, str]]:
        messages = self._get_messages()
        result = messages[-n:] if messages else []
        logger.info(f"Retrieved {len(result)} messages from conversation store for session {self.session_id}")
        return result

    def get_all_messages(self) -> List[Dict[str, str]]:
        return self._get_messages().copy()

    def clear_history(self):
        infra.redis_client.delete(f"conversation:{self.session_id}")
        logger.info(f"Cleared history for session {self.session_id}")

    def set_messages(self, messages: List[Dict[str, str]]):
        self._set_messages(messages)
        logger.info(f"Set {len(messages)} messages in conversation store for session {self.session_id}")

    def get_session_id(self) -> str:
        return self.session_id


def get_or_create_conversation_store(session_id: str, user_id: str = None) -> ConversationStore:
    return ConversationStore(session_id, user_id)


def clear_session_store(session_id: str):
    infra.redis_client.delete(f"conversation:{session_id}")
    logger.info(f"Cleared conversation store for session: {session_id}")
