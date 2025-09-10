import json
import logging
from typing import Set

from auth.dependencies.session_dependencies import get_session_service
from auth.services.session_service import SessionService
from common.services.redis_service import get_redis_client
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from app.services.unified_service import UnifiedService
from app.util.websocket_helpers import handle_ack, handle_invoke

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/plan",
    tags=["plan"],
)


def get_unified_service() -> UnifiedService:
    return UnifiedService()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    session_service: SessionService = Depends(get_session_service),
    redis: Redis = Depends(get_redis_client),
) -> None:
    session_id = websocket.cookies.get("session_id")

    user_id = session_service.validate_session(session_id)

    if not user_id:
        await websocket.close(code=1008, reason="Invalid session")
        return

    await websocket.accept()
    redis_tasks: Set = set()

    await websocket.send_json({"type": "session_established", "session_id": session_id})

    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(s=data)

            if data.get("type") == "ack":
                await handle_ack(data=data, redis=redis)
                continue

            await handle_invoke(
                websocket=websocket,
                data=data,
                session_id=session_id,
                redis=redis,
                redis_tasks=redis_tasks,
            )
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: session_id={session_id}")
        for task in redis_tasks:
            task.cancel()
