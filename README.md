# ⚡ Salesforce Lead Generation Engine

An automated, signal-based **Lead Generation & Buying Intent Intelligence Engine** built specifically for Salesforce consulting agencies, system integrators, AppExchange partners, and freelance Salesforce developers/architects.

This repository tracks high-intent buying signals (hiring activity, RFPs, digital transformation news, and web tech stack footprints) to automatically discover, score, and generate cold outreach pitches for Salesforce projects.

---

## 🌟 Key Features

- **💼 Job Board Hiring Signal Detection**: Automatically scans and identifies companies actively recruiting for Salesforce roles (*Salesforce Developer, Admin, CPQ Specialist, Solution Architect*), indicating urgent project staffing or consulting needs.
- **🎯 Intent & RFP Scraping**: Finds companies issuing RFPs for Salesforce implementations, migrations (e.g., Hubspot/Microsoft Dynamics to Salesforce), or digital transformation rollouts.
- **🔍 Domain Web Tech Stack Scanner**: Scans company websites for Salesforce digital footprints (*Pardot/Marketing Cloud, Salesforce Web-to-Lead forms, LiveAgent Chat, Experience Cloud/Communities*).
- **📊 Dynamic Lead Scoring Engine**: Ranks leads on a composite scale of `0-100` and assigns grades (`A+ Hot Opportunity`, `A High Priority`, `B`, `C`).
- **✉️ Automated Outreach Pitch Generator**: Drafts personalized cold email subjects and body copy tailored specifically to the buying signal detected (RFP response, staff augmentation, stack audit).
- **📁 Multi-Channel Data Export & Sync**: Exports lead lists directly to CSV and JSON, or syncs automatically to Salesforce CRM via Salesforce Web-to-Lead webhooks.
- **🌐 Interactive Web Dashboard**: Includes a built-in dark-themed web GUI (`app.py`) for real-time lead monitoring and management.

---

## 🏗️ Project Architecture

```
/
├── CHANGES.md                 # Mandatory project changelog & edit history
├── README.md                  # Complete project documentation
├── config.yaml                # Target roles, keywords, and scoring weights
├── requirements.txt           # Python dependencies
├── main.py                    # Interactive CLI runner
├── app.py                     # Web Dashboard UI server
├── src/
│   ├── collectors/
│   │   ├── job_signals.py     # Hiring signal collector for Salesforce roles
│   │   ├── tech_detector.py   # Web tech stack scanner (Pardot, Web-to-Lead, LiveAgent)
│   │   └── intent_finder.py   # Intent & RFP signal finder
│   ├── processing/
│   │   ├── lead_scorer.py     # Lead scoring algorithm
│   │   └── outreach_generator.py # Cold email & pitch generator
│   └── export/
│       └── exporter.py        # CSV, JSON, and Web-to-Lead exporter
└── tests/
    └── test_lead_generation.py# Automated unit test suite
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
