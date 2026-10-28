"""
FastAPI Benchmark & Evaluation Endpoints
Component Tag: [A. Benchmark API]
"""

import os
import json
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from evaluation.benchmark import BenchmarkSuite

router = APIRouter(prefix="/evaluation", tags=["Evaluation & Benchmarks"])

RESULTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "datasets", "evaluation_results", "benchmark_latest.json")

@router.post("/run")
def run_evaluation_benchmark(db: Session = Depends(get_db)):
    """
    POST /evaluation/run
    Executes benchmark experiments comparing 6 baselines, 10k scalability test, and ablation matrix.
    """
    suite = BenchmarkSuite(db)

    # Sample evaluation dataset queries
    dataset_queries = [
        {
            "query_id": "q001",
            "query": "What is the current inventory stock quantity of Quantum X Laptop?",
            "gold_sources": ["src_demo_sql"],
            "gold_answer": "45 units in Warehouse A."
        },
        {
            "query_id": "q002",
            "query": "What does the company return policy say about unopened merchandise?",
            "gold_sources": ["src_demo_doc"],
            "gold_answer": "Unopened merchandise can be returned within 30 days."
        },
        {
            "query_id": "q003",
            "query": "Which product has generated the highest sales revenue?",
            "gold_sources": ["src_demo_sql"],
            "gold_answer": "Quantum X Laptop (P-101)."
        }
    ]

    baselines_summary = suite.run_all_baselines_comparison(dataset_queries)
    scalability_results = suite.run_scalability_experiment([100, 1000, 5000, 10000])
    ablation_summary = suite.run_ablation_study(dataset_queries)

    output = {
        "baselines_summary": baselines_summary["summary"],
        "scalability_experiment": scalability_results,
        "ablation_study": ablation_summary,
        "detailed_baseline_outputs": baselines_summary["detailed_results"]
    }

    # Save to evaluation_results directory
    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    return {
        "status": "success",
        "message": "Benchmark suite executed successfully.",
        "results": output
    }

@router.get("/results")
def get_latest_evaluation_results():
    """
    GET /evaluation/results
    Fetch latest cached evaluation experiment results.
    """
    if not os.path.exists(RESULTS_PATH):
        return {
            "status": "empty",
            "message": "No evaluation benchmark results found. Run POST /evaluation/run first."
        }
    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
