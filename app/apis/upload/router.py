import logging
from typing import Any, Dict

from auth.dependencies.auth_dependencies import get_current_user
from auth.schemas.user import User
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
)

from app.services.upload_service import UploadService
from app.util.session_utils import get_user_id_and_handle_rotation

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/upload",
    tags=["upload"],
)


def get_upload_service() -> UploadService:
    return UploadService()


@router.post("/document")
async def upload_document(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    user_context: str = Form("Create a PRD based on this document"),
    current_user: User = Depends(get_current_user),
    upload_service: UploadService = Depends(get_upload_service),
) -> Dict[str, Any]:
    user_id = get_user_id_and_handle_rotation(request, response)

    try:
        logger.info(f"Processing uploaded document: {file.filename} for user {user_id}")

        content = await file.read()

        result = upload_service.process_document_upload(
            file_content=content, filename=file.filename, user_context=user_context
        )

        if result:
            return result
        else:
            raise HTTPException(
                status_code=500, detail="Failed to generate PRD from document"
            )

    except ValueError as e:
        logger.warning(f"Document upload validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Document upload processing failed")
        raise HTTPException(status_code=500, detail=str(e))
