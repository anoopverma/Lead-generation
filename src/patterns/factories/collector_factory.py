from typing import Dict, Any
from ..strategies.base import ICollectorStrategy
from ..strategies.collector_strategies import (
    JobSignalCollectorStrategy,
    IntentSignalCollectorStrategy,
    TechDetectorCollectorStrategy,
    FreeTierEnrichmentCollectorStrategy
)

class CollectorFactory:
    """
    Factory pattern class for creating signal and enrichment collector strategies.
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
        else:
            raise ValueError(f"Unknown collector strategy type: '{collector_type}'")
