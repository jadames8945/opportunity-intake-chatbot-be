from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel


class ChatHistory(BaseModel):
    username: str
    title: str
    chat_history: List[Dict[str, str]]
    created_at: datetime
