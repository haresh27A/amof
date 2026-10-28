"""
AMORA Multi-Objective Source Ranker
Component Tag: [C. AMORA Proposed Functionality - Multi-Objective Ranking]

Formulas:
  Score_i = W_r R_i + W_l L_i + W_f F_i + W_h H_i - W_c C_i - W_k K_i
  Pareto Mode: Fast Non-Dominated Sorting algorithm

  Dempster-Shafer Theory (DST) Source Belief Fusion:
    Each quality dimension d is treated as an independent Body of Evidence (BoE).
    For each dimension d with score s_d ∈ [0,1]:
        m_d(H)  = s_d          (belief that source is a top-quality source)
        m_d(Ω)  = 1 - s_d      (uncertainty / open-world mass)

    Pairwise DST combination rule (Dempster's rule):
        Given two BoEs A and B:
            K_AB = m_A(H) * m_B(∅)  + m_A(∅) * m_B(H)   (conflict mass, always 0 here)
            m_AB(H) = (m_A(H)*m_B(H) + m_A(H)*m_B(Ω) + m_A(Ω)*m_B(H)) / (1 - K_conflict)
            m_AB(Ω) = (m_A(Ω)*m_B(Ω)) / (1 - K_conflict)

    Applied iteratively across all evidence dimensions to yield m_fused(H) ∈ [0,1].
    Final DST-boosted score = α * amora_score + (1 - α) * m_fused(H)
"""

from typing import List, Dict, Any, Tuple
from pydantic import BaseModel
from database.models import SourceModel, SourceQualityModel
from amora.weights import DynamicWeights
from amora.profiler import SourceProfiler

class RankedSource(BaseModel):
    source_id: str
    name: str
    source_type: str
    domain: str
    tool_type: str
    endpoint_or_schema: str
    score: float
    relevance: float
    reliability: float
    freshness: float
    cost: float
    historical_success: float
    conflict: float
    pareto_rank: int = 1
    # Dempster-Shafer Theory fused belief score (0-1)
    dst_belief: float = 0.0
    # Final blended score combining AMORA score + DST belief
    dst_combined_score: float = 0.0

