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
            "Company Name", "Domain", "Category", "Project Description", "Timeline",
            "Budget", "Latitude", "Longitude", "Google Maps Link", "Contact Details",
            "Confidence Score", "Lead Score", "Grade"
        ]

        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for lead in leads:
                lat = lead.get("latitude", "")
                lon = lead.get("longitude", "")
                maps_url = lead.get("maps_url", f"https://www.google.com/maps/search/?api=1&query={lat},{lon}" if lat and lon else "")

                writer.writerow({
                    "Company Name": lead.get("company_name", ""),
                    "Domain": lead.get("domain", ""),
                    "Category": lead.get("category", "N/A"),
                    "Project Description": lead.get("project_description", lead.get("intent_signal") or lead.get("hiring_signal", "")),
                    "Timeline": lead.get("timeline", "Immediate"),
                    "Budget": lead.get("budget", "N/A"),
                    "Latitude": lat,
                    "Longitude": lon,
                    "Google Maps Link": maps_url,
                    "Contact Details": lead.get("contact_details", lead.get("contact_title", "")),
                    "Confidence Score": f"{lead.get('confidence_score', 0)}%",
                    "Lead Score": lead.get("score", 0),
                    "Grade": lead.get("grade", "B")
                })

        logger.info(f"Successfully exported {len(leads)} leads to CSV: {filepath}")
        return filepath

    def export_to_excel(self, leads: List[Dict[str, Any]], filename: str = "google_maps_website_leads.xls") -> str:
        """Exports leads list to a styled Microsoft Excel Spreadsheet (.xls/.xlsx compatible format)."""
        filepath = os.path.join(self.output_dir, filename)
        if not leads:
            logger.warning("No leads provided for Excel export.")
            return filepath

        xml_lines = [
            '<?xml version="1.0"?>',
            '<?mso-application progid="Excel.Sheet"?>',
            '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"',
            ' xmlns:o="urn:schemas-microsoft-com:office:office"',
            ' xmlns:x="urn:schemas-microsoft-com:office:excel"',
            ' xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">',
            ' <Styles>',
            '  <Style ss:ID="HeaderStyle">',
            '   <Font ss:FontName="Segoe UI" ss:Size="11" ss:Color="#FFFFFF" ss:Bold="1"/>',
            '   <Interior ss:Color="#EC4899" ss:Pattern="Solid"/>',
            '   <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>',
            '  </Style>',
            '  <Style ss:ID="DataStyle">',
            '   <Font ss:FontName="Segoe UI" ss:Size="10" ss:Color="#111827"/>',
            '   <Alignment ss:Vertical="Center"/>',
            '  </Style>',
            '  <Style ss:ID="BoldStyle">',
            '   <Font ss:FontName="Segoe UI" ss:Size="10" ss:Color="#059669" ss:Bold="1"/>',
            '   <Alignment ss:Vertical="Center"/>',
            '  </Style>',
            ' </Styles>',
            ' <Worksheet ss:Name="Google Maps Website Leads">',
            '  <Table>',
            '   <Row ss:Height="24">',
            '    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Company Name</Data></Cell>',
            '    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Domain</Data></Cell>',
            '    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Category</Data></Cell>',
            '    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Rating</Data></Cell>',
            '    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Review Count</Data></Cell>',
            '    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Project Description</Data></Cell>',
            '    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Timeline</Data></Cell>',
            '    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Est. Web Budget</Data></Cell>',
            '    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Latitude</Data></Cell>',
            '    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Longitude</Data></Cell>',
            '    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Google Maps Link</Data></Cell>',
            '    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Phone</Data></Cell>',
            '    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Location</Data></Cell>',
            '    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Confidence Score</Data></Cell>',
            '    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Lead Score</Data></Cell>',
            '    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Grade</Data></Cell>',
            '   </Row>'
        ]

        def escape_xml(val):
            return str(val or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

        for lead in leads:
            lat = lead.get("latitude", "")
            lon = lead.get("longitude", "")
            maps_url = lead.get("maps_url", f"https://www.google.com/maps/search/?api=1&query={lat},{lon}" if lat and lon else "")

            xml_lines.append('   <Row ss:Height="20">')
            xml_lines.append(f'    <Cell ss:StyleID="DataStyle"><Data ss:Type="String">{escape_xml(lead.get("company_name"))}</Data></Cell>')
            xml_lines.append(f'    <Cell ss:StyleID="DataStyle"><Data ss:Type="String">{escape_xml(lead.get("domain", ""))}</Data></Cell>')
            xml_lines.append(f'    <Cell ss:StyleID="DataStyle"><Data ss:Type="String">{escape_xml(lead.get("category", "Local Business"))}</Data></Cell>')
            xml_lines.append(f'    <Cell ss:StyleID="DataStyle"><Data ss:Type="String">{escape_xml(lead.get("rating", ""))}</Data></Cell>')
            xml_lines.append(f'    <Cell ss:StyleID="DataStyle"><Data ss:Type="String">{escape_xml(lead.get("review_count", ""))}</Data></Cell>')
            xml_lines.append(f'    <Cell ss:StyleID="DataStyle"><Data ss:Type="String">{escape_xml(lead.get("project_description", ""))}</Data></Cell>')
            xml_lines.append(f'    <Cell ss:StyleID="DataStyle"><Data ss:Type="String">{escape_xml(lead.get("timeline", "Immediate"))}</Data></Cell>')
            xml_lines.append(f'    <Cell ss:StyleID="BoldStyle"><Data ss:Type="String">{escape_xml(lead.get("estimated_budget") or lead.get("budget", ""))}</Data></Cell>')
            xml_lines.append(f'    <Cell ss:StyleID="DataStyle"><Data ss:Type="String">{escape_xml(lat)}</Data></Cell>')
            xml_lines.append(f'    <Cell ss:StyleID="DataStyle"><Data ss:Type="String">{escape_xml(lon)}</Data></Cell>')
            xml_lines.append(f'    <Cell ss:StyleID="DataStyle"><Data ss:Type="String">{escape_xml(maps_url)}</Data></Cell>')
            xml_lines.append(f'    <Cell ss:StyleID="DataStyle"><Data ss:Type="String">{escape_xml(lead.get("phone", ""))}</Data></Cell>')
            xml_lines.append(f'    <Cell ss:StyleID="DataStyle"><Data ss:Type="String">{escape_xml(lead.get("location", ""))}</Data></Cell>')
            xml_lines.append(f'    <Cell ss:StyleID="DataStyle"><Data ss:Type="String">{escape_xml(lead.get("confidence_score", 0))}%</Data></Cell>')
            xml_lines.append(f'    <Cell ss:StyleID="DataStyle"><Data ss:Type="String">{escape_xml(lead.get("score", 0))}</Data></Cell>')
            xml_lines.append(f'    <Cell ss:StyleID="DataStyle"><Data ss:Type="String">{escape_xml(lead.get("grade", "B"))}</Data></Cell>')
            xml_lines.append('   </Row>')

        xml_lines.append('  </Table>')
        xml_lines.append(' </Worksheet>')
        xml_lines.append('</Workbook>')

        with open(filepath, mode="w", encoding="utf-8") as f:
            f.write("\n".join(xml_lines))

        logger.info(f"Successfully exported {len(leads)} leads to Excel: {filepath}")
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
