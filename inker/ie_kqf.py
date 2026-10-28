"""
INKER IE-KQF: Knowledge Query Formulator
Component Tag: [B. INKER-Inspired Functionality]

Formula:
  q+ = concat(P, I)
  where:
    P = useful phrases extracted from model knowledge/reasoning
    I = important information from the original query
"""

from typing import List
from pydantic import BaseModel
from inker.confidence import QueryAnalyzer

class IEKQFResult(BaseModel):
    original_query: str
    key_information: List[str]
    reasoning_phrases: List[str]
    retrieval_query: str

class IE_KQF:
    """
    Decides WHAT information should be retrieved and formulates retrieval query q+.
    Tag: [B. INKER-Inspired Functionality]
    """

    def formulate(self, query: str) -> IEKQFResult:
        """
        Formulate expanded retrieval query q+ = concat(P, I)
        """
        # Extract I: key information (entities, key nouns, numbers)
        entities = QueryAnalyzer.extract_entities(query)
        
        # Clean query words excluding stop words
        stopwords = {"what", "is", "the", "a", "an", "of", "for", "to", "in", "on", "with", "how", "which"}
        query_words = [w for w in query.split() if w.lower() not in stopwords]
        
        key_information = list(dict.fromkeys(entities + query_words))
        
        # Extract P: reasoning context & domain intent phrases
        reasoning_phrases = []
        q_lower = query.lower()
        
        if "inventory" in q_lower or "stock" in q_lower or "quantity" in q_lower:
            reasoning_phrases.append("real-time inventory stock levels")
        if "return policy" in q_lower or "refund" in q_lower or "warranty" in q_lower:
            reasoning_phrases.append("official company policies document")
        if "sales" in q_lower or "revenue" in q_lower or "order" in q_lower:
            reasoning_phrases.append("order records database query")
        if "specification" in q_lower or "manual" in q_lower or "details" in q_lower:
            reasoning_phrases.append("technical product documentation")

        if not reasoning_phrases:
            reasoning_phrases.append("fact verification and detailed specs")

        # Formulate q+ = concat(P, I)
        p_str = " ".join(reasoning_phrases)
        i_str = " ".join(key_information[:8])
        retrieval_query = f"{i_str} {p_str}".strip()

        return IEKQFResult(
            original_query=query,
            key_information=key_information,
            reasoning_phrases=reasoning_phrases,
            retrieval_query=retrieval_query
        )
