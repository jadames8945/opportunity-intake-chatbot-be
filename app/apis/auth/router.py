import logging

from fastapi import APIRouter, Depends, HTTPException

from app.exceptions.user_exceptions import check_credentials, MissingCredentialsException, UserException
from app.schemas.user import User, UserCredentials
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


def get_auth_service():
    return AuthService()


@auth_router.post("/register", response_model=User)
async def register_user(
        user: User,
        auth_service: AuthService = Depends(get_auth_service)
) -> User:
    try:
        check_credentials(user.username, user.password)

        user_response = await auth_service.register_user(user)

        return user_response
    except MissingCredentialsException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@auth_router.post("/login", response_model=User)
async def login_user(
        user_credentials: UserCredentials,
        auth_service: AuthService = Depends(get_auth_service)
) -> User:
    try:
        check_credentials(user_credentials.username, user_credentials.password)
        result = await auth_service.authenticate_user(user_credentials.username, user_credentials.password)
        logger.info(f"Logged in user {result}")
        return result
    except MissingCredentialsException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except UserException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
