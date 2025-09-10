import asyncio
import logging
import uuid
from typing import Any, Dict, List, Set, Tuple

from common.services.redis_service import listen_and_forward_redis_stream

logger = logging.getLogger(__name__)


async def handle_ack(data: Dict[str, Any], redis: Any) -> None:
    stream_id = data.get("stream_id")
    result_channel = data.get("result_channel")

    if stream_id and result_channel:
        try:
            await redis.xack(
                name=result_channel, groupname="websocket-consumer-group", id=stream_id
            )
            logger.info(f"ACKed message {stream_id} on {result_channel}")
        except Exception as e:
            logger.warning(f"Failed to ACK message: {e}")


async def _validate_user_input(
    data: Dict[str, Any], session_id: str, websocket: Any
) -> Tuple[bool, str]:
    user_input = data.get("user_input", "").strip()

    if not user_input:
        await websocket.send_json(
            {
                "status": "error",
                "session_id": session_id,
                "error": "user_input is required",
            }
        )
        return False, ""
    return True, user_input


async def _invoke_background_task(
    user_input: str, session_id: str, result_channel: str
) -> bool:
    try:
        from worker.tasks import invoke_unified_stream

        invoke_unified_stream.delay(
            user_input=user_input, session_id=session_id, result_channel=result_channel
        )

        logger.info(f"WebSocket task initiated for session {session_id}")
        return True

    except Exception as e:
        logger.error(f"WebSocket task failed: {e}")
        return False


async def _setup_redis_streaming(
    redis: Any, result_channel: str, websocket: Any, redis_tasks: Set
) -> Set:
    task = asyncio.create_task(
        coro=listen_and_forward_redis_stream(
            redis=redis, result_channel=result_channel, websocket=websocket
        )
    )

    redis_tasks.add(task)
    return {t for t in redis_tasks if not t.done()}


async def handle_invoke(
    websocket: Any,
    data: Dict[str, Any],
    session_id: str,
    redis: Any,
    redis_tasks: Set,
) -> Set:
    result_channel = f"invoke_result_{session_id}_{uuid.uuid4().hex}"

    is_valid, user_input = await _validate_user_input(
        data=data, session_id=session_id, websocket=websocket
    )

    if not is_valid:
        return redis_tasks

    task_success = await _invoke_background_task(
        user_input=user_input, session_id=session_id, result_channel=result_channel
    )

    if not task_success:
        await websocket.send_json(
            {
                "status": "error",
                "session_id": session_id,
                "error": "Failed to start background task",
            }
        )
        return redis_tasks

    await websocket.send_json(
        {
            "status": "in_progress",
            "session_id": session_id,
            "result_channel": result_channel,
        }
    )

    redis_tasks = await _setup_redis_streaming(
        redis=redis,
        result_channel=result_channel,
        websocket=websocket,
        redis_tasks=redis_tasks,
    )

    return redis_tasks
