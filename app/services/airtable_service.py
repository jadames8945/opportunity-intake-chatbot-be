import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pyairtable import Api

from app.caches.airtable_cache import AirtableCache
from app.config.airtable_config import airtable_config
from app.schemas.airtable_submission import AirtableSubmissionRequest

logger = logging.getLogger(__name__)


class AirtableService:
    def __init__(self):
        self.airtable_cache = AirtableCache()
        self.config = airtable_config

        if not self.config.is_configured():
            logger.warning("Airtable credentials not configured")
            return

        self.api = Api(self.config.api_key)
        self.base = self.api.base(self.config.base_id)
        self.opportunity_table = self.base.table(self.config.opportunity_table_id)
        self.client_table = self.base.table(self.config.client_table_id)
        self.stakeholder_table = self.base.table(self.config.stakeholder_table_id)

    async def get_all_records(self, table_id: str) -> List[Dict[str, Any]]:
        try:
            table = self.base.table(table_id)
            records = table.all()
            logger.info(f"Retrieved {len(records)} records from table {table_id}")
            return records
        except Exception as e:
            logger.error(f"Error getting records from table {table_id}: {str(e)}")
            return []

    async def get_client(self, client_name: str) -> Optional[str]:
        try:
            records = self.client_table.all(
                formula=f"{{Name}}='{client_name}'", max_records=1
            )
            if records:
                record_id = records[0]["id"]
                logger.info(f"Found existing client: {record_id}")
                return record_id
            else:
                logger.info(f"No existing client found for: {client_name}")
                return None
        except Exception as e:
            logger.error(f"Error getting client {client_name}: {str(e)}")
            return None

    async def get_stakeholders(
        self, stakeholder_names: List[str]
    ) -> Optional[List[str]]:
        if not stakeholder_names:
            return None

        try:
            if len(stakeholder_names) == 1:
                formula = f"{{Name}}='{stakeholder_names[0]}'"
            else:
                name_conditions = [f"{{Name}}='{name}'" for name in stakeholder_names]
                formula = f"OR({', '.join(name_conditions)})"

            records = self.stakeholder_table.all(
                formula=formula, max_records=len(stakeholder_names)
            )

            if records:
                record_ids = [record["id"] for record in records]
                logger.info(f"Found existing stakeholders: {record_ids}")
                return record_ids
            else:
                logger.info(f"No existing stakeholders found for: {stakeholder_names}")
                return None
        except Exception as e:
            logger.error(f"Error getting stakeholders {stakeholder_names}: {str(e)}")
            return None

    def _find_client_in_cache(
        self, client_name: str, cache_data: Dict
    ) -> Optional[str]:
        for client in cache_data.get("clients", []):
            if client.get("fields", {}).get("Name") == client_name:
                return client["id"]
        return None

    def _find_stakeholders_in_cache(
        self, stakeholder_names: List[str], cache_data: Dict
    ) -> List[str]:
        found_ids = []
        for stakeholder_name in stakeholder_names:
            for stakeholder in cache_data.get("stakeholders", []):
                if stakeholder.get("fields", {}).get("Name") == stakeholder_name:
                    found_ids.append(stakeholder["id"])
                    break
        return found_ids

    async def load_all_data_from_airtable(self) -> Dict[str, List[Dict[str, Any]]]:
        cached_data = self.airtable_cache.get_data()

        if cached_data and any(cached_data.values()):
            logger.info("Airtable cache already populated, returning cached data")
            return cached_data

        try:
            clients = await self.get_all_records(self.config.client_table_id)
            stakeholders = await self.get_all_records(self.config.stakeholder_table_id)
            opportunities = await self.get_all_records(self.config.opportunity_table_id)

            data = {
                "clients": clients,
                "stakeholders": stakeholders,
                "opportunities": opportunities,
            }

            self.airtable_cache.set_data(data)

            logger.info(
                f"Cached Airtable data: {len(clients)} clients, {len(stakeholders)} stakeholders, {len(opportunities)} opportunities"
            )

            return data
        except Exception as e:
            logger.error(f"Error loading Airtable data: {str(e)}")
            return {"clients": [], "stakeholders": [], "opportunities": []}

    async def check_opportunity_name_exists(
        self, opportunity_name: str, cache_data: Dict[str, List[Dict[str, Any]]]
    ) -> bool:
        try:
            for opportunity in cache_data.get("opportunities", []):
                if (
                    opportunity.get("fields", {}).get("Opportunity Name")
                    == opportunity_name
                ):
                    return True

            records = self.opportunity_table.all(
                formula=f"{{Opportunity Name}}='{opportunity_name}'", max_records=1
            )

            return len(records) > 0

        except Exception as e:
            logger.error(f"Error checking opportunity name existence: {str(e)}")
            return False

    def _build_opportunity_fields(
        self,
        submission: AirtableSubmissionRequest,
        opportunity_name: str,
        client_id: Optional[str] = None,
        stakeholder_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        current_date = datetime.now().strftime("%Y-%m-%d")

        fields = {
            "Opportunity Name": opportunity_name,
            "Opportunity ID": submission.data.jupiter_id,
            "Notes": f"Overview: {submission.data.opportunity_overview}\nAI Component: {submission.data.ai_component}\n\nUrgency: {submission.data.urgency}\nAdditional: {submission.data.additional_notes}\nSubmitted by: {submission.submitted_by}",
            "Opportunity Size": submission.data.deal_size,
            "Archetype": submission.data.archetype,
            "FDE Status": submission.data.opportunity_status,
            "Urgency": submission.data.urgency,
            "Source": submission.data.opportunity_source,
            "Technology Preferences": (
                ", ".join(submission.data.preferred_platforms_technologies)
                if submission.data.preferred_platforms_technologies
                else ""
            ),
            "AI Pattern": submission.data.ai_component,
            "Date Created": current_date,
            "Last Updated": current_date,
        }

        if client_id:
            fields["Clients"] = [client_id]

        if stakeholder_ids:
            fields["Internal Stakeholders"] = stakeholder_ids

        return fields

    async def submit_opportunity_intake(
        self, submission: AirtableSubmissionRequest
    ) -> Dict[str, Any]:
        if not self.config.is_configured():
            raise Exception("Airtable not configured")

        try:
            cache_data = self.airtable_cache.get_data()

            opportunity_name = (
                submission.data.opportunity_name or submission.data.client_name
            )

            if await self.check_opportunity_name_exists(
                opportunity_name=opportunity_name, cache_data=cache_data
            ):
                return {
                    "success": False,
                    "message": f"An opportunity with the name '{opportunity_name}' already exists. Please choose a different name.",
                    "record_id": None,
                    "duplicate_name": opportunity_name,
                }

            client_id = self._find_client_in_cache(
                submission.data.client_name, cache_data
            )
            if client_id is None:
                client_id = await self.get_client(submission.data.client_name)

            stakeholder_ids = self._find_stakeholders_in_cache(
                submission.data.internal_stakeholders, cache_data
            )
            if len(stakeholder_ids) != len(submission.data.internal_stakeholders):
                stakeholder_ids = await self.get_stakeholders(
                    submission.data.internal_stakeholders
                )

            fields = self._build_opportunity_fields(
                submission=submission,
                client_id=client_id,
                stakeholder_ids=stakeholder_ids,
                opportunity_name=opportunity_name,
            )

            record = self.opportunity_table.create(fields, typecast=True)

            record_id = record["id"]

            await self._update_cache_with_new_opportunity(
                new_record=record, cache_data=cache_data
            )

            logger.info(f"Successfully submitted to Airtable: {record_id}")

            return {
                "success": True,
                "message": "Successfully submitted to Airtable",
                "record_id": record_id,
            }

        except Exception as e:
            logger.error(f"Error submitting to Airtable: {str(e)}")
            return {
                "success": False,
                "message": f"Error submitting to Airtable: {str(e)}",
                "record_id": None,
            }

    async def _update_cache_with_new_opportunity(
        self, new_record: Dict[str, Any], cache_data: Dict[str, List[Dict[str, Any]]]
    ):
        try:
            if "opportunities" not in cache_data:
                cache_data["opportunities"] = []

            cache_data["opportunities"].append(new_record)

            self.airtable_cache.set_data(cache_data)

            logger.info(
                f"Updated cache with new opportunity: {new_record.get('id', 'unknown')}"
            )

        except Exception as e:
            logger.error(f"Error updating cache with new opportunity: {str(e)}")
