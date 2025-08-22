import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)

_session_stores: Dict[str, 'ConversationStore'] = {}


class ConversationStore:
    def __init__(self, session_id: str = None, user_id: str = None):
        self.session_id = session_id or "default"
        self.user_id = user_id
        self._messages: List[Dict[str, str]] = []
        logger.info(f"ConversationStore initialized for session: {self.session_id}")

    def add_message(self, content: str, role: str = "user", user_id: str = None):
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        self._messages.append(message)
        logger.info(f"Added {role} message to conversation store for session {self.session_id}: {content[:50]}...")

    def add_conversation_turn(self, user_input: str, assistant_response: str, user_id: str = None):
        self.add_message(user_input, "user", user_id)
        self.add_message(assistant_response, "assistant", user_id)
        logger.info(f"Added conversation turn to store for session {self.session_id}: user + assistant messages")

    def get_last_n_messages(self, n: int = 10, user_id: str = None) -> List[Dict[str, str]]:
        messages = self._messages[-n:] if self._messages else []
        logger.info(f"Retrieved {len(messages)} messages from conversation store for session {self.session_id}")
        return messages

    def get_all_messages(self, user_id: str = None) -> List[Dict[str, str]]:
        return self._messages.copy()

    def clear_history(self, user_id: str = None):
        self._messages.clear()
        logger.info(f"Cleared history for session {self.session_id}")

    def set_messages(self, messages: List[Dict[str, str]]):
        """Set messages directly (used when loading from database)"""
        self._messages = messages.copy()
        logger.info(f"Set {len(messages)} messages in conversation store for session {self.session_id}")

    def get_session_id(self) -> str:
        return self.session_id


def get_or_create_conversation_store(session_id: str, user_id: str = None) -> ConversationStore:
    global _session_stores
    
    if session_id not in _session_stores:
        _session_stores[session_id] = ConversationStore(session_id, user_id)
        logger.info(f"Created new conversation store for session: {session_id}")
    else:
        logger.info(f"Reusing existing conversation store for session: {session_id}")
    
    return _session_stores[session_id]


def clear_session_store(session_id: str):
    global _session_stores
    if session_id in _session_stores:
        del _session_stores[session_id]
        logger.info(f"Cleared conversation store for session: {session_id}")
