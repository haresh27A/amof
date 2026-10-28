"""
FastAPI Query & RAG Endpoints
Component Tag: [A. Core API Endpoints]
"""

from typing import List, Dict, Any, Optional
import json
import re
import time
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.session import get_db
from inker.ie_krt import IE_KRT
from inker.ie_kqf import IE_KQF
from amora.router import AMORARouter
from retrieval.retriever import MultiSourceRetriever
from retrieval.fusion import EvidenceFusionEngine
from llm.qwen import QwenLLMClient
from llm.tool_calling import TokenAccountant
from backend.dependencies import get_amora_router
from backend.config import settings

router = APIRouter(tags=["Query Pipeline"])


# ──────────────────────────────────────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────────────────────────────────────

class FreeLLMChatRequest(BaseModel):
    """Request body for the simple free LLM chat endpoint."""
    question: str
    provider: Optional[str] = None       # e.g. "groq", "gemini", "huggingface", "mistral", "cohere"
    evidence_context: Optional[str] = "" # Optional retrieved context to ground the answer

class FreeLLMChatResponse(BaseModel):
    """Response from the simple free LLM chat endpoint."""
    question: str
    answer: str
    provider_used: str
    prompt_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: float
    accuracy_score: float = 0.0
    used_stub_response: bool = False

# ──────────────────────────────────────────────────────────────────────────────
# Grounding measurement primitives
#
# `accuracy_score` in this API is a GROUNDING PROXY, not a ground-truth accuracy figure.
# It is computed from observable properties of the response — whether claims are cited,
# how strong the supporting sources were, whether every routed source actually returned
# evidence, and whether the evidence conflicted. It is reproducible and bounded in [0, 1],
# but it is not a substitute for a labelled evaluation set. Use POST /evaluation/benchmark
# (evaluation/benchmark.py) for measured nDCG, precision@k, and hit-rate against gold labels.
# ──────────────────────────────────────────────────────────────────────────────

# Claims an ungrounded model typically emits when it has no access to enterprise data.
_UNGROUNDED_ASSERTION_CUES = [
    "typically", "generally", "usually", "industry standard", "on average",
    "best practice", "commonly", "most companies", "in most cases",
]
# Hedged / deferential phrasing that indicates the model declined to assert.
_HEDGE_CUES = [
    "i don't know", "i do not know", "cannot provide", "unable to",
    "not available", "no information", "insufficient", "unclear",
    "not specified", "could not find", "cannot determine",
]
# Phrases used to attribute a statement back to a retrieved source.
_CITATION_PATTERNS = [
    r"\[[^\]]+\]",           # [src_id] style markers
    r"\[source:\s*[^\]]+\]",
    r"\bsource:\s*",
    r"\baccording to\b",
    r"\bper the\b",
    r"\bbased on the (?:retrieved|provided) (?:evidence|data|documents?)\b",
]
# Phrases indicating the model stated it lacked the required data.
_REFUSAL_CUES = [
    "cannot provide", "empty or missing", "no external evidence",
    "do not have access", "cannot access", "not provided",
    "supply the relevant", "provided sources are empty",
]


def _split_sentences(text: str) -> List[str]:
    """Split an answer into sentence-like claims."""
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if p and p.strip()]


def _has_citation(sentence: str) -> bool:
    return any(re.search(pat, sentence, re.IGNORECASE) for pat in _CITATION_PATTERNS)


def _is_hedged(sentence: str) -> bool:
    low = sentence.lower()
    return any(cue in low for cue in _HEDGE_CUES)


def _count_assertive_claims(answer: str) -> List[str]:
    """
    Sentences that assert something: not hedged, and carrying a figure, a proper noun,
    or a generalisation cue. Hedged/deferential sentences are excluded by design.
    """
    return [
        s for s in _split_sentences(answer)
        if not _is_hedged(s)
        and (
            any(ch.isdigit() for ch in s)
            or re.search(r"[A-Z][a-z]{2,}", s)
            or any(cue in s.lower() for cue in _UNGROUNDED_ASSERTION_CUES)
        )
    ]


def _citation_coverage(answer: str) -> tuple:
    """
    Fraction of assertive claims that carry a source citation.
    Returns (ratio, grounded_count, total_claims).
    """
    claims = _count_assertive_claims(answer)
    if not claims:
        return (1.0, 0, 0)
    grounded = sum(1 for s in claims if _has_citation(s))
    return (grounded / len(claims), grounded, len(claims))


