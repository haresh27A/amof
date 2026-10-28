"""
AMORA Dynamic Source Profiler
Component Tag: [C. AMORA Proposed Functionality - Dynamic Source Profiling]

Formulas:
  Relevance R_i in [0, 1]
  Reliability L_i = alpha * success_rate + beta * availability (alpha + beta = 1)
  Freshness F_i = exp(-lambda * delta_t)
  Cost C_i in [0, 1]
  Historical Success H_i = (successes + alpha) / (attempts + alpha + beta)
  Conflict Rate K_i in [0, 1]
"""

import math
from datetime import datetime, timezone
from typing import Dict, Any
from backend.config import settings
from database.models import SourceQualityModel, SourceModel

class SourceProfiler:
    """
    Computes dynamic normalized feature metrics for candidate sources.
    Tag: [C. AMORA Proposed Functionality - Dynamic Source Profiling]
    """

    @staticmethod
    def compute_reliability(
        qual: SourceQualityModel, 
        alpha: float = settings.alpha_reliability, 
        beta: float = settings.beta_availability
    ) -> float:
        """
        L_i = alpha * success_rate_i + beta * availability_i (alpha + beta = 1)
        """
        success_rate = qual.historical_success if qual.historical_success is not None else 1.0
        availability = qual.availability if qual.availability is not None else 1.0
        
        # Ensure alpha + beta = 1.0
        tot = alpha + beta
        a_norm = alpha / tot
        b_norm = beta / tot

        L_i = a_norm * success_rate + b_norm * availability
        return max(0.0, min(1.0, float(L_i)))

    @staticmethod
    def compute_freshness(
        src: SourceModel, 
        qual: SourceQualityModel, 
        lambda_param: float = settings.lambda_freshness
    ) -> float:
        """
        F_i = exp(-lambda * delta_t_hours)
        For sources where freshness is non-applicable, returns neutral value 1.0.
        """
        if src.updated_at is None:
            return qual.freshness if qual.freshness is not None else 1.0

        now = datetime.now(timezone.utc)
        up_time = src.updated_at
        if up_time.tzinfo is None:
            up_time = up_time.replace(tzinfo=timezone.utc)

        delta_t_hours = max(0.0, (now - up_time).total_seconds() / 3600.0)
        
        # Exponential decay calculation
        F_i = math.exp(-lambda_param * delta_t_hours)
        return max(0.0, min(1.0, float(F_i)))

    @staticmethod
    def compute_historical_success(qual: SourceQualityModel) -> float:
        """
        H_i = Bayesian smoothed success rate
        """
        return max(0.0, min(1.0, float(qual.historical_success or 1.0)))

    @staticmethod
    def compute_cost(qual: SourceQualityModel) -> float:
        """
        C_i in [0, 1] normalized cost penalty.
        """
        return max(0.0, min(1.0, float(qual.cost or 0.0)))

    @staticmethod
    def compute_conflict_rate(qual: SourceQualityModel) -> float:
        """
        K_i in [0, 1] normalized conflict penalty.
        """
        return max(0.0, min(1.0, float(qual.conflict_rate or 0.0)))
