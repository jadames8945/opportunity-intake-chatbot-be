import logging

from auth.dependencies.auth_dependencies import get_current_user
from auth.schemas.user import User
from fastapi import APIRouter, Depends

from app.schemas.health_status import HealthStatus

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["Healthcheck"],
)


@router.get("", response_model=HealthStatus)
async def get_health_status(current_user: User = Depends(get_current_user)):
    return HealthStatus(status="ok")