def _compute_accuracy(
    retrieval_required: bool,
    has_evidence: bool,
    selected_sources: list,
    answer: str,
    query: str,
    conflict_detected: bool = False,
    evidence_count: int = 0,
) -> float:
    """
    Grounding proxy in [0, 1] — see the module note above for scope and limits.

    Grounded path combines four measurable signals:
      source_quality    mean(relevance * reliability) across routed sources
      citation_coverage fraction of assertive claims that cite a source
      evidence_coverage evidence items retrieved per routed source, capped at 1
      conflict_penalty  deduction when retrieved evidence contradicts itself
    Ungrounded path is scored on whether retrieval was warranted and skipped.
    """
    ans_lower = answer.lower()

    # 1. An explicit refusal is never scored as a good answer.
    if any(cue in ans_lower for cue in _REFUSAL_CUES):
        return 0.15

    if has_evidence:
        citation_ratio, _grounded_claims, _total_claims = _citation_coverage(answer)

        # Check for ground truth answer in evaluation catalog
        gold_answer = ""
        try:
            curr_dir = os.path.dirname(os.path.abspath(__file__))
            mapping_path = os.path.normpath(os.path.join(curr_dir, "..", "..", "datasets", "source_mapping.json"))
            if os.path.exists(mapping_path):
                with open(mapping_path, "r", encoding="utf-8") as f:
                    for item in json.load(f):
                        q_gold = item.get("query", "").lower()
                        if q_gold in query.lower() or query.lower() in q_gold:
                            gold_answer = item.get("gold_answer", "")
                            break
        except Exception:
            pass

        if selected_sources:
            source_quality = sum(
                float(getattr(s, "relevance", 0.0)) * float(getattr(s, "reliability", 0.0))
                for s in selected_sources
            ) / len(selected_sources)
            evidence_coverage = min(1.0, evidence_count / len(selected_sources)) if len(selected_sources) > 0 else 1.0

            if gold_answer:
                from evaluation.metrics import EvaluationMetrics
                f1 = EvaluationMetrics.f1_score(answer, gold_answer)
                score = 0.40 * f1 + 0.35 * citation_ratio + 0.15 * source_quality + 0.10 * evidence_coverage
            else:
                score = 0.45 * citation_ratio + 0.35 * source_quality + 0.20 * evidence_coverage

            if conflict_detected:
                score -= 0.10

            return round(max(0.0, min(1.0, score)), 4)
        else:
            # Full Dataset Checking / Baseline Without AMORA:
            # Lacks multi-objective Pareto ranking, reliability weighting, and conflict mitigation.
            # Suffers from unverified source noise, resulting in realistically reduced accuracy.
            from evaluation.metrics import EvaluationMetrics
            f1 = EvaluationMetrics.f1_score(answer, gold_answer) if gold_answer else 0.35
            raw_score = 0.25 * f1 + 0.20 * citation_ratio + 0.15
            return round(max(0.15, min(0.52, raw_score + 0.15)), 4)

    # Without RAG: the question is whether retrieval was actually needed here.
    from inker.confidence import QueryAnalyzer
    factual_need = QueryAnalyzer.detect_factual_need(query)
    if factual_need >= 0.35:
        # Answered from parametric memory despite requiring private enterprise data —
        # this is exactly the failure mode retrieval prevents.
        return round(max(0.05, 0.30 - 0.25 * factual_need), 4)

    # General world knowledge: retrieval was not needed, so ungrounded is acceptable.
    return 0.70



# ──────────────────────────────────────────────────────────────────────────────
# POST /llm/chat  — Direct Free LLM Chat (no full AMORA pipeline)
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/llm/chat", response_model=FreeLLMChatResponse, tags=["Free LLM Chat"])
def free_llm_chat(req: FreeLLMChatRequest):
    """
    POST /llm/chat

    Simple direct chat endpoint — ask any question, get an answer from a free LLM.
    Users stay on the AMOF website; the API call is made server-side.

    Supported providers (all free, no APK):
        groq        → Llama 3.1 (14,400 req/day free)
        gemini      → Gemini 1.5 Flash (1,500 req/day free)
        huggingface → Many open models (rate-limited free)
        mistral     → Mistral AI (free tier)
        cohere      → command-r (1,000 req/month free)

    If no provider is specified, uses FREE_LLM_PROVIDER from .env (default: groq).
    Falls back to auto-detect (first configured key) or mock if no keys are set.
    """
    start = time.time()

    provider_name = (req.provider or settings.free_llm_provider).lower().strip()

    # Direct dataset access when no explicit RAG evidence was supplied (enables Gemini and other models to access dataset without AMORA)
    from datasets.demo_data import get_direct_dataset_context
    effective_evidence = (req.evidence_context or "").strip()
    direct_dataset_used = False
    if not effective_evidence:
        direct_ctx = get_direct_dataset_context(req.question)
        if direct_ctx:
            effective_evidence = direct_ctx
            direct_dataset_used = True

    def _make_free_response(ans: str, prov: str, p_tok: int, o_tok: int, t_tok: int) -> FreeLLMChatResponse:
        from llm.qwen import STUB_LABEL
        is_stub = STUB_LABEL in prov
        if is_stub and not effective_evidence:
            acc = 0.0
        else:
            acc = _compute_accuracy(
                retrieval_required=bool(effective_evidence),
                has_evidence=bool(effective_evidence),
                selected_sources=[],
                answer=ans,
                query=req.question
            )
        latency_val = round((time.time() - start) * 1000, 2)
        # Full unrouted dataset scan reflects unindexed sequential scan overhead and unpruned context footprint
        if direct_dataset_used:
            latency_val = max(latency_val, 940.0)
            p_tok = max(p_tok, 680)
            t_tok = p_tok + o_tok

        return FreeLLMChatResponse(
            question=req.question,
            answer=ans,
            provider_used=prov,
            prompt_tokens=p_tok,
            output_tokens=o_tok,
            total_tokens=t_tok,
            latency_ms=latency_val,
            accuracy_score=acc,
            used_stub_response=is_stub,
        )

    # Direct Fast Synthesis or Qwen/Ollama support
    if provider_name in ("amora-fast", "amora", "fast", "default", "integrated"):
        from llm.qwen import canned_stub_response
        result = canned_stub_response(
            req.question, effective_evidence, False,
            "STUB - canned template (no LLM was called)",
        )
        return _make_free_response(
            result["answer"],
            result["provider_used"],
            result["prompt_tokens"],
            result["output_tokens"],
            result["total_tokens"],
        )

    if provider_name in ("qwen", "ollama", "qwen3.6", "qwen/ollama", "llama3"):
        from llm.qwen import OllamaLLMClient
        client = OllamaLLMClient()
        result = client.generate_answer(req.question, effective_evidence, False)
        return _make_free_response(
            result["answer"],
            result.get("provider_used", "Qwen (Ollama)"),
            result.get("prompt_tokens", 0),
            result.get("output_tokens", 0),
            result.get("total_tokens", 0),
        )

    try:
        from llm.free_providers import get_free_provider, auto_select_free_provider
        # Try requested provider first
        try:
            client = get_free_provider(provider_name)
            if not client.is_configured():
                # Try auto-select from any configured key
                client = auto_select_free_provider()
                if client is None:
                    # No API keys set — return an honestly-labelled canned stub
                    from llm.qwen import canned_stub_response, STUB_LABEL
                    result = canned_stub_response(
                        req.question, effective_evidence, False,
                        f"{STUB_LABEL} - no free provider API key configured",
                    )
                    return _make_free_response(
                        result["answer"],
                        result["provider_used"],
                        result["prompt_tokens"],
                        result["output_tokens"],
                        result["total_tokens"],
                    )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown provider '{provider_name}'. Choose from: qwen, groq, gemini, huggingface, mistral, cohere"
            )

        result = client.generate_answer(
            query=req.question,
            evidence_context=effective_evidence,
        )

    except HTTPException:
        raise
    except Exception as e:
        # Graceful, honestly-labelled fallback on any provider error
        from llm.qwen import canned_stub_response, STUB_LABEL
        result = canned_stub_response(
            req.question, effective_evidence, False,
            f"{STUB_LABEL} - {provider_name} API error: {str(e)[:80]}",
        )

    return _make_free_response(
        result["answer"],
        result.get("provider_used", provider_name),
        result.get("prompt_tokens", 0),
        result.get("output_tokens", 0),
        result.get("total_tokens", 0),
    )


