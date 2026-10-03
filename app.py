#!/usr/bin/env python3
"""
Salesforce & Local Business Website Lead Generation Engine - Web Application Server
Serves index.html (Salesforce Enterprise Leads) & website_leads.html (Google Maps Local Business Leads).
Runs on http://localhost:8000
"""

import http.server
import socketserver
import json
import os
import urllib.parse

from src.patterns import CollectorFactory, ScoringStrategyFactory, ExporterFactory
from src.processing.outreach_generator import OutreachGenerator
from src.utils.logger import get_logger

logger = get_logger("WebAppServer")
PORT = 8000

# Global cached lead stores for fast web interaction
SCANNED_LEADS = []
SCANNED_WEBSITE_LEADS = []

def run_project_scan() -> list:
    """Executes full Salesforce scan, enrichment, and scoring via Strategy & Factory patterns."""
    global SCANNED_LEADS
    logger.info("Executing Salesforce project scan via Collector & Scoring Factories...")

    job_strategy = CollectorFactory.create_collector("job_signals")
    intent_strategy = CollectorFactory.create_collector("intent_signals")
    tech_strategy = CollectorFactory.create_collector("tech_detector")
    enrichment_strategy = CollectorFactory.create_collector("enrichment")
    linkedin_strategy = CollectorFactory.create_collector("linkedin")
    linkdapi_strategy = CollectorFactory.create_collector("linkdapi")
    freelance_strategy = CollectorFactory.create_collector("freelance")

    job_leads = job_strategy.collect()
    intent_leads = intent_strategy.collect()
    freelance_leads = freelance_strategy.collect()
    seed_leads = linkdapi_strategy.collect()
    all_intent_leads = intent_leads + freelance_leads + seed_leads

    enrichment_strategy.collect(leads=job_leads + all_intent_leads)
    linkedin_strategy.collect(leads=job_leads + all_intent_leads)

    domains = list({l.get("domain") for l in job_leads + all_intent_leads if l.get("domain")})
    tech_scans = tech_strategy.collect(domains=domains)

    scoring_strategy = ScoringStrategyFactory.create_scoring_strategy("default")
    scored_leads = scoring_strategy.score_and_filter(
        job_leads=job_leads,
        tech_scans=tech_scans,
        intent_leads=all_intent_leads,
        min_confidence=60
    )

    pitch_gen = OutreachGenerator()
    for lead in scored_leads:
        lead["pitch"] = pitch_gen.generate_pitch(lead)

    SCANNED_LEADS = scored_leads
    logger.info(f"Scan complete. Retained {len(SCANNED_LEADS)} verified leads.")
    return SCANNED_LEADS


def run_website_scan() -> list:
    """Executes Google Maps local business website lead scan & scoring via Strategy & Factory patterns."""
    global SCANNED_WEBSITE_LEADS
    logger.info("Executing Google Maps local business scan via Collector & Scoring Factories...")

    gmaps_strategy = CollectorFactory.create_collector("google_maps")
    gmaps_leads = gmaps_strategy.collect()

    scoring_strategy = ScoringStrategyFactory.create_scoring_strategy("default")
    scored_leads = scoring_strategy.score_and_filter(
        job_leads=[],
        tech_scans=[],
        intent_leads=gmaps_leads,
        min_confidence=60
    )

    pitch_gen = OutreachGenerator()
    for lead in scored_leads:
        lead["pitch"] = pitch_gen.generate_pitch(lead)

    SCANNED_WEBSITE_LEADS = scored_leads
    logger.info(f"Google Maps scan complete. Retained {len(SCANNED_WEBSITE_LEADS)} verified website leads.")
    return SCANNED_WEBSITE_LEADS


class SalesforceLeadAppHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        url_path = urllib.parse.urlparse(self.path).path

        if url_path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open("index.html", "rb") as f:
                self.wfile.write(f.read())

        elif url_path == "/website_leads.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open("website_leads.html", "rb") as f:
                self.wfile.write(f.read())

        elif url_path in ["/api/scan", "/api/leads"]:
            leads = run_project_scan()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(leads).encode("utf-8"))

        elif url_path in ["/api/scan/website", "/api/website-leads"]:
            leads = run_website_scan()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(leads).encode("utf-8"))

        elif url_path in ["/api/export/csv", "/export"]:
            global SCANNED_LEADS
            if not SCANNED_LEADS:
                SCANNED_LEADS = run_project_scan()

            csv_exporter = ExporterFactory.create_exporter("csv")
            filepath = csv_exporter.export(SCANNED_LEADS, filename="salesforce_project_leads.csv")

            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="salesforce_project_leads.csv"')
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(500, "Failed to generate CSV export file.")

        elif url_path in ["/api/export/website-csv"]:
            global SCANNED_WEBSITE_LEADS
            if not SCANNED_WEBSITE_LEADS:
                SCANNED_WEBSITE_LEADS = run_website_scan()

            csv_exporter = ExporterFactory.create_exporter("csv")
            filepath = csv_exporter.export(SCANNED_WEBSITE_LEADS, filename="google_maps_website_leads.csv")

            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="google_maps_website_leads.csv"')
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(500, "Failed to generate website CSV export file.")

        elif url_path in ["/api/export/website-excel", "/api/export/excel"]:
            if not SCANNED_WEBSITE_LEADS:
                SCANNED_WEBSITE_LEADS = run_website_scan()

            excel_exporter = ExporterFactory.create_exporter("excel")
            filepath = excel_exporter.export(SCANNED_WEBSITE_LEADS, filename="google_maps_website_leads.xls")

            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.ms-excel")
                self.send_header("Content-Disposition", 'attachment; filename="google_maps_website_leads.xls"')
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(500, "Failed to generate Excel export file.")

        else:
            self.send_error(404, "Page Not Found")

    def do_POST(self):
        url_path = urllib.parse.urlparse(self.path).path

        if url_path == "/api/scan":
            leads = run_project_scan()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(leads).encode("utf-8"))
        elif url_path == "/api/scan/website":
            leads = run_website_scan()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(leads).encode("utf-8"))
        else:
            self.send_error(404, "Endpoint Not Found")


def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), SalesforceLeadAppHandler) as httpd:
        logger.info(f"🌐 Lead Generation Dashboard active at: http://localhost:{PORT}")
        logger.info(f"   ⚡ Salesforce Leads: http://localhost:{PORT}/index.html")
        logger.info(f"   🗺️ Local Business Website Leads: http://localhost:{PORT}/website_leads.html")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Dashboard server stopped.")

if __name__ == "__main__":
    run_server()
