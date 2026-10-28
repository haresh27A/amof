"""
Unit Tests for Core AMORA Algorithms
Component Tag: [C. AMORA Proposed Functionality Tests]
"""

import pytest
import math
from amora.weights import DynamicWeightGenerator
from amora.profiler import SourceProfiler
from amora.ranking import MultiObjectiveRanker, RankedSource
from amora.conflict import ConflictDetector
from database.models import SourceModel, SourceQualityModel

def test_dynamic_weights_sum_to_one():
    queries = [
        "What is the current real-time inventory level?",
        "Compare return policy details and legal terms.",
        "What is the price of SKU-101?",
        "List all customers."
    ]
    for q in queries:
        weights = DynamicWeightGenerator.generate_weights(q)
        total_w = weights.W_r + weights.W_l + weights.W_f + weights.W_c + weights.W_h + weights.W_k
        assert math.isclose(total_w, 1.0, abs_tol=1e-5), f"Weights sum to {total_w} for query: {q}"

def test_source_profiler_formulas():
    qual = SourceQualityModel(
        source_id="src_test",
        reliability=0.95,
        freshness=0.90,
        cost=0.10,
        latency=0.05,
        availability=0.99,
        conflict_rate=0.02,
        historical_success=0.98
    )
    
    L_i = SourceProfiler.compute_reliability(qual, alpha=0.6, beta=0.4)
    assert 0.0 <= L_i <= 1.0
    
    H_i = SourceProfiler.compute_historical_success(qual)
    assert H_i == 0.98

def test_pareto_ranking_mode():
    s1 = RankedSource(
        source_id="s1", name="Best Source", source_type="SQL", domain="sales", tool_type="sql_tool",
        endpoint_or_schema="", score=0.9, relevance=0.95, reliability=0.99, freshness=0.95,
        cost=0.02, historical_success=0.99, conflict=0.0
    )
    s2 = RankedSource(
        source_id="s2", name="Worst Source", source_type="SQL", domain="sales", tool_type="sql_tool",
        endpoint_or_schema="", score=0.4, relevance=0.40, reliability=0.50, freshness=0.40,
        cost=0.80, historical_success=0.50, conflict=0.2
    )

    ranked = MultiObjectiveRanker._compute_pareto_ranks([s1, s2])
    assert ranked[0].pareto_rank == 1
    assert ranked[1].pareto_rank >= 1

def test_conflict_detector():
    ev1 = {"source_name": "Source A", "content": "The stock level is 45 units in 2026."}
    ev2 = {"source_name": "Source B", "content": "The stock level is 90 units in 2024."}

    report = ConflictDetector.analyze_evidence_conflict([ev1, ev2])
    assert report["conflict_score"] > 0.0
    assert len(report["flagged_conflicts"]) > 0
