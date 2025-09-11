import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple

from common.services.redis_service import get_sync_redis_client

logger = logging.getLogger(__name__)


class SessionService:
    def __init__(self):
        self.redis = get_sync_redis_client()
        self.session_prefix = "session:"
        self.session_ttl = 86400
        self.rotation_threshold = 1800

    def create_session(self, user_id: str) -> str:
        session_id = str(uuid.uuid4())

        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_accessed": datetime.utcnow().isoformat(),
            "rotation_count": 0,
        }

        self.redis.hset(f"{self.session_prefix}{session_id}", mapping=session_data)
        self.redis.expire(f"{self.session_prefix}{session_id}", self.session_ttl)

        logger.info(f"Created session {session_id} for user {user_id}")

        return session_id

    def validate_session(self, session_id: str) -> Tuple[Optional[str], Optional[str]]:
        if not session_id:
            return None, None

        session_key = f"{self.session_prefix}{session_id}"
        session_data = self.redis.hgetall(session_key)

        if not session_data:
            return None, None

        should_rotate, new_session_id = self._should_rotate(session_data)

        if should_rotate:
            new_session_id = self._rotate_session(session_data, session_id)
            return session_data.get("user_id"), new_session_id

        self.redis.hset(session_key, "last_accessed", datetime.utcnow().isoformat())
        self.redis.expire(session_key, self.session_ttl)
        return session_data.get("user_id"), None

    def _should_rotate(self, session_data: dict) -> Tuple[bool, Optional[str]]:
        try:
            created_at = datetime.fromisoformat(session_data["created_at"])
            rotation_count = int(session_data.get("rotation_count", 0))

            time_remaining = (
                created_at + timedelta(seconds=self.session_ttl)
            ) - datetime.utcnow()

            should_rotate = (
                time_remaining.total_seconds() < self.rotation_threshold
                and rotation_count < 10
            )

            return should_rotate, str(uuid.uuid4()) if should_rotate else None
        except:
            return False, None

    def _rotate_session(self, old_session_data: dict, old_session_id: str) -> str:
        new_session_id = str(uuid.uuid4())

        new_session_data = {
            "user_id": old_session_data["user_id"],
            "created_at": datetime.utcnow().isoformat(),
            "last_accessed": datetime.utcnow().isoformat(),
            "rotation_count": int(old_session_data.get("rotation_count", 0)) + 1,
        }

        new_session_key = f"{self.session_prefix}{new_session_id}"

        self.redis.hset(new_session_key, mapping=new_session_data)
        self.redis.expire(new_session_key, self.session_ttl)

        old_session_key = f"{self.session_prefix}{old_session_id}"
        self.redis.delete(old_session_key)

        logger.info(f"Rotated session {old_session_id} -> {new_session_id}")
        return new_session_id

    def invalidate_session(self, session_id: str) -> bool:
        if not session_id:
            return False

        session_key = f"{self.session_prefix}{session_id}"
        result = self.redis.delete(session_key)

        logger.info(f"Invalidated session {session_id}")
        return result > 0

    def invalidate_user_sessions(self, user_id: str) -> int:
        pattern = f"{self.session_prefix}*"
        sessions = self.redis.keys(pattern)
        invalidated = 0

        for session_key in sessions:
            session_data = self.redis.hgetall(session_key)
            if session_data.get("user_id") == user_id:
                self.redis.delete(session_key)
                invalidated += 1

        logger.info(f"Invalidated {invalidated} sessions for user {user_id}")
        return invalidated

    def cleanup_expired_sessions(self) -> int:
        pattern = f"{self.session_prefix}*"
        sessions = self.redis.keys(pattern)
        cleaned = 0

        for session_key in sessions:
            if not self.redis.exists(session_key):
                cleaned += 1

        logger.info(f"Cleaned up {cleaned} expired sessions")
        return cleaned
