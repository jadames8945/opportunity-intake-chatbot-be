from fastapi import APIRouter, Depends, HTTPException, Response

from auth.dependencies.session_dependencies import get_session_service
from auth.schemas.microsoft_auth import MicrosoftLoginRequest
from auth.schemas.token import Token
from auth.services.microsoft_auth_service import MicrosoftAuthService
from auth.services.session_service import SessionService

microsoft_auth_router = APIRouter(prefix="", tags=["microsoft"])


def get_microsoft_auth_service():
    return MicrosoftAuthService()


@microsoft_auth_router.post("/auth/microsoft-login", response_model=Token)
async def microsoft_login(
    response: Response,
    request: MicrosoftLoginRequest,
    microsoft_auth_service: MicrosoftAuthService = Depends(get_microsoft_auth_service),
    session_service: SessionService = Depends(get_session_service),
):
    try:
        user_info = await microsoft_auth_service.validate_microsoft_token(
            request.accessToken
        )
        user = await microsoft_auth_service.get_or_create_user_from_microsoft(user_info)
        access_token = microsoft_auth_service.create_jwt_token(user)

        user_id = user.id
        if not user_id:
            raise HTTPException(status_code=500, detail="User ID not found")

        session_id = session_service.create_session(user_id)
        session_service.set_session_cookie(response=response, session_id=session_id)

        return Token(access_token=access_token, user=user.model_dump())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Microsoft login failed: {str(e)}")
