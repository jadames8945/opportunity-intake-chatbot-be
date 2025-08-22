from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ChatHistoryRequest(BaseModel):
    session_id: str
    chat_title: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = None
