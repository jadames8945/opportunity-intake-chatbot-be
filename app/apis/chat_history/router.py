import logging
from datetime import datetime
from typing import Any, Dict, List

from auth.dependencies.auth_dependencies import get_current_user
from auth.schemas.user import User
from fastapi import APIRouter, Depends, Request, Response

from app.schemas.chat_history_request import (
    ChatHistoryRequest,
    ChatHistoryUpdateRequest,
)
from app.services.chat_history_service import ChatHistoryService
from app.util.session_utils import get_user_id_and_handle_rotation

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat_history",
    tags=["chat_history"],
)


def get_chat_history_service() -> ChatHistoryService:
    return ChatHistoryService()


@router.get("")
async def load_chat_history_on_login(
    current_user: User = Depends(get_current_user),
    username: str = None,
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service),
) -> List[Dict[str, Any]]:
    return await chat_history_service.get_all_chat_histories(
        username=current_user.username
    )


@router.post("/load")
async def load_chat_history(
    request: Request,
    response: Response,
    chat_history_request: ChatHistoryRequest,
    current_user: User = Depends(get_current_user),
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service),
) -> List[Dict[str, str]]:
    user_id = get_user_id_and_handle_rotation(request, response)

    logger.info(
        f"Received load request: user_id={user_id}, chat_title={chat_history_request.chat_title}"
    )

    if chat_history_request.chat_title is None or chat_history_request.username is None:
        raise Exception("chat_title or username cannot be None")

    return await chat_history_service.load_chat_history_into_store(
        session_id=user_id, messages=chat_history_request.messages
    )


@router.delete("/delete")
async def delete_chat_history(
    request: Request,
    response: Response,
    chat_history_request: ChatHistoryRequest,
    current_user: User = Depends(get_current_user),
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service),
) -> Dict[str, Any]:
    user_id = get_user_id_and_handle_rotation(request, response)

    logger.info(
        f"Delete request from user_id={user_id} for chat_title={chat_history_request.chat_title}"
    )

    if not chat_history_request.chat_title or not chat_history_request.username:
        raise Exception("chat_title or username cannot be None")

    return await chat_history_service.delete_chat_history(
        request=chat_history_request, user_id=user_id
    )


@router.post("/save")
async def save_chat_history(
    request: Request,
    response: Response,
    chat_history_request: ChatHistoryRequest,
    current_user: User = Depends(get_current_user),
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service),
) -> Dict[str, str]:
    user_id = get_user_id_and_handle_rotation(request, response)

    username = chat_history_request.username

    messages = (
        chat_history_request.messages
        if hasattr(chat_history_request, "messages")
        else []
    )

    if not username:
        raise Exception("username cannot be None")

    if not messages:
        raise Exception("No messages provided")

    logger.info(
        f"Saving new chat history for user {user_id} with {len(messages)} messages"
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
    request: Request,
    response: Response,
    chat_history_request: ChatHistoryUpdateRequest,
    current_user: User = Depends(get_current_user),
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service),
) -> Dict[str, str]:
    user_id = get_user_id_and_handle_rotation(request, response)

    username = chat_history_request.username
    chat_id = chat_history_request.chat_id
    messages = chat_history_request.messages

    if not chat_id or not username:
        raise Exception("chat_id and username cannot be None")

    if not messages:
        raise Exception("No messages provided")

    logger.info(
        f"Updating chat history for chat_id '{chat_id}' with {len(messages)} messages"
    )

    return await chat_history_service.update_chat_history(chat_id, messages, username)
