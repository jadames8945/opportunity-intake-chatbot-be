import asyncio
import logging
import uuid
from typing import List, Dict

from common.services.redis_service import listen_and_forward_redis_stream

logger = logging.getLogger(__name__)


async def handle_ack(data, redis):
    stream_id = data.get("stream_id")
    result_channel = data.get("result_channel")

    if stream_id and result_channel:
        try:
            await redis.xack(result_channel, "websocket-consumer-group", stream_id)
            logger.info(f"ACKed message {stream_id} on {result_channel}")
        except Exception as e:
            logger.warning(f"Failed to ACK message: {e}")


async def _validate_user_input(
        data: dict, session_id: str, websocket
) -> tuple[bool, str]:
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
        from app.infrastructure import infra

        conversation_store = infra.get_conversation_store(session_id=session_id)

        chat_history = conversation_store.get_all_messages()

        invoke_unified_stream.delay(
            user_input=user_input,
            session=session_id,
            result_channel=result_channel,
            chat_history=chat_history
        )

        logger.info(f"WebSocket task initiated for session {session_id}")
        return True

    except Exception as e:
        logger.error(f"WebSocket task failed: {e}")
        return False


async def _setup_redis_streaming(
        redis, result_channel: str, websocket, redis_tasks: set
) -> set:
    task = asyncio.create_task(
        listen_and_forward_redis_stream(
            redis=redis, result_channel=result_channel, websocket=websocket
        )
    )

    redis_tasks.add(task)
    return {t for t in redis_tasks if not t.done()}


async def handle_invoke(
        websocket,
        data,
        session_id,
        redis,
        redis_tasks,
):
    result_channel = f"invoke_result_{session_id}_{uuid.uuid4().hex}"

    is_valid, user_input = await _validate_user_input(
        data=data,
        session_id=session_id,
        websocket=websocket
    )

    if not is_valid:
        return session_id, redis_tasks

    task_success = await _invoke_background_task(
        user_input=user_input,
        session_id=session_id,
        result_channel=result_channel
    )

    if not task_success:
        await websocket.send_json(
            {
                "status": "error",
                "session_id": session_id,
                "error": "Failed to start background task",
            }
        )
        return session_id, redis_tasks

    await websocket.send_json(
        {
            "status": "in_progress",
            "session_id": session_id,
            "result_channel": result_channel,
        }
    )

    redis_tasks = await _setup_redis_streaming(
        redis,
        result_channel,
        websocket,
        redis_tasks
    )

    return session_id, redis_tasks


def queue_save_task(
        title: str,
        chat_history: List[Dict[str, str]],
        username: str
) -> str:
    try:
        from worker.tasks import save_chat_history_task
        
        task = save_chat_history_task.delay(
            title=title,
            chat_history=chat_history,
            username=username
        )
        
        task_id = str(task.id)
        logger.info(f"Queued chat history save task: {task_id}")
        
        return task_id

    except Exception as e:
        logger.error(f"Failed to queue save task: {e}")
        return str(uuid.uuid4())
