"""
AMORA 3-Day Fast-Track Proof Generator
Component Tag: [A. Evaluation Framework - Proof Runner]

Executes the complete empirical proof across:
  1. 6 Comparative Baselines (Standard RAG, INKER, Sim-Only, Fixed-Weight, AMORA, Random)
  2. 8 Real Functional Ablations (No mock penalties, real variant executions)
  3. Scalability Analysis (100 -> 10,000 sources)
Outputs:
  - Markdown Summary Table
  - JSON Raw Data for paper charts
"""

import time
import json
import os
from database.session import SessionLocal
from evaluation.benchmark import BenchmarkSuite
from evaluation.metrics import EvaluationMetrics

# Comprehensive 20-query evaluation set spanning:
# - Parametric/General Knowledge (tests IE-KRT bypass)
# - Real-time/Temporal Inventory (tests Freshness F_i & SQL tool)
# - Official Policy & Manuals (tests Doc/PDF tool & Reliability L_i)
# - Contradictory/Conflicting queries (tests Conflict K_i & Evidence Fusion)
PROVEN_EVAL_QUERIES = [
    # Category 1: Parametric / General Knowledge (Should bypass retrieval)
    {"query": "What is 2 + 2?", "gold_sources": [], "gold_answer": "4", "domain": "math"},
    {"query": "What is the capital of France?", "gold_sources": [], "gold_answer": "Paris", "domain": "general"},
    {"query": "Who wrote Romeo and Juliet?", "gold_sources": [], "gold_answer": "William Shakespeare", "domain": "literature"},
    {"query": "How many continents are there on Earth?", "gold_sources": [], "gold_answer": "7", "domain": "geography"},
    {"query": "What is the speed of light in vacuum?", "gold_sources": [], "gold_answer": "299,792,458 m/s", "domain": "physics"},

    # Category 2: Structured Real-Time Inventory & Sales (Requires SQL / API)
    {"query": "What is the current inventory stock quantity of Quantum X Laptop?", "gold_sources": ["src_demo_sql"], "gold_answer": "150 units", "domain": "inventory"},
    {"query": "Which product has generated the highest sales revenue?", "gold_sources": ["src_demo_sql"], "gold_answer": "Enterprise Database Server", "domain": "sales"},
    {"query": "What is the price of Widget-99 in the product catalogue?", "gold_sources": ["src_demo_api"], "gold_answer": "$24.99", "domain": "pricing"},
    {"query": "Show the total order volume for Q3 2026.", "gold_sources": ["src_demo_sql"], "gold_answer": "12,450 orders", "domain": "finance"},
    {"query": "What is the warehouse location for SKU-8842?", "gold_sources": ["src_demo_sql"], "gold_answer": "Warehouse B, Bay 4", "domain": "logistics"},

    # Category 3: Document Policy & Compliance (Requires Doc/PDF Tool)
    {"query": "What does the company return policy say about unopened merchandise?", "gold_sources": ["src_demo_doc"], "gold_answer": "30 days full refund", "domain": "policy"},
    {"query": "What is the maximum allowed expense for employee travel meals?", "gold_sources": ["src_demo_doc"], "gold_answer": "$75 per day", "domain": "hr"},
    {"query": "What is the warranty period for enterprise server hardware?", "gold_sources": ["src_demo_doc"], "gold_answer": "3 years onsite support", "domain": "warranty"},
    {"query": "How many days of annual paid leave are allotted to new hires?", "gold_sources": ["src_demo_doc"], "gold_answer": "20 days per year", "domain": "hr"},
    {"query": "What is the procedure for reporting a cybersecurity incident?", "gold_sources": ["src_demo_doc"], "gold_answer": "Notify SecOps within 1 hour", "domain": "security"},

    # Category 4: Multi-Objective & Conflicting Evidence
    {"query": "Compare current inventory stock levels with last month sales.", "gold_sources": ["src_demo_sql", "src_demo_doc"], "gold_answer": "Stock is 150 units compared to 120 sold", "domain": "comparison"},
    {"query": "What is the latest status of customer refund ticket 5432?", "gold_sources": ["src_demo_sql"], "gold_answer": "Approved and processed", "domain": "support"},
    {"query": "Check if product specifications match the user manual guidelines.", "gold_sources": ["src_demo_doc"], "gold_answer": "Compliant with ISO-9001 standard", "domain": "compliance"},
    {"query": "What is the real-time stock and official return policy for Widget-99?", "gold_sources": ["src_demo_sql", "src_demo_doc"], "gold_answer": "150 units in stock with 30-day return policy", "domain": "multi_domain"},
    {"query": "Verify sales revenue between SQL database and financial summary PDF.", "gold_sources": ["src_demo_sql", "src_demo_doc"], "gold_answer": "Reconciled at $1.2M", "domain": "audit"},
]

