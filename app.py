#!/usr/bin/env python3
"""
Salesforce & Local Business Website Lead Generation Engine - Web Application Server
Serves index.html (Salesforce Enterprise Leads) & website_leads.html (Google Maps Local Business Leads).
Caches scanned leads in local JSON files (output/salesforce_scanned_leads.json & output/google_maps_scanned_leads.json).
Loads instantly from local file unless a fresh rescan is explicitly requested.
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

# Cache file paths
SALESFORCE_CACHE_PATH = os.path.join("output", "salesforce_scanned_leads.json")
WEBSITE_CACHE_PATH = os.path.join("output", "google_maps_scanned_leads.json")

# Global cached lead stores for fast in-memory web interaction
SCANNED_LEADS = []
SCANNED_WEBSITE_LEADS = []

def run_project_scan(force: bool = False) -> list:
    """
    Executes Salesforce project scan via Strategy & Factory patterns.
    If force is False and local JSON cache file exists, loads and serves instantly from file.
    Otherwise performs full live scan and caches results to local JSON file.
    """
    global SCANNED_LEADS

    if not force and os.path.exists(SALESFORCE_CACHE_PATH):
        try:
            logger.info(f"⚡ Loading Salesforce project leads instantly from local JSON file ({SALESFORCE_CACHE_PATH})...")
            with open(SALESFORCE_CACHE_PATH, "r", encoding="utf-8") as f:
                SCANNED_LEADS = json.load(f)
            logger.info(f"Loaded {len(SCANNED_LEADS)} cached leads instantly from local JSON file.")
            return SCANNED_LEADS
        except Exception as e:
            logger.warning(f"Failed to read local JSON cache file: {e}. Running fresh live scan...")

    logger.info("Executing fresh live Salesforce project scan via Collector & Scoring Factories...")

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

    # Save results to local JSON cache file
    try:
        os.makedirs("output", exist_ok=True)
        with open(SALESFORCE_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(SCANNED_LEADS, f, indent=2)
        logger.info(f"Saved {len(SCANNED_LEADS)} scanned leads to local JSON cache file ({SALESFORCE_CACHE_PATH}).")
    except Exception as e:
        logger.warning(f"Could not save JSON cache file: {e}")

    return SCANNED_LEADS


def run_website_scan(force: bool = False) -> list:
    """
    Executes Google Maps local business website lead scan & scoring via Strategy & Factory patterns.
    If force is False and local JSON cache file exists, loads and serves instantly from file.
    Otherwise performs full live scan and caches results to local JSON file.
    """
    global SCANNED_WEBSITE_LEADS

    if not force and os.path.exists(WEBSITE_CACHE_PATH):
        try:
            logger.info(f"⚡ Loading Google Maps website leads instantly from local JSON file ({WEBSITE_CACHE_PATH})...")
            with open(WEBSITE_CACHE_PATH, "r", encoding="utf-8") as f:
                SCANNED_WEBSITE_LEADS = json.load(f)
            logger.info(f"Loaded {len(SCANNED_WEBSITE_LEADS)} cached website leads instantly from local JSON file.")
            return SCANNED_WEBSITE_LEADS
        except Exception as e:
            logger.warning(f"Failed to read local website cache JSON file: {e}. Running fresh live scan...")

    logger.info("Executing fresh live Google Maps scan via Collector & Scoring Factories...")

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

    # Save results to local JSON cache file
    try:
        os.makedirs("output", exist_ok=True)
        with open(WEBSITE_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(SCANNED_WEBSITE_LEADS, f, indent=2)
        logger.info(f"Saved {len(SCANNED_WEBSITE_LEADS)} website leads to local JSON cache file ({WEBSITE_CACHE_PATH}).")
    except Exception as e:
        logger.warning(f"Could not save website JSON cache file: {e}")

    return SCANNED_WEBSITE_LEADS


class SalesforceLeadAppHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        url_path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)
        force_scan = query_params.get("force", ["false"])[0].lower() in ["true", "1", "yes"]

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
            leads = run_project_scan(force=force_scan)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(leads).encode("utf-8"))

        elif url_path in ["/api/scan/website", "/api/website-leads"]:
            leads = run_website_scan(force=force_scan)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(leads).encode("utf-8"))

        elif url_path in ["/api/export/csv", "/export"]:
            global SCANNED_LEADS
            if not SCANNED_LEADS:
                SCANNED_LEADS = run_project_scan(force=False)

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
                SCANNED_WEBSITE_LEADS = run_website_scan(force=False)

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
                SCANNED_WEBSITE_LEADS = run_website_scan(force=False)

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
        parsed_url = urllib.parse.urlparse(self.path)
        url_path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        force_scan = query_params.get("force", ["false"])[0].lower() in ["true", "1", "yes"]

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            try:
                body = json.loads(self.rfile.read(content_length).decode("utf-8"))
                if body.get("force") or body.get("fresh") or body.get("force_rescan"):
                    force_scan = True
            except Exception:
                pass

        if url_path == "/api/scan":
            leads = run_project_scan(force=force_scan)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(leads).encode("utf-8"))
        elif url_path == "/api/scan/website":
            leads = run_website_scan(force=force_scan)
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

