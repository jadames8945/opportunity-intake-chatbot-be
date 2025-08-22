import logging

from fastapi import APIRouter

from app.schemas.health_status import HealthStatus

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["Healthcheck"],
)


@router.get("", response_model=HealthStatus)
async def get_health_status():
    return HealthStatus(status="ok")
