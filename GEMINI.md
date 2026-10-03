# Salesforce Lead Generation Engine Guidelines

## Architectural Rules
- Follow the Strategy and Factory design patterns in `src/patterns/`.
- All signal collectors must implement `ICollectorStrategy` and be registered in `CollectorFactory`.
- All scoring models must implement `IScoringStrategy` and be registered in `ScoringStrategyFactory`.
- All exporters must implement `IExporterStrategy` and be registered in `ExporterFactory`.
- Client entry points (`main.py`, `app.py`) must instantiate components via Factory methods only.
- Maintain confidence score filtering threshold (> 60%).
- Ensure `index.html` requires explicit user click on "SCAN FOR PROJECTS" (no auto-scan on page load).

## Operational Rules
- Always log changes to `CHANGES.md`.
- Do not run `git push` unless explicitly asked.
- Verify changes with `pytest tests/`.
