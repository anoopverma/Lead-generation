# ⚡ Salesforce Lead Generation Engine

An automated, signal-based **Lead Generation & Buying Intent Intelligence Engine** built specifically for Salesforce consulting agencies, system integrators, AppExchange partners, and freelance Salesforce developers/architects.

This repository tracks high-intent buying signals (hiring activity, RFPs, digital transformation news, and web tech stack footprints) to automatically discover, score, and generate cold outreach pitches for Salesforce projects.

---

## 🌟 Key Features

- **💼 Job Board Hiring Signal Detection**: Automatically scans and identifies companies actively recruiting for Salesforce roles (*Salesforce Developer, Admin, CPQ Specialist, Solution Architect*), indicating urgent project staffing or consulting needs.
- **🎯 Intent & RFP Scraping**: Finds companies issuing RFPs for Salesforce implementations, migrations (e.g., Hubspot/Microsoft Dynamics to Salesforce), or digital transformation rollouts.
- **🔍 Domain Web Tech Stack Scanner**: Scans company websites for Salesforce digital footprints (*Pardot/Marketing Cloud, Salesforce Web-to-Lead forms, LiveAgent Chat, Experience Cloud/Communities*).
- **🌐 Free-Tier Scanning & Enrichment APIs**:
  - **Apollo.io API**: B2B profiles, company employee counts, and firmographic data (50 free credits/mo).
  - **Hunter.io API**: Verified email domain pattern discovery and email verification (50 free searches/mo).
  - **Lessie AI API**: Real-time multi-channel profile scanning.
  - **OpenCorporates API**: 100% free corporate registry legal status verification.
  - **SEC EDGAR API**: Free US government financial filings & public C-suite officer data.
  - **OpenWeb Ninja API**: Google Maps & local business website contact extraction.
- **📊 Dynamic Lead & Confidence Scoring Engine**:
  - **Lead Score (0-100)**: Evaluates project budget, hiring urgency, and RFP value.
  - **Confidence Score (0-100%)**: Measures data verification quality (verified email format from Hunter.io, legal registration status from OpenCorporates, active website tech stack footprint).
  - **Confidence Filter (> 60%)**: Automatically filters out low-confidence leads below 60% verification threshold.
- **✉️ Automated Outreach Pitch Generator**: Drafts personalized cold email subjects and body copy tailored specifically to the buying signal detected (RFP response, staff augmentation, stack audit).
- **📁 Multi-Channel Data Export & Sync**: Exports lead lists directly to CSV and JSON, or syncs automatically to Salesforce CRM via Salesforce Web-to-Lead webhooks.
- **🌐 Interactive Web Dashboard**: Includes a built-in dark-themed web GUI (`app.py`) for real-time lead monitoring and management.

---

## ⚡ Salesforce Org Integration Patterns

To connect these Free Tier Scanning APIs directly to your Salesforce Org:

1. **Asynchronous Apex (@future / Queueable)**:
   Avoid synchronous Apex triggers to prevent callout timeout errors. Use `@future(callout=true)` or `Queueable` Apex to scan and enrich incoming leads in background jobs.
2. **Salesforce Flow + External Services**:
   Import OpenAPI/Swagger specifications for Hunter.io or Apollo directly into **Salesforce External Services** to enrich leads natively inside Record-Triggered Flows without writing code.

---

## 🏗️ Project Architecture (Strategy + Factory Design Patterns)

```
/
├── CHANGES.md                 # Mandatory project changelog & edit history
├── README.md                  # Complete project documentation
├── config.yaml                # Target roles, keywords, scoring & filtering settings
├── requirements.txt           # Python dependencies
├── main.py                    # Interactive CLI runner (uses Strategy & Factory patterns)
├── app.py                     # Web Dashboard UI server (uses Strategy & Factory patterns)
├── src/
│   ├── patterns/              # Design Patterns Architecture
│   │   ├── strategies/        # Strategy Pattern implementations
│   │   │   ├── base.py        # Abstract interfaces (ICollectorStrategy, IScoringStrategy, IExporterStrategy)
│   │   │   ├── collector_strategies.py # Signal collection strategies
│   │   │   ├── scoring_strategies.py   # DefaultWeighted & StrictVerification scoring strategies
│   │   │   └── exporter_strategies.py  # CSV, JSON, Salesforce Web-to-Lead strategies
│   │   └── factories/         # Factory Pattern implementations
│   │       ├── collector_factory.py    # CollectorFactory for dynamic signal collectors
│   │       ├── scoring_factory.py      # ScoringStrategyFactory for scoring strategies
│   │       └── exporter_factory.py     # ExporterFactory for exporter strategies
│   ├── collectors/            # Concrete collector engines (Job, Intent, Tech, Free Tier APIs)
│   ├── processing/            # Lead scoring & pitch generator
│   └── export/                # Exporters (CSV, JSON, Salesforce Web-to-Lead)
└── tests/
    └── test_lead_generation.py# Automated unit test suite (8 passing tests)
```

---

## 🚀 Quickstart Guide

### 1. Installation

Clone the repository and install the lightweight requirements:

```bash
git clone https://github.com/your-username/salesforce-lead-generation.git
cd salesforce-lead-generation
pip install -r requirements.txt
```

### 2. Run via CLI

Run the full pipeline directly in your terminal:

```bash
python3 main.py
```

### 3. Launch Web Dashboard UI

Start the interactive Web Dashboard on `http://localhost:8000`:

```bash
python3 app.py
```

Open `http://localhost:8000` in your web browser to view the lead pipeline and pitch recommendations.

---

## 🧪 Running Unit Tests

To verify all collectors, scoring, and exporters are working cleanly:

```bash
pytest tests/
```

---

## ⚙️ Configuration (`config.yaml`)

Customize target roles, intent keywords, and scoring weights in `config.yaml`:

```yaml
target_roles:
  - "Salesforce Administrator"
  - "Salesforce Developer"
  - "Salesforce Consultant"

scoring_weights:
  hiring_signal: 40
  tech_stack_match: 30
  intent_news_match: 30
```

---

## 🤝 Salesforce CRM Web-to-Lead Integration

To push generated leads directly into your Salesforce instance without API fees, add your Salesforce OID to `.env`:

```env
SALESFORCE_OID=00D000000000000
SALESFORCE_WEB_TO_LEAD_URL=https://webto.salesforce.com/servlet/servlet.WebToLead?encoding=UTF-8
```

---

## 📜 License & Compliance

Distributed under the MIT License. Designed for ethical B2B market intelligence and public lead research.
