#!/usr/bin/env python3
"""
Salesforce Lead Generation Engine - Main CLI Interface
"""

import sys
import yaml
import os
from src.collectors.job_signals import JobSignalCollector
from src.collectors.tech_detector import TechDetectorCollector
from src.collectors.intent_finder import IntentFinderCollector
from src.processing.lead_scorer import LeadScorer
from src.processing.outreach_generator import OutreachGenerator
from src.export.exporter import LeadExporter
from src.utils.logger import get_logger

logger = get_logger("MainCLI")

def load_config(config_path: str = "config.yaml") -> dict:
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}

def run_pipeline():
    print("=" * 70)
    print("🚀 SALESFORCE LEAD GENERATION ENGINE - PROJECT FINDER 🚀")
    print("=" * 70)

    config = load_config()

    # 1. Collect Job Signals
    print("\n[1/5] Collecting Salesforce Hiring Signals...")
    job_collector = JobSignalCollector(roles=config.get("target_roles"))
    job_leads = job_collector.search_job_signals()

    # 2. Collect Intent & RFP Signals
    print("\n[2/5] Searching for Salesforce RFPs & Digital Transformation Intent...")
    intent_collector = IntentFinderCollector()
    intent_leads = intent_collector.find_intent_leads()

    # 3. Detect Web Tech Stack Footprints
    print("\n[3/5] Scanning Target Domains for Salesforce Footprints...")
    tech_collector = TechDetectorCollector()
    domains_to_scan = list({l.get("domain") for l in job_leads + intent_leads if l.get("domain")})
    tech_scans = [tech_collector.scan_domain(d) for d in domains_to_scan]

    # 4. Score & Prioritize Leads
    print("\n[4/5] Scoring & Ranking Salesforce Project Leads...")
    scorer = LeadScorer()
    scored_leads = scorer.score_and_merge_leads(job_leads, tech_scans, intent_leads)

    # 5. Display Top Opportunities & Pitch Samples
    print("\n" + "=" * 70)
    print(f"🔥 DISCOVERED TOP {len(scored_leads)} SALESFORCE PROJECT LEADS 🔥")
    print("=" * 70)

    pitch_gen = OutreachGenerator()
    for idx, lead in enumerate(scored_leads, start=1):
        print(f"\n#{idx} {lead['company_name']} ({lead['domain']})")
        print(f"   Score: {lead['score']}/100 | Grade: {lead['grade']}")
        print(f"   Location: {lead['location']}")
        if lead.get('hiring_signal'):
            print(f"   Hiring Signal: {lead['hiring_signal']}")
        if lead.get('intent_signal'):
            print(f"   Intent / RFP: {lead['intent_signal']}")
        if lead.get('tech_footprint'):
            print(f"   Tech Stack Detected: {', '.join(lead['tech_footprint'])}")

        pitch = pitch_gen.generate_pitch(lead)
        print(f"   --------------------------------------------------")
        print(f"   ✉️  Sample Pitch Subject: {pitch['subject']}")
        print(f"   --------------------------------------------------")

    # 6. Export Results
    print("\n[5/5] Exporting Leads...")
    exporter = LeadExporter()
    csv_file = exporter.export_to_csv(scored_leads)
    json_file = exporter.export_to_json(scored_leads)

    print(f"\n✅ Pipeline Execution Completed!")
    print(f"📁 CSV Export: {csv_file}")
    print(f"📁 JSON Export: {json_file}")
    print("=" * 70)

if __name__ == "__main__":
    run_pipeline()