class DempsterShaferScorer:
    """
    Dempster-Shafer Theory (DST) evidence fusion scorer for source quality analysis.

    Each quality dimension is treated as an independent Body of Evidence (BoE).
    The classic Dempster combination rule fuses all BoEs into a single
    unified belief mass m_fused(H) ∈ [0,1] representing the combined
    degree of belief that a source is a high-quality top source.

    Tag: [C. AMORA Proposed Functionality - Multi-Objective Ranking / DST Fusion]
    """

    @staticmethod
    def _combine_two_boes(
        m1_H: float, m1_omega: float,
        m2_H: float, m2_omega: float
    ) -> tuple:
        """
        Apply Dempster's combination rule to two Bodies of Evidence.

        Hypothesis space: {H, Ω} where
            H     = "source is high quality"
            Ω     = full frame (uncertainty / open-world mass)
            ∅     = empty set (conflict — not possible in our binary frame,
                    so K_conflict = 0 and no normalisation denominator issue)

        Combination:
            m12(H) = m1(H)*m2(H) + m1(H)*m2(Ω) + m1(Ω)*m2(H)
            m12(Ω) = m1(Ω)*m2(Ω)
            (No conflict mass K since H ∩ Ω = H ≠ ∅)

        Returns:
            (m12_H, m12_omega)
        """
        m12_H = m1_H * m2_H + m1_H * m2_omega + m1_omega * m2_H
        m12_omega = m1_omega * m2_omega

        # Normalise in case of floating-point drift
        total = m12_H + m12_omega
        if total > 0:
            m12_H /= total
            m12_omega /= total

        return m12_H, m12_omega

    @classmethod
    def compute_belief(
        cls,
        relevance: float,
        reliability: float,
        freshness: float,
        historical_success: float,
        cost: float = 0.0,
        conflict: float = 0.0
    ) -> float:
        """
        Compute the Dempster-Shafer fused belief m_fused(H) for a source.

        Positive evidence dimensions (higher → more belief in H):
            relevance, reliability, freshness, historical_success

        Negative evidence dimensions (higher → less belief in H, i.e. inverted):
            cost, conflict  →  treated as (1 - value) so high cost/conflict
            reduces the overall fused belief.

        Args:
            relevance:          Relevance score ∈ [0, 1]
            reliability:        Reliability score ∈ [0, 1]
            freshness:          Freshness score ∈ [0, 1]
            historical_success: Historical success rate ∈ [0, 1]
            cost:               Normalised cost ∈ [0, 1]  (inverted for DST)
            conflict:           Conflict rate ∈ [0, 1]    (inverted for DST)

        Returns:
            m_fused_H: Combined DST belief score ∈ [0, 1]
        """
        # --- Build Bodies of Evidence (BoE) as (m_H, m_Omega) pairs ---
        # Clamp all inputs to [0, 1] to guard against profile edge cases
        def _clamp(v: float) -> float:
            return max(0.0, min(1.0, float(v)))

        # Positive dimensions: belief = score, uncertainty = 1 - score
        boes = [
            (_clamp(relevance),          1.0 - _clamp(relevance)),
            (_clamp(reliability),         1.0 - _clamp(reliability)),
            (_clamp(freshness),           1.0 - _clamp(freshness)),
            (_clamp(historical_success),  1.0 - _clamp(historical_success)),
        ]

        # Negative dimensions: invert so high cost/conflict → low belief
        inv_cost     = 1.0 - _clamp(cost)
        inv_conflict = 1.0 - _clamp(conflict)
        boes.append((inv_cost,     1.0 - inv_cost))
        boes.append((inv_conflict, 1.0 - inv_conflict))

        # --- Iterative DST combination across all BoEs ---
        m_H, m_omega = boes[0]
        for m2_H, m2_omega in boes[1:]:
            m_H, m_omega = cls._combine_two_boes(m_H, m_omega, m2_H, m2_omega)

        return round(m_H, 6)