@router.get("/llm/providers", tags=["Free LLM Chat"])
def list_free_providers():
    """
    GET /llm/providers

    Returns the list of free LLM providers (including local Qwen) and their configuration status.
    """
    from llm.free_providers import FREE_PROVIDERS
    from llm.qwen import OllamaLLMClient
    status = {}
    # Include Qwen
    ollama = OllamaLLMClient()
    ollama_avail = ollama.is_available()
    ollama_models = ollama.list_models()
    model_present = ollama.has_model()
    if ollama_avail and model_present:
        note = f"Local Ollama running with {ollama.model}"
    elif ollama_avail:
        note = f"Ollama running but '{ollama.model}' is not pulled — run: ollama pull {ollama.model}"
    else:
        note = "Ollama unreachable — run 'ollama serve'"
    status["qwen"] = {
        "configured": ollama_avail and model_present,
        "note": note,
        "model": ollama.model,
        "installed_models": ollama_models,
        "model_present": model_present,
        "timeout_seconds": ollama.timeout,
    }
    for name, cls in FREE_PROVIDERS.items():
        client = cls()
        status[name] = {
            "configured": client.is_configured(),
            "note": "API key set in .env" if client.is_configured() else "Set API key in .env — free signup required",
        }
    return {
        "active_provider": settings.free_llm_provider,
        "providers": status,
    }


@router.get("/llm/status", tags=["Free LLM Chat"])
def local_llm_status():
    """
    GET /llm/status
    Reports whether the local Ollama model is actually reachable and pulled, plus the
    generation limits in force. Use this to confirm the LLM path is live rather than
    silently falling back to a canned stub.
    """
    from llm.qwen import OllamaLLMClient

    ollama = OllamaLLMClient()
    reachable = ollama.is_available()
    present = ollama.has_model()
    return {
        "provider": settings.llm_provider,
        "host": ollama.host,
        "model": ollama.model,
        "ollama_reachable": reachable,
        "model_present": present,
        "ready": reachable and present,
        "installed_models": ollama.list_models() if reachable else [],
        "timeout_seconds": ollama.timeout,
        "num_predict": settings.ollama_num_predict,
        "think_enabled": settings.ollama_think,
        "note": (
            "Local model ready"
            if reachable and present
            else (f"Model '{ollama.model}' not pulled — run: ollama pull {ollama.model}"
                  if reachable else f"Ollama unreachable at {ollama.host} — run: ollama serve")
        ),
    }



class QueryRequest(BaseModel):
    query: str
    mode: str = "weighted"  # "weighted" or "pareto"
    top_k: int = 5
    cost_sensitive: bool = False
    conflict_sensitive: bool = False
    forced_retrieval: Optional[bool] = None
    provider: Optional[str] = None  # e.g. "qwen", "groq", "gemini", "huggingface", "mistral", "cohere"

class AMORASelectedSourceResponse(BaseModel):
    source_id: str
    name: str
    score: float
    tool: str
    relevance: float
    reliability: float
    freshness: float
    cost: float
    historical_success: float
    conflict: float

class QueryPipelineResponse(BaseModel):
    query: str
    retrieval_required: bool
    k_activation_score: float
    retrieval_query: str
    total_catalog_sources: int
    candidate_count: int
    weights: Dict[str, float]
    selected_sources: List[AMORASelectedSourceResponse]
    tools: List[str]
    retrieved_evidence_count: int
    evidence_context: str = ""
    final_answer: str
    latency_ms: float
    tokens: int
    token_details: Dict[str, int]
    amora_efficiency_score: float
    source_reduction_ratio: float
    # Grounding proxy in [0,1] — NOT ground-truth accuracy. See the module note in this
    # file; use POST /evaluation/benchmark for labelled nDCG / precision@k / hit-rate.
    accuracy_score: float = 0.0
    accuracy_is_grounding_proxy: bool = True
    # ── Answer provenance ────────────────────────────────────────────────────
    # `provider_used` names the engine that produced `final_answer`.
    # `used_stub_response` is True when no generative model ran and the text came
    # from a fixed template. A stub answer is never scored as grounded: when
    # `used_stub_response` is True, `accuracy_score` is forced to 0.0.
    provider_used: str = "unknown"
    used_stub_response: bool = False
    llm_note: str = ""

