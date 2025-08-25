import json
import logging
import uuid
from typing import Dict, Any


from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from pydantic import BaseModel
from redis.asyncio import Redis

from app.managers.ConnectionManager import ConnectionManager
from app.services.unified_service import UnifiedService
from app.util.websocket_helpers import handle_ack, handle_invoke
from common.services.redis_service import get_redis_client

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/plan",
    tags=["plan"],
)


def get_connection_manager():
    return ConnectionManager()


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        session_id: str,
        manager: ConnectionManager = Depends(get_connection_manager),
        redis: Redis = Depends(get_redis_client)
) -> None:
    try:
        await manager.connect(websocket, session_id)
        logger.info(f"WebSocket connection established for session: {session_id}")

        redis_tasks = set()

        await websocket.send_json({
            "type": "session_established",
            "session_id": session_id
        })
        logger.info(f"Session established message sent for session: {session_id}")

        try:
            while True:
                try:
                    data = await websocket.receive_text()
                    logger.info(f"Received WebSocket data for session {session_id}: {data[:100]}...")
                    
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
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error for session {session_id}: {e}")
                    try:
                        await websocket.send_json({
                            "status": "error",
                            "session_id": session_id,
                            "error": "Invalid JSON format"
                        })
                    except Exception:
                        logger.warning(f"Could not send error response to closed WebSocket for session {session_id}")
                        break
                except Exception as e:
                    logger.error(f"Error processing WebSocket message for session {session_id}: {e}")
                    try:
                        await websocket.send_json({
                            "status": "error",
                            "session_id": session_id,
                            "error": f"Message processing error: {str(e)}"
                        })
                    except Exception:
                        logger.warning(f"Could not send error response to closed WebSocket for session {session_id}")
                        break
                    
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: session_id={session_id}")
        except Exception as e:
            logger.error(f"Unexpected error in WebSocket loop for session {session_id}: {e}")
        finally:
            manager.disconnect(session_id)
            for task in redis_tasks:
                task.cancel()
                
    except Exception as e:
        logger.error(f"Failed to establish WebSocket connection for session {session_id}: {e}")
        if websocket.client_state.CONNECTED:
            await websocket.close(code=1011, reason=f"Connection error: {str(e)}")
