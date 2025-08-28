import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

import aiohttp

from app.config.airtable_config import airtable_config
from app.schemas.airtable_submission import AirtableSubmissionRequest

logger = logging.getLogger(__name__)


class AirtableService:
    def __init__(self):
        self.config = airtable_config

        if not self.config.is_configured():
            logger.warning("Airtable credentials not configured")

    async def get_table_data(
            self,
            table_id: str,
            filter_formula: Optional[str] = None,
            max_records: int = 100
    ) -> Optional[Dict[str, Any]]:
        url = f"{self.config.get_base_url()}/{table_id}"

        headers = self.config.get_headers()

        params = {"maxRecords": max_records}

        if filter_formula:
            params["filterByFormula"] = filter_formula

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url, headers=headers, params=params) as response:
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
        result = await self.get_table_data(self.config.client_table_id, filter_formula, 1)

        if result and result.get("records"):
            record_id = result["records"][0].get("id")
            logger.info(f"Found existing client: {record_id}")
            return record_id
        else:
            logger.info(f"No existing client found for: {client_name}")
            return None

    async def get_reference_records(self, names: List[str], table_id: str, entity_type: str) -> Optional[List[str]]:
        if not names:
            return None

        if len(names) == 1:
            filter_formula = f"{{Name}}='{names[0]}'"
        else:
            name_conditions = [f"{{Name}}='{name}'" for name in names]
            filter_formula = f"OR({', '.join(name_conditions)})"

        result = await self.get_table_data(table_id, filter_formula, len(names))

        if result and result.get("records"):
            record_ids = [record.get("id") for record in result["records"]]
            logger.info(f"Found existing {entity_type}: {record_ids}")
            return record_ids
        else:
            logger.info(f"No existing {entity_type} found for: {names}")
            return None

    async def get_stakeholder(self, stakeholder_names: List[str]) -> Optional[List[str]]:
        return await self.get_reference_records(
            names=stakeholder_names,
            table_id=self.config.stakeholder_table_id,
            entity_type="stakeholders"
        )

    def _build_opportunity_payload(
            self,
            submission: AirtableSubmissionRequest,
            client_id: Optional[str] = None,
            stakeholder_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
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

        if stakeholder_ids:
            fields["Internal Stakeholders"] = stakeholder_ids

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
            
        opportunity_table_url: str = f"{self.config.get_base_url()}/{self.config.opportunity_table_id}"

        headers: Dict[str, Any] = self.config.get_headers()

        client_id: str | None = await self.get_client(submission.data.client_name)

        stakeholder_ids: List[str] | None = await self.get_stakeholder(submission.data.key_stakeholders)

        data: Dict[str, Any] = self._build_opportunity_payload(
            submission=submission,
            client_id=client_id,
            stakeholder_ids= stakeholder_ids
        )

        return await self._make_airtable_request(
            url=opportunity_table_url,
            headers=headers,
            data=data
        )
