import logging
from typing import List, Dict
from datetime import datetime

from fastapi import APIRouter, Depends

from app.schemas.chat_history_request import ChatHistoryRequest
from app.services.chat_history_service import ChatHistoryService
from app.util.websocket_helpers import queue_save_task

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat_history",
    tags=["chat_history"],
)


def get_chat_history_service() -> ChatHistoryService:
    return ChatHistoryService()


@router.get("")
def load_chat_history_on_login(
    username: str,
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service)
):
    return chat_history_service.get_all_chat_histories(username)


@router.post("/load")
def load_chat_history(
        request: ChatHistoryRequest,
        chat_history_service: ChatHistoryService = Depends(get_chat_history_service),
) -> List[Dict[str, str]]:
    logger.info(f"Received load request: session_id={request.session_id}, chat_title={request.chat_title}")

    if request.session_id is None or request.chat_title is None or request.username is None:
        raise Exception(f"session_id, chat_title, or username cannot be None")

    return chat_history_service.get_chat_history_from_database(
        session_id=request.session_id,
        chat_title=request.chat_title,
        username=request.username
    )


@router.delete("/delete")
def delete_chat_history(
        request: ChatHistoryRequest,
        chat_history_service: ChatHistoryService = Depends(get_chat_history_service)
) -> Dict[str, str]:
    if not request.session_id or not request.chat_title or not request.username:
        raise Exception("session_id, chat_title, or username cannot be None")

    return chat_history_service.delete_chat_history(request)


@router.post("/save")
async def save_chat_history(
        request: ChatHistoryRequest,
        chat_history_service: ChatHistoryService = Depends(get_chat_history_service),
) -> Dict[str, str]:
    session_id = request.session_id
    username = request.username
    messages = request.messages if hasattr(request, 'messages') else []

    if not session_id or not username:
        raise Exception("session_id and username cannot be None")

    if not messages:
        raise Exception("No messages provided")

    logger.info(f"Saving chat history for session {session_id} with {len(messages)} messages")

    stream = chat_history_service.generate_title_stream(messages)

    if not stream:
        raise Exception("Failed to generate title")

    title = ""
    for chunk in stream:
        if chunk.content:
            title += chunk.content

    clean_title = title.strip().strip('"').strip("'")
    current_time = datetime.utcnow()

    task_id = queue_save_task(title=clean_title, chat_history=messages, username=username)

    return {"title": clean_title, "task_id": task_id, "status": "queued", "created_at": current_time.isoformat()}
