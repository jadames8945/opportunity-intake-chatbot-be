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


@router.get("/opportunities")
async def get_opportunity_intakes(
    username: str = None,
    airtable_service: AirtableService = Depends(get_airtable_service)
):
    try:
        result = await airtable_service.get_opportunity_intakes(username)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "records": result["records"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        logger.error(f"Error retrieving opportunity intakes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def airtable_health_check(
    airtable_service: AirtableService = Depends(get_airtable_service)
):
    try:
        base_id = airtable_service.base_id
        api_key = airtable_service.api_key
        
        if not base_id or not api_key:
            return {
                "status": "unconfigured",
                "message": "Airtable credentials not configured"
            }
        
        return {
            "status": "configured",
            "message": "Airtable service is configured and ready"
        }
        
    except Exception as e:
        logger.error(f"Error checking Airtable health: {str(e)}")
        return {
            "status": "error",
            "message": f"Error checking Airtable health: {str(e)}"
        } 