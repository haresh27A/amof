"""
INKER IE-KRT: Knowledge Retrieval Trigger
Component Tag: [B. INKER-Inspired Functionality]

Formula:
  K(t_i) = (E - m_i) * S_i
  where:
    E = query complexity [0, 1]
    m_i = model/token confidence [0, 1]
    S_i = semantic contribution [0, 1]
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel
from inker.confidence import QueryAnalyzer

class IEKRTResult(BaseModel):
    retrieval_required: bool
    k_activation_score: float
    confidence: float
    reason: str
    mode_used: str

class IE_KRT:
    """
    Decides WHEN external retrieval is required.
    Tag: [B. INKER-Inspired Functionality]
    """
    
    def __init__(self, activation_threshold: float = 0.15):
        self.threshold = activation_threshold

    def evaluate(
        self, 
        query: str, 
        model_logits: Optional[Dict[str, Any]] = None,
        forced_retrieval: Optional[bool] = None
    ) -> IEKRTResult:
        """
        Evaluate if external retrieval is necessary.
        """
        if forced_retrieval is not None:
            return IEKRTResult(
                retrieval_required=forced_retrieval,
                k_activation_score=1.0 if forced_retrieval else 0.0,
                confidence=1.0,
                reason="Forced retrieval override",
                mode_used="manual"
            )

        query_complexity = QueryAnalyzer.estimate_complexity(query)  # E
        factual_need = QueryAnalyzer.detect_factual_need(query)
        temporal_need = QueryAnalyzer.detect_temporal_need(query)

        # Mode A: Model Logits / Token Confidence available
        if model_logits and "token_confidence" in model_logits:
            mode = "Mode A (Model-Confidence)"
            m_i = float(model_logits["token_confidence"])
            S_i = max(0.4, factual_need + temporal_need)
        else:
            # Mode B: Fallback Query-Uncertainty Mode
            mode = "Mode B (Query-Uncertainty Fallback)"
            # Internal model confidence for generic/factual queries is estimated as inversely proportional to specific data needs
            m_i = max(0.1, 1.0 - (0.5 * factual_need + 0.4 * temporal_need))
            S_i = min(1.0, 0.3 + factual_need * 0.4 + temporal_need * 0.3)

        # INKER Activation Score Formula: K = (E - m_i) * S_i
        # We ensure a minimum baseline activation when factual/temporal urgency is high
        raw_k = (query_complexity - m_i) * S_i
        # Scaled activation formula accounting for external knowledge dependence:
        k_activation = max(raw_k, (factual_need + temporal_need) * 0.6)

        retrieval_required = k_activation >= self.threshold

        reason = (
            f"High external knowledge need detected (activation score K={k_activation:.3f} >= threshold {self.threshold:.3f})."
            if retrieval_required else
            f"Parametric model knowledge sufficient (activation score K={k_activation:.3f} < threshold {self.threshold:.3f})."
        )

        return IEKRTResult(
            retrieval_required=retrieval_required,
            k_activation_score=round(float(k_activation), 4),
            confidence=round(float(1.0 - m_i), 4),
            reason=reason,
            mode_used=mode
        )
