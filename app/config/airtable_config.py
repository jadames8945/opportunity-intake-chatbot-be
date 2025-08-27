import os
from typing import Optional


class AirtableConfig:
    def __init__(self):
        self.base_id: str = "appUbE4r8Z4HaPdwI"
        self.api_key: Optional[str] = os.getenv("AIRTABLE_API_KEY")
        self.table_name: str = os.getenv("AIRTABLE_TABLE_NAME", "Opportunity Intake")

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def get_base_url(self) -> str:
        return f"https://api.airtable.com/v0/{self.base_id}"

    def get_headers(self) -> dict:
        if not self.api_key:
            raise ValueError("AIRTABLE_API_KEY not configured")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }


airtable_config = AirtableConfig()
