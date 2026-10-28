"""
AMORA Metadata Repository & FAISS Index Manager
Component Tag: [C. AMORA Proposed Functionality - Scalable Pre-filtering]
"""

from typing import List, Dict, Any, Optional, Tuple
import json
import numpy as np
import faiss
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from database.models import SourceModel, SourceQualityModel, SourceEmbeddingModel, RetrievalLogModel
from backend.config import settings
from metadata.generator import encode_text_to_vector, encoder_signature

# Process-level FAISS index cache.
# Keyed by database URL + dimension + a cheap fingerprint of the embedding table, so the
# index is rebuilt only when the embedded source set actually changes. Without this the
# index was rebuilt from scratch on every MetadataRepository construction, i.e. every request.
_INDEX_CACHE: Dict[str, Any] = {
    "key": None,
    "index": None,
    "source_id_map": [],
    "dim": None,
}


class MetadataRepository:
    """
    Manages persistence of metadata in DB and maintains FAISS vector index for fast pre-filtering.
    Tag: [C. AMORA Proposed Functionality - Scalable Pre-filtering]
    """

    def __init__(self, db: Session):
        self.db = db
        self.dim = settings.embedding_dimension
        self.signature = encoder_signature()
        self.faiss_index, self.source_id_map = self._get_or_build_index()

    def _stale_condition(self):
        """
        SQL predicate matching embeddings not produced by the active encoder.

        NULL signatures (rows written before signature tracking existed) must be matched
        explicitly, since `col != value` evaluates to NULL for NULL columns in SQL.
        """
        return or_(
            SourceEmbeddingModel.encoder_signature.is_(None),
            SourceEmbeddingModel.encoder_signature != self.signature,
        )

    def _embedding_fingerprint(self) -> Tuple[int, int]:
        """
        Cheap fingerprint of the embedding table:
        (total rows, rows produced by the active encoder).

        Any insert, delete, or encoder re-tag changes one of these, which invalidates the
        cached FAISS index. A signature mismatch means the vector was produced by a
        different encoder and must not enter the index.
        """
        total = self.db.query(func.count(SourceEmbeddingModel.source_id)).scalar() or 0
        matching = (
            self.db.query(func.count(SourceEmbeddingModel.source_id))
            .filter(SourceEmbeddingModel.encoder_signature == self.signature)
            .scalar()
            or 0
        )
        return int(total), int(matching)

    def _get_or_build_index(self) -> Tuple[Any, List[str]]:
        """Return the cached FAISS index when still valid, otherwise rebuild it."""
        total, matching = self._embedding_fingerprint()
        key = (settings.database_url, self.dim, self.signature, total, matching)

        cached = _INDEX_CACHE
        if cached["key"] == key and cached["index"] is not None:
            return cached["index"], cached["source_id_map"]

        index, source_ids = self._build_index()
        _INDEX_CACHE["key"] = key
        _INDEX_CACHE["index"] = index
        _INDEX_CACHE["source_id_map"] = source_ids
        _INDEX_CACHE["dim"] = self.dim
        return index, source_ids

    def invalidate_index_cache(self) -> None:
        """Force the next index access to rebuild from the database."""
        _INDEX_CACHE["key"] = None
        _INDEX_CACHE["index"] = None
        _INDEX_CACHE["source_id_map"] = []

    def _build_index(self) -> Tuple[Any, List[str]]:
        """
        Rebuild the in-memory FAISS index from stored embeddings.

        Only vectors tagged with the active encoder signature are ingested — mixing vectors
        from different encoders in an inner-product index produces meaningless similarities.
        """
        index = faiss.IndexFlatIP(self.dim)
        source_ids: List[str] = []

        records = (
            self.db.query(SourceEmbeddingModel)
            .join(
                SourceModel,
                SourceModel.source_id == SourceEmbeddingModel.source_id,
            )
            .filter(
                SourceModel.active.is_(True),
                SourceEmbeddingModel.encoder_signature == self.signature,
            )
            .all()
        )

        vectors = []
        for rec in records:
            try:
                v = np.asarray(json.loads(rec.embedding_json), dtype=np.float32)
            except (TypeError, ValueError):
                continue
            if v.shape[0] != self.dim:
                continue
            vectors.append(v)
            source_ids.append(rec.source_id)

        if vectors:
            index.add(np.vstack(vectors))

        total_rows = self.db.query(func.count(SourceEmbeddingModel.source_id)).scalar() or 0
        stale_rows = (
            self.db.query(func.count(SourceEmbeddingModel.source_id))
            .filter(self._stale_condition())
            .scalar()
            or 0
        )
        if stale_rows:
            print(
                f"[AMORA] FAISS index excluded {stale_rows} of {total_rows} embedding(s) not "
                f"produced by encoder '{self.signature}'. Re-register those sources (or call "
                "regenerate_stale_embeddings) to bring them into the index."
            )

        return index, source_ids

    def _reconstruct_embedding_text(self, source_id: str) -> Optional[str]:
        """
        Best-effort reconstruction of the embedded text for a row that predates
        `embedding_text` tracking.

        Mirrors the blob built by MetadataGenerator.generate_source_metadata, minus the
        profiler-derived "Details:" segment (schema/endpoint/document summaries), which is
        not persisted on the source row. The result is a close approximation rather than an
        exact reproduction, so it is only used when no stored text is available.
        """
        src = self.db.query(SourceModel).filter(SourceModel.source_id == source_id).first()
        if not src:
            return None
        return (
            f"{src.name} Domain: {src.domain}. Description: {src.description or ''}. "
            f"Capabilities: {src.capabilities or ''}."
        )

    def regenerate_stale_embeddings(self) -> int:
        """
        Re-embed any stored vector whose encoder signature no longer matches the active one.

        Prefers the exact stored `embedding_text`; falls back to reconstructing the text from
        the source row. Returns the number of rows regenerated.
        """
        stale = (
            self.db.query(SourceEmbeddingModel)
            .filter(self._stale_condition())
            .all()
        )

        regenerated = 0
        approximate = 0
        for rec in stale:
            text = rec.embedding_text
            if not text:
                text = self._reconstruct_embedding_text(rec.source_id)
                if not text:
                    continue
                rec.embedding_text = text
                approximate += 1
            rec.embedding = encode_text_to_vector(text, self.dim)
            rec.encoder_signature = self.signature
            regenerated += 1

        if regenerated:
            self.db.commit()
            self.invalidate_index_cache()
            if approximate:
                print(
                    f"[AMORA] {approximate} embedding(s) were re-encoded from reconstructed "
                    "source text rather than stored text. Re-register those sources for an "
                    "exact re-embedding."
                )
        return regenerated

    def register_source(self, metadata_dict: Dict[str, Any]) -> SourceModel:
        """Register or update source in database and FAISS index."""
        src_data = dict(metadata_dict["source"])
        qual_data = dict(metadata_dict["quality"])
        emb_data = dict(metadata_dict["embedding"])

        # Convert timestamp strings to datetime objects if needed for SQLite compatibility
        from datetime import datetime
        if isinstance(src_data.get("created_at"), str):
            src_data["created_at"] = datetime.fromisoformat(src_data["created_at"])
        if isinstance(src_data.get("updated_at"), str):
            src_data["updated_at"] = datetime.fromisoformat(src_data["updated_at"])

        # Check existing
        existing_src = self.db.query(SourceModel).filter(SourceModel.source_id == src_data["source_id"]).first()
        if existing_src:
            for k, v in src_data.items():
                if k not in ["created_at"]:
                    setattr(existing_src, k, v)

            existing_qual = self.db.query(SourceQualityModel).filter(SourceQualityModel.source_id == src_data["source_id"]).first()
            if existing_qual:
                for k, v in qual_data.items():
                    setattr(existing_qual, k, v)

            existing_emb = self.db.query(SourceEmbeddingModel).filter(SourceEmbeddingModel.source_id == src_data["source_id"]).first()
            if existing_emb:
                existing_emb.embedding = emb_data["embedding"]
                existing_emb.encoder_signature = emb_data.get(
                    "encoder_signature", self.signature
                )
                if emb_data.get("embedding_text"):
                    existing_emb.embedding_text = emb_data["embedding_text"]

            self.db.commit()
            self.invalidate_index_cache()
            return existing_src

        # Create new
        src_obj = SourceModel(**src_data)
        qual_obj = SourceQualityModel(**qual_data)
        emb_obj = SourceEmbeddingModel(source_id=emb_data["source_id"])
        emb_obj.embedding = emb_data["embedding"]
        emb_obj.encoder_signature = emb_data.get("encoder_signature", self.signature)
        emb_obj.embedding_text = emb_data.get("embedding_text")

        self.db.add(src_obj)
        self.db.add(qual_obj)
        self.db.add(emb_obj)
        self.db.commit()
        self.invalidate_index_cache()
        return src_obj

    def get_source_with_quality(self, source_id: str) -> Optional[Tuple[SourceModel, SourceQualityModel]]:
        """Retrieve source and quality profile."""
        src = self.db.query(SourceModel).filter(SourceModel.source_id == source_id).first()
        if not src:
            return None
        qual = self.db.query(SourceQualityModel).filter(SourceQualityModel.source_id == source_id).first()
        return (src, qual)

    def get_all_active_sources(self) -> List[Tuple[SourceModel, SourceQualityModel]]:
        """Get all active sources with quality profiles."""
        results = self.db.query(SourceModel, SourceQualityModel).join(
            SourceQualityModel, SourceModel.source_id == SourceQualityModel.source_id
        ).filter(SourceModel.active == True).all()
        return results

    def search_faiss_candidates(self, query_vector: list[float], top_n: int = 200) -> List[Tuple[str, float]]:
        """
        Fast dense vector pre-filtering using FAISS.
        Tag: [C. AMORA Proposed Functionality - Stage 2 Pre-filtering]
        """
        index, source_id_map = self.faiss_index, self.source_id_map
        if index.ntotal == 0:
            return []

        top_n = min(top_n, index.ntotal)
        qv = np.array([query_vector], dtype=np.float32)
        distances, indices = index.search(qv, top_n)

        candidates = []
        for dist, idx in zip(distances[0], indices[0]):
            if 0 <= idx < len(source_id_map):
                s_id = source_id_map[idx]
                candidates.append((s_id, float(dist)))
        return candidates

    def record_retrieval_event(self, query_id: str, source_id: str, tool: str, success: bool, latency: float, doc_count: int = 1):
        """Log retrieval execution and dynamically update historical success and reliability."""
        log = RetrievalLogModel(
            query_id=query_id,
            source_id=source_id,
            tool=tool,
            retrieval_success=success,
            retrieval_latency=latency,
            retrieved_documents=doc_count
        )
        self.db.add(log)
        
        # Update historical success in quality record
        qual = self.db.query(SourceQualityModel).filter(SourceQualityModel.source_id == source_id).first()
        if qual:
            total_logs = self.db.query(RetrievalLogModel).filter(RetrievalLogModel.source_id == source_id).count()
            successful_logs = self.db.query(RetrievalLogModel).filter(
                RetrievalLogModel.source_id == source_id, RetrievalLogModel.retrieval_success == True
            ).count()
            
            # Bayesian smoothing formula: H_i = (successes + alpha) / (attempts + alpha + beta)
            alpha = settings.bayes_alpha
            beta = settings.bayes_beta
            qual.historical_success = float((successful_logs + alpha) / (total_logs + alpha + beta))

            if not success:
                # Dynamically decay reliability upon failure
                qual.reliability = max(0.1, qual.reliability * 0.9)

        self.db.commit()
