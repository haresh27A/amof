"""
Base Retrieval Tool Specification
Component Tag: [C. AMORA Proposed Functionality - Source-Tool Coordination]
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class RetrievalResult(BaseModel):
    source_id: str
    source_name: str
    tool_type: str
    content: str
    timestamp: str
    retrieval_score: float
    source_score: float
    raw_data: Optional[Dict[str, Any]] = None
    success: bool = True
    error_message: Optional[str] = None


class BaseRetrievalTool(ABC):
    """
    Standardized tool interface for source-tool coordination in AMORA.
    Tag: [C. AMORA Proposed Functionality - Source-Tool Coordination]
    """

    @abstractmethod
    def can_handle(self, tool_type: str) -> bool:
        """Returns true if this tool can handle the source's tool_type."""
        pass

    @abstractmethod
    def retrieve(self, query: str, source_metadata: Dict[str, Any], source_score: float = 1.0) -> RetrievalResult:
        """Executes retrieval against the selected source."""
        pass

    @abstractmethod
    def health_check(self, source_metadata: Dict[str, Any]) -> bool:
        """Verifies connector availability."""
        pass