class MultiObjectiveRanker:
    """
    Ranks candidate sources using dynamic multi-objective weighted score or Pareto frontier,
    enhanced with Dempster-Shafer Theory (DST) belief fusion for top-source identification.
    Tag: [C. AMORA Proposed Functionality - Multi-Objective Ranking]
    """

    # Weight α for blending AMORA score vs DST belief in the final combined score.
    # α = 1.0 → pure AMORA score;  α = 0.0 → pure DST belief
    DST_ALPHA: float = 0.55

    @classmethod
    def rank_sources(
        cls,
        candidates: List[Tuple[SourceModel, SourceQualityModel, float]],
        weights: DynamicWeights,
        top_k: int = 5,
        mode: str = "weighted",  # "weighted" or "pareto"
        dst_alpha: float = None   # Override DST_ALPHA if provided
    ) -> List[RankedSource]:
        """
        Rank candidate sources using the AMORA multi-objective score.
        Augments each source with a Dempster-Shafer Theory (DST) fused belief
        score and a final blended dst_combined_score used for top-source selection.

        DST Belief Fusion (see module docstring for full formula):
            m_fused(H) = iterative Dempster combination of BoEs for
            relevance, reliability, freshness, historical_success, 1-cost, 1-conflict

        Final ranking key (when mode="weighted"):
            dst_combined_score = α * amora_score + (1 - α) * dst_belief
        """
        alpha = dst_alpha if dst_alpha is not None else cls.DST_ALPHA
        scored_sources: List[RankedSource] = []

        for src, qual, R_i in candidates:
            L_i = SourceProfiler.compute_reliability(qual)
            F_i = SourceProfiler.compute_freshness(src, qual)
            H_i = SourceProfiler.compute_historical_success(qual)
            C_i = SourceProfiler.compute_cost(qual)
            K_i = SourceProfiler.compute_conflict_rate(qual)

            # ── AMORA Score Formula ──────────────────────────────────────────
            # Score_i = W_r*R_i + W_l*L_i + W_f*F_i + W_h*H_i - W_c*C_i - W_k*K_i
            amora_score = (
                weights.W_r * R_i +
                weights.W_l * L_i +
                weights.W_f * F_i +
                weights.W_h * H_i -
                weights.W_c * C_i -
                weights.W_k * K_i
            )

            # ── Dempster-Shafer Belief Fusion ────────────────────────────────
            # Combines all quality dimensions as independent Bodies of Evidence
            # to yield m_fused(H): degree of belief source is a top source.
            dst_belief = DempsterShaferScorer.compute_belief(
                relevance=float(R_i),
                reliability=float(L_i),
                freshness=float(F_i),
                historical_success=float(H_i),
                cost=float(C_i),
                conflict=float(K_i)
            )

            # ── Blended Final Score ──────────────────────────────────────────
            # dst_combined_score = α * amora_score + (1 - α) * dst_belief
            dst_combined = alpha * float(amora_score) + (1.0 - alpha) * dst_belief

            scored_sources.append(RankedSource(
                source_id=src.source_id,
                name=src.name,
                source_type=src.type,
                domain=src.domain,
                tool_type=src.tool_type,
                endpoint_or_schema=src.endpoint_or_schema or "",
                score=round(float(amora_score), 4),
                relevance=round(float(R_i), 4),
                reliability=round(float(L_i), 4),
                freshness=round(float(F_i), 4),
                cost=round(float(C_i), 4),
                historical_success=round(float(H_i), 4),
                conflict=round(float(K_i), 4),
                pareto_rank=1,
                dst_belief=round(dst_belief, 4),
                dst_combined_score=round(dst_combined, 4)
            ))

        if mode == "pareto":
            scored_sources = cls._compute_pareto_ranks(scored_sources)
            # Sort primarily by pareto rank (ascending), secondarily by DST combined score (descending)
            scored_sources.sort(key=lambda s: (s.pareto_rank, -s.dst_combined_score))
        else:
            # Weighted mode: sort by DST-blended score (AMORA + DST belief) descending
            scored_sources.sort(key=lambda s: s.dst_combined_score, reverse=True)

        return scored_sources[:top_k]

    @classmethod
    def _compute_pareto_ranks(cls, sources: List[RankedSource]) -> List[RankedSource]:
        """
        Fast Non-Dominated Sorting for Pareto optimization.
        Objectives to MAXIMIZE: relevance, reliability, freshness, historical_success
        Objectives to MINIMIZE: cost, conflict

        The objective vectors are projected once up front (cost/conflict negated so every
        objective is maximised), which turns the pairwise comparison into plain tuple
        comparisons instead of re-reading model attributes and rebuilding tuples per pair.
        """
        n = len(sources)
        if n == 0:
            return sources

        # Maximisation projection: negate the two objectives we want to minimise.
        objectives = [
            (
                s.relevance,
                s.reliability,
                s.freshness,
                s.historical_success,
                -s.cost,
                -s.conflict,
            )
            for s in sources
        ]

        domination_counts = [0] * n
        dominated_sets: List[List[int]] = [[] for _ in range(n)]
        current_front: List[int] = []

        # A solution with zero dominators is non-dominated, so it starts on the first front.
        for i in range(n):
            oi = objectives[i]
            for j in range(n):
                if i == j:
                    continue
                oj = objectives[j]
                # i dominates j: at least as good everywhere, strictly better somewhere.
                if all(a >= b for a, b in zip(oi, oj)) and any(a > b for a, b in zip(oi, oj)):
                    dominated_sets[i].append(j)
                elif all(b >= a for a, b in zip(oi, oj)) and any(b > a for a, b in zip(oi, oj)):
                    domination_counts[i] += 1
            if domination_counts[i] == 0:
                current_front.append(i)

        rank = 1
        while current_front:
            next_front: List[int] = []
            for i in current_front:
                for j in dominated_sets[i]:
                    domination_counts[j] -= 1
                    if domination_counts[j] == 0:
                        next_front.append(j)
            for i in current_front + next_front:
                sources[i].pareto_rank = rank
            current_front = next_front
            rank += 1

        return sources