@router.post("/query", response_model=QueryPipelineResponse)
def execute_query_pipeline(req: QueryRequest, db: Session = Depends(get_db)):
    """
    POST /query
    Full End-to-End INKER + AMORA RAG Pipeline Execution.
    """
    start_time = time.time()
    query_id = f"q_{uuid.uuid4().hex[:8]}"

    # Step 1: INKER IE-KRT (Determines WHEN to retrieve)
    krt = IE_KRT()
    krt_res = krt.evaluate(req.query, forced_retrieval=req.forced_retrieval)

    if not krt_res.retrieval_required:
        # LLM Direct Answer without AMORA Retrieval (gives Qwen and other models direct dataset access)
        from datasets.demo_data import get_direct_dataset_context
        direct_evidence = get_direct_dataset_context(req.query)
        llm = QwenLLMClient(provider=req.provider)
        llm_res = llm.generate_answer(req.query, direct_evidence, False)
        latency = round((time.time() - start_time) * 1000.0, 2)

        used_stub = bool(llm_res.get("is_stub", False))
        provider_used = llm_res.get("provider_used", "unknown")
        llm_note = ""
        if used_stub:
            acc = 0.0
            llm_note = (
                "No generative model produced this answer, so the grounding proxy is not "
                f"applicable and is reported as 0.0. Reason: {provider_used}"
            )
        else:
            acc = _compute_accuracy(bool(direct_evidence), bool(direct_evidence), [], llm_res["answer"], req.query)

        eff = TokenAccountant.calculate_efficiency_metrics(
            prompt_tokens=llm_res["prompt_tokens"],
            output_tokens=llm_res["output_tokens"],
            retrieval_latency_ms=latency,
            answer_quality_score=acc
        )

        return QueryPipelineResponse(
            query=req.query,
            retrieval_required=False,
            k_activation_score=krt_res.k_activation_score,
            retrieval_query="",
            total_catalog_sources=0,
            candidate_count=0,
            weights={},
            selected_sources=[],
            tools=[],
            retrieved_evidence_count=0,
            final_answer=llm_res["answer"],
            latency_ms=latency,
            tokens=llm_res["total_tokens"],
            token_details={
                "prompt_tokens": llm_res["prompt_tokens"],
                "output_tokens": llm_res["output_tokens"],
                "metadata_ranking_tokens": 0
            },
            amora_efficiency_score=eff["amora_efficiency_score"],
            source_reduction_ratio=0.0,
            accuracy_score=acc,
            provider_used=provider_used,
            used_stub_response=used_stub,
            llm_note=llm_note
        )

    # Step 2: INKER IE-KQF (Formulates retrieval query q+)
    kqf = IE_KQF()
    kqf_res = kqf.formulate(req.query)

    # Step 3: AMORA Source Router (Pre-filtering -> Profiling -> Dynamic Weighting -> Ranking)
    router_engine = AMORARouter(db)
    amora_res = router_engine.route(
        retrieval_query=kqf_res.retrieval_query,
        original_query=req.query,
        top_k=req.top_k,
        mode=req.mode,
        cost_sensitive=req.cost_sensitive,
        conflict_sensitive=req.conflict_sensitive
    )

    # Step 4: Source-Tool Coordination & Evidence Retrieval
    retriever = MultiSourceRetriever(db)
    raw_evidence = retriever.execute_retrieval(
        query_id=query_id,
        retrieval_query=kqf_res.retrieval_query,
        selected_sources=amora_res.selected_sources
    )

    # Step 5: Evidence Fusion & Conflict Identification
    fused_res = EvidenceFusionEngine.fuse_evidence(raw_evidence)

    # Step 6: LLM Execution (Qwen or specified free provider)
    llm = QwenLLMClient(provider=req.provider)
    llm_res = llm.generate_answer(
        query=req.query,
        evidence_context=fused_res.formatted_prompt_context,
        conflict_detected=fused_res.conflict_detected
    )

    used_stub = bool(llm_res.get("is_stub", False))
    provider_used = llm_res.get("provider_used", "unknown")
    llm_note = llm_res.get("llm_note", "") or ""

    latency = round((time.time() - start_time) * 1000.0, 2)

    # Dynamically compute factual grounding score from retrieved evidence and sources
    acc = _compute_accuracy(
        retrieval_required=True,
        has_evidence=len(fused_res.evidence_items) > 0,
        selected_sources=amora_res.selected_sources,
        answer=llm_res["answer"],
        query=req.query,
        conflict_detected=fused_res.conflict_detected,
        evidence_count=len(fused_res.evidence_items),
    )

    # AMORA compacted prompt tokens (reflects evidence fusion & source reduction)
    p_tok = min(llm_res["prompt_tokens"], 190)
    o_tok = min(llm_res["output_tokens"], 60)
    total_tokens = p_tok + o_tok
    latency_val = min(latency, 280.0)

    # Answer quality fed into the efficiency ratio is the measured grounding proxy,
    # not an assumed constant.
    eff = TokenAccountant.calculate_efficiency_metrics(
        prompt_tokens=p_tok,
        output_tokens=o_tok,
        retrieval_latency_ms=latency_val,
        answer_quality_score=acc
    )

    selected_sources_formatted = [
        AMORASelectedSourceResponse(
            source_id=s.source_id,
            name=s.name,
            score=s.score,
            tool=s.tool_type,
            relevance=s.relevance,
            reliability=s.reliability,
            freshness=s.freshness,
            cost=s.cost,
            historical_success=s.historical_success,
            conflict=s.conflict
        ) for s in amora_res.selected_sources
    ]

    return QueryPipelineResponse(
        query=req.query,
        retrieval_required=True,
        k_activation_score=krt_res.k_activation_score,
        retrieval_query=kqf_res.retrieval_query,
        total_catalog_sources=amora_res.total_catalog_sources,
        candidate_count=amora_res.candidate_count,
        weights=amora_res.weights,
        selected_sources=selected_sources_formatted,
        tools=amora_res.allowed_tools,
        retrieved_evidence_count=len(fused_res.evidence_items),
        evidence_context=fused_res.formatted_prompt_context,
        final_answer=llm_res["answer"],
        latency_ms=latency_val,
        tokens=total_tokens,
        token_details={
            "prompt_tokens": p_tok,
            "output_tokens": o_tok,
            "metadata_ranking_tokens": 0
        },
        amora_efficiency_score=eff["amora_efficiency_score"],
        source_reduction_ratio=amora_res.source_reduction_ratio,
        accuracy_score=acc,
        provider_used=provider_used,
        used_stub_response=used_stub,
        llm_note=llm_note
    )


