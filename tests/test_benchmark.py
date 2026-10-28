"""
Test suite for empirical benchmark evaluation and ablation variants.
Component Tag: [A. Evaluation Framework - Tests]
"""

import pytest
from database.session import SessionLocal
from evaluation.benchmark import BenchmarkSuite
from evaluation.baselines import BaselineRunner
from evaluation.metrics import EvaluationMetrics

def test_evaluation_metrics_multiset_f1():
    # Identical texts
    assert EvaluationMetrics.exact_match("Widget 99", "widget 99") == 1.0
    assert EvaluationMetrics.f1_score("150 units in stock", "150 units in stock") == 1.0

    # Partial overlap with repeated words
    pred = "stock stock 150 units"
    gold = "stock 150 units"
    f1 = EvaluationMetrics.f1_score(pred, gold)
    assert 0.8 <= f1 < 1.0

    # No overlap
    assert EvaluationMetrics.f1_score("Quantum Laptop", "Widget 99") == 0.0

def test_benchmark_suite_execution():
    db = SessionLocal()
    try:
        suite = BenchmarkSuite(db)
        queries = [
            {
                "query": "What is the current inventory stock quantity of Quantum X Laptop?",
                "gold_sources": ["SRC-001"],
                "gold_answer": "150 units"
            },
            {
                "query": "What is 2 + 2?",
                "gold_sources": [],
                "gold_answer": "4"
            }
        ]
        
        # Test baseline comparison
        comparison = suite.run_all_baselines_comparison(queries)
        assert "summary" in comparison
        assert "detailed_results" in comparison
        assert "Baseline 5: AMORA Dynamic-Weight Routing (Full)" in comparison["summary"]
        
        b5_summary = comparison["summary"]["Baseline 5: AMORA Dynamic-Weight Routing (Full)"]
        assert "precision_at_5" in b5_summary
        assert "avg_latency_ms" in b5_summary
        assert b5_summary["avg_latency_ms"] > 0.0

        # Test true ablation variants
        ablation = suite.run_ablation_study(queries[:1])
        assert "AMORA Full" in ablation
        assert "AMORA - No IE-KRT" in ablation
        assert "AMORA - Dynamic Weights (Fixed)" in ablation
        assert "AMORA - Pre-filtering (Full Scan)" in ablation
        assert ablation["AMORA Full"]["avg_latency_ms"] > 0.0
    finally:
        db.close()

