"""
Unit Tests for Tool Connectors and Source-Tool Coordination
Component Tag: [C. Source-Tool Coordination Tests]
"""

import pytest
from tools.sql_tool import SQLTool
from tools.api_tool import APITool
from tools.vector_tool import VectorTool
from tools.document_tool import DocumentTool
from tools.web_tool import WebTool

def test_tool_can_handle():
    sql_tool = SQLTool()
    api_tool = APITool()
    vec_tool = VectorTool()
    doc_tool = DocumentTool()
    web_tool = WebTool()

    assert sql_tool.can_handle("sql_tool") == True
    assert sql_tool.can_handle("api_tool") == False
    assert api_tool.can_handle("api_tool") == True
    assert vec_tool.can_handle("vector_tool") == True
    assert doc_tool.can_handle("doc_tool") == True
    assert web_tool.can_handle("web_tool") == True

def test_tool_retrieval_execution():
    sql_tool = SQLTool()
    res = sql_tool.retrieve("products", {"source_id": "s1", "name": "Sales DB", "endpoint_or_schema": ""}, source_score=0.9)
    
    assert res.success == True
    assert res.source_id == "s1"
    assert len(res.content) > 0
