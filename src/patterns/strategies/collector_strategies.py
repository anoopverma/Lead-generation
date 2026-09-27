from typing import List, Dict, Any
from .base import ICollectorStrategy
from ...collectors.job_signals import JobSignalCollector
from ...collectors.intent_finder import IntentFinderCollector
from ...collectors.tech_detector import TechDetectorCollector
from ...collectors.enrichment_apis import FreeTierEnrichmentCollector

class JobSignalCollectorStrategy(ICollectorStrategy):
    """Concrete Collector Strategy for Salesforce Job Hiring Signals."""

    def __init__(self, roles: List[str] = None):
        self.collector = JobSignalCollector(roles=roles)

    def collect(self, **kwargs) -> List[Dict[str, Any]]:
        query = kwargs.get("query", "Salesforce")
        location = kwargs.get("location", "United States")
        return self.collector.search_job_signals(query=query, location=location)


class IntentSignalCollectorStrategy(ICollectorStrategy):
    """Concrete Collector Strategy for Salesforce RFPs & Digital Transformation news."""

    def __init__(self):
        self.collector = IntentFinderCollector()

    def collect(self, **kwargs) -> List[Dict[str, Any]]:
        keywords = kwargs.get("keywords")
        return self.collector.find_intent_leads(keywords=keywords)


class TechDetectorCollectorStrategy(ICollectorStrategy):
    """Concrete Collector Strategy for domain web tech stack footprints."""

    def __init__(self):
        self.collector = TechDetectorCollector()

    def collect(self, **kwargs) -> List[Dict[str, Any]]:
        domains = kwargs.get("domains", [])
        return [self.collector.scan_domain(domain) for domain in domains]


class FreeTierEnrichmentCollectorStrategy(ICollectorStrategy):
    """Concrete Collector Strategy for Free Tier B2B Scanning APIs (Apollo, Hunter, OpenCorporates)."""

    def __init__(self, config: Dict[str, Any] = None):
        self.collector = FreeTierEnrichmentCollector(config=config)

    def collect(self, **kwargs) -> List[Dict[str, Any]]:
        leads = kwargs.get("leads", [])
        for lead in leads:
            self.collector.enrich_lead_full(lead)
        return leads
