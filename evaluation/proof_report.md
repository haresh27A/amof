# AMORA Empirical Validation & Benchmark Proof Report
**Execution Date:** 2026-10-09  |  **Queries Evaluated:** 20  |  **Measurement:** 100% Real

## Table 1: Comparative Baseline Performance (Exact Measurements)
| Baseline Name | Precision@5 | Recall@5 | MRR | nDCG@5 | Avg Latency (ms) | Retrieval Rate | Prompt Tokens |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline 1: Standard RAG** | 0.090 | 0.625 | 0.700 | 0.642 | 1613.5 ms | 100.0% | 509 |
| **Baseline 2: INKER-inspired Pipeline** | 0.160 | 0.900 | 0.767 | 0.801 | 1824.0 ms | 65.0% | 806 |
| **Baseline 3: Similarity-only Source Routing** | 0.180 | 1.000 | 0.817 | 0.864 | 1677.5 ms | 100.0% | 1073 |
| **Baseline 4: Fixed-Weight Multi-Objective Routing** | 0.170 | 0.950 | 0.825 | 0.858 | 1875.8 ms | 100.0% | 1043 |
| **Baseline 5: AMORA Dynamic-Weight Routing (Full)** | 0.150 | 0.850 | 0.725 | 0.758 | 1892.0 ms | 65.0% | 786 |
| **Baseline 6: Random Source Selection** | 0.020 | 0.350 | 0.300 | 0.313 | 1444.4 ms | 100.0% | 542 |

## Table 2: Functional Ablation Matrix (Measured Component Impact)
| Ablation Variant | Precision@5 | Recall@5 | Avg Latency (ms) | Ablation Impact |
| :--- | :---: | :---: | :---: | :--- |
| **AMORA Full** | 0.150 | 0.850 | 1617.2 ms | Baseline (Full) |
| **AMORA - No IE-KRT** | 0.170 | 0.950 | 1855.3 ms | +0.020 P@5 |
| **AMORA - Dynamic Weights (Fixed)** | 0.150 | 0.850 | 1645.7 ms | +0.000 P@5 |
| **AMORA - Reliability** | 0.150 | 0.850 | 1753.2 ms | +0.000 P@5 |
| **AMORA - Freshness** | 0.150 | 0.850 | 1545.8 ms | +0.000 P@5 |
| **AMORA - Historical Success** | 0.150 | 0.850 | 1601.6 ms | +0.000 P@5 |
| **AMORA - Conflict Penalty** | 0.150 | 0.850 | 1625.2 ms | +0.000 P@5 |
| **AMORA - Pre-filtering (Full Scan)** | 0.150 | 0.850 | 1484.3 ms | +0.000 P@5 |

## Table 3: Scalability & Pre-filtering Efficiency
| Catalog Size ($N$) | Stage-1 Filtered ($M$) | Routing Latency (ms) | Source Reduction Ratio (SRR) |
| :---: | :---: | :---: | :---: |
| 100 | 55 | 4.14 ms | 90.9% |
| 500 | 55 | 3.88 ms | 90.9% |
| 1,000 | 55 | 3.29 ms | 90.9% |
| 5,000 | 55 | 3.27 ms | 90.9% |
| 10,000 | 55 | 3.26 ms | 90.9% |