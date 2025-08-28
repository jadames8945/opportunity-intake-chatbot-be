from pydantic import BaseModel
from typing import List, Optional


class OpportunityIntakeData(BaseModel):
    client_name: str
    deal_size: str
    key_stakeholders: List[str]
    opportunity_overview: str
    opportunity_source: str
    opportunity_status: str
    pursuit_lead: str
    ai_component: str
    urgency: str
    preferred_platforms_technologies: List[str]
    requested_support: List[str]
    additional_notes: Optional[str] = ""


class AirtableSubmissionRequest(BaseModel):
    data: OpportunityIntakeData
    username: str
    session_id: str


class AirtableSubmissionResponse(BaseModel):
    success: bool
    message: str
    record_id: Optional[str] = None 