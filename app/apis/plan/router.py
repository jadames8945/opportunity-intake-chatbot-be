import json
import logging
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from redis.asyncio import Redis

from app.services.unified_service import UnifiedService
from app.util.websocket_helpers import handle_ack, handle_invoke
from common.services.redis_service import get_redis_client

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/plan",
    tags=["plan"],
)


def get_unified_service():
    return UnifiedService()


@router.websocket("/ws")
async def websocket_endpoint(
        websocket: WebSocket,
        redis: Redis = Depends(get_redis_client)
) -> None:
    await websocket.accept()
    session_id = str(uuid.uuid4())
    redis_tasks = set()

    await websocket.send_json({
        "type": "session_established",
        "session_id": session_id
    })

    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)

            if data.get("type") == "ack":
                await handle_ack(data, redis)
                continue

            session_id, redis_tasks = await handle_invoke(
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
