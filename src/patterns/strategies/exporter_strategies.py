from typing import List, Dict, Any
from .base import IExporterStrategy
from ...export.exporter import LeadExporter

class CSVExporterStrategy(IExporterStrategy):
    """Concrete Exporter Strategy for CSV output."""

    def __init__(self, output_dir: str = "output"):
        self.exporter = LeadExporter(output_dir=output_dir)

    def export(self, leads: List[Dict[str, Any]], filename: str = "salesforce_leads.csv") -> str:
        return self.exporter.export_to_csv(leads, filename=filename or "salesforce_leads.csv")


class JSONExporterStrategy(IExporterStrategy):
    """Concrete Exporter Strategy for JSON output."""

    def __init__(self, output_dir: str = "output"):
        self.exporter = LeadExporter(output_dir=output_dir)

    def export(self, leads: List[Dict[str, Any]], filename: str = "salesforce_leads.json") -> str:
        return self.exporter.export_to_json(leads, filename=filename or "salesforce_leads.json")


class ExcelExporterStrategy(IExporterStrategy):
    """Concrete Exporter Strategy for Excel spreadsheet (.xls/.xlsx) output."""

    def __init__(self, output_dir: str = "output"):
        self.exporter = LeadExporter(output_dir=output_dir)

    def export(self, leads: List[Dict[str, Any]], filename: str = "google_maps_website_leads.xls") -> str:
        return self.exporter.export_to_excel(leads, filename=filename or "google_maps_website_leads.xls")



class SalesforceWebToLeadExporterStrategy(IExporterStrategy):
    """Concrete Exporter Strategy for Salesforce CRM Web-to-Lead sync."""

    def __init__(self, oid: str, endpoint_url: str = None):
        self.exporter = LeadExporter()
        self.oid = oid
        self.endpoint_url = endpoint_url

    def export(self, leads: List[Dict[str, Any]], filename: str = None) -> List[bool]:
        results = []
        for lead in leads:
            res = self.exporter.sync_to_salesforce_web_to_lead(
                lead=lead,
                oid=self.oid,
                endpoint_url=self.endpoint_url
            )
            results.append(res)
        return results
