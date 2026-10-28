"""
AMORA Offline Metadata Generator & Embedding Pipeline
Component Tag: [A. Offline Metadata Generation]
"""

from typing import Dict, Any, List, Optional, Tuple
import datetime
import threading
import numpy as np
from sentence_transformers import SentenceTransformer

from backend.config import settings
from metadata.sql_profiler import SQLProfiler
from metadata.api_profiler import APIProfiler
from metadata.document_profiler import DocumentProfiler

# Global singleton encoder to avoid re-loading model on every call.
# FastAPI dispatches sync endpoints on a threadpool, so guard loading with a lock.
_embedding_model: Optional[Any] = None
_model_load_lock = threading.Lock()

# Sentinel stored in _embedding_model when the semantic model is unavailable.
_FALLBACK_SENTINEL = "hash-fallback"


def _load_embedding_model() -> Any:
    """Resolve the embedding backend once, thread-safely. Returns the model or the fallback sentinel."""
    if settings.embedding_backend == "hash" or settings.embedding_model == "fallback":
        return _FALLBACK_SENTINEL

    try:
        model = SentenceTransformer(settings.embedding_model)
    except Exception as exc:
        if settings.embedding_backend == "model":
            raise RuntimeError(
                f"EMBEDDING_BACKEND=model but '{settings.embedding_model}' could not be loaded: {exc}"
            ) from exc
        print(
            f"[AMORA] Semantic embedding model '{settings.embedding_model}' unavailable ({exc}); "
            "falling back to the deterministic hash encoder. Relevance scoring will be "
            "lexical only until the model can be installed."
        )
        return _FALLBACK_SENTINEL

    # Renamed in newer sentence-transformers releases; support both.
    get_dim = getattr(model, "get_embedding_dimension", None) or model.get_sentence_embedding_dimension
    model_dim = get_dim()
    if model_dim is not None and model_dim != settings.embedding_dimension:
        msg = (
            f"'{settings.embedding_model}' produces {model_dim}-dim vectors but "
            f"EMBEDDING_DIMENSION is {settings.embedding_dimension}."
        )
        if settings.embedding_backend == "model":
            raise RuntimeError(msg)
        print(f"[AMORA] {msg} Falling back to the deterministic hash encoder.")
        return _FALLBACK_SENTINEL

    return model


def get_embedding_model() -> Any:
    """Lazily resolve and cache the embedding backend. Returns the model or the fallback sentinel."""
    global _embedding_model
    if _embedding_model is None:
        with _model_load_lock:
            if _embedding_model is None:
                _embedding_model = _load_embedding_model()
    return _embedding_model


def encoder_signature() -> str:
    """
    Identity of the active encoder: backend + model name + dimension.
    Stored alongside every embedding so vectors from different encoders are never mixed
    inside a single FAISS index.
    """
    model = get_embedding_model()
    backend = "hash" if model is _FALLBACK_SENTINEL else settings.embedding_model
    return f"{backend}:{settings.embedding_dimension}"


def _hash_fallback_vector(text: str, dim: int) -> List[float]:
    """
    Deterministic md5-bucketed bag-of-words vector.

    This is a LEXICAL fallback, not a semantic embedding: it captures term overlap only and
    provides no notion of synonymy or paraphrase. It exists so the system degrades gracefully
    when the SentenceTransformer backend cannot be loaded.
    """
    import hashlib
    words = text.lower().split()
    vec = np.zeros(dim, dtype=np.float32)
    for w in words:
        h = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16)
        vec[h % dim] += 1.0 if (h % 2 == 0) else -1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    else:
        vec[0] = 1.0
    return vec.tolist()


