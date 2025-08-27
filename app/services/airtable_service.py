import logging
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime
from app.schemas.airtable_submission import AirtableSubmissionRequest
from app.config.airtable_config import airtable_config

logger = logging.getLogger(__name__)


class AirtableService:
    def __init__(self):
        self.config = airtable_config
        
        if not self.config.is_configured():
            logger.warning("Airtable credentials not configured")
    
    def _build_opportunity_fields(self, submission: AirtableSubmissionRequest) -> Dict[str, Any]:
        current_date = datetime.now().strftime("%Y-%m-%d")

        return {
            "Opportunity Name": submission.data.client_name,
            "Internal Stakeholders": ["recSZpAkfxGGG26kl"],
            "Notes": f"Overview: {submission.data.opportunity_overview}\nAI Component: {submission.data.ai_component}\nDeal Size: {submission.data.deal_size}\nUrgency: {submission.data.urgency}\nAdditional: {submission.data.additional_notes}",
            # "FDE Status": "",
            "Date Created": current_date,
            "Clients": ["rech6g1CGU9J2ojbY"],
            # "Technology Preferences": [submission.data.preferred_platforms_technologies],
            "Last Updated": current_date
        }

    def _create_airtable_payload(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "records": [
                {
                    "fields": fields
                }
            ]
        }

    async def _make_airtable_request(self, url: str, headers: Dict[str, str], data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        record_id = result.get("records", [{}])[0].get("id")
                        logger.info(f"Successfully submitted to Airtable: {record_id}")
                        return {
                            "success": True,
                            "message": "Successfully submitted to Airtable",
                            "record_id": record_id
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Airtable API error: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "message": f"Airtable API error: {response.status} - {error_text}",
                            "record_id": None
                        }
        except Exception as e:
            logger.error(f"Error submitting to Airtable: {str(e)}")
            return {
                "success": False,
                "message": f"Error submitting to Airtable: {str(e)}",
                "record_id": None
            }

    async def submit_opportunity_intake(self, submission: AirtableSubmissionRequest) -> Dict[str, Any]:
        if not self.config.is_configured():
            raise Exception("Airtable not configured")

        url = self.config.get_table_url()
        headers = self.config.get_headers()

        fields = self._build_opportunity_fields(submission)
        data = self._create_airtable_payload(fields)
        
        return await self._make_airtable_request(url, headers, data)
    
    async def get_opportunity_intakes(self, username: Optional[str] = None) -> Dict[str, Any]:
        if not self.config.is_configured():
            raise Exception("Airtable not configured")
        
        url = self.config.get_table_url()
        headers = self.config.get_headers()
        
        params = {}
        if username:
            params["filterByFormula"] = f"{{Username}}='{username}'"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "message": "Successfully retrieved from Airtable",
                            "records": result.get("records", [])
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Airtable API error: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "message": f"Airtable API error: {response.status}",
                            "records": []
                        }
        except Exception as e:
            logger.error(f"Error retrieving from Airtable: {str(e)}")
            return {
                "success": False,
                "message": f"Error retrieving from Airtable: {str(e)}",
                "records": None
            } 