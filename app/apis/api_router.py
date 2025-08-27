from fastapi import APIRouter

from app.apis.healthcheck.router import router as healthcheck_router
from app.apis.plan.router import router as plan_router
from app.apis.upload.router import router as upload_router
from app.apis.chat_history.router import router as chat_history_router
from app.apis.airtable.router import router as airtable_router
from auth.apis.auth.router import auth_router
api_router = APIRouter()

api_router.include_router(plan_router)
api_router.include_router(upload_router)
api_router.include_router(healthcheck_router)
api_router.include_router(chat_history_router)
api_router.include_router(airtable_router)
api_router.include_router(auth_router)
