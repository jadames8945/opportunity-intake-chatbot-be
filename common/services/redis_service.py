import json
import logging
import os
from typing import AsyncGenerator

from fastapi import WebSocket
from redis import Redis as RedisSync
from redis.asyncio import Redis


def get_redis_url():
    return os.getenv("REDIS_SERVER")


logger = logging.getLogger(__name__)


def get_sync_redis_client() -> RedisSync:
    return RedisSync.from_url(
        get_redis_url(),
        decode_responses=True,
        max_connections=20,
        retry_on_timeout=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        health_check_interval=30,
    )


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    """Get async Redis client - creates new connection for each request."""
    client = Redis.from_url(get_redis_url(), decode_responses=True)
    try:
        yield client
    finally:
        await client.close()


async def listen_and_forward_redis_stream(
        redis: Redis,
        result_channel: str,
        websocket: WebSocket
):
    last_id = "0-0"
    try:
        while True:
            response = await redis.xread({result_channel: last_id}, block=100, count=10)
            if response:
                stream, messages = response[0]
                for msg_id, msg in messages:
                    last_id = msg_id

                    payload = {
                        k.decode() if isinstance(k, bytes) else k: (
                            v.decode() if isinstance(v, bytes) else v
                        )
                        for k, v in msg.items()
                    }

                    if "result" in payload:
                        try:
                            payload["result"] = json.loads(payload["result"])
                        except Exception:
                            pass
                    await websocket.send_json(payload)
    except Exception as e:
        logger.error(f"Error in Redis stream listener: {e}")
