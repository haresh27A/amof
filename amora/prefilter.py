"""
AMORA Scalable Pre-filtering Pipeline
Component Tag: [C. AMORA Proposed Functionality - Scalable Pre-filtering]

Stage 1: Programmatic Hard Filters (Active status, tool/domain compatibility)
Stage 2: FAISS Dense Vector Cosine Similarity Search (10,000+ -> 200 candidates)
"""

from typing import List, Tuple, Dict, Any, Optional
from database.models import SourceModel, SourceQualityModel
from metadata.repository import MetadataRepository
from metadata.generator import encode_text_to_vector

class PrefilterEngine:
    """
    Scalable two-stage pre-filter reducing 10,000+ candidate sources down to top N candidate sources.
    Tag: [C. AMORA Proposed Functionality - Scalable Pre-filtering]
    """

    def __init__(self, repo: MetadataRepository):
        self.repo = repo

    def prefilter(
        self,
        retrieval_query: str,
        top_n: int = 200,
        required_tool: Optional[str] = None,
        target_domain: Optional[str] = None
    ) -> List[Tuple[SourceModel, SourceQualityModel, float]]:
        """
        Execute Stage 1 & Stage 2 pre-filtering.
        Returns list of (SourceModel, SourceQualityModel, cosine_similarity_R_i).
        """
        # 1. Generate retrieval query embedding vector
        query_vector = encode_text_to_vector(retrieval_query)

        # 2. Stage 2: Fast FAISS dense vector search
        faiss_candidates = self.repo.search_faiss_candidates(query_vector, top_n=top_n * 2)

        results = []
        for s_id, cos_sim in faiss_candidates:
            res = self.repo.get_source_with_quality(s_id)
            if not res:
                continue
            src, qual = res

            # 3. Stage 1: Hard Filtering Rules
            if not src.active:
                continue
            if required_tool and src.tool_type != required_tool:
                continue
            if target_domain and target_domain.lower() != "general" and src.domain.lower() != target_domain.lower():
                # Allow cross-domain fallback if high similarity
                if cos_sim < 0.4:
                    continue

            # Normalized Relevance R_i in [0, 1]
            R_i = max(0.0, min(1.0, float((cos_sim + 1.0) / 2.0) if cos_sim <= 1.0 else cos_sim))
            results.append((src, qual, R_i))

            if len(results) >= top_n:
                break

        return results
