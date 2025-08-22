import logging
from typing import Dict

from pymongo import MongoClient

from common.mongo_infrastructure import infra as mongo_infra
from common.redis_infrastructure import infra as redis_infra
from app.config.conversation_store import get_or_create_conversation_store

logger = logging.getLogger(__name__)


class AppInfrastructure:
    def __init__(self):
        self._initialized: bool = False

    def setup(self):
        if self._initialized:
            return

        try:
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize app infrastructure: {e}")
            raise

    def get_conversation_store(self, session_id: str):
        return get_or_create_conversation_store(session_id)

    @property
    def redis_client(self):
        return redis_infra.redis_client

    @property
    def mongo_client(self) -> MongoClient:
        return mongo_infra.mongo_config

    def is_initialized(self) -> bool:
        return self._initialized


infra = AppInfrastructure()
