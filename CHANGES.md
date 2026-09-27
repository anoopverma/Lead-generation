# Project Changes Log

All notable changes, features, bug fixes, and updates to the **Salesforce Lead Generation Engine** repository will be documented in this file.

---

## [1.0.0] - 2026-09-27

### Added
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
