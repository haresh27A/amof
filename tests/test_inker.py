"""
Unit Tests for INKER IE-KRT and IE-KQF
Component Tag: [B. INKER-Inspired Functionality Tests]
"""

import pytest
from inker.ie_krt import IE_KRT
from inker.ie_kqf import IE_KQF
from inker.confidence import QueryAnalyzer

def test_query_analyzer_complexity():
    q_simple = "What is X?"
    q_complex = "Compare the quarterly inventory stock level of product X versus product Y and verify company return policy."
    
    comp_simple = QueryAnalyzer.estimate_complexity(q_simple)
    comp_complex = QueryAnalyzer.estimate_complexity(q_complex)
    
    assert comp_simple < comp_complex
    assert 0.0 <= comp_simple <= 1.0
    assert 0.0 <= comp_complex <= 1.0

def test_ie_krt_retrieval_decision():
    krt = IE_KRT(activation_threshold=0.25)
    
    # Generic greeting should not require retrieval
    res_generic = krt.evaluate("Hello, how are you?")
    assert res_generic.retrieval_required == False
    
    # Factual inventory query should require retrieval
    res_factual = krt.evaluate("What is the current inventory stock of Quantum X Laptop?")
    assert res_factual.retrieval_required == True
    assert res_factual.k_activation_score >= 0.25

def test_ie_kqf_formulation():
    kqf = IE_KQF()
    res = kqf.formulate("What is the current inventory stock quantity of Quantum X Laptop?")
    
    assert "Quantum" in res.key_information or "Laptop" in res.key_information
    assert len(res.retrieval_query) > 0
    assert res.original_query.startswith("What is")