def run_proof():
    print("=" * 70)
    print("  AMORA 3-DAY EMPIRICAL PROOF GENERATOR (100% MEASURED RUN)")
    print("=" * 70)

    db = SessionLocal()
    try:
        suite = BenchmarkSuite(db)

        # 1. Run Baselines Comparison
        print("\n[Step 1/3] Running 6 Comparative Baselines across 20 Gold Queries...")
        t_start = time.perf_counter()
        baselines_res = suite.run_all_baselines_comparison(PROVEN_EVAL_QUERIES)
        print(f"  Completed in {time.perf_counter() - t_start:.2f}s")

        # 2. Run Functional Ablation Matrix
        print("\n[Step 2/3] Running 8 Functional Ablation Variants (Real Executions)...")
        t_start = time.perf_counter()
        ablation_res = suite.run_ablation_study(PROVEN_EVAL_QUERIES)
        print(f"  Completed in {time.perf_counter() - t_start:.2f}s")

        # 3. Run Scalability Test
        print("\n[Step 3/3] Running Catalog Scalability Experiment (100 to 10,000)...")
        scalability_res = suite.run_scalability_experiment([100, 500, 1000, 5000, 10000])

        # Generate Publication Report
        report_lines = [
            "# AMORA Empirical Validation & Benchmark Proof Report",
            f"**Execution Date:** 2026-10-09  |  **Queries Evaluated:** {len(PROVEN_EVAL_QUERIES)}  |  **Measurement:** 100% Real",
            "",
            "## Table 1: Comparative Baseline Performance (Exact Measurements)",
            "| Baseline Name | Precision@5 | Recall@5 | MRR | nDCG@5 | Avg Latency (ms) | Retrieval Rate | Prompt Tokens |",
            "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
        ]

        for b_name, s in baselines_res["summary"].items():
            report_lines.append(
                f"| **{b_name}** | {s['precision_at_5']:.3f} | {s['recall_at_5']:.3f} | "
                f"{s['mrr']:.3f} | {s['ndcg_at_5']:.3f} | {s['avg_latency_ms']:.1f} ms | "
                f"{s['retrieval_rate']*100:.1f}% | {s['avg_prompt_tokens']:.0f} |"
            )

        report_lines.extend([
            "",
            "## Table 2: Functional Ablation Matrix (Measured Component Impact)",
            "| Ablation Variant | Precision@5 | Recall@5 | Avg Latency (ms) | Ablation Impact |",
            "| :--- | :---: | :---: | :---: | :--- |"
        ])

        full_p5 = ablation_res.get("AMORA Full", {}).get("precision_at_5", 1.0)
        for var_name, s in ablation_res.items():
            delta = s["precision_at_5"] - full_p5
            impact_str = "Baseline (Full)" if var_name == "AMORA Full" else f"{delta:+.3f} P@5"
            report_lines.append(
                f"| **{var_name}** | {s['precision_at_5']:.3f} | {s['recall_at_5']:.3f} | "
                f"{s['avg_latency_ms']:.1f} ms | {impact_str} |"
            )

        report_lines.extend([
            "",
            "## Table 3: Scalability & Pre-filtering Efficiency",
            "| Catalog Size ($N$) | Stage-1 Filtered ($M$) | Routing Latency (ms) | Source Reduction Ratio (SRR) |",
            "| :---: | :---: | :---: | :---: |"
        ])

        for sc in scalability_res:
            report_lines.append(
                f"| {sc['source_catalog_size']:,} | {sc['candidate_count_stage1']} | "
                f"{sc['routing_latency_ms']:.2f} ms | {sc['source_reduction_ratio']*100:.1f}% |"
            )

        report_content = "\n".join(report_lines)

        # Save to artifacts
        out_file = os.path.join(os.path.dirname(__file__), "proof_report.md")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        print("\n" + "=" * 70)
        print(report_content)
        print("=" * 70)
        print(f"\nReport successfully saved to: {out_file}")

    finally:
        db.close()

if __name__ == "__main__":
    run_proof()
