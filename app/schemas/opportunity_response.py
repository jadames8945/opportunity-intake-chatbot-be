from typing import Any, Dict

from pydantic import BaseModel


class OpportunityResponse(BaseModel):
    agent_name: str = "Opportunity Intake Assistant"
    result: str

    @staticmethod
    def build_opportunity_result(
        user_input: str,
        opportunity_content: str,
    ) -> Dict[str, Any]:
        opportunity_response = OpportunityResponse(
            result=opportunity_content,
        )

        return opportunity_response.model_dump(mode="json")
