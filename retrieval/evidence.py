"""
AMORA Evidence Data Representation
Component Tag: [C. AMORA Proposed Functionality - Evidence Structure]
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel

class EvidenceRecord(BaseModel):
    """
    Standardized evidence representation across heterogeneous tools.
    Tag: [C. AMORA Proposed Functionality - Evidence Structure]
    """
    source_id: str
    source_name: str
    tool_type: str
    content: str
    timestamp: str
    retrieval_score: float
    source_score: float
    metadata: Optional[Dict[str, Any]] = None
