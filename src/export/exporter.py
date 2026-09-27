import csv
import json
import os
import requests
from typing import List, Dict, Any
from ..utils.logger import get_logger

logger = get_logger("LeadExporter")

class LeadExporter:
    """
    Handles exporting lead data into CSV, JSON, or syncing directly to Salesforce CRM via Web-to-Lead endpoint.
    """

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def export_to_csv(self, leads: List[Dict[str, Any]], filename: str = "salesforce_leads.csv") -> str:
        """Exports leads list to a structured CSV file."""
        filepath = os.path.join(self.output_dir, filename)
        if not leads:
            logger.warning("No leads provided for CSV export.")
            return filepath

        fieldnames = [
            "company_name", "domain", "score", "grade",
            "hiring_signal", "hiring_count", "intent_signal",
            "tech_footprint", "location", "contact_title"
        ]

        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for lead in leads:
                row = lead.copy()
                if isinstance(row.get("tech_footprint"), list):
                    row["tech_footprint"] = "; ".join(row["tech_footprint"])
                writer.writerow(row)

        logger.info(f"Successfully exported {len(leads)} leads to CSV: {filepath}")
        return filepath

    def export_to_json(self, leads: List[Dict[str, Any]], filename: str = "salesforce_leads.json") -> str:
        """Exports leads list to a JSON file."""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, mode="w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2)

        logger.info(f"Successfully exported {len(leads)} leads to JSON: {filepath}")
        return filepath

    def sync_to_salesforce_web_to_lead(self, lead: Dict[str, Any], oid: str, endpoint_url: str = None) -> bool:
        """
        Submits a lead directly into Salesforce CRM via Salesforce Web-to-Lead HTML form action.
        """
        if not oid:
            logger.error("Salesforce Org ID (OID) is required for Web-to-Lead sync.")
            return False

        url = endpoint_url or "https://webto.salesforce.com/servlet/servlet.WebToLead?encoding=UTF-8"
        payload = {
            "oid": oid,
            "company": lead.get("company_name", "Unknown Company"),
            "last_name": lead.get("contact_title", "Salesforce Project Lead"),
            "email": f"info@{lead.get('domain', 'example.com')}",
            "description": f"Lead Score: {lead.get('score')} ({lead.get('grade')}). Signal: {lead.get('intent_signal') or lead.get('hiring_signal')}",
            "lead_source": "Salesforce Lead Generation Engine"
        }

        try:
            logger.info(f"Pushing lead '{lead.get('company_name')}' to Salesforce Web-to-Lead...")
            response = requests.post(url, data=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"Lead successfully posted to Salesforce Web-to-Lead.")
                return True
            else:
                logger.warning(f"Salesforce Web-to-Lead returned status {response.status_code}.")
                return False
        except Exception as e:
            logger.error(f"Failed to submit lead to Salesforce Web-to-Lead: {str(e)}")
            return False
