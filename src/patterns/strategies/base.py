from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ICollectorStrategy(ABC):
    """
    Strategy interface for lead data collectors (Job Hiring Signals, Intent/RFPs, Tech Stack, Free-Tier APIs).
    """

    @abstractmethod
    def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """Collects and returns lead data records."""
        pass


class IScoringStrategy(ABC):
    """
    Strategy interface for scoring and verifying leads.
    """

    @abstractmethod
    def score_and_filter(
        self,
        job_leads: List[Dict[str, Any]],
        tech_scans: List[Dict[str, Any]],
        intent_leads: List[Dict[str, Any]],
        min_confidence: int = 60
    ) -> List[Dict[str, Any]]:
        """Calculates lead score, confidence score, and filters out unverified leads."""
        pass


class IExporterStrategy(ABC):
    """
    Strategy interface for lead exporters (CSV, JSON, Salesforce Web-to-Lead).
    """

    @abstractmethod
    def export(self, leads: List[Dict[str, Any]], filename: str = None) -> Any:
        """Exports structured lead records to a destination format or CRM."""
        pass
