from typing import List, Optional

from pydantic import BaseModel


class OpportunityIntakeData(BaseModel):
    opportunity_name: Optional[str] = None
    client_name: str
    jupiter_id: Optional[str] = ""
    deal_size: str
    internal_stakeholders: List[str]
    external_stakeholders: List[str]
    opportunity_overview: str
    opportunity_source: str
    opportunity_status: str
    ai_component: str
    urgency: str
    preferred_platforms_technologies: List[str]
    archetype: str
    additional_notes: Optional[str] = ""


class AirtableSubmissionRequest(BaseModel):
    data: OpportunityIntakeData
    username: str
    session_id: str
    submitted_by: str


class AirtableSubmissionResponse(BaseModel):
    success: bool
    message: str
    record_id: Optional[str] = None
