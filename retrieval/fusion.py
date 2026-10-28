"""
Evidence Fusion & Deduplication Engine
Component Tag: [C. AMORA Proposed Functionality - Evidence Fusion]
"""

from typing import List, Dict, Any
from pydantic import BaseModel
from amora.conflict import ConflictDetector

class EvidenceItem(BaseModel):
    source_id: str
    source_name: str
    tool: str
    content: str
    timestamp: str
    retrieval_score: float
    source_score: float
    fused_score: float

class FusionResult(BaseModel):
    evidence_items: List[EvidenceItem]
    conflict_detected: bool
    conflict_score: float
    flagged_conflicts: List[Dict[str, Any]]
    formatted_prompt_context: str

class EvidenceFusionEngine:
    """
    Deduplicates, scores, checks for conflicts, and formats retrieved evidence for LLM prompt.
    Tag: [C. AMORA Proposed Functionality - Evidence Fusion]
    """

    @classmethod
    def fuse_evidence(cls, raw_results: List[Dict[str, Any]]) -> FusionResult:
        """
        Deduplicate items, rank by fused score (retrieval_score * source_score), and detect conflicts.
        """
        seen_contents = set()
        deduped = []

        for item in raw_results:
            content = str(item.get("content", "")).strip()
            if not content:
                continue
            
            # Simple content deduplication hash key
            content_key = content.lower()[:120]
            if content_key in seen_contents:
                continue
            seen_contents.add(content_key)

            ret_score = float(item.get("retrieval_score", 0.8))
            src_score = float(item.get("source_score", 0.8))
            fused_score = float(ret_score * 0.4 + src_score * 0.6)

            evidence_obj = EvidenceItem(
                source_id=item.get("source_id", "unknown"),
                source_name=item.get("source_name", "Unknown Source"),
                tool=item.get("tool_type", item.get("tool", "tool")),
                content=content,
                timestamp=item.get("timestamp", ""),
                retrieval_score=round(ret_score, 4),
                source_score=round(src_score, 4),
                fused_score=round(fused_score, 4)
            )
            deduped.append(evidence_obj)

        # Sort evidence by fused score descending
        deduped.sort(key=lambda e: e.fused_score, reverse=True)

        # Detect conflicts across evidence
        conflict_report = ConflictDetector.analyze_evidence_conflict([e.model_dump() for e in deduped])

        # Format evidence block cleanly to minimize token overhead (take top focused chunks)
        prompt_blocks = []
        top_chunks = deduped[:2] if len(deduped) > 2 else deduped
        for idx, item in enumerate(top_chunks, 1):
            clean_content = item.content.strip()
            lines = [l.strip() for l in clean_content.splitlines() if l.strip() and not l.strip().startswith("==")]
            block = f"[Source: {item.source_name}]\n" + "\n".join(lines[:6])
            prompt_blocks.append(block)

        formatted_context = "\n\n".join(prompt_blocks)

        return FusionResult(
            evidence_items=deduped,
            conflict_detected=len(conflict_report["flagged_conflicts"]) > 0,
            conflict_score=conflict_report["conflict_score"],
            flagged_conflicts=conflict_report["flagged_conflicts"],
            formatted_prompt_context=formatted_context
        )
