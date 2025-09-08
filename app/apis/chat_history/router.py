import logging
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends

from app.schemas.chat_history_request import (
    ChatHistoryRequest,
    ChatHistoryUpdateRequest,
)
from app.services.chat_history_service import ChatHistoryService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat_history",
    tags=["chat_history"],
)


def get_chat_history_service() -> ChatHistoryService:
    return ChatHistoryService()


@router.get("")
async def load_chat_history_on_login(
    username: str,
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service),
) -> List[Dict[str, Any]]:
    return await chat_history_service.get_all_chat_histories(username=username)


@router.post("/load")
async def load_chat_history(
    request: ChatHistoryRequest,
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service),
) -> List[Dict[str, str]]:
    logger.info(
        f"Received load request: session_id={request.session_id}, chat_title={request.chat_title}"
    )

    if (
        request.session_id is None
        or request.chat_title is None
        or request.username is None
    ):
        raise Exception("session_id, chat_title, or username cannot be None")

    return await chat_history_service.load_chat_history_into_store(
        session_id=request.session_id, messages=request.messages
    )


@router.delete("/delete")
async def delete_chat_history(
    request: ChatHistoryRequest,
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service),
) -> Dict[str, Any]:
    if not request.session_id or not request.chat_title or not request.username:
        raise Exception("session_id, chat_title, or username cannot be None")

    return await chat_history_service.delete_chat_history(request=request)


@router.post("/save")
async def save_chat_history(
    request: ChatHistoryRequest,
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service),
) -> Dict[str, str]:
    session_id = request.session_id
    username = request.username
    messages = request.messages if hasattr(request, "messages") else []

    if not session_id or not username:
        raise Exception("session_id and username cannot be None")

    if not messages:
        raise Exception("No messages provided")

    logger.info(
        f"Saving new chat history for session {session_id} with {len(messages)} messages"
    )

    stream = chat_history_service.generate_title_stream(chat_history=messages)

    if not stream:
        raise Exception("Failed to generate title")

    title = ""
    for chunk in stream:
        if chunk.content:
            title += chunk.content

    clean_title = title.strip().strip('"').strip("'")
    current_time = datetime.utcnow()

    chat_id = await chat_history_service.save_to_mongodb(
        title=clean_title, chat_history=messages, username=username
    )

    if not chat_id:
        raise Exception("Failed to save chat history")

    return {
        "title": clean_title,
        "chat_id": chat_id,
        "status": "saved",
        "created_at": current_time.isoformat(),
    }


@router.put("/")
async def update_chat_history(
    request: ChatHistoryUpdateRequest,
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service),
) -> Dict[str, str]:
    username = request.username
    chat_id = request.chat_id
    messages = request.messages

    if not chat_id or not username:
        raise Exception("chat_id and username cannot be None")

    if not messages:
        raise Exception("No messages provided")

    logger.info(
        f"Updating chat history for chat_id '{chat_id}' with {len(messages)} messages"
    )

    return await chat_history_service.update_chat_history(chat_id, messages, username)
