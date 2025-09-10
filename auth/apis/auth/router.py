from auth.exceptions.user_exceptions import (
    MissingCredentialsException,
    UserException,
    check_credentials,
)
from auth.schemas.token import Token
from auth.schemas.user import User, UserCredentials
from auth.services.auth_service import AuthService, logger
from fastapi import APIRouter, Depends, HTTPException, Response

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
) -> User:
    try:
        check_credentials(user.username, user.password)

        session_id = auth_service.create_session_id()

        user_response = await auth_service.register_user(user)

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
) -> Token:
    try:
        check_credentials(user_credentials.username, user_credentials.password)

        session_id = auth_service.create_session_id()

        result = await auth_service.login_user(user_credentials)

        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=86400,
        )

        logger.info(f"Logged in user {result.user}")

        return result
    except MissingCredentialsException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except UserException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
