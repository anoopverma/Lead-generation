from typing import List, Dict, Any
from .base import ICollectorStrategy
from ...collectors.job_signals import JobSignalCollector
from ...collectors.intent_finder import IntentFinderCollector
from ...collectors.tech_detector import TechDetectorCollector
from ...collectors.enrichment_apis import FreeTierEnrichmentCollector
from ...collectors.linkedin_scanner import LinkedInScannerCollector
from ...collectors.freelance_marketplace import FreelanceMarketplaceCollector

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


class LinkedInCollectorStrategy(ICollectorStrategy):
    """Concrete Collector Strategy for scanning LinkedIn public profiles and company pages."""

    def __init__(self, api_key: str = None):
        self.scanner = LinkedInScannerCollector(api_key=api_key)

    def collect(self, **kwargs) -> List[Dict[str, Any]]:
        leads = kwargs.get("leads", [])
        results = []
        for lead in leads:
            company = lead.get("company_name", "")
            domain = lead.get("domain", "")
            info = self.scanner.search_linkedin_decision_makers(company, domain)
            lead["linkedin_info"] = info
            
            # Enrich contact details with LinkedIn profile if available
            decision_makers = info.get("decision_makers", [])
            if decision_makers:
                dm = decision_makers[0]
                lead["contact_details"] = f"{dm['name']} - {dm['title']} ({dm['linkedin_url']})"

            results.append(info)
        return results


class FreelanceMarketplaceCollectorStrategy(ICollectorStrategy):
    """Concrete Collector Strategy for scanning Upwork & Freelancer.com project feeds."""

    def __init__(self, keywords: List[str] = None):
        self.collector = FreelanceMarketplaceCollector(keywords=keywords)

    def collect(self, **kwargs) -> List[Dict[str, Any]]:
        return self.collector.collect_all_marketplace_leads()
