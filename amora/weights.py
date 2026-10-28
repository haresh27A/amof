"""
AMORA Dynamic Weight Generator
Component Tag: [C. AMORA Proposed Functionality - Dynamic Weight Generation]

Constraint:
  W_r + W_l + W_f + W_c + W_h + W_k = 1
"""

from typing import Dict
from pydantic import BaseModel
from inker.confidence import QueryAnalyzer

class DynamicWeights(BaseModel):
    W_r: float  # Relevance weight
    W_l: float  # Reliability weight
    W_f: float  # Freshness weight
    W_c: float  # Cost weight penalty
    W_h: float  # Historical success weight
    W_k: float  # Conflict penalty weight

    def to_dict(self) -> Dict[str, float]:
        return {
            "relevance": round(self.W_r, 4),
            "reliability": round(self.W_l, 4),
            "freshness": round(self.W_f, 4),
            "cost": round(self.W_c, 4),
            "historical_success": round(self.W_h, 4),
            "conflict": round(self.W_k, 4)
        }


class DynamicWeightGenerator:
    """
    Extracts query characteristics and dynamically computes objective weights sum(W) = 1.
    Tag: [C. AMORA Proposed Functionality - Dynamic Weight Generation]
    """

    @classmethod
    def generate_weights(
        cls,
        query: str,
        cost_sensitive: bool = False,
        conflict_sensitive: bool = False
    ) -> DynamicWeights:
        """
        Transparent rule-based dynamic weight generator.
        """
        # Feature extraction
        q_complexity = QueryAnalyzer.estimate_complexity(query)
        q_freshness_need = QueryAnalyzer.detect_temporal_need(query)
        q_reliability_need = QueryAnalyzer.detect_factual_need(query)
        q_ambiguity = max(0.0, 1.0 - q_complexity)

        # Baseline initial weights
        w_r = 0.30  # Relevance
        w_l = 0.20  # Reliability
        w_f = 0.15  # Freshness
        w_c = 0.10  # Cost
        w_h = 0.15  # Historical success
        w_k = 0.10  # Conflict

        # Rule 1: High temporal urgency -> increase Freshness weight
        if q_freshness_need > 0.5:
            delta_f = 0.25 * q_freshness_need
            w_f += delta_f
            w_r -= delta_f * 0.5
            w_h -= delta_f * 0.5

        # Rule 2: Factual/authoritative lookup -> increase Reliability weight
        if q_reliability_need > 0.5:
            delta_l = 0.20 * q_reliability_need
            w_l += delta_l
            w_c -= delta_l * 0.5
            w_k -= delta_l * 0.5

        # Rule 3: Cost-sensitive constraints
        if cost_sensitive:
            w_c += 0.20
            w_r -= 0.10
            w_f -= 0.10

        # Rule 4: Ambiguous queries -> rely heavily on Relevance
        if q_ambiguity > 0.6:
            w_r += 0.15
            w_h -= 0.15

        # Rule 5: Conflict sensitivity
        if conflict_sensitive or "compare" in query.lower() or "versus" in query.lower():
            w_k += 0.15
            w_l += 0.05
            w_r -= 0.10

        # Clamp all raw weights > 0.02
        w_r = max(0.05, w_r)
        w_l = max(0.05, w_l)
        w_f = max(0.05, w_f)
        w_c = max(0.02, w_c)
        w_h = max(0.05, w_h)
        w_k = max(0.02, w_k)

        # Normalize sum(W) = 1.0
        total_w = w_r + w_l + w_f + w_c + w_h + w_k
        W_r = float(w_r / total_w)
        W_l = float(w_l / total_w)
        W_f = float(w_f / total_w)
        W_c = float(w_c / total_w)
        W_h = float(w_h / total_w)
        W_k = float(w_k / total_w)

        return DynamicWeights(
            W_r=W_r,
            W_l=W_l,
            W_f=W_f,
            W_c=W_c,
            W_h=W_h,
            W_k=W_k
        )
