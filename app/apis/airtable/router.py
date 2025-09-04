import logging

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.airtable_submission import (
    AirtableSubmissionRequest,
    AirtableSubmissionResponse,
)
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
    airtable_service: AirtableService = Depends(get_airtable_service),
):
    try:
        result = await airtable_service.submit_opportunity_intake(submission)

        if result["success"]:
            return AirtableSubmissionResponse(
                success=True, message=result["message"], record_id=result["record_id"]
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    except Exception as e:
        logger.error(f"Error submitting opportunity intake: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/load-cache")
async def load_airtable_cache(
    airtable_service: AirtableService = Depends(get_airtable_service),
):
    try:
        data = await airtable_service.load_all_data_from_airtable()

        total_records = (
            len(data["clients"])
            + len(data["stakeholders"])
            + len(data["opportunities"])
        )

        return {
            "success": True,
            "message": f"Successfully loaded {total_records} records from Airtable",
            "data": {
                "clients_count": len(data["clients"]),
                "stakeholders_count": len(data["stakeholders"]),
                "opportunities_count": len(data["opportunities"]),
            },
        }

    except Exception as e:
        logger.error(f"Error loading Airtable cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
