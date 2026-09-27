import pytest
import os
import json
from src.collectors.job_signals import JobSignalCollector
from src.collectors.tech_detector import TechDetectorCollector
from src.collectors.intent_finder import IntentFinderCollector
from src.collectors.enrichment_apis import FreeTierEnrichmentCollector
from src.processing.lead_scorer import LeadScorer
from src.processing.outreach_generator import OutreachGenerator
from src.export.exporter import LeadExporter

def test_job_signal_collector():
    collector = JobSignalCollector()
    leads = collector.search_job_signals()
    assert isinstance(leads, list)
    assert len(leads) > 0
    assert "company_name" in leads[0]
    assert "signal_type" in leads[0]

def test_tech_detector_collector():
    collector = TechDetectorCollector()
    res = collector.scan_domain("acmehealthtech.example.com")
    assert isinstance(res, dict)
    assert "has_salesforce" in res
    assert "detected_technologies" in res

def test_intent_finder_collector():
    collector = IntentFinderCollector()
    leads = collector.find_intent_leads()
    assert isinstance(leads, list)
    assert len(leads) > 0
    assert "intent_signal" in leads[0]

def test_free_tier_enrichment_collector():
    collector = FreeTierEnrichmentCollector()
    lead = {"company_name": "Acme Tech", "domain": "acmetech.example.com"}
    enriched = collector.enrich_lead_full(lead)

    assert "enrichment" in enriched
    assert enriched["enrichment"]["is_enriched"] is True
    assert "hunter_email" in enriched["enrichment"]
    assert "apollo_b2b" in enriched["enrichment"]
    assert "opencorporates" in enriched["enrichment"]

def test_lead_scorer_and_outreach():
    job_collector = JobSignalCollector()
    job_leads = job_collector.search_job_signals()
    
    intent_collector = IntentFinderCollector()
    intent_leads = intent_collector.find_intent_leads()
    
    tech_collector = TechDetectorCollector()
    tech_scans = [tech_collector.scan_domain("acmehealthtech.example.com")]

    scorer = LeadScorer()
    scored = scorer.score_and_merge_leads(job_leads, tech_scans, intent_leads)

    assert len(scored) > 0
    assert scored[0]["score"] >= 0
    assert "grade" in scored[0]

    pitch_gen = OutreachGenerator()
    pitch = pitch_gen.generate_pitch(scored[0])
    assert "subject" in pitch
    assert "body" in pitch

def test_exporter(tmp_path):
    exporter = LeadExporter(output_dir=str(tmp_path))
    sample_leads = [{
        "company_name": "Test Company",
        "domain": "test.com",
        "score": 90,
        "grade": "A+",
        "hiring_signal": "Developer",
        "intent_signal": "RFP",
        "tech_footprint": ["Pardot"]
    }]

    csv_path = exporter.export_to_csv(sample_leads, filename="test.csv")
    assert os.path.exists(csv_path)

    json_path = exporter.export_to_json(sample_leads, filename="test.json")
    assert os.path.exists(json_path)
