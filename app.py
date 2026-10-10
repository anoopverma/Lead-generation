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
import hashlib
import secrets

from src.patterns import CollectorFactory, ScoringStrategyFactory, ExporterFactory
from src.processing.outreach_generator import OutreachGenerator
from src.utils.logger import get_logger

logger = get_logger("WebAppServer")

def load_env_file(env_path: str = ".env"):
    """Loads key=value pairs from .env file into os.environ if present."""
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                if key and key not in os.environ:
                    os.environ[key] = val

load_env_file()

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
PORT = int(os.environ.get("PORT", 8000))

ACTIVE_SESSIONS = set()

def generate_session_token(username: str) -> str:
    token = hashlib.sha256(f"{username}:{secrets.token_hex(16)}".encode("utf-8")).hexdigest()
    ACTIVE_SESSIONS.add(token)
    return token

def verify_session(cookie_header: str) -> bool:
    if not cookie_header:
        return False
    cookies = urllib.parse.parse_qs(cookie_header.replace("; ", "&"))
    session_ids = cookies.get("session_id", [])
    for sid in session_ids:
        if sid in ACTIVE_SESSIONS:
            return True
    return False


# Cache file paths
SALESFORCE_CACHE_PATH = os.path.join("output", "salesforce_scanned_leads.json")
WEBSITE_CACHE_PATH = os.path.join("output", "google_maps_scanned_leads.json")
INDIA_CACHE_PATH = os.path.join("output", "india_scanned_leads.json")
DELHI_NCR_CACHE_PATH = os.path.join("output", "delhi_ncr_scanned_leads.json")
DEVOPS_CACHE_PATH = os.path.join("output", "devops_scanned_leads.json")

# Global cached lead stores for fast in-memory web interaction
SCANNED_LEADS = []
SCANNED_WEBSITE_LEADS = []
SCANNED_INDIA_LEADS = []
SCANNED_DELHI_NCR_LEADS = []
SCANNED_DEVOPS_LEADS = []


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