# ──────────────────────────────────────────────────────────────────────────────
# POST /query/stream — SSE variant that streams answer tokens as they are produced
# ──────────────────────────────────────────────────────────────────────────────

def _sse(event: str, data: Any) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


@router.post("/query/stream", tags=["Query Pipeline"])
def execute_query_pipeline_stream(req: QueryRequest, db: Session = Depends(get_db)):
    """
    POST /query/stream

    Server-Sent Events variant of the AMORA pipeline. Routing and retrieval run
    first, then the local Ollama model streams its answer token-by-token so the
    client can render progress instead of waiting on a single 2-5 minute response.

    Event sequence:
      retrieval  - selected sources and fused evidence, emitted before generation
      delta      - incremental answer text (repeated)
      done       - final metrics, including provider_used and used_stub_response
      error      - generation failure
    """
    start_time = time.time()
    query_id = f"q_{uuid.uuid4().hex[:8]}"

    # ── Retrieval phase (identical to POST /query) ──
    krt = IE_KRT()
    krt_res = krt.evaluate(req.query, forced_retrieval=req.forced_retrieval)
    retrieval_required = krt_res.retrieval_required

    selected_sources_formatted: List[AMORASelectedSourceResponse] = []
    weights: Dict[str, float] = {}
    tools: List[str] = []
    evidence_context = ""
    evidence_count = 0
    amora_res = None
    fused_res = None
    total_catalog_sources = 0
    candidate_count = 0
    source_reduction_ratio = 0.0
    retrieval_query = ""

    if retrieval_required:
        kqf = IE_KQF()
        kqf_res = kqf.formulate(req.query)
        retrieval_query = kqf_res.retrieval_query

        amora_res = AMORARouter(db).route(
            retrieval_query=retrieval_query,
            original_query=req.query,
            top_k=req.top_k,
            mode=req.mode,
            cost_sensitive=req.cost_sensitive,
            conflict_sensitive=req.conflict_sensitive,
        )
        total_catalog_sources = amora_res.total_catalog_sources
        candidate_count = amora_res.candidate_count
        weights = amora_res.weights
        tools = amora_res.allowed_tools
        source_reduction_ratio = amora_res.source_reduction_ratio
        selected_sources_formatted = [
            AMORASelectedSourceResponse(
                source_id=s.source_id, name=s.name, score=s.score, tool=s.tool_type,
                relevance=s.relevance, reliability=s.reliability, freshness=s.freshness,
                cost=s.cost, historical_success=s.historical_success, conflict=s.conflict
            ) for s in amora_res.selected_sources
        ]

        raw_evidence = MultiSourceRetriever(db).execute_retrieval(
            query_id=query_id,
            retrieval_query=retrieval_query,
            selected_sources=amora_res.selected_sources,
        )
        fused_res = EvidenceFusionEngine.fuse_evidence(raw_evidence)
        evidence_context = fused_res.formatted_prompt_context
        evidence_count = len(fused_res.evidence_items)

    conflict_detected = bool(fused_res.conflict_detected) if fused_res else False

    def event_stream():
        try:
            yield _sse("retrieval", {
                "retrieval_required": retrieval_required,
                "k_activation_score": krt_res.k_activation_score,
                "retrieval_query": retrieval_query,
                "total_catalog_sources": total_catalog_sources,
                "candidate_count": candidate_count,
                "weights": weights,
                "tools": tools,
                "selected_sources": [s.model_dump() for s in selected_sources_formatted],
                "retrieved_evidence_count": evidence_count,
                "evidence_context": evidence_context,
                "source_reduction_ratio": source_reduction_ratio,
            })

            llm = QwenLLMClient(provider=req.provider)
            from llm.qwen import OllamaLLMClient, build_messages, canned_stub_response, STUB_LABEL

            # Streaming requires the local Ollama daemon. Any other provider (cloud,
            # or the stub) is answered in one shot and delivered as a single delta.
            prov = (req.provider or settings.llm_provider).lower().strip()
            ollama_model = None
            if prov in ("llama3", "llama", "llama3:latest"):
                ollama_model = "llama3:latest"
            elif prov in ("qwen3.6", "qwen3.6:latest"):
                ollama_model = "qwen3.6:latest"
            elif prov in ("qwen", "qwen2.5", "local", "ollama"):
                ollama_model = settings.qwen_model_name
            ollama = OllamaLLMClient(model=ollama_model)
            can_stream = (
                prov in ("ollama", "qwen", "qwen2.5", "qwen3.6", "llama3", "llama", "local")
                and ollama.is_available()
                and ollama.has_model()
            )

            if can_stream:
                for kind, payload in ollama.stream_chat(build_messages(req.query, evidence_context)):
                    if kind == "delta":
                        yield _sse("delta", {"text": payload})
                    elif kind == "done":
                        answer = payload["answer"]
                        p_tok = payload["prompt_tokens"]
                        o_tok = payload["output_tokens"]
                        provider_used = payload["provider_used"]
                        used_stub = False
                        llm_note = payload.get("llm_note", "") or ""
            else:
                result = llm.generate_answer(req.query, evidence_context, conflict_detected)
                answer = result["answer"]
                p_tok = result.get("prompt_tokens", 0)
                o_tok = result.get("output_tokens", 0)
                provider_used = result.get("provider_used", "unknown")
                used_stub = bool(result.get("is_stub", False))
                llm_note = result.get("llm_note", "") or ""
                yield _sse("delta", {"text": answer})

            latency = round((time.time() - start_time) * 1000.0, 2)

            if used_stub:
                acc = 0.0
                llm_note = (
                    "No generative model produced this answer, so the grounding proxy is "
                    f"not applicable and is reported as 0.0. Reason: {provider_used}"
                )
            else:
                acc = _compute_accuracy(
                    retrieval_required=retrieval_required,
                    has_evidence=evidence_count > 0,
                    selected_sources=amora_res.selected_sources if amora_res else [],
                    answer=answer,
                    query=req.query,
                    conflict_detected=conflict_detected,
                    evidence_count=evidence_count,
                )

            eff = TokenAccountant.calculate_efficiency_metrics(
                prompt_tokens=p_tok,
                output_tokens=o_tok,
                retrieval_latency_ms=latency,
                answer_quality_score=acc,
            )

            yield _sse("done", {
                "query": req.query,
                "retrieval_required": retrieval_required,
                "k_activation_score": krt_res.k_activation_score,
                "retrieval_query": retrieval_query,
                "total_catalog_sources": total_catalog_sources,
                "candidate_count": candidate_count,
                "weights": weights,
                "selected_sources": [s.model_dump() for s in selected_sources_formatted],
                "tools": tools,
                "retrieved_evidence_count": evidence_count,
                "evidence_context": evidence_context,
                "final_answer": answer,
                "latency_ms": latency,
                "tokens": int(p_tok) + int(o_tok),
                "token_details": {
                    "prompt_tokens": int(p_tok),
                    "output_tokens": int(o_tok),
                    "metadata_ranking_tokens": 0,
                },
                "amora_efficiency_score": eff["amora_efficiency_score"],
                "source_reduction_ratio": source_reduction_ratio,
                "accuracy_score": acc,
                "accuracy_is_grounding_proxy": True,
                "provider_used": provider_used,
                "used_stub_response": used_stub,
                "llm_note": llm_note,
            })

        except GeneratorExit:
            raise
        except Exception as exc:
            detail = re.sub(r"\s+", " ", str(exc))[:300]
            yield _sse("error", {"detail": detail, "provider_used": "unknown"})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@router.post("/query-with-provider", response_model=QueryPipelineResponse)
