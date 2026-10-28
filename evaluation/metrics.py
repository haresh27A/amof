"""
AMORA Research Metrics & Evaluation Formulas
Component Tag: [A. Evaluation Framework]

Includes:
  Source Reduction Ratio (SRR) = 1 - (N_selected / N_total)
  Source Selection Precision@K & Recall@K
  MRR, nDCG@K
  Exact Match (EM), F1
  AMORA Efficiency Score
"""

import math
import re
from typing import List, Set, Dict, Any

class EvaluationMetrics:
    """
    Computes precision, recall, SRR, nDCG, EM, F1, and AMORA efficiency score.
    Tag: [A. Evaluation Framework]
    """

    @staticmethod
    def source_reduction_ratio(n_selected: int, n_total: int) -> float:
        """SRR = 1 - (N_selected / N_total)"""
        if n_total <= 0:
            return 0.0
        return max(0.0, 1.0 - (n_selected / float(n_total)))

    @staticmethod
    def precision_at_k(selected_sources: List[str], gold_sources: List[str], k: int = 5) -> float:
        """Precision@K = relevant_selected / K"""
        if not selected_sources or k <= 0:
            return 0.0
        top_k_selected = selected_sources[:k]
        relevant_count = sum(1 for s in top_k_selected if s in gold_sources)
        return float(relevant_count / float(k))

    @staticmethod
    def recall_at_k(selected_sources: List[str], gold_sources: List[str], k: int = 5) -> float:
        """Recall@K = relevant_selected / total_relevant"""
        if not gold_sources:
            return 1.0  # If no gold source needed, return 1.0
        if not selected_sources or k <= 0:
            return 0.0
        top_k_selected = selected_sources[:k]
        relevant_count = sum(1 for s in top_k_selected if s in gold_sources)
        return float(relevant_count / float(len(gold_sources)))

    @staticmethod
    def mean_reciprocal_rank(selected_sources: List[str], gold_sources: List[str]) -> float:
        """MRR = 1 / rank of first relevant source."""
        if not gold_sources:
            return 1.0
        for rank, s_id in enumerate(selected_sources, 1):
            if s_id in gold_sources:
                return 1.0 / rank
        return 0.0

    @staticmethod
    def ndcg_at_k(selected_sources: List[str], gold_sources: List[str], k: int = 5) -> float:
        """nDCG@K normalized discounted cumulative gain."""
        if not gold_sources:
            return 1.0
        dcg = 0.0
        for rank, s_id in enumerate(selected_sources[:k], 1):
            rel = 1.0 if s_id in gold_sources else 0.0
            dcg += rel / math.log2(rank + 1)

        idcg = sum(1.0 / math.log2(r + 1) for r in range(1, min(len(gold_sources), k) + 1))
        if idcg == 0.0:
            return 0.0
        return float(dcg / idcg)

    @staticmethod
    def exact_match(prediction: str, ground_truth: str) -> float:
        """Normalized string exact match."""
        p_clean = re.sub(r'[^\w\s]', '', prediction.lower()).strip()
        g_clean = re.sub(r'[^\w\s]', '', ground_truth.lower()).strip()
        return 1.0 if p_clean == g_clean else 0.0

    @staticmethod
    def f1_score(prediction: str, ground_truth: str) -> float:
        """
        Token-level F1 score between prediction and ground truth text (SQuAD/HotpotQA multiset standard).
        """
        from collections import Counter
        p_tokens = re.sub(r'[^\w\s]', '', prediction.lower()).split()
        g_tokens = re.sub(r'[^\w\s]', '', ground_truth.lower()).split()
        if not p_tokens or not g_tokens:
            return 0.0

        p_counter = Counter(p_tokens)
        g_counter = Counter(g_tokens)
        common_count = sum((p_counter & g_counter).values())
        if common_count == 0:
            return 0.0

        precision = common_count / float(len(p_tokens))
        recall = common_count / float(len(g_tokens))
        if precision + recall == 0:
            return 0.0
        return float(2 * (precision * recall) / (precision + recall))
