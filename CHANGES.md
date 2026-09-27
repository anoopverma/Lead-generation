# Project Changes Log

All notable changes, features, bug fixes, and updates to the **Salesforce Lead Generation Engine** repository will be documented in this file.

---

## [1.0.0] - 2026-09-27

### Added
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
