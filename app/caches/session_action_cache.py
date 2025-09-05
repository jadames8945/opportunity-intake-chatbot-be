import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from common.redis_infrastructure import infra

logger = logging.getLogger(__name__)


class SessionActionCache:
    def __init__(self):
        self.redis = infra.redis_client
        self.cache_ttl = 3600

    def _get_cache_key(self, session_id: str) -> str:
        return f"session_actions:{session_id}"

    def add_action(
        self,
        session_id: str,
        action_type: str,
        action_data: Dict[str, Any],
        status: str = "pending",
        result: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add an action to the session cache"""
        try:
            cache_key = self._get_cache_key(session_id)

            existing_actions = self.get_session_actions(session_id)

            action = {
                "id": f"{action_type}_{datetime.now().timestamp()}",
                "type": action_type,
                "data": action_data,
                "status": status,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            }

            existing_actions.append(action)

            self.redis.set(cache_key, json.dumps(existing_actions), ex=self.cache_ttl)

            logger.info(f"Added {action_type} action to session {session_id}")

        except Exception as e:
            logger.error(f"Error adding action to session cache: {str(e)}")

    def update_action_result(
        self,
        session_id: str,
        action_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update the result of an action"""
        try:
            cache_key = self._get_cache_key(session_id)
            actions = self.get_session_actions(session_id)

            for action in actions:
                if action["id"] == action_id:
                    action["status"] = status
                    action["result"] = result
                    action["updated_at"] = datetime.now().isoformat()
                    break

            self.redis.set(cache_key, json.dumps(actions), ex=self.cache_ttl)

            logger.info(f"Updated action {action_id} status to {status}")

        except Exception as e:
            logger.error(f"Error updating action result: {str(e)}")

    def get_session_actions(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all actions for a session"""
        try:
            cache_key = self._get_cache_key(session_id)
            cached_data = self.redis.get(cache_key)

            if cached_data:
                return json.loads(cached_data)
            return []

        except Exception as e:
            logger.error(f"Error getting session actions: {str(e)}")
            return []

    def get_recent_actions(
        self, session_id: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get recent actions for context"""
        actions = self.get_session_actions(session_id)
        return actions[-limit:] if actions else []

    def get_action_by_type(
        self, session_id: str, action_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get the most recent action of a specific type"""
        actions = self.get_session_actions(session_id)

        for action in reversed(actions):
            if action["type"] == action_type:
                return action

        return None

    def add_success_action(
        self, session_id: str, action: str, result: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a success action to the session cache"""
        self.update_action_result(
            session_id=session_id,
            action_id=f"{action}_{datetime.now().timestamp()}",
            status="success",
            result=result,
        )

    def add_error_action(
        self, session_id: str, action: str, result: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add an error action to the session cache"""
        self.update_action_result(
            session_id=session_id,
            action_id=f"{action}_{datetime.now().timestamp()}",
            status="failed",
            result=result,
        )

    def add_pending_action(
        self, session_id: str, action: str, data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a pending action to the session cache and return the action ID"""
        action_id = f"{action}_{datetime.now().timestamp()}"
        self.update_action_result(
            session_id=session_id,
            action_id=action_id,
            status="pending",
            result=data,
        )
        return action_id
