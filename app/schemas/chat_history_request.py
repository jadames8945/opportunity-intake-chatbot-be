from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ChatHistoryRequest(BaseModel):
    session_id: str
    username: str
    chat_title: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = None


class ChatHistoryUpdateRequest(BaseModel):
    username: str
    chat_id: str
    messages: List[Dict[str, Any]]
