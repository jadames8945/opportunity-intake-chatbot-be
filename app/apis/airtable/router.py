import logging
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.airtable_submission import AirtableSubmissionRequest, AirtableSubmissionResponse
from app.services.airtable_service import AirtableService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/airtable",
    tags=["airtable"],
)


def get_airtable_service():
    return AirtableService()


@router.post("/submit", response_model=AirtableSubmissionResponse)
async def submit_opportunity_intake(
    submission: AirtableSubmissionRequest,
    airtable_service: AirtableService = Depends(get_airtable_service)
):
    try:
        result = await airtable_service.submit_opportunity_intake(submission)
        
        if result["success"]:
            return AirtableSubmissionResponse(
                success=True,
                message=result["message"],
                record_id=result["record_id"]
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        logger.error(f"Error submitting opportunity intake: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 