import logging

from celery import Celery

from common.services.redis_service import get_redis_url

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
REDIS_URL = get_redis_url()

logging.getLogger("langchain").setLevel(logging.ERROR)
logging.getLogger("langchain_core").setLevel(logging.ERROR)
logging.getLogger("langchain_openai").setLevel(logging.ERROR)

worker_app = Celery(
    "celery",
    backend=REDIS_URL,
    broker=REDIS_URL,
)