def run_india_scan(force: bool = False) -> list:
    """
    Executes India-exclusive Salesforce & Website lead scan & scoring via Strategy & Factory patterns.
    If force is False and local JSON cache file exists, loads and serves instantly from file.
    Otherwise performs full live scan and caches results to local JSON file.
    """
    global SCANNED_INDIA_LEADS

    if not force and os.path.exists(INDIA_CACHE_PATH):
        try:
            logger.info(f"⚡ Loading India leads instantly from local JSON file ({INDIA_CACHE_PATH})...")
            with open(INDIA_CACHE_PATH, "r", encoding="utf-8") as f:
                SCANNED_INDIA_LEADS = json.load(f)
            logger.info(f"Loaded {len(SCANNED_INDIA_LEADS)} cached India leads instantly from local JSON file.")
            return SCANNED_INDIA_LEADS
        except Exception as e:
            logger.warning(f"Failed to read local India cache JSON file: {e}. Running fresh live scan...")

    logger.info("Executing fresh live India scan via Collector & Scoring Factories...")

    india_strategy = CollectorFactory.create_collector("india")
    india_leads = india_strategy.collect()

    scoring_strategy = ScoringStrategyFactory.create_scoring_strategy("default")
    scored_leads = scoring_strategy.score_and_filter(
        job_leads=[],
        tech_scans=[],
        intent_leads=india_leads,
        min_confidence=60
    )

    pitch_gen = OutreachGenerator()
    for lead in scored_leads:
        lead["pitch"] = pitch_gen.generate_pitch(lead)

    SCANNED_INDIA_LEADS = scored_leads

    # Save results to local JSON cache file
    try:
        os.makedirs("output", exist_ok=True)
        with open(INDIA_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(SCANNED_INDIA_LEADS, f, indent=2)
        logger.info(f"Saved {len(SCANNED_INDIA_LEADS)} India leads to local JSON cache file ({INDIA_CACHE_PATH}).")
    except Exception as e:
        logger.warning(f"Could not save India JSON cache file: {e}")

    return SCANNED_INDIA_LEADS


def run_delhi_ncr_scan(force: bool = False) -> list:
    """
    Executes Delhi-NCR local business website lead scan & scoring via Strategy & Factory patterns.
    If force is False and local JSON cache file exists, loads and serves instantly from file.
    Otherwise performs full live scan and caches results to local JSON file.
    """
    global SCANNED_DELHI_NCR_LEADS

    if not force and os.path.exists(DELHI_NCR_CACHE_PATH):
        try:
            logger.info(f"⚡ Loading Delhi-NCR leads instantly from local JSON file ({DELHI_NCR_CACHE_PATH})...")
            with open(DELHI_NCR_CACHE_PATH, "r", encoding="utf-8") as f:
                SCANNED_DELHI_NCR_LEADS = json.load(f)
            logger.info(f"Loaded {len(SCANNED_DELHI_NCR_LEADS)} cached Delhi-NCR leads instantly from local JSON file.")
            return SCANNED_DELHI_NCR_LEADS
        except Exception as e:
            logger.warning(f"Failed to read local Delhi-NCR cache JSON file: {e}. Running fresh live scan...")

    logger.info("Executing fresh live Delhi-NCR scan via Collector & Scoring Factories...")

    delhi_strategy = CollectorFactory.create_collector("delhi_ncr")
    delhi_leads = delhi_strategy.collect()

    scoring_strategy = ScoringStrategyFactory.create_scoring_strategy("default")
    scored_leads = scoring_strategy.score_and_filter(
        job_leads=[],
        tech_scans=[],
        intent_leads=delhi_leads,
        min_confidence=60
    )

    pitch_gen = OutreachGenerator()
    for lead in scored_leads:
        lead["pitch"] = pitch_gen.generate_pitch(lead)

    SCANNED_DELHI_NCR_LEADS = scored_leads

    # Save results to local JSON cache file
    try:
        os.makedirs("output", exist_ok=True)
        with open(DELHI_NCR_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(SCANNED_DELHI_NCR_LEADS, f, indent=2)
        logger.info(f"Saved {len(SCANNED_DELHI_NCR_LEADS)} Delhi-NCR leads to local JSON cache file ({DELHI_NCR_CACHE_PATH}).")
    except Exception as e:
        logger.warning(f"Could not save Delhi-NCR JSON cache file: {e}")

    return SCANNED_DELHI_NCR_LEADS


def run_devops_scan(force: bool = False) -> list:
    """
    Executes DevOps & Cloud Infrastructure lead scan & scoring via Strategy & Factory patterns.
    If force is False and local JSON cache file exists, loads and serves instantly from file.
    Otherwise performs full live scan and caches results to local JSON file.
    """
    global SCANNED_DEVOPS_LEADS

    if not force and os.path.exists(DEVOPS_CACHE_PATH):
        try:
            logger.info(f"⚡ Loading DevOps project leads instantly from local JSON file ({DEVOPS_CACHE_PATH})...")
            with open(DEVOPS_CACHE_PATH, "r", encoding="utf-8") as f:
                SCANNED_DEVOPS_LEADS = json.load(f)
            logger.info(f"Loaded {len(SCANNED_DEVOPS_LEADS)} cached DevOps leads instantly from local JSON file.")
            return SCANNED_DEVOPS_LEADS
        except Exception as e:
            logger.warning(f"Failed to read local DevOps cache JSON file: {e}. Running fresh live scan...")

    logger.info("Executing fresh live DevOps scan via Collector & Scoring Factories...")

    devops_strategy = CollectorFactory.create_collector("devops")
    devops_leads = devops_strategy.collect()

    scoring_strategy = ScoringStrategyFactory.create_scoring_strategy("default")
    scored_leads = scoring_strategy.score_and_filter(
        job_leads=[],
        tech_scans=[],
        intent_leads=devops_leads,
        min_confidence=60
    )

    pitch_gen = OutreachGenerator()
    for lead in scored_leads:
        lead["pitch"] = pitch_gen.generate_pitch(lead)

    SCANNED_DEVOPS_LEADS = scored_leads

    # Save results to local JSON cache file
    try:
        os.makedirs("output", exist_ok=True)
        with open(DEVOPS_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(SCANNED_DEVOPS_LEADS, f, indent=2)
        logger.info(f"Saved {len(SCANNED_DEVOPS_LEADS)} DevOps leads to local JSON cache file ({DEVOPS_CACHE_PATH}).")
    except Exception as e:
        logger.warning(f"Could not save DevOps JSON cache file: {e}")

    return SCANNED_DEVOPS_LEADS


class SalesforceLeadAppHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        url_path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)
        force_scan = query_params.get("force", ["false"])[0].lower() in ["true", "1", "yes"]

        # Public Login Page
        if url_path in ["/login", "/login.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open("login.html", "rb") as f:
                self.wfile.write(f.read())
            return

        # Logout Route
        if url_path in ["/api/logout", "/logout"]:
            cookie_header = self.headers.get("Cookie", "")
            cookies = urllib.parse.parse_qs(cookie_header.replace("; ", "&"))
            session_ids = cookies.get("session_id", [])
            for sid in session_ids:
                if sid in ACTIVE_SESSIONS:
                    ACTIVE_SESSIONS.remove(sid)
            self.send_response(302)
            self.send_header("Location", "/login.html")
            self.send_header("Set-Cookie", "session_id=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT")
            self.end_headers()
            return

        # Check authentication for protected routes
        is_authenticated = verify_session(self.headers.get("Cookie", ""))
        if not is_authenticated:
            if url_path.startswith("/api/"):
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized. Please log in."}).encode("utf-8"))
            else:
                self.send_response(302)
                self.send_header("Location", "/login.html")
                self.end_headers()
            return

        # Protected Page & API Routes
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

        elif url_path == "/india_leads.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open("india_leads.html", "rb") as f:
                self.wfile.write(f.read())

        elif url_path == "/delhi_ncr_leads.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open("delhi_ncr_leads.html", "rb") as f:
                self.wfile.write(f.read())

        elif url_path == "/devops_leads.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open("devops_leads.html", "rb") as f:
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

        elif url_path in ["/api/scan/india", "/api/india-leads"]:
            leads = run_india_scan(force=force_scan)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(leads).encode("utf-8"))

        elif url_path in ["/api/scan/delhi-ncr", "/api/delhi-ncr-leads", "/api/scan/delhi_ncr"]:
            leads = run_delhi_ncr_scan(force=force_scan)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(leads).encode("utf-8"))

        elif url_path in ["/api/scan/devops", "/api/devops-leads", "/api/scan/devops_project"]:
            leads = run_devops_scan(force=force_scan)
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

        elif url_path in ["/api/export/india-csv"]:
            global SCANNED_INDIA_LEADS
            if not SCANNED_INDIA_LEADS:
                SCANNED_INDIA_LEADS = run_india_scan(force=False)

            csv_exporter = ExporterFactory.create_exporter("csv")
            filepath = csv_exporter.export(SCANNED_INDIA_LEADS, filename="india_salesforce_website_leads.csv")

            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="india_salesforce_website_leads.csv"')
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(500, "Failed to generate India CSV export file.")

        elif url_path in ["/api/export/delhi-ncr-csv"]:
            global SCANNED_DELHI_NCR_LEADS
            if not SCANNED_DELHI_NCR_LEADS:
                SCANNED_DELHI_NCR_LEADS = run_delhi_ncr_scan(force=False)

            csv_exporter = ExporterFactory.create_exporter("csv")
            filepath = csv_exporter.export(SCANNED_DELHI_NCR_LEADS, filename="delhi_ncr_website_leads.csv")

            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="delhi_ncr_website_leads.csv"')
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(500, "Failed to generate Delhi-NCR CSV export file.")

        elif url_path in ["/api/export/devops-csv"]:
            global SCANNED_DEVOPS_LEADS
            if not SCANNED_DEVOPS_LEADS:
                SCANNED_DEVOPS_LEADS = run_devops_scan(force=False)

            csv_exporter = ExporterFactory.create_exporter("csv")
            filepath = csv_exporter.export(SCANNED_DEVOPS_LEADS, filename="devops_project_leads.csv")

            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="devops_project_leads.csv"')
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(500, "Failed to generate DevOps CSV export file.")

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

        elif url_path in ["/api/export/india-excel"]:
            if not SCANNED_INDIA_LEADS:
                SCANNED_INDIA_LEADS = run_india_scan(force=False)

            excel_exporter = ExporterFactory.create_exporter("excel")
            filepath = excel_exporter.export(SCANNED_INDIA_LEADS, filename="india_salesforce_website_leads.xls")

            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.ms-excel")
                self.send_header("Content-Disposition", 'attachment; filename="india_salesforce_website_leads.xls"')
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(500, "Failed to generate India Excel export file.")

        elif url_path in ["/api/export/delhi-ncr-excel"]:
            if not SCANNED_DELHI_NCR_LEADS:
                SCANNED_DELHI_NCR_LEADS = run_delhi_ncr_scan(force=False)

            excel_exporter = ExporterFactory.create_exporter("excel")
            filepath = excel_exporter.export(SCANNED_DELHI_NCR_LEADS, filename="delhi_ncr_website_leads.xls")

            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.ms-excel")
                self.send_header("Content-Disposition", 'attachment; filename="delhi_ncr_website_leads.xls"')
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(500, "Failed to generate Delhi-NCR Excel export file.")

        elif url_path in ["/api/export/devops-excel"]:
            if not SCANNED_DEVOPS_LEADS:
                SCANNED_DEVOPS_LEADS = run_devops_scan(force=False)

            excel_exporter = ExporterFactory.create_exporter("excel")
            filepath = excel_exporter.export(SCANNED_DEVOPS_LEADS, filename="devops_project_leads.xls")

            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.ms-excel")
                self.send_header("Content-Disposition", 'attachment; filename="devops_project_leads.xls"')
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(500, "Failed to generate DevOps Excel export file.")

        else:
            self.send_error(404, "Page Not Found")

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        url_path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        content_length = int(self.headers.get("Content-Length", 0))
        body = {}
        if content_length > 0:
            try:
                body = json.loads(self.rfile.read(content_length).decode("utf-8"))
            except Exception:
                pass

        # Login Endpoint (Public)
        if url_path == "/api/login":
            req_username = body.get("username", "").strip()
            req_password = body.get("password", "")

            if req_username == ADMIN_USERNAME and req_password == ADMIN_PASSWORD:
                token = generate_session_token(req_username)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Set-Cookie", f"session_id={token}; Path=/; HttpOnly")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "redirect": "/index.html"}).encode("utf-8"))
            else:
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Invalid username or password"}).encode("utf-8"))
            return

        # Check authentication for protected POST endpoints
        if not verify_session(self.headers.get("Cookie", "")):
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized. Please log in."}).encode("utf-8"))
            return

        force_scan = query_params.get("force", ["false"])[0].lower() in ["true", "1", "yes"]
        if body.get("force") or body.get("fresh") or body.get("force_rescan"):
            force_scan = True

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
        elif url_path == "/api/scan/india":
            leads = run_india_scan(force=force_scan)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(leads).encode("utf-8"))
        elif url_path in ["/api/scan/delhi-ncr", "/api/scan/delhi_ncr"]:
            leads = run_delhi_ncr_scan(force=force_scan)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(leads).encode("utf-8"))
        elif url_path in ["/api/scan/devops", "/api/scan/devops_project"]:
            leads = run_devops_scan(force=force_scan)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(leads).encode("utf-8"))
        else:
            self.send_error(404, "Endpoint Not Found")



class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def run_server():
    server_address = ("0.0.0.0", PORT)
    with ThreadedTCPServer(server_address, SalesforceLeadAppHandler) as httpd:
        logger.info(f"🌐 Lead Generation Dashboard active at: http://0.0.0.0:{PORT}")
        logger.info(f"   🔐 Login Page: http://localhost:{PORT}/login.html")
        logger.info(f"   ⚡ Salesforce Leads: http://localhost:{PORT}/index.html")
        logger.info(f"   🗺️ Local Business Website Leads: http://localhost:{PORT}/website_leads.html")
        logger.info(f"   🇮🇳 India Opportunities: http://localhost:{PORT}/india_leads.html")
        logger.info(f"   🏛️ Delhi-NCR Leads: http://localhost:{PORT}/delhi_ncr_leads.html")
        logger.info(f"   🚀 DevOps Projects: http://localhost:{PORT}/devops_leads.html")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Dashboard server stopped.")


if __name__ == "__main__":
    run_server()


