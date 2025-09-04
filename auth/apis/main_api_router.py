from auth.apis.auth.router import auth_router
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(auth_router)