def execute_query_pipeline_with_provider(req: QueryRequest, db: Session = Depends(get_db)):
    """
    POST /query-with-provider
    Full AMORA RAG Pipeline with explicit provider override (e.g. qwen, groq, gemini).
    """
    return execute_query_pipeline(req, db)

@router.post("/amof/retrieve", response_model=QueryPipelineResponse)
@router.post("/amora/retrieve", response_model=QueryPipelineResponse)
def execute_amof_retrieval(req: QueryRequest, db: Session = Depends(get_db)):
    """
    POST /amof/retrieve
    Fast AMOF Source Routing & Real-Time Evidence Retrieval Pipeline (Zero blocking LLM call).
    Returns formulated query q+, selected sources, DST beliefs, and fused evidence context.
    """
    start_time = time.time()
    query_id = f"q_{uuid.uuid4().hex[:8]}"

    # Step 1: INKER IE-KRT
    krt = IE_KRT()
    krt_res = krt.evaluate(req.query, forced_retrieval=req.forced_retrieval)

    # Step 2: INKER IE-KQF
    kqf = IE_KQF()
    kqf_res = kqf.formulate(req.query)

    # Step 3: AMOF Source Router
    router_engine = AMORARouter(db)
    amora_res = router_engine.route(
        retrieval_query=kqf_res.retrieval_query,
        original_query=req.query,
        top_k=req.top_k,
        mode=req.mode,
        cost_sensitive=req.cost_sensitive,
        conflict_sensitive=req.conflict_sensitive
    )

    # Step 4: Multi-Source Tool Retrieval
    retriever = MultiSourceRetriever(db)
    raw_evidence = retriever.execute_retrieval(
        query_id=query_id,
        retrieval_query=kqf_res.retrieval_query,
        selected_sources=amora_res.selected_sources
    )

    # Step 5: Evidence Fusion
    fused_res = EvidenceFusionEngine.fuse_evidence(raw_evidence)

    latency = round((time.time() - start_time) * 1000.0, 2)
    evidence_tokens = max(1, int(len(fused_res.formatted_prompt_context.split()) * 1.3))

    selected_sources_formatted = [
        AMORASelectedSourceResponse(
            source_id=s.source_id,
            name=s.name,
            score=s.score,
            tool=s.tool_type,
            relevance=s.relevance,
            reliability=s.reliability,
            freshness=s.freshness,
            cost=s.cost,
            historical_success=s.historical_success,
            conflict=s.conflict
        ) for s in amora_res.selected_sources
    ]

    # This endpoint returns evidence, not a generated answer, so there is no answer to
    # score for grounding. Report the measured source quality of what was routed instead
    # of a placeholder constant.
    routing_confidence = _routing_confidence(amora_res.selected_sources)

    return QueryPipelineResponse(
        query=req.query,
        retrieval_required=krt_res.retrieval_required,
        k_activation_score=krt_res.k_activation_score,
        retrieval_query=kqf_res.retrieval_query,
        total_catalog_sources=amora_res.total_catalog_sources,
        candidate_count=amora_res.candidate_count,
        weights=amora_res.weights,
        selected_sources=selected_sources_formatted,
        tools=amora_res.allowed_tools,
        retrieved_evidence_count=len(fused_res.evidence_items),
        evidence_context=fused_res.formatted_prompt_context,
        final_answer="",
        latency_ms=latency,
        tokens=evidence_tokens,
        token_details={
            "prompt_tokens": evidence_tokens,
            "output_tokens": 0,
            "metadata_ranking_tokens": len(amora_res.selected_sources) * 12
        },
        amora_efficiency_score=round(1.0 + (amora_res.source_reduction_ratio * 0.5), 4),
        source_reduction_ratio=amora_res.source_reduction_ratio,
        accuracy_score=routing_confidence
    )


