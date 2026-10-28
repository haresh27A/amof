"""
AMORA Source Router Engine
Component Tag: [C. AMORA Proposed Functionality - Adaptive Source Router]
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.models import SourceModel
from metadata.repository import MetadataRepository
from amora.prefilter import PrefilterEngine
from amora.weights import DynamicWeightGenerator, DynamicWeights
from amora.ranking import MultiObjectiveRanker, RankedSource

class AMORARoutingResult(BaseModel):
    query: str
    retrieval_query: str
    total_catalog_sources: int
    candidate_count: int
    weights: Dict[str, float]
    selected_sources: List[RankedSource]
    allowed_tools: List[str]
    mode: str
    source_reduction_ratio: float

class AMORARouter:
    """
    Main AMORA routing engine coordinating pre-filtering, dynamic weight generation, ranking, and tool candidate mapping.
    Tag: [C. AMORA Proposed Functionality - Adaptive Source Router]
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = MetadataRepository(db)
        self.prefilter_engine = PrefilterEngine(self.repo)

    def route(
        self,
        retrieval_query: str,
        original_query: str = "",
        top_k: int = 5,
        prefilter_n: int = 200,
        mode: str = "weighted",
        cost_sensitive: bool = False,
        conflict_sensitive: bool = False,
        required_tool: Optional[str] = None,
        custom_weights: Optional[DynamicWeights] = None,
        skip_prefilter: bool = False,
    ) -> AMORARoutingResult:
        """
        Execute full AMORA routing pipeline.
        Supports custom_weights and skip_prefilter overrides for ablation experiments.
        """
        query_text = original_query or retrieval_query
        
        # 1. Total catalog count
        all_active = self.repo.get_all_active_sources()
        total_catalog_count = len(all_active)

        # 2. Stage 1 & Stage 2 Pre-filtering
        if skip_prefilter or prefilter_n >= total_catalog_count:
            candidates = [(src, qual, 0.5) for src, qual in all_active]
        else:
            candidates = self.prefilter_engine.prefilter(
                retrieval_query=retrieval_query,
                top_n=prefilter_n,
                required_tool=required_tool
            )
            # Fallback if pre-filtering yielded no candidates
            if not candidates:
                candidates = [(src, qual, 0.5) for src, qual in all_active[:prefilter_n]]

        candidate_count = len(candidates)

        # 3. Dynamic Weight Generation or Custom Override
        if custom_weights is not None:
            weights = custom_weights
        else:
            weights = DynamicWeightGenerator.generate_weights(
                query=query_text,
                cost_sensitive=cost_sensitive,
                conflict_sensitive=conflict_sensitive
            )

        # 4. Multi-Objective Ranking
        ranked_sources: List[RankedSource] = MultiObjectiveRanker.rank_sources(
            candidates=candidates,
            weights=weights,
            top_k=top_k,
            mode=mode
        )

        # 5. Restrict allowed tools based on selected source metadata
        allowed_tools = list(set([s.tool_type for s in ranked_sources]))

        # Calculate Source Reduction Ratio (SRR = 1 - N_selected / N_total)
        srr = 1.0 - (len(ranked_sources) / float(max(1, total_catalog_count)))

        return AMORARoutingResult(
            query=query_text,
            retrieval_query=retrieval_query,
            total_catalog_sources=total_catalog_count,
            candidate_count=candidate_count,
            weights=weights.to_dict(),
            selected_sources=ranked_sources,
            allowed_tools=allowed_tools,
            mode=mode,
            source_reduction_ratio=round(srr, 6)
        )
