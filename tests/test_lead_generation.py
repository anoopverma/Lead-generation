import pytest
import os
import json
from src.patterns import CollectorFactory, ScoringStrategyFactory, ExporterFactory
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

    enrichment_collector = FreeTierEnrichmentCollector()
    for lead in job_leads:
        enrichment_collector.enrich_lead_full(lead)

    scorer = LeadScorer(min_confidence_score=60)
    scored = scorer.score_and_merge_leads(job_leads, tech_scans, intent_leads)

    assert len(scored) > 0
    assert scored[0]["score"] >= 0
    assert "confidence_score" in scored[0]
    assert scored[0]["confidence_score"] > 60
    assert "grade" in scored[0]

    pitch_gen = OutreachGenerator()
    pitch = pitch_gen.generate_pitch(scored[0])
    assert "subject" in pitch
    assert "body" in pitch

def test_confidence_filtering():
    scorer = LeadScorer(min_confidence_score=60)
    job_leads = [{
        "company_name": "Low Conf Inc",
        "domain": "lowconf.example.com",
        "role_posted": "Salesforce Admin",
        "hiring_count": 1
    }]
    tech_scans = []
    intent_leads = []

    # Unenriched lead has base confidence 50% <= 60%, so it should be filtered out
    filtered_leads = scorer.score_and_merge_leads(job_leads, tech_scans, intent_leads, min_confidence=60)
    assert len(filtered_leads) == 0

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

def test_design_patterns_strategy_and_factory(tmp_path):
    # Test CollectorFactory
    job_strat = CollectorFactory.create_collector("job_signals")
    intent_strat = CollectorFactory.create_collector("intent_signals")
    tech_strat = CollectorFactory.create_collector("tech_detector")
    enrichment_strat = CollectorFactory.create_collector("enrichment")

    job_leads = job_strat.collect()
    intent_leads = intent_strat.collect()
    enrichment_strat.collect(leads=job_leads + intent_leads)
    tech_scans = tech_strat.collect(domains=["acme.example.com"])

    assert len(job_leads) > 0
    assert len(intent_leads) > 0
    assert len(tech_scans) == 1

    # Test ScoringStrategyFactory
    scoring_strat = ScoringStrategyFactory.create_scoring_strategy("default")
    scored = scoring_strat.score_and_filter(job_leads, tech_scans, intent_leads, min_confidence=60)
    assert isinstance(scored, list)
    assert len(scored) > 0

    # Test ExporterFactory
    csv_exp = ExporterFactory.create_exporter("csv", config={"export_settings": {"output_dir": str(tmp_path)}})
    path = csv_exp.export(scored, filename="strat_test.csv")
    assert os.path.exists(path)

def test_linkedin_scanner_and_strategy():
    from src.collectors.linkedin_scanner import LinkedInScannerCollector
    scanner = LinkedInScannerCollector()
    res = scanner.search_linkedin_decision_makers("Acme Health", "acmehealth.com")
    assert "decision_makers" in res
    assert len(res["decision_makers"]) > 0

    linkedin_strat = CollectorFactory.create_collector("linkedin")
    sample_leads = [{"company_name": "Acme Tech", "domain": "acmetech.com"}]
    collected = linkedin_strat.collect(leads=sample_leads)
    assert len(collected) == 1
    assert "linkedin_info" in sample_leads[0]

def test_freelance_marketplace_collector():
    from src.collectors.freelance_marketplace import FreelanceMarketplaceCollector
    collector = FreelanceMarketplaceCollector()
    leads = collector.collect_all_marketplace_leads()
    assert isinstance(leads, list)
    assert len(leads) > 0
    assert "project_description" in leads[0]
    assert "budget" in leads[0]

    freelance_strat = CollectorFactory.create_collector("freelance")
    strat_leads = freelance_strat.collect()
    assert len(strat_leads) > 0

def test_github_linkedin_scrapers_and_strategies():
    from src.collectors.linkedin_directory_scraper import LinkedInDirectoryScraperCollector
    collector = LinkedInDirectoryScraperCollector()

    dir_leads = collector.scrape_company_employee_directory("Acme Corp", "acmecorp.com")
    assert isinstance(dir_leads, list)
    assert len(dir_leads) > 0

    seed_leads = collector.discover_similar_seed_leads("Salesforce Director")
    assert isinstance(seed_leads, list)
    assert len(seed_leads) > 0

    dir_strat = CollectorFactory.create_collector("linkedin_directory")
    res_dir = dir_strat.collect(leads=[{"company_name": "Test Co", "domain": "testco.com"}])
    assert len(res_dir) > 0

    seed_strat = CollectorFactory.create_collector("linkdapi")
    res_seed = seed_strat.collect()
    assert len(res_seed) > 0

def test_google_maps_collector_and_strategy():
    from src.collectors.google_maps_collector import GoogleMapsLeadCollector
    collector = GoogleMapsLeadCollector()
    leads = collector.search_no_website_businesses()
    assert isinstance(leads, list)
    assert len(leads) > 0
    assert leads[0]["has_website"] is False
    assert "Missing Website" in leads[0]["website_status"]
    assert leads[0]["rating"] >= 4.0

    gmaps_strat = CollectorFactory.create_collector("google_maps")
    strat_leads = gmaps_strat.collect()
    assert len(strat_leads) > 0
    assert strat_leads[0]["lead_type"] == "google_maps_no_website"

    scoring_strat = ScoringStrategyFactory.create_scoring_strategy("default")
    scored = scoring_strat.score_and_filter([], [], strat_leads, min_confidence=60)
    assert len(scored) > 0
    assert scored[0]["confidence_score"] > 60

    pitch_gen = OutreachGenerator()
    pitch = pitch_gen.generate_pitch(scored[0])
    assert "Mobile Website" in pitch["subject"]


