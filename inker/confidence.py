"""
INKER Query Confidence & Ambiguity Estimator
Component Tag: [B. INKER-Inspired Functionality]
"""

import re
from typing import Dict, Any

class QueryAnalyzer:
    """
    Analyzes user queries for complexity, entity density, temporal cues, and factual lookup flags.
    Distinguishes between private enterprise data needs (RAG required) and common parametric knowledge (No RAG).
    Tag: [B. INKER-Inspired Functionality]
    """

    TEMPORAL_KEYWORDS = {
        "latest", "recent", "current", "today", "yesterday", "now", "2025", "2026", 
        "updated", "realtime", "real-time", "newest", "live status", "restock date"
    }
    
    # Specific enterprise/private data terms that require external database access
    ENTERPRISE_FACTUAL_KEYWORDS = {
        "inventory", "stock", "return policy", "price", "unit price", "specification",
        "manual", "sales", "revenue", "order", "sku", "warehouse", "refund", "warranty",
        "quantum x", "aura pro", "employee", "salary", "table", "database record",
        "q1", "q2", "q3", "q4", "compliance manual", "supplier"
    }

    # General world knowledge patterns that standard LLMs already know
    GENERAL_KNOWLEDGE_PATTERNS = [
        r"\bcapital of\b",
        r"\bwho (is|was|wrote|invented|discovered)\b",
        r"\bwhat is (the capital|a|an|photosynthesis|python|gravity|ai|machine learning)\b",
        r"\bmeaning of\b",
        r"\bcurrency of\b",
        r"\bhow (to|does|do)\b",
        r"\btranslate\b",
        r"\bdefine\b"
    ]

    @classmethod
    def estimate_complexity(cls, query: str) -> float:
        """
        Estimate query complexity E in [0, 1] based on word length, logical operators, and clause structures.
        """
        words = query.strip().split()
        if not words:
            return 0.0

        length_score = min(len(words) / 25.0, 1.0)
        has_multi_clause = 0.3 if any(w in query.lower() for w in ["and", "or", "versus", "vs", "compare", "if", "while"]) else 0.0
        has_punctuation = 0.2 if any(char in query for char in ["?", ",", ";", ":"]) else 0.0

        return min(length_score * 0.5 + has_multi_clause + has_punctuation, 1.0)

    @classmethod
    def extract_entities(cls, query: str) -> list[str]:
        """Simple rule/regex entity extraction (capitalized words, quoted strings, product IDs)."""
        quoted = re.findall(r'"([^"]*)"', query)
        capitalized = re.findall(r'\b[A-Z][a-z0-9_]+\b', query)
        codes = re.findall(r'\b[A-Za-z0-9]+-[0-9]+\b', query)
        
        entities = list(set(quoted + capitalized + codes))
        return entities

    @classmethod
    def detect_temporal_need(cls, query: str) -> float:
        """Returns temporal sensitivity score in [0, 1]."""
        q_lower = query.lower()
        score = 0.0
        for kw in cls.TEMPORAL_KEYWORDS:
            if kw in q_lower:
                score += 0.4
        return min(score, 1.0)

    @classmethod
    def detect_factual_need(cls, query: str) -> float:
        """
        Returns external private enterprise factual lookup urgency in [0, 1].
        Returns 0.0 for common general world knowledge.
        """
        q_lower = query.lower().strip()

        # Check if query is standard general knowledge
        for pat in cls.GENERAL_KNOWLEDGE_PATTERNS:
            if re.search(pat, q_lower):
                # Unless it explicitly asks for enterprise terms
                if not any(term in q_lower for term in ["stock", "inventory", "quantum", "warehouse", "order", "revenue", "return policy"]):
                    return 0.0

        score = 0.0
        for kw in cls.ENTERPRISE_FACTUAL_KEYWORDS:
            if kw in q_lower:
                score += 0.45

        return min(score, 1.0)
