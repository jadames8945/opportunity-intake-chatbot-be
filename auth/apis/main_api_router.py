from fastapi import APIRouter

from auth.apis.auth.microsoft_auth_controller import microsoft_auth_router
from auth.apis.auth.router import auth_router
from auth.apis.users.router import users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(microsoft_auth_router)
api_router.include_router(users_router)