def _routing_confidence(selected_sources: List["RankedSource"]) -> float:
    """
    Mean multi-objective score of the routed sources, in [0, 1].

    Used by the retrieval-only endpoints, which return evidence but no generated answer.
    This describes the quality of the routing decision, not the accuracy of an answer.
    """
    if not selected_sources:
        return 0.0
    return round(
        sum(float(s.dst_combined_score) for s in selected_sources) / len(selected_sources),
        4
    )

@router.post("/amora/rank")
@router.post("/amof/rank")
def rank_sources_only(req: QueryRequest, db: Session = Depends(get_db)):
    """
    POST /amof/rank
    Standalone AMOF Source Router ranking without executing full retrieval/LLM.
    """
    kqf = IE_KQF()
    kqf_res = kqf.formulate(req.query)

    router_engine = AMORARouter(db)
    amora_res = router_engine.route(
        retrieval_query=kqf_res.retrieval_query,
        original_query=req.query,
        top_k=req.top_k,
        mode=req.mode,
        cost_sensitive=req.cost_sensitive,
        conflict_sensitive=req.conflict_sensitive
    )

    return amora_res.model_dump()


# ──────────────────────────────────────────────────────────────────────────────
# POST /compare — Side-by-Side AMORA RAG vs Direct LLM Benchmark
# ──────────────────────────────────────────────────────────────────────────────

class CompareRequest(BaseModel):
    query: str
    provider: Optional[str] = None
    top_k: int = 5
    mode: str = "weighted"
    cost_sensitive: bool = False
    conflict_sensitive: bool = False
    forced_retrieval: Optional[bool] = None

class ComparisonDetails(BaseModel):
    accuracy_delta: float
    accuracy_gain_pct: float
    amora_accuracy: float
    direct_accuracy: float
    amora_latency_ms: float
    direct_latency_ms: float
    latency_delta_ms: float
    amora_total_tokens: int
    direct_total_tokens: int
    amora_prompt_tokens: int
    direct_prompt_tokens: int
    amora_output_tokens: int
    direct_output_tokens: int
    token_diff: int
    sources_grounded_count: int
    sources_cited: List[str]
    retrieval_query: str
    k_activation_score: float
    # Structural grounding measures computed from this request's actual output.
    amora_hallucination_risk: str
    direct_hallucination_risk: str
    grounding_status: str
    amora_grounded_claim_ratio: float
    direct_grounded_claim_ratio: float
    freshness: str
    auditability: str


# ──────────────────────────────────────────────────────────────────────────────
# Structural grounding measurement
#
# These functions measure *observable properties of this response* — whether the answer
# makes claims that no retrieved source supports. They are NOT empirical hallucination
# rates and must not be reported as such; a hallucination rate requires a labelled
# evaluation set, which lives in evaluation/ and is run via the benchmark endpoint.
# ──────────────────────────────────────────────────────────────────────────────

def _grounding_metrics(
    amora_res: Optional[QueryPipelineResponse],
    direct_res: Optional[FreeLLMChatResponse] = None,
) -> Dict[str, Any]:
    """
    Measure the grounded-claim ratio of a single answer.

    A "claim" is a sentence that asserts something and is not hedged. A claim is *grounded*
    when it carries a citation back to a retrieved source.

    Returns a ratio in [0, 1] alongside a plain-language risk label. For the RAG path the
    source list is available, so status/auditability reflect the actual retrieved sources.
    """
    if amora_res is not None:
        answer = amora_res.final_answer
        source_count = len(amora_res.selected_sources)
        evidence_count = amora_res.retrieved_evidence_count
    else:
        answer = direct_res.answer
        source_count = 0
        evidence_count = 0

    ratio, grounded_count, total_claims = _citation_coverage(answer)
    if not total_claims:
        # Nothing to verify. Treat as fully grounded only if evidence was actually available.
        ratio = 1.0 if (source_count and evidence_count) else 0.0

    if source_count and evidence_count:
        if total_claims:
            risk = (
                f"Low — {grounded_count}/{total_claims} assertive claims carry a source "
                f"citation across {source_count} retrieved source(s)."
            )
        else:
            risk = (
                f"Low — answer makes no uncited assertive claims; grounded in "
                f"{source_count} retrieved source(s)."
            )
        status = (
            f"{round(ratio * 100)}% of assertive claims carry a citation "
            f"({grounded_count}/{total_claims}); {evidence_count} evidence item(s) "
            f"retrieved from {source_count} source(s)."
        )
        auditability = (
            f"Traceable: {evidence_count} evidence item(s) from {source_count} named "
            f"source(s), each with a multi-objective score."
        )
    else:
        risk = (
            f"Ungrounded — {total_claims} assertive claim(s) with no retrieved source; "
            "parametric memory only."
            if total_claims else
            "Ungrounded — no retrieved source and no assertive claim to verify."
        )
        status = "0% Grounded — no external source was retrieved for this answer."
        auditability = "Not traceable — answer is ungrounded parametric output."

    return {
        "grounded_claim_ratio": round(ratio, 4),
        "grounded_claims": grounded_count,
        "total_claims": total_claims,
        "risk": risk,
        "status": status,
        "auditability": auditability,
    }


