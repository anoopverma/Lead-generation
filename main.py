#!/usr/bin/env python3
"""
Salesforce & Google Maps Local Business Lead Generation Engine - Refactored CLI Interface
Uses Strategy Pattern + Factory Pattern for dynamic signal collection, scoring, and exporters.
"""

import sys
import yaml
import os

from src.patterns import CollectorFactory, ScoringStrategyFactory, ExporterFactory
from src.processing.outreach_generator import OutreachGenerator
from src.utils.logger import get_logger

logger = get_logger("MainCLI")

def load_config(config_path: str = "config.yaml") -> dict:
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}

def run_pipeline():
    print("=" * 70)
    print("🚀 SALESFORCE & LOCAL BUSINESS LEAD ENGINE (Strategy & Factory Architecture) 🚀")
    print("=" * 70)

    config = load_config()

    # 1. Instantiate Collector Strategies using CollectorFactory
    job_strategy = CollectorFactory.create_collector("job_signals", config=config)
    intent_strategy = CollectorFactory.create_collector("intent_signals", config=config)
    tech_strategy = CollectorFactory.create_collector("tech_detector", config=config)
    enrichment_strategy = CollectorFactory.create_collector("enrichment", config=config)
    linkedin_strategy = CollectorFactory.create_collector("linkedin", config=config)
    linkdapi_strategy = CollectorFactory.create_collector("linkdapi", config=config)
    freelance_strategy = CollectorFactory.create_collector("freelance", config=config)
    gmaps_strategy = CollectorFactory.create_collector("google_maps", config=config)

    # 2. Collect Signals via Strategies
    print("\n[1/6] Collecting Salesforce Hiring Signals...")
    job_leads = job_strategy.collect()

    print("\n[2/6] Searching for Salesforce RFPs, Upwork, Freelancer & LinkdAPI Seed Discoveries...")
    intent_leads = intent_strategy.collect()
    freelance_leads = freelance_strategy.collect()
    seed_leads = linkdapi_strategy.collect()
    all_intent_leads = intent_leads + freelance_leads + seed_leads

    print("\n[3/6] Scanning Google Maps for Local Businesses Lacking Websites...")
    gmaps_leads = gmaps_strategy.collect()
    print(f"      Discovered {len(gmaps_leads)} high-reputation local businesses without websites.")

    print("\n[4/6] Scanning Target Domains & Running Enrichment APIs...")
    domains_to_scan = list({l.get("domain") for l in job_leads + all_intent_leads if l.get("domain")})
    tech_scans = tech_strategy.collect(domains=domains_to_scan)
    enrichment_strategy.collect(leads=job_leads + all_intent_leads)
    linkedin_strategy.collect(leads=job_leads + all_intent_leads)

    # 3. Score & Filter Leads using ScoringStrategyFactory
    min_conf = config.get("filtering", {}).get("min_confidence_score", 60)
    print(f"\n[5/6] Scoring & Filtering Leads (Strategy: DefaultWeighted, Min Confidence > {min_conf}%)...")
    scoring_strategy = ScoringStrategyFactory.create_scoring_strategy("default", config=config)
    scored_sf_leads = scoring_strategy.score_and_filter(
        job_leads=job_leads,
        tech_scans=tech_scans,
        intent_leads=all_intent_leads,
        min_confidence=min_conf
    )

    scored_gmaps_leads = scoring_strategy.score_and_filter(
        job_leads=[],
        tech_scans=[],
        intent_leads=gmaps_leads,
        min_confidence=min_conf
    )

    # 4. Display Results
    pitch_gen = OutreachGenerator()

    print("\n" + "=" * 70)
    print(f"🔥 DISCOVERED {len(scored_sf_leads)} HIGH-CONFIDENCE SALESFORCE LEADS (> {min_conf}%) 🔥")
    print("=" * 70)

    for idx, lead in enumerate(scored_sf_leads, start=1):
        print(f"\n#{idx} {lead['company_name']} ({lead['domain']})")
        print(f"   Lead Score: {lead['score']}/100 | Confidence Score: {lead['confidence_score']}% | Grade: {lead['grade']}")
        print(f"   Location: {lead['location']}")
        if lead.get('hiring_signal'):
            print(f"   Hiring Signal: {lead['hiring_signal']}")
        if lead.get('intent_signal'):
            print(f"   Intent / RFP: {lead['intent_signal']}")

        pitch = pitch_gen.generate_pitch(lead)
        print(f"   --------------------------------------------------")
        print(f"   ✉️  Sample Pitch Subject: {pitch['subject']}")
        print(f"   --------------------------------------------------")

    print("\n" + "=" * 70)
    print(f"🗺️ DISCOVERED {len(scored_gmaps_leads)} GOOGLE MAPS WEBSITE LEADS (> {min_conf}%) 🗺️")
    print("=" * 70)

    for idx, lead in enumerate(scored_gmaps_leads, start=1):
        print(f"\n#{idx} {lead['company_name']} - {lead.get('category', 'Local Business')}")
        print(f"   Reputation: {lead.get('rating')}⭐ ({lead.get('review_count')} reviews) | Website: NO WEBSITE")
        print(f"   Lead Score: {lead['score']}/100 | Confidence Score: {lead['confidence_score']}% | Grade: {lead['grade']}")
        print(f"   GPS Coordinates: {lead.get('latitude')}, {lead.get('longitude')}")
        print(f"   Google Maps Link: {lead.get('maps_url')}")
        print(f"   Phone: {lead.get('phone')} | Location: {lead.get('location')}")

        pitch = pitch_gen.generate_pitch(lead)
        print(f"   --------------------------------------------------")
        print(f"   ✉️  Web Pitch Subject: {pitch['subject']}")
        print(f"   --------------------------------------------------")

    # 5. Export Leads using ExporterFactory
    print("\n[6/6] Exporting Leads via ExporterFactory Strategies...")
    csv_exporter = ExporterFactory.create_exporter("csv", config=config)
    json_exporter = ExporterFactory.create_exporter("json", config=config)

    csv_file = csv_exporter.export(scored_sf_leads, filename="salesforce_project_leads.csv")
    json_file = json_exporter.export(scored_sf_leads, filename="salesforce_project_leads.json")
    gmaps_csv = csv_exporter.export(scored_gmaps_leads, filename="google_maps_website_leads.csv")

    print(f"\n✅ Pipeline Execution Completed Successfully!")
    print(f"📁 Salesforce CSV Export: {csv_file}")
    print(f"📁 Salesforce JSON Export: {json_file}")
    print(f"📁 Google Maps Website Leads CSV: {gmaps_csv}")
    print("=" * 70)

if __name__ == "__main__":
    run_pipeline()
