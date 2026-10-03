from typing import Dict, Any
from ..strategies.base import IExporterStrategy
from ..strategies.exporter_strategies import (
    CSVExporterStrategy,
    JSONExporterStrategy,
    ExcelExporterStrategy,
    SalesforceWebToLeadExporterStrategy
)

class ExporterFactory:
    """
    Factory pattern class for instantiating lead export strategies.
    """

    @staticmethod
    def create_exporter(format_type: str, config: Dict[str, Any] = None) -> IExporterStrategy:
        fmt = format_type.lower().strip()
        config = config or {}
        output_dir = config.get("export_settings", {}).get("output_dir", "output")

        if fmt in ["csv", "text/csv"]:
            return CSVExporterStrategy(output_dir=output_dir)
        elif fmt in ["excel", "xlsx", "xls", "application/vnd.ms-excel"]:
            return ExcelExporterStrategy(output_dir=output_dir)
        elif fmt in ["json", "application/json"]:
            return JSONExporterStrategy(output_dir=output_dir)
        elif fmt in ["salesforce", "webtolead", "crm"]:
            oid = config.get("export_settings", {}).get("oid", "")
            url = config.get("export_settings", {}).get("salesforce_web_to_lead_url")
            return SalesforceWebToLeadExporterStrategy(oid=oid, endpoint_url=url)
        else:
            raise ValueError(f"Unknown exporter strategy format: '{format_type}'")