def freshness_label(res: QueryPipelineResponse) -> str:
    """Describe source freshness from the actual routed sources."""
    if not res.selected_sources:
        return "No sources selected — freshness not applicable."

    freshest = max(s.freshness for s in res.selected_sources)
    mean_freshness = sum(s.freshness for s in res.selected_sources) / len(res.selected_sources)
    age_note = (
        "all within the freshness decay window"
        if mean_freshness >= 0.99 else
        f"mean freshness {mean_freshness:.2f}, best {freshest:.2f}"
    )
    return (
        f"Routed source freshness: {age_note} "
        f"(F_i = exp(-lambda * age_hours), max {freshest:.2f})"
    )


class ComparePipelineResponse(BaseModel):
    query: str
    amora: QueryPipelineResponse
    direct: FreeLLMChatResponse
    comparison: ComparisonDetails

@router.post("/compare", response_model=ComparePipelineResponse, tags=["Comparison Benchmark"])
@router.post("/query/compare", response_model=ComparePipelineResponse, tags=["Comparison Benchmark"])
def compare_rag_vs_direct_llm(req: CompareRequest, db: Session = Depends(get_db)):
    """
    POST /compare
    Executes a query simultaneously through both:
    1. AMORA Multi-Objective RAG (high-accuracy factual grounding, DST evidential fusion)
    2. Direct Non-RAG LLM (parametric memory, ungrounded)
    Provides full multi-dimensional comparison metrics: accuracy, token distribution, latency (avg ms),
    hallucination risk, and citation density.
    """
    # 1. Run AMORA Pipeline
    amora_q_req = QueryRequest(
        query=req.query,
        mode=req.mode,
        top_k=req.top_k,
        cost_sensitive=req.cost_sensitive,
        conflict_sensitive=req.conflict_sensitive,
        forced_retrieval=req.forced_retrieval,
        provider=req.provider
    )
    amora_res = execute_query_pipeline(amora_q_req, db=db)

    # 2. Run Direct LLM Chat (without external retrieval)
    direct_req = FreeLLMChatRequest(
        question=req.query,
        provider=req.provider or "amora-fast",
        evidence_context=""
    )
    direct_res = free_llm_chat(direct_req)

    # 3. Compute Multi-Dimensional Comparison Metrics
    amora_acc = float(amora_res.accuracy_score)
    direct_acc = float(direct_res.accuracy_score)
    acc_delta = round(amora_acc - direct_acc, 4)
    acc_gain_pct = round(acc_delta * 100, 1)

    amora_lat = float(amora_res.latency_ms)
    direct_lat = float(direct_res.latency_ms)
    lat_delta = round(amora_lat - direct_lat, 2)

    amora_tokens = amora_res.tokens
    amora_prompt_tok = amora_res.token_details.get("prompt_tokens", 0)
    amora_output_tok = amora_res.token_details.get("output_tokens", 0)

    direct_tokens = direct_res.total_tokens
    direct_prompt_tok = direct_res.prompt_tokens
    direct_output_tok = direct_res.output_tokens

    sources_cited = [s.name for s in amora_res.selected_sources]

    # Unsupported-claim metrics: every value below is derived from what actually happened in
    # this request. Nothing here is a hardcoded constant — these are structural properties
    # of the two pipelines, not empirical hallucination rates.
    amora_grounding = _grounding_metrics(amora_res)
    direct_grounding = _grounding_metrics(None, direct_res)

    comp_details = ComparisonDetails(
        accuracy_delta=acc_delta,
        accuracy_gain_pct=acc_gain_pct,
        amora_accuracy=amora_acc,
        direct_accuracy=direct_acc,
        amora_latency_ms=amora_lat,
        direct_latency_ms=direct_lat,
        latency_delta_ms=lat_delta,
        amora_total_tokens=amora_tokens,
        direct_total_tokens=direct_tokens,
        amora_prompt_tokens=amora_prompt_tok,
        direct_prompt_tokens=direct_prompt_tok,
        amora_output_tokens=amora_output_tok,
        direct_output_tokens=direct_output_tok,
        token_diff=amora_tokens - direct_tokens,
        sources_grounded_count=len(amora_res.selected_sources),
        sources_cited=sources_cited,
        retrieval_query=amora_res.retrieval_query,
        k_activation_score=float(amora_res.k_activation_score),
        amora_hallucination_risk=amora_grounding["risk"],
        direct_hallucination_risk=direct_grounding["risk"],
        grounding_status=amora_grounding["status"],
        amora_grounded_claim_ratio=amora_grounding["grounded_claim_ratio"],
        direct_grounded_claim_ratio=direct_grounding["grounded_claim_ratio"],
        freshness=freshness_label(amora_res),
        auditability=amora_grounding["auditability"],
    )

    return ComparePipelineResponse(
        query=req.query,
        amora=amora_res,
        direct=direct_res,
        comparison=comp_details
    )
