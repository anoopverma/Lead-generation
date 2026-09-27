from typing import Dict, Any
from ..strategies.base import ICollectorStrategy
from ..strategies.collector_strategies import (
    JobSignalCollectorStrategy,
    IntentSignalCollectorStrategy,
    TechDetectorCollectorStrategy,
    FreeTierEnrichmentCollectorStrategy,
    LinkedInCollectorStrategy,
    LinkedInDirectoryScraperStrategy,
    LinkdAPIDiscoverStrategy,
    FreelanceMarketplaceCollectorStrategy
)

class CollectorFactory:
    """
    Factory pattern class for creating signal and enrichment collector strategies.
    Supports GitHub open-source LinkedIn scrapers & seed profile discovery engines.
    """

    @staticmethod
    def create_collector(collector_type: str, config: Dict[str, Any] = None) -> ICollectorStrategy:
        ctype = collector_type.lower().strip()
        config = config or {}

        if ctype in ["job", "job_signals", "hiring"]:
            return JobSignalCollectorStrategy(roles=config.get("target_roles"))
        elif ctype in ["intent", "rfp", "intent_signals"]:
            return IntentSignalCollectorStrategy()
        elif ctype in ["tech", "tech_detector", "footprint"]:
            return TechDetectorCollectorStrategy()
        elif ctype in ["enrichment", "free_tier_apis", "b2b_enrichment"]:
            return FreeTierEnrichmentCollectorStrategy(config=config.get("free_tier_apis"))
        elif ctype in ["linkedin", "linkedin_scanner", "social_profiles"]:
            return LinkedInCollectorStrategy(api_key=config.get("free_tier_apis", {}).get("linkedin_api_key"))
        elif ctype in ["linkedin_directory", "tufayellus_scraper", "employee_directory"]:
            return LinkedInDirectoryScraperStrategy(config=config)
        elif ctype in ["linkdapi", "seed_discovery", "linkedin_discover"]:
            return LinkdAPIDiscoverStrategy(config=config)
        elif ctype in ["freelance", "upwork", "freelancer", "marketplace"]:
            return FreelanceMarketplaceCollectorStrategy(keywords=config.get("intent_keywords"))
        else:
            raise ValueError(f"Unknown collector strategy type: '{collector_type}'")
