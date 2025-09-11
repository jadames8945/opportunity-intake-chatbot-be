from auth.services.session_service import SessionService
from fastapi import HTTPException, Request


def get_session_service() -> SessionService:
    return SessionService()


def get_current_user_id(
    request: Request, session_service: SessionService = None
) -> str:
    if session_service is None:
        session_service = get_session_service()

    session_id = request.cookies.get("session_id")

    user_id, _ = session_service.validate_session(session_id)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return user_id
