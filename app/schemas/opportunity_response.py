from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class OpportunityResponse(BaseModel):
    """Dedicated response model for opportunity intake"""

    agent_name: str = "Opportunity Intake Assistant"
    result: str

    @staticmethod
    def build_opportunity_result(
        user_input: str,
        opportunity_content: str,
    ) -> Dict[str, Any]:
        """Helper to build an opportunity response"""
        opportunity_response = OpportunityResponse(
            result=opportunity_content,
        )

        return opportunity_response.model_dump(mode="json")
