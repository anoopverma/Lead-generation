from typing import Dict, Any
from ..strategies.base import IScoringStrategy
from ..strategies.scoring_strategies import (
    DefaultWeightedScoringStrategy,
    StrictVerificationScoringStrategy
)

class ScoringStrategyFactory:
    """
    Factory pattern class for instantiating lead scoring and confidence verification strategies.
    """

    @staticmethod
    def create_scoring_strategy(strategy_type: str = "default", config: Dict[str, Any] = None) -> IScoringStrategy:
        stype = strategy_type.lower().strip()
        config = config or {}
        min_conf = config.get("filtering", {}).get("min_confidence_score", 60)

        if stype in ["default", "weighted"]:
            return DefaultWeightedScoringStrategy(min_confidence_score=min_conf)
        elif stype in ["strict", "high_verification"]:
            return StrictVerificationScoringStrategy(min_confidence_score=min_conf)
        else:
            raise ValueError(f"Unknown scoring strategy type: '{strategy_type}'")