def encode_text_to_vector(text: str, dim: Optional[int] = None) -> List[float]:
    """
    Encode text to an L2-normalized vector.

    Uses the configured SentenceTransformer backend when available so cosine similarity
    reflects real semantic relatedness; otherwise falls back to the deterministic hash
    encoder. Either way the result is unit-normalized, which is what the FAISS
    IndexFlatIP inner-product index requires.
    """
    dim = dim or settings.embedding_dimension
    model = get_embedding_model()

    if model is not _FALLBACK_SENTINEL:
        try:
            vec = np.asarray(
                model.encode(text, convert_to_numpy=True, normalize_embeddings=True),
                dtype=np.float32,
            ).reshape(-1)
            if vec.shape[0] == dim:
                norm = float(np.linalg.norm(vec))
                if norm > 0:
                    return (vec / norm).tolist()
        except Exception:
            # Encoder failed at inference time — degrade rather than fail the request.
            pass

    return _hash_fallback_vector(text, dim)


class MetadataGenerator:
    """
    Generates structured offline metadata for external sources without LLM query overhead.
    Tag: [A. Offline Metadata Generation]
    """

    @classmethod
    def generate_source_metadata(
        cls,
        source_id: str,
        name: str,
        source_type: str,
        domain: str,
        description: str,
        endpoint_or_schema: str,
        tool_type: Optional[str] = None,
        reliability: float = 1.0,
        cost: float = 0.0,
        latency: float = 0.1,
        availability: float = 1.0,
        freshness: float = 1.0
    ) -> Dict[str, Any]:
        """
        Extract profile info, assemble metadata, and generate vector embedding.
        """
        st_lower = source_type.lower()
        
        # Tool Type determination
        if not tool_type:
            if "sql" in st_lower or "database" in st_lower:
                tool_type = "sql_tool"
            elif "api" in st_lower or "rest" in st_lower:
                tool_type = "api_tool"
            elif "pdf" in st_lower or "doc" in st_lower or "file" in st_lower:
                tool_type = "doc_tool"
            elif "vector" in st_lower or "faiss" in st_lower:
                tool_type = "vector_tool"
            elif "web" in st_lower or "url" in st_lower:
                tool_type = "web_tool"
            else:
                tool_type = "doc_tool"

        schema_summary = ""
        endpoint_summary = ""
        document_summary = ""
        capabilities = f"Retrieval access for domain '{domain}' with tool type '{tool_type}'."

        if tool_type == "sql_tool":
            sql_prof = SQLProfiler.profile_database(endpoint_or_schema)
            schema_summary = sql_prof["schema_summary"]
            capabilities += " " + sql_prof["capabilities"]
        elif tool_type == "api_tool":
            api_prof = APIProfiler.profile_openapi_spec(endpoint_or_schema)
            endpoint_summary = api_prof["endpoint_summary"]
            capabilities += " " + api_prof["capabilities"]
        elif tool_type == "doc_tool":
            doc_prof = DocumentProfiler.profile_file(endpoint_or_schema)
            document_summary = doc_prof["document_summary"]
            capabilities += " " + doc_prof["capabilities"]
        else:
            capabilities += " Vector semantic knowledge search."

        # Metadata text blob for embedding
        text_for_embedding = f"{name} Domain: {domain}. Description: {description}. Capabilities: {capabilities}. Details: {schema_summary} {endpoint_summary} {document_summary}".strip()

        # Offline Embedding Generation
        vector = encode_text_to_vector(text_for_embedding)

        now_obj = datetime.datetime.now(datetime.timezone.utc)

        return {
            "source": {
                "source_id": source_id,
                "name": name,
                "type": source_type,
                "domain": domain,
                "description": description,
                "capabilities": capabilities,
                "tool_type": tool_type,
                "endpoint_or_schema": endpoint_or_schema,
                "active": True,
                "created_at": now_obj,
                "updated_at": now_obj
            },
            "quality": {
                "source_id": source_id,
                "reliability": reliability,
                "freshness": freshness,
                "cost": cost,
                "latency": latency,
                "availability": availability,
                "conflict_rate": 0.0,
                "historical_success": 1.0
            },
            "embedding": {
                "source_id": source_id,
                "embedding": vector,
                "encoder_signature": encoder_signature(),
                "embedding_text": text_for_embedding,
            },
            "summary_fields": {
                "schema_summary": schema_summary,
                "endpoint_summary": endpoint_summary,
                "document_summary": document_summary
            }
        }
