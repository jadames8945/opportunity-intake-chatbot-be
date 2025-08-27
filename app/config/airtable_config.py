import os
from typing import Optional


class AirtableConfig:
    def __init__(self):
        self.base_id: Optional[str] = os.getenv("AIRTABLE_BASE_ID")
        self.api_key: Optional[str] = os.getenv("AIRTABLE_API_KEY")
        self.table_id: Optional[str] = os.getenv("AIRTABLE_TABLE_ID")
        self.table_name: str = os.getenv("AIRTABLE_TABLE_NAME", "Opportunity Intake")
    
    def is_configured(self) -> bool:
        return bool(self.base_id and self.api_key and self.table_id)
    
    def get_base_url(self) -> str:
        if not self.base_id:
            raise ValueError("AIRTABLE_BASE_ID not configured")
        return f"https://api.airtable.com/v0/{self.base_id}"
    
    def get_table_url(self) -> str:
        if not self.table_id:
            raise ValueError("AIRTABLE_TABLE_ID not configured")
        return f"{self.get_base_url()}/{self.table_id}"
    
    def get_headers(self) -> dict:
        if not self.api_key:
            raise ValueError("AIRTABLE_API_KEY not configured")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }


airtable_config = AirtableConfig() 