---
description: Design pattern and architectural adherence rules for the Salesforce Lead Generation Engine codebase.
always_on: true
---

# Architectural Adherence Rules

When modifying or expanding the **Salesforce Lead Generation Engine** codebase, you MUST adhere to the following architectural design rules:

---

## 1. Design Patterns Mandatory Usage

- **Strategy Pattern (`src/patterns/strategies/`)**:
  - All new signal collectors MUST inherit from `ICollectorStrategy` and implement `.collect(**kwargs) -> List[Dict[str, Any]]`.
  - All new scoring strategies MUST inherit from `IScoringStrategy` and implement `.score_and_filter(...)`.
  - All new exporters MUST inherit from `IExporterStrategy` and implement `.export(...)`.

- **Factory Pattern (`src/patterns/factories/`)**:
  - All new strategies MUST be registered in the corresponding factory (`CollectorFactory`, `ScoringStrategyFactory`, `ExporterFactory`).
  - Client callers (such as `main.py`, `app.py`, CLI commands, web routes) MUST instantiate strategies ONLY via factory calls (e.g. `CollectorFactory.create_collector(...)`). Direct instantiation of concrete strategy classes in entry points is strictly prohibited.

---

## 2. Modular Layer Boundaries

- **Collectors Layer (`src/collectors/`)**: Contains raw signal gathering and enrichment APIs. Collectors must return standard dictionaries containing lead attributes (`company_name`, `domain`, `signal_type`, etc.).
- **Processing Layer (`src/processing/`)**: Contains lead scoring logic (`LeadScorer`) and personalized pitch generation (`OutreachGenerator`). Scoring logic must remain decoupled from data collection.
- **Export Layer (`src/export/`)**: Contains serialization mechanisms (CSV, JSON, Salesforce Web-to-Lead API). Exporters must consume generic lead dictionary lists.
- **Presentation Layer (`app.py`, `main.py`, `index.html`)**: Entry points must only coordinate the execution flow using Factories and Strategies.

---

## 3. Data Quality & Confidence Gate

- Every lead MUST be evaluated for both `score` (0-100) and `confidence_score` (0-100%).
- Data quality verification rules (Hunter.io email format, OpenCorporates legal status, domain tech stack match) must be computed in `LeadScorer`.
- Leads with `confidence_score` $\le 60\%$ MUST be automatically filtered out by default (`min_confidence_score = 60`).

---

## 4. UI Behavior & Scan Rules

- The web interface (`index.html`) MUST display a clean initial state upon load.
- Scanning and enrichment MUST ONLY be triggered when the user explicitly clicks the **`🔍 SCAN FOR PROJECTS`** button (`POST /api/scan`). Automatic background scanning on page load is forbidden.

---

## 5. Verification & Changelog Requirements

- **Unit Testing**: Every new collector, strategy, factory registration, or core logic change MUST have unit test coverage in `tests/test_lead_generation.py`. Run `pytest tests/` to verify before declaring completion.
- **Changelog**: All notable changes, updates, bug fixes, or architectural additions MUST be recorded in [`CHANGES.md`](file:///Users/anoop/Project/Lead%20geneation/CHANGES.md).
- **Git Push Guard**: Do NOT execute `git push` to remote repositories unless explicitly requested by the user.
