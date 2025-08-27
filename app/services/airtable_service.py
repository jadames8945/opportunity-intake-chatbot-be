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
    
    async def get_table_data(self, table_id: str, filter_formula: Optional[str] = None, max_records: int = 100) -> Optional[Dict[str, Any]]:
        url = f"{self.config.get_base_url()}/{table_id}"
        headers = self.config.get_headers()
        
        params = {"maxRecords": max_records}
        if filter_formula:
            params["filterByFormula"] = filter_formula
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Successfully retrieved data from table {table_id}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to get data from table {table_id}: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error getting data from table {table_id}: {str(e)}")
            return None
    
    async def get_client(self, client_name: str) -> Optional[str]:
        filter_formula = f"{{Name}}='{client_name}'"
        result = await self.get_table_data("tbl3HMYotN9F1qWjP", filter_formula, 1)
        
        if result and result.get("records"):
            record_id = result["records"][0].get("id")
            logger.info(f"Found existing client: {record_id}")
            return record_id
        else:
            logger.info(f"No existing client found for: {client_name}")
            return None
    
    async def get_stakeholder(self, stakeholder_name: str) -> Optional[str]:
        filter_formula = f"{{Name}}='{stakeholder_name}'"
        result = await self.get_table_data("tblbbJI9qgVo8ZHtz", filter_formula, 1)
        
        if result and result.get("records"):
            record_id = result["records"][0].get("id")
            logger.info(f"Found existing stakeholder: {record_id}")
            return record_id
        else:
            logger.info(f"No existing stakeholder found for: {stakeholder_name}")
            return None

    def _build_opportunity_fields(self, submission: AirtableSubmissionRequest, client_id: Optional[str] = None, stakeholder_id: Optional[str] = None) -> Dict[str, Any]:
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        fields = {
            "Opportunity Name": submission.data.client_name,
            "Notes": f"Overview: {submission.data.opportunity_overview}\nAI Component: {submission.data.ai_component}\n\nUrgency: {submission.data.urgency}\nAdditional: {submission.data.additional_notes}",
            "Opportunity Size": submission.data.deal_size,
            "Date Created": current_date,
            "Last Updated": current_date
        }
        
        if client_id:
            fields["Clients"] = [client_id]
        
        if stakeholder_id:
            fields["Internal Stakeholders"] = [stakeholder_id]
        
        return fields
    
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
        
        client_id = await self.get_client(submission.data.client_name)

        stakeholder_id = await self.get_stakeholder(submission.data.pursuit_lead)
        
        fields = self._build_opportunity_fields(submission, client_id, stakeholder_id)

        data = self._create_airtable_payload(fields)
        
        return await self._make_airtable_request(url, headers, data) 