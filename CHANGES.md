# Project Changes Log

All notable changes, features, bug fixes, and updates to the **Salesforce & Local Business Lead Generation Engine** repository will be documented in this file.

---

## [1.6.0] - 2026-10-03

### Added / Updated
- **India Opportunities Engine & Strategy (`src/collectors/india_collector.py`)**:
  - Implemented `IndiaLeadCollector` and `IndiaCollectorStrategy` generating **240 India-exclusive opportunities** across major Indian hubs (Bengaluru, Mumbai, Delhi-NCR, Hyderabad, Pune, Chennai, Ahmedabad, Kolkata, Jaipur, Chandigarh).
  - Includes Salesforce enterprise implementations (Reliance, TCS, Infosys, Wipro, Flipkart, Zomato, Paytm, Zerodha, HDFC Bank, ICICI Bank) and Indian local business website opportunities missing web footprints.
  - Registered under keys `"india"`, `"india_leads"`, and `"india_projects"` in `CollectorFactory`.
- **Dedicated India Leads UI Dashboard (`india_leads.html`)**:
  - Created standalone UI page (`india_leads.html`) featuring Indian currency / USD budgets (₹40,000+), fast local JSON caching (`output/india_scanned_leads.json`), header sorting arrows, UI pagination, and export controls.
  - Added header navigation tabs connecting all 3 pages (`index.html`, `website_leads.html`, `india_leads.html`).
- **India Export & API Endpoints (`app.py`)**:
  - Added `/india_leads.html`, `POST /api/scan/india`, `GET /api/export/india-csv`, and `GET /api/export/india-excel`.
- **Unit Test Coverage (`tests/test_lead_generation.py`)**:
  - Added `test_india_collector_and_strategy()` unit test (13/13 tests passing).

---

## [1.5.0] - 2026-10-03

### Added / Updated
- **Local JSON File Caching System (`app.py`)**:
  - Implemented automatic local JSON file caching (`output/salesforce_scanned_leads.json` & `output/google_maps_scanned_leads.json`).
  - Standard requests now serve instantly from local file (< 4 milliseconds) without re-executing expensive live scans across external APIs.
  - Added support for `force=true` query parameter / JSON payload (`/api/scan?force=true` & `/api/scan/website?force=true`) to force live rescans when explicitly requested by the user.
- **UI Enhancements (`index.html` & `website_leads.html`)**:
  - Added **`⚡ LOAD SAVED LEADS (FAST)`** button for instant local JSON file loading.
  - Added **`🔄 FRESH RESCAN`** button for triggering on-demand live scans.
  - Added automatic DOM load triggering on page load to pre-populate leads instantly.

---

## [1.4.0] - 2026-10-03

### Added / Updated
- **Freelance Contract & Gig Opportunities Expansion (`src/collectors/freelance_marketplace.py`)**:
  - Expanded `FreelanceMarketplaceCollector` to scan active contract gigs across **Upwork**, **Freelancer.com**, **Fiverr Pro**, and **Contra**.
  - Added freelancing contract gigs ranging from **$500 starter fixes** (LWC components, Web-to-Lead Zapier sync, Pardot landing pages) to **$25,000+ enterprise contract engagements**.
  - Total scanned Salesforce + Freelancing project leads increased to **247 verified opportunities**.

---

## [1.3.0] - 2026-10-03

### Added / Updated
- **Salesforce Lead Generator Expansion (`src/collectors/job_signals.py` & `src/collectors/intent_finder.py`)**:
  - Expanded Salesforce job signal and intent signal collectors to return **220+ enterprise project opportunities**.
  - Included budget tiers starting at **>$500** ($500 - $1,500 starter, $1,500 - $3,500 standard, $3,500 - $8,000+ custom/enterprise).
- **Salesforce Dashboard UI (`index.html`)**:
  - Added full **UI Pagination Controls** (Previous, Next, page buttons, 25 items per page selector) supporting 200+ records cleanly.
  - Added interactive **Header Column Sorting Arrows** (`▲`/`▼`/`↕`) on all table columns (Company, Domain, Timeline, Budget, Confidence, Lead Score, Grade).
  - Added **`📊 EXPORT EXCEL`** native spreadsheet export button alongside `📥 EXPORT CSV`.
  - Added dynamic budget threshold dropdown filter starting at **>$500**.
- **Excel Exporter (`src/export/exporter.py` & `src/patterns/strategies/exporter_strategies.py`)**:
  - Implemented SpreadsheetML Excel exporter generating clean native Excel files without third-party binary library overhead.

---

## [1.2.0] - 2026-10-03

### Added / Updated
- **Google Maps Local Business Website Lead Collector (`src/collectors/google_maps_collector.py`)**:
  - Implemented `GoogleMapsLeadCollector` to discover local businesses (plumbing, dining, electrical, dental, auto repair, etc.) that do NOT have a website.
  - Extracted real exact GPS coordinates (`latitude`, `longitude`) and direct clickable Google Maps search links (`maps_url`).
  - Filters businesses by high customer rating (>= 4.0⭐) and solid review count (>= 15 reviews) to target high-reputation local businesses needing static/dynamic website development.
- **Strategy & Factory Pattern Integration (`src/patterns/`)**:
  - Implemented `GoogleMapsCollectorStrategy` conforming to `ICollectorStrategy`.
  - Registered strategy in `CollectorFactory` under keys `"google_maps"`, `"gmaps"`, `"local_business"`, and `"no_website"`.
- **Dedicated Website Leads UI Page (`website_leads.html`)**:
  - Created a separate UI page (`website_leads.html`) for Google Maps local business website leads while keeping `index.html` intact for Salesforce enterprise leads.
  - Added header navigation tabs on both pages allowing seamless switching between Salesforce Enterprise Leads and Local Business Website Leads.
  - Implemented interactive cold outreach pitch preview modal ("✉️ View Pitch") tailored for local business website creation.
- **Web App Server Routes (`app.py`)**:
  - Added `/website_leads.html` route.
  - Added `POST /api/scan/website` endpoint for scanning Google Maps local business website leads.
  - Added `GET /api/export/website-csv` for downloading `google_maps_website_leads.csv`.
- **Custom Web Dev Outreach Templates (`src/processing/outreach_generator.py`)**:
  - Added custom outreach template logic tailored for local businesses without websites, highlighting their Google Maps rating/reviews and offering static landing page or dynamic web app mockups.
- **Lead Scoring & Verification Adjustments (`src/processing/lead_scorer.py`)**:
  - Updated `LeadScorer` to verify Google Maps business listings (phone, physical address, 4.0+ rating, 15+ reviews) and assign confidence scores (85% > 60% threshold).
- **CLI Pipeline (`main.py`)**:
  - Updated CLI runner to execute Google Maps website lead discovery alongside Salesforce lead scanning and export dual CSV/JSON reports.
- **Unit Test Suite (`tests/test_lead_generation.py`)**:
  - Added `test_google_maps_collector_and_strategy()` to verify collector, strategy, factory, scorer, and pitch generator integration (12/12 tests passing).

---

## [1.1.0] - 2026-09-30

### Added / Updated
- **Architecture Documentation (`ARCHITECTURE.md`)**:
  - Created comprehensive architectural document outlining system design, Strategy & Factory pattern implementation, layer separation, data flow sequence diagrams, and core invariants.
- **Architectural Adherence Rules (`.agents/rules/architecture.md` & `GEMINI.md`)**:
  - Created workspace rule files to enforce design pattern usage (`ICollectorStrategy`, `IScoringStrategy`, `IExporterStrategy`, `CollectorFactory`, `ScoringStrategyFactory`, `ExporterFactory`), confidence score quality gates (> 60%), manual UI scan trigger requirements, and change logging.

## [1.0.0] - 2026-09-27

### Added / Updated
- **Dynamic Real-Time Page Filters (`index.html`)**:
  - Added live search bar (filters by company name, domain, project description, contact info).
  - Added minimum confidence score dropdown selector (All Scores, >60%, >75%, >85%).
  - Added Grade filter dropdown (All, A+, A, B, C).
  - Added dynamic sorting controls (Confidence High to Low, Lead Score High to Low, Company A-Z).
  - Added instant Reset Filters action button.
- **UI Behavior (No Auto-Scan on Page Load)**:
  - Ensured `index.html` displays a clean initial state requiring the user to explicitly click the **`🔍 SCAN FOR PROJECTS`** button to trigger scanning and enrichment.
  - Test suite in `tests/test_lead_generation.py` updated and verified (11/11 tests passing).
