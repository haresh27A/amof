"""
AMORA Multi-Source Tool Execution & Failure Handling Engine
Component Tag: [C. AMORA Proposed Functionality - Source-Tool Coordination & Failure Handling]
"""

from typing import List, Dict, Any, Tuple, Optional
import time
from sqlalchemy.orm import Session

from amora.ranking import RankedSource
from metadata.repository import MetadataRepository
from tools.base import BaseRetrievalTool, RetrievalResult
from tools.sql_tool import SQLTool
from tools.api_tool import APITool
from tools.vector_tool import VectorTool
from tools.document_tool import DocumentTool
from tools.web_tool import WebTool

class MultiSourceRetriever:
    """
    Coordinates tool execution across AMORA-selected sources with failover & retry.
    Tag: [C. AMORA Proposed Functionality - Source-Tool Coordination & Failure Handling]
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = MetadataRepository(db)
        # Register available tool connectors
        self.tools: List[BaseRetrievalTool] = [
            SQLTool(),
            APITool(),
            VectorTool(),
            DocumentTool(),
            WebTool()
        ]

    def _get_tool_for_source(self, tool_type: str) -> BaseRetrievalTool:
        """Find matching tool connector for source tool_type."""
        for tool in self.tools:
            if tool.can_handle(tool_type):
                return tool
        # Default fallback tool
        return DocumentTool()

    def execute_retrieval(
        self,
        query_id: str,
        retrieval_query: str,
        selected_sources: List[RankedSource],
        all_candidate_pool: Optional[List[RankedSource]] = None,
        max_retries: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Execute tool retrieval for selected sources. If a source fails, retry with next candidate.
        """
        retrieved_results = []
        active_sources = list(selected_sources)
        backup_candidates = [s for s in (all_candidate_pool or []) if s.source_id not in [x.source_id for x in selected_sources]]

        for source in active_sources:
            tool_connector = self._get_tool_for_source(source.tool_type)
            
            # Source Metadata payload for tool execution
            src_metadata = {
                "source_id": source.source_id,
                "name": source.name,
                "type": source.source_type,
                "tool_type": source.tool_type,
                "endpoint_or_schema": source.endpoint_or_schema
            }

            start_time = time.time()
            success = False
            ret_res: Optional[RetrievalResult] = None

            # Attempt retrieval
            for attempt in range(max_retries):
                try:
                    ret_res = tool_connector.retrieve(
                        query=retrieval_query,
                        source_metadata=src_metadata,
                        source_score=source.score
                    )
                    if ret_res.success:
                        success = True
                        break
                except Exception as e:
                    success = False

            latency = round((time.time() - start_time) * 1000.0, 2)  # ms

            # Log retrieval event & dynamically update quality profile in DB
            self.repo.record_retrieval_event(
                query_id=query_id,
                source_id=source.source_id,
                tool=source.tool_type,
                success=success,
                latency=latency,
                doc_count=1 if success else 0
            )

            if success and ret_res:
                retrieved_results.append(ret_res.model_dump())
            else:
                # Failure handling: Failover to backup candidate source if available
                if backup_candidates:
                    fallback_source = backup_candidates.pop(0)
                    fallback_tool = self._get_tool_for_source(fallback_source.tool_type)
                    fb_meta = {
                        "source_id": fallback_source.source_id,
                        "name": fallback_source.name,
                        "type": fallback_source.source_type,
                        "tool_type": fallback_source.tool_type,
                        "endpoint_or_schema": fallback_source.endpoint_or_schema
                    }
                    try:
                        fb_res = fallback_tool.retrieve(retrieval_query, fb_meta, fallback_source.score)
                        if fb_res.success:
                            retrieved_results.append(fb_res.model_dump())
                    except Exception:
                        pass

        return retrieved_results
