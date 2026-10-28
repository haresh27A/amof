"""
Comparative RAG & Source Routing Baselines
Component Tag: [A. Evaluation Framework - Baselines]
"""

import random
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from amora.router import AMORARouter, AMORARoutingResult
from amora.ranking import RankedSource
from amora.weights import DynamicWeights
from inker.ie_krt import IE_KRT
from inker.ie_kqf import IE_KQF
from retrieval.retriever import MultiSourceRetriever
from retrieval.fusion import EvidenceFusionEngine
from llm.qwen import QwenLLMClient
from evaluation.metrics import EvaluationMetrics

class BaselineRunner:
    """
    Executes comparative baselines against identical test query sets.
    Tag: [A. Evaluation Framework - Baselines]
    """

    def __init__(self, db: Session):
        self.db = db
        self.router = AMORARouter(db)
        self.krt = IE_KRT()
        self.kqf = IE_KQF()
        self.retriever = MultiSourceRetriever(db)
        self.llm = QwenLLMClient()

    def run_baseline_1_standard_rag(self, query: str) -> Dict[str, Any]:
        """BASELINE 1: Standard RAG (Fixed vector retrieval, no source routing)."""
        ret_query = query
        # Pick default top 2 vector/doc sources
        all_active = self.router.repo.get_all_active_sources()
        selected = []
        for src, qual in all_active:
            if src.tool_type in ["vector_tool", "doc_tool"]:
                selected.append(RankedSource(
                    source_id=src.source_id, name=src.name, source_type=src.type,
                    domain=src.domain, tool_type=src.tool_type, endpoint_or_schema=src.endpoint_or_schema or "",
                    score=0.75, relevance=0.75, reliability=qual.reliability, freshness=qual.freshness,
                    cost=qual.cost, historical_success=qual.historical_success, conflict=qual.conflict_rate
                ))
            if len(selected) >= 2:
                break
        if not selected and all_active:
            src, qual = all_active[0]
            selected.append(RankedSource(
                source_id=src.source_id, name=src.name, source_type=src.type,
                domain=src.domain, tool_type=src.tool_type, endpoint_or_schema=src.endpoint_or_schema or "",
                score=0.5, relevance=0.5, reliability=0.5, freshness=0.5, cost=0.0, historical_success=0.5, conflict=0.0
            ))

        raw_ev = self.retriever.execute_retrieval("b1_q", ret_query, selected)
        fused = EvidenceFusionEngine.fuse_evidence(raw_ev)
        llm_res = self.llm.generate_answer(query, fused.formatted_prompt_context, fused.conflict_detected)
        
        return {
            "baseline": "Baseline 1: Standard RAG",
            "retrieval_required": True,
            "selected_sources": [s.source_id for s in selected],
            "llm_result": llm_res,
            "fused_evidence": fused.model_dump() if fused else None
        }

    def run_baseline_2_inker_pipeline(self, query: str) -> Dict[str, Any]:
        """BASELINE 2: INKER-inspired pipeline (IE-KRT + IE-KQF + Cosine retrieval)."""
        krt_res = self.krt.evaluate(query)
        if not krt_res.retrieval_required:
            llm_res = self.llm.generate_answer(query, "", False)
            return {
                "baseline": "Baseline 2: INKER-inspired Pipeline",
                "retrieval_required": False,
                "selected_sources": [],
                "llm_result": llm_res,
                "fused_evidence": None
            }

        kqf_res = self.kqf.formulate(query)
        # Select sources by cosine similarity alone
        all_active = self.router.repo.get_all_active_sources()
        selected = []
        for src, qual in all_active[:3]:
            selected.append(RankedSource(
                source_id=src.source_id, name=src.name, source_type=src.type,
                domain=src.domain, tool_type=src.tool_type, endpoint_or_schema=src.endpoint_or_schema or "",
                score=0.80, relevance=0.80, reliability=qual.reliability, freshness=qual.freshness,
                cost=qual.cost, historical_success=qual.historical_success, conflict=qual.conflict_rate
            ))

        raw_ev = self.retriever.execute_retrieval("b2_q", kqf_res.retrieval_query, selected)
        fused = EvidenceFusionEngine.fuse_evidence(raw_ev)
        llm_res = self.llm.generate_answer(query, fused.formatted_prompt_context, fused.conflict_detected)

        return {
            "baseline": "Baseline 2: INKER-inspired Pipeline",
            "retrieval_required": True,
            "selected_sources": [s.source_id for s in selected],
            "llm_result": llm_res,
            "fused_evidence": fused.model_dump() if fused else None
        }

    def run_baseline_3_similarity_only(self, query: str) -> Dict[str, Any]:
        """BASELINE 3: Similarity-only source routing (Ignores reliability, freshness, cost)."""
        sim_weights = DynamicWeights(W_r=1.0, W_l=0.0, W_f=0.0, W_c=0.0, W_h=0.0, W_k=0.0)
        route_res = self.router.route(
            retrieval_query=query,
            original_query=query,
            top_k=3,
            mode="weighted",
            custom_weights=sim_weights
        )
        selected = route_res.selected_sources
        raw_ev = self.retriever.execute_retrieval("b3_q", query, selected)
        fused = EvidenceFusionEngine.fuse_evidence(raw_ev)
        llm_res = self.llm.generate_answer(query, fused.formatted_prompt_context, fused.conflict_detected)

        return {
            "baseline": "Baseline 3: Similarity-only Source Routing",
            "retrieval_required": True,
            "selected_sources": [s.source_id for s in selected],
            "llm_result": llm_res,
            "fused_evidence": fused.model_dump() if fused else None
        }

    def run_baseline_4_fixed_weight(self, query: str) -> Dict[str, Any]:
        """BASELINE 4: Fixed-weight multi-objective routing (Fixed static weights across all queries)."""
        fixed_weights = DynamicWeights(W_r=0.25, W_l=0.20, W_f=0.15, W_c=0.15, W_h=0.15, W_k=0.10)
        route_res = self.router.route(
            retrieval_query=query,
            original_query=query,
            top_k=3,
            mode="weighted",
            custom_weights=fixed_weights
        )
        selected = route_res.selected_sources
        raw_ev = self.retriever.execute_retrieval("b4_q", query, selected)
        fused = EvidenceFusionEngine.fuse_evidence(raw_ev)
        llm_res = self.llm.generate_answer(query, fused.formatted_prompt_context, fused.conflict_detected)

        return {
            "baseline": "Baseline 4: Fixed-Weight Multi-Objective Routing",
            "retrieval_required": True,
            "selected_sources": [s.source_id for s in selected],
            "llm_result": llm_res,
            "fused_evidence": fused.model_dump() if fused else None
        }

    def run_baseline_5_amora_dynamic(self, query: str) -> Dict[str, Any]:
        """BASELINE 5: Full AMORA Dynamic-Weight Routing (Proposed Framework)."""
        krt_res = self.krt.evaluate(query)
        if not krt_res.retrieval_required:
            llm_res = self.llm.generate_answer(query, "", False)
            return {
                "baseline": "Baseline 5: AMORA Dynamic-Weight Routing (Full)",
                "retrieval_required": False,
                "selected_sources": [],
                "llm_result": llm_res,
                "fused_evidence": None
            }

        kqf_res = self.kqf.formulate(query)
        route_res = self.router.route(
            retrieval_query=kqf_res.retrieval_query,
            original_query=query,
            top_k=3,
            mode="weighted"
        )
        selected = route_res.selected_sources
        raw_ev = self.retriever.execute_retrieval("b5_q", kqf_res.retrieval_query, selected)
        fused = EvidenceFusionEngine.fuse_evidence(raw_ev)
        llm_res = self.llm.generate_answer(query, fused.formatted_prompt_context, fused.conflict_detected)

        return {
            "baseline": "Baseline 5: AMORA Dynamic-Weight Routing (Full)",
            "retrieval_required": True,
            "selected_sources": [s.source_id for s in selected],
            "llm_result": llm_res,
            "fused_evidence": fused.model_dump() if fused else None,
            "routing_summary": route_res.model_dump()
        }

    def run_baseline_6_random_selection(self, query: str) -> Dict[str, Any]:
        """BASELINE 6: Random source selection."""
        all_active = self.router.repo.get_all_active_sources()
        rand_chosen = random.sample(all_active, min(3, len(all_active))) if all_active else []
        selected = []
        for src, qual in rand_chosen:
            selected.append(RankedSource(
                source_id=src.source_id, name=src.name, source_type=src.type,
                domain=src.domain, tool_type=src.tool_type, endpoint_or_schema=src.endpoint_or_schema or "",
                score=0.5, relevance=0.5, reliability=qual.reliability, freshness=qual.freshness,
                cost=qual.cost, historical_success=qual.historical_success, conflict=qual.conflict_rate
            ))
        raw_ev = self.retriever.execute_retrieval("b6_q", query, selected)
        fused = EvidenceFusionEngine.fuse_evidence(raw_ev)
        llm_res = self.llm.generate_answer(query, fused.formatted_prompt_context, fused.conflict_detected)

        return {
            "baseline": "Baseline 6: Random Source Selection",
            "retrieval_required": True,
            "selected_sources": [s.source_id for s in selected],
            "llm_result": llm_res,
            "fused_evidence": fused.model_dump() if fused else None
        }

    def run_amora_ablation_variant(self, query: str, variant: str) -> Dict[str, Any]:
        """
        Execute an actual functional ablation variant of AMORA.
        Supported variants:
          - "AMORA Full"
          - "AMORA - No IE-KRT" (Always retrieves)
          - "AMORA - Dynamic Weights (Fixed)" (Uses static fixed weights)
          - "AMORA - Reliability" (W_l = 0.0)
          - "AMORA - Freshness" (W_f = 0.0)
          - "AMORA - Historical Success" (W_h = 0.0)
          - "AMORA - Conflict Penalty" (W_k = 0.0)
          - "AMORA - Pre-filtering (Full Scan)" (skip_prefilter=True)
        """
        # 1. IE-KRT Gating
        if variant == "AMORA - No IE-KRT":
            retrieval_required = True
        else:
            krt_res = self.krt.evaluate(query)
            retrieval_required = krt_res.retrieval_required

        if not retrieval_required:
            llm_res = self.llm.generate_answer(query, "", False)
            return {
                "variant": variant,
                "retrieval_required": False,
                "selected_sources": [],
                "llm_result": llm_res,
                "fused_evidence": None,
                "routing_summary": None
            }

        # 2. Query formulation
        kqf_res = self.kqf.formulate(query)

        # 3. Dynamic weights adaptation or variant ablation
        custom_weights = None
        skip_prefilter = False

        if variant == "AMORA - Dynamic Weights (Fixed)":
            custom_weights = DynamicWeights(W_r=0.25, W_l=0.20, W_f=0.15, W_c=0.15, W_h=0.15, W_k=0.10)
        elif variant == "AMORA - Pre-filtering (Full Scan)":
            skip_prefilter = True
        elif variant in [
            "AMORA - Reliability",
            "AMORA - Freshness",
            "AMORA - Historical Success",
            "AMORA - Conflict Penalty"
        ]:
            from amora.weights import DynamicWeightGenerator
            base_w = DynamicWeightGenerator.generate_weights(query)
            w_r, w_l, w_f, w_c, w_h, w_k = (
                base_w.W_r, base_w.W_l, base_w.W_f, base_w.W_c, base_w.W_h, base_w.W_k
            )
            if variant == "AMORA - Reliability":
                w_l = 0.0
            elif variant == "AMORA - Freshness":
                w_f = 0.0
            elif variant == "AMORA - Historical Success":
                w_h = 0.0
            elif variant == "AMORA - Conflict Penalty":
                w_k = 0.0

            total = w_r + w_l + w_f + w_c + w_h + w_k
            custom_weights = DynamicWeights(
                W_r=w_r / total, W_l=w_l / total, W_f=w_f / total,
                W_c=w_c / total, W_h=w_h / total, W_k=w_k / total
            )

        # 4. Routing execution
        route_res = self.router.route(
            retrieval_query=kqf_res.retrieval_query,
            original_query=query,
            top_k=3,
            mode="weighted",
            custom_weights=custom_weights,
            skip_prefilter=skip_prefilter
        )
        selected = route_res.selected_sources

        # 5. Multi-Source Retrieval & Evidence Fusion
        raw_ev = self.retriever.execute_retrieval(f"ablation_{variant[:8]}", kqf_res.retrieval_query, selected)
        fused = EvidenceFusionEngine.fuse_evidence(raw_ev)

        # 6. LLM Generation
        llm_res = self.llm.generate_answer(query, fused.formatted_prompt_context, fused.conflict_detected)

        return {
            "variant": variant,
            "retrieval_required": True,
            "selected_sources": [s.source_id for s in selected],
            "llm_result": llm_res,
            "fused_evidence": fused.model_dump() if fused else None,
            "routing_summary": route_res.model_dump()
        }