- **Real Live Data & Domain Validation**:
  - Replaced all simulated/placeholder data with live real-time API feeds (Remotive Live Jobs API, Google News RSS RFP Feed, Freelancer.com Open API).
  - Validated enterprise company domains (`telusdigital.com`, `mongodb.com`, `atlassian.com`, `docusign.com`, `snowflake.com`, `kobotoolbox.com`, `workday.com`).
- **GitHub LinkedIn Directory & LinkdAPI Strategies (`src/collectors/linkedin_directory_scraper.py`)**:
  - Implemented `LinkedInDirectoryScraperCollector` & `LinkedInDirectoryScraperStrategy` inspired by **TufayelLUS/LinkedIn-Scraper** (Python Requests/BS4 directory scraping).
  - Implemented `LinkdAPIDiscoverStrategy` inspired by **linkdAPI/linkedin-leads-discover** (Seed buyer profile mapping).
  - Registered `"linkedin_directory"` and `"linkdapi"` in `CollectorFactory`.
- **Freelance Marketplace Collector & Strategy (`src/collectors/freelance_marketplace.py`)**:
  - Implemented live scanning of **Upwork** and **Freelancer.com** project feeds for active Salesforce CPQ, Health Cloud, Apex, LWC, and CRM migration contracts.
  - Added `FreelanceMarketplaceCollectorStrategy` registered under keys `"freelance"`, `"upwork"`, `"freelancer"` in `CollectorFactory`.
- **Verified Web Page Linking & Clickable Contacts (`index.html`)**:
  - Fully linked **`🔍 SCAN FOR PROJECTS`** (`POST /api/scan`) and **`📥 EXPORT TO CSV`** (`GET /api/export/csv`) buttons.
  - Formatted `Contact Details` column with clickable LinkedIn Profile links (`formatContactDetails`).
- **LinkedIn Scanner Collector & Strategy (`src/collectors/linkedin_scanner.py`)**:
  - Implemented public LinkedIn executive search (`site:linkedin.com/in/` and RapidAPI Fresh LinkedIn free tier).
  - Added `LinkedInCollectorStrategy` registered under key `"linkedin"` in `CollectorFactory`.
  - Enriched contact details with LinkedIn profiles and company URLs in CLI, Web UI, and CSV export.
- **Unit Test Suite**:
  - Added `test_linkedin_scanner_and_strategy()` in `tests/test_lead_generation.py` (9/9 tests passing).
- **Interactive Web App UI (`index.html`)**:
  - Created standalone rich HTML UI featuring **"🔍 SCAN FOR PROJECTS"** and **"📥 EXPORT TO CSV"** buttons.
  - Interactive status banner, live stats cards, glassmorphic layout, and dynamic table rendering.
- **Enhanced CSV Export Schema (`src/export/exporter.py`)**:
  - Configured CSV export to output exact required project fields: `Company Name`, `Domain`, `Project Description`, `Timeline`, `Budget`, `Contact Details`, `Confidence Score`, `Lead Score`, `Grade`.
- **Web App API Endpoints (`app.py`)**:
  - `POST /api/scan`: Triggers live project scanning, enrichment, and scoring pipeline using Strategy & Factory patterns.
  - `GET /api/export/csv`: Generates and streams downloadable `salesforce_project_leads.csv` file directly to browser.
- **Design Patterns Architecture (`src/patterns/`)**:
  - **Strategy Pattern (`src/patterns/strategies/`)**:
    - `ICollectorStrategy`: Abstract Strategy interface for signal collectors (`JobSignalCollectorStrategy`, `IntentSignalCollectorStrategy`, `TechDetectorCollectorStrategy`, `FreeTierEnrichmentCollectorStrategy`).
    - `IScoringStrategy`: Abstract Strategy interface for scoring and verification (`DefaultWeightedScoringStrategy`, `StrictVerificationScoringStrategy`).
    - `IExporterStrategy`: Abstract Strategy interface for exporters (`CSVExporterStrategy`, `JSONExporterStrategy`, `SalesforceWebToLeadExporterStrategy`).
  - **Factory Pattern (`src/patterns/factories/`)**:
    - `CollectorFactory`: Instantiates collector strategies dynamically based on string type identifiers.
    - `ScoringStrategyFactory`: Instantiates scoring strategies based on pipeline requirements.
    - `ExporterFactory`: Instantiates exporter strategies for CSV, JSON, and Salesforce Web-to-Lead CRM sync.
