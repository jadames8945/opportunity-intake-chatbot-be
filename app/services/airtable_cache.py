import json
import logging
from typing import Dict, List, Any

from common.redis_infrastructure import infra

logger = logging.getLogger(__name__)


class AirtableCache:
    def __init__(self):
        self.redis = infra.redis_client
        self.cache_ttl = 3600

    def set_data(self, data: Dict[str, List[Dict[str, Any]]]):
        try:
            cache_key = "airtable_cache:global"
            result = self.redis.set(cache_key, json.dumps(data), ex=self.cache_ttl)
            logger.info(f"Redis set result: {result}")
            logger.info(f"Cached Airtable data with TTL {self.cache_ttl}s")
            logger.info(f"Cache key used: {cache_key}")
        except Exception as e:
            logger.error(f"Error caching Airtable data: {str(e)}")

    def get_data(self) -> Dict[str, List[Dict[str, Any]]]:
        try:
            cache_key = "airtable_cache:global"
            cached_data = self.redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return {"clients": [], "stakeholders": [], "opportunities": []}
        except Exception as e:
            logger.error(f"Error getting cached Airtable data: {str(e)}")
            return {"clients": [], "stakeholders": [], "opportunities": []}

    def clear_cache(self):
        try:
            cache_key = "airtable_cache:global"
            self.redis.delete(cache_key)
            logger.info(f"Cleared Airtable cache")
        except Exception as e:
            logger.error(f"Error clearing Airtable cache: {str(e)}")
