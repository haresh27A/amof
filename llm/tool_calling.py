"""
LLM Tool Calling & Token Accounting Utilities
Component Tag: [A. LLM Utilities]
"""

from typing import Dict, Any

class TokenAccountant:
    """
    Tracks and breaks down token allocation across offline AMORA ranking, prompt context, and output generation.
    Tag: [C. AMORA Proposed Functionality - Token Optimization Analysis]
    """

    @staticmethod
    def calculate_efficiency_metrics(
        prompt_tokens: int,
        output_tokens: int,
        retrieval_latency_ms: float,
        answer_quality_score: float = 0.90,
        alpha: float = 0.4,
        beta: float = 0.3,
        gamma: float = 0.3
    ) -> Dict[str, float]:
        """
        Calculates AMORA Efficiency Score:
        Efficiency = Answer Quality / (alpha * Token Cost + beta * Latency + gamma * Retrieval Cost)
        """
        total_tokens = prompt_tokens + output_tokens
        
        # Normalized metrics [0, 1] for typical bounds
        norm_tokens = min(1.0, total_tokens / 5000.0)
        norm_latency = min(1.0, retrieval_latency_ms / 2000.0)
        norm_cost = min(1.0, total_tokens * 0.00002)

        denominator = alpha * norm_tokens + beta * norm_latency + gamma * norm_cost
        denominator = max(0.01, denominator)

        amora_efficiency_score = answer_quality_score / denominator

        return {
            "prompt_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "metadata_ranking_tokens": 0,  # 0 because AMORA metadata ranking happens outside the LLM!
            "retrieval_latency_ms": round(retrieval_latency_ms, 2),
            "normalized_token_cost": round(norm_tokens, 4),
            "normalized_latency": round(norm_latency, 4),
            "amora_efficiency_score": round(float(amora_efficiency_score), 4)
        }