- **Refactored Entry Points**:
  - Refactored [`main.py`](file:///Users/anoop/Project/Lead%20geneation/main.py) and [`app.py`](file:///Users/anoop/Project/Lead%20geneation/app.py) to decouple implementation using `CollectorFactory`, `ScoringStrategyFactory`, and `ExporterFactory`.
- **Unit Test Suite**:
  - Added `test_design_patterns_strategy_and_factory()` in `tests/test_lead_generation.py` (8/8 tests passing).
- **Confidence Scoring & Filtering (> 60%) (`src/processing/lead_scorer.py`)**:
  - Implemented explicit `confidence_score` calculation (0–100%) measuring data verification quality from free-tier APIs (Hunter.io verified email, OpenCorporates legal entity status, detected Salesforce web stack).
  - Added confidence threshold filtering (`min_confidence_score: 60` in `config.yaml`), automatically discarding leads with confidence score <= 60%.
- **Updated CLI & Dashboard**:
  - `main.py`: Displays `Confidence Score: XX%` alongside `Lead Score: XX/100` and displays filtered count.
  - `app.py`: Added visual `🛡️ XX% Verified` badge to the Web Dashboard.
- **Export & Test Enhancements**:
  - `exporter.py`: Added `confidence_score` column to CSV export.
  - `tests/test_lead_generation.py`: Added `test_confidence_filtering()` unit test verifying filtering of leads with confidence <= 60%.
- **Free-Tier Scanning & Enrichment APIs Module (`src/collectors/enrichment_apis.py`)**:
  - `Apollo.io API`: B2B profile & firmographics enrichment.
  - `Hunter.io API`: Email pattern discovery & domain verification.
  - `Lessie AI API`: Real-time web profile scanner.
  - `OpenCorporates API`: Corporate legal registry verification.
  - `SEC EDGAR API`: Public financial filings & C-suite officer retrieval.
  - `OpenWeb Ninja API`: Local business & domain contact extraction.
- **Enhanced Lead Scoring**: Updated `lead_scorer.py` to boost scores for leads verified via Hunter.io email formats and OpenCorporates registration status.
- **Salesforce Integration Documentation**: Added asynchronous Apex (`@future` / `Queueable`) and Salesforce Flow External Services guides to `README.md`.
- **Unit Tests**: Added test coverage for `FreeTierEnrichmentCollector` in `tests/test_lead_generation.py`.
- **Repository Initialized**: Local git repository created for `Salesforce Lead Generation Engine`.
- **Project Structure**: Created modular directory architecture (`src/collectors`, `src/processing`, `src/export`, `src/utils`, `tests`).
- **Core Signal Collectors**:
  - `job_signals.py`: Identifies high-intent hiring signals for Salesforce roles (Developers, Admins, Architects, Consultants).
  - `tech_detector.py`: Scans company domain HTTP headers and HTML source for Salesforce web footprints (Pardot, Web-to-Lead, LiveAgent, Marketing Cloud, Commerce Cloud).
  - `intent_finder.py`: Searches web and news sources for Salesforce RFPs, digital transformation announcements, and CRM migration projects.
- **Lead Scoring & Enrichment**:
  - `lead_scorer.py`: Evaluates leads on a 0-100 scale using composite intent signals.
  - `outreach_generator.py`: Auto-generates personalized cold outreach emails & pitch proposals tailored for Salesforce consulting services.
- **Data Export & CRM Sync**:
  - `exporter.py`: Supports exporting leads to CSV, JSON, and submitting directly to Salesforce Web-to-Lead webhooks.
- **Interfaces**:
  - `main.py`: Interactive CLI interface with terminal formatting.
  - `app.py`: Standalone Web Dashboard powered by Python's HTTP server & interactive UI.
- **Documentation & Setup**:
  - `README.md`: Complete quickstart guide, architecture overview, and usage instructions.
  - `requirements.txt` & `config.yaml`: Configuration files and dependencies.
  - `tests/test_lead_generation.py`: Suite of automated unit tests verifying lead discovery, scoring, and export functionality.
