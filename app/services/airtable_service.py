import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from pyairtable import Api

from app.config.airtable_config import airtable_config
from app.schemas.airtable_submission import AirtableSubmissionRequest

logger = logging.getLogger(__name__)


class AirtableService:
    def __init__(self):
        self.config = airtable_config

        if not self.config.is_configured():
            logger.warning("Airtable credentials not configured")
            return

        self.api = Api(self.config.api_key)
        self.base = self.api.base(self.config.base_id)
        self.opportunity_table = self.base.table(self.config.opportunity_table_id)
        self.client_table = self.base.table(self.config.client_table_id)
        self.stakeholder_table = self.base.table(self.config.stakeholder_table_id)

    async def get_client(self, client_name: str) -> Optional[str]:
        try:
            records = self.client_table.all(formula=f"{{Name}}='{client_name}'", max_records=1)
            if records:
                record_id = records[0]['id']
                logger.info(f"Found existing client: {record_id}")
                return record_id
            else:
                logger.info(f"No existing client found for: {client_name}")
                return None
        except Exception as e:
            logger.error(f"Error getting client {client_name}: {str(e)}")
            return None

    async def get_stakeholders(self, stakeholder_names: List[str]) -> Optional[List[str]]:
        if not stakeholder_names:
            return None

        try:
            if len(stakeholder_names) == 1:
                formula = f"{{Name}}='{stakeholder_names[0]}'"
            else:
                name_conditions = [f"{{Name}}='{name}'" for name in stakeholder_names]
                formula = f"OR({', '.join(name_conditions)})"

            records = self.stakeholder_table.all(formula=formula, max_records=len(stakeholder_names))

            if records:
                record_ids = [record['id'] for record in records]
                logger.info(f"Found existing stakeholders: {record_ids}")
                return record_ids
            else:
                logger.info(f"No existing stakeholders found for: {stakeholder_names}")
                return None
        except Exception as e:
            logger.error(f"Error getting stakeholders {stakeholder_names}: {str(e)}")
            return None

    def _build_opportunity_fields(
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
            "FDE Status": submission.data.opportunity_status,
            "Urgency": submission.data.urgency,
            "Source": submission.data.opportunity_source,
            "Technology Preferences": submission.data.preferred_platforms_technologies,
            "Date Created": current_date,
            "Last Updated": current_date
        }

        if client_id:
            fields["Clients"] = [client_id]

        if stakeholder_ids:
            fields["Internal Stakeholders"] = stakeholder_ids

        return fields

    async def submit_opportunity_intake(self, submission: AirtableSubmissionRequest) -> Dict[str, Any]:
        if not self.config.is_configured():
            raise Exception("Airtable not configured")

        try:
            client_id = await self.get_client(submission.data.client_name)
            stakeholder_ids = await self.get_stakeholders(submission.data.key_stakeholders)

            fields = self._build_opportunity_fields(submission, client_id, stakeholder_ids)

            record = self.opportunity_table.create(fields)
            record_id = record['id']

            logger.info(f"Successfully submitted to Airtable: {record_id}")
            return {
                "success": True,
                "message": "Successfully submitted to Airtable",
                "record_id": record_id
            }

        except Exception as e:
            logger.error(f"Error submitting to Airtable: {str(e)}")
            return {
                "success": False,
                "message": f"Error submitting to Airtable: {str(e)}",
                "record_id": None
            }
