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
    logger.info(f"User {current_user.username} uploading document: {file.filename}")

    try:
        file_content = await file.read()
        result = upload_service.process_document_upload(
            file_content=file_content,
            filename=file.filename,
            user_context=user_context,
        )

        return {
            "success": True,
            "message": "Document processed successfully",
            "result": result,
        }

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
