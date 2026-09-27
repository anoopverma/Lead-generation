from typing import List, Dict, Any
from .base import IScoringStrategy
from ...processing.lead_scorer import LeadScorer

class DefaultWeightedScoringStrategy(IScoringStrategy):
    """Concrete Scoring Strategy using multi-signal weights and confidence filtering."""

    def __init__(self, min_confidence_score: int = 60):
        self.scorer = LeadScorer(min_confidence_score=min_confidence_score)

    def score_and_filter(
        self,
        job_leads: List[Dict[str, Any]],
        tech_scans: List[Dict[str, Any]],
        intent_leads: List[Dict[str, Any]],
        min_confidence: int = None
    ) -> List[Dict[str, Any]]:
        return self.scorer.score_and_merge_leads(
            job_leads=job_leads,
            tech_scans=tech_scans,
            intent_leads=intent_leads,
            min_confidence=min_confidence
        )


class StrictVerificationScoringStrategy(IScoringStrategy):
    """Concrete Scoring Strategy enforcing strict verification (must have verified tech or email)."""

    def __init__(self, min_confidence_score: int = 75):
        self.scorer = LeadScorer(min_confidence_score=min_confidence_score)

    def score_and_filter(
        self,
        job_leads: List[Dict[str, Any]],
        tech_scans: List[Dict[str, Any]],
        intent_leads: List[Dict[str, Any]],
        min_confidence: int = None
    ) -> List[Dict[str, Any]]:
        threshold = min_confidence if min_confidence is not None else 75
        leads = self.scorer.score_and_merge_leads(
            job_leads=job_leads,
            tech_scans=tech_scans,
            intent_leads=intent_leads,
            min_confidence=threshold
        )
        # Require active tech footprint or verified email for strict verification
        return [
            l for l in leads
            if l.get("tech_footprint") or l.get("enrichment", {}).get("hunter_email", {}).get("emails_found")
        ]
