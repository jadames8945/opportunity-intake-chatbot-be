from auth.dependencies.session_dependencies import get_session_service
from auth.services.session_service import SessionService
from fastapi import HTTPException, Request, Response


def get_user_id_from_session(request: Request) -> str:
    session_service = get_session_service()
    session_id = request.cookies.get("session_id")
    user_id, new_session_id = session_service.validate_session(session_id)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    return user_id


def get_user_id_and_handle_rotation(request: Request, response: Response) -> str:
    session_service = get_session_service()
    session_id = request.cookies.get("session_id")
    user_id, new_session_id = session_service.validate_session(session_id)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")

    if new_session_id:
        response.set_cookie(
            key="session_id",
            value=new_session_id,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=86400,
        )

    return user_id
