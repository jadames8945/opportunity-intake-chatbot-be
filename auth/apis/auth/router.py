from typing import Dict

from auth.dependencies.session_dependencies import get_session_service
from auth.exceptions.user_exceptions import (
    MissingCredentialsException,
    UserException,
    check_credentials,
)
from auth.schemas.token import Token
from auth.schemas.user import User, UserCredentials
from auth.services.auth_service import AuthService, logger
from auth.services.session_service import SessionService
from fastapi import APIRouter, Depends, HTTPException, Request, Response

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


def get_auth_service():
    return AuthService()


@auth_router.get("")
async def get_health_status():
    return {"status": "ok"}


@auth_router.post("/register", response_model=User)
async def register_user(
    response: Response,
    user: User,
    auth_service: AuthService = Depends(get_auth_service),
    session_service: SessionService = Depends(get_session_service),
) -> User:
    try:
        check_credentials(user.username, user.password)

        user_response = await auth_service.register_user(user)

        session_id = session_service.create_session(user_response.id)

        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=86400,
        )

        return user_response
    except MissingCredentialsException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@auth_router.post("/login", response_model=Token)
async def login_user(
    response: Response,
    user_credentials: UserCredentials,
    auth_service: AuthService = Depends(get_auth_service),
    session_service: SessionService = Depends(get_session_service),
) -> Token:
    try:
        check_credentials(user_credentials.username, user_credentials.password)

        token: Token = await auth_service.login_user(user_credentials)

        user_id = token.user.get("id")

        if not user_id:
            raise HTTPException(status_code=500, detail="User ID not found")

        session_id = session_service.create_session(user_id)

        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=86400,
        )

        logger.info(f"Logged in user {token.user}")

        return token
    except MissingCredentialsException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except UserException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@auth_router.post("/logout")
async def logout_user(
    request: Request,
    response: Response,
    session_service: SessionService = Depends(get_session_service),
) -> Dict[str, str]:
    session_id = request.cookies.get("session_id")

    if session_id:
        session_service.invalidate_session(session_id)

    response.delete_cookie(
        key="session_id", httponly=True, secure=False, samesite="lax"
    )

    return {"message": "Logged out successfully"}
