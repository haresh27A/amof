"""
AMORA Evidence Conflict Detector
Component Tag: [C. AMORA Proposed Functionality - Conflict Detection]
"""

import re
from typing import List, Dict, Any

class ConflictDetector:
    """
    Detects basic factual conflicts (numeric, date, or status disagreements) across candidate evidence snippets.
    Tag: [C. AMORA Proposed Functionality - Conflict Detection]
    """

    @classmethod
    def analyze_evidence_conflict(cls, evidence_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Scan evidence snippets for numeric or date contradictions.
        Returns overall conflict score in [0, 1] and detailed flagged conflicts.
        """
        if len(evidence_items) <= 1:
            return {"conflict_score": 0.0, "flagged_conflicts": []}

        conflicts = []
        numbers_by_source = {}
        dates_by_source = {}

        for item in evidence_items:
            s_name = item.get("source_name", item.get("source_id", "Unknown"))
            text = str(item.get("content", ""))

            # Extract numbers
            numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
            numbers_by_source[s_name] = set(numbers)

            # Extract year dates
            dates = re.findall(r'\b(?:19|20)\d{2}\b', text)
            dates_by_source[s_name] = set(dates)

        # Check pairwise numeric conflicts
        sources = list(evidence_items)
        for i in range(len(sources)):
            for j in range(i + 1, len(sources)):
                s1 = sources[i].get("source_name", "Source 1")
                s2 = sources[j].get("source_name", "Source 2")

                num1 = numbers_by_source.get(s1, set())
                num2 = numbers_by_source.get(s2, set())

                # If both have numbers but disjoint set of numbers for same topic
                if num1 and num2 and num1.isdisjoint(num2):
                    conflicts.append({
                        "type": "numeric_disagreement",
                        "sources": [s1, s2],
                        "details": f"Disagreement in numeric values between {s1} ({list(num1)[:3]}) and {s2} ({list(num2)[:3]})."
                    })

                date1 = dates_by_source.get(s1, set())
                date2 = dates_by_source.get(s2, set())
                if date1 and date2 and date1.isdisjoint(date2):
                    conflicts.append({
                        "type": "date_disagreement",
                        "sources": [s1, s2],
                        "details": f"Disagreement in temporal reference dates between {s1} ({list(date1)}) and {s2} ({list(date2)})."
                    })

        conflict_score = min(1.0, len(conflicts) * 0.3)
        return {
            "conflict_score": round(conflict_score, 4),
            "flagged_conflicts": conflicts
        }
