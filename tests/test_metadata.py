"""
Unit Tests for Metadata Extractor & Repository
Component Tag: [A. Metadata Generation Tests]
"""

import pytest
from metadata.generator import MetadataGenerator
from metadata.sql_profiler import SQLProfiler
from metadata.document_profiler import DocumentProfiler

def test_sql_profiler_fallback():
    prof = SQLProfiler.profile_database("sqlite:///non_existent.db")
    assert "schema_summary" in prof
    assert "capabilities" in prof

def test_document_profiler_fallback():
    prof = DocumentProfiler.profile_file("non_existent_file.pdf")
    assert prof["size_bytes"] == 0

def test_metadata_generator_structure():
    meta = MetadataGenerator.generate_source_metadata(
        source_id="src_test_meta",
        name="Test SQL DB",
        source_type="SQL Database",
        domain="finance",
        description="Database of financial ledgers.",
        endpoint_or_schema="sqlite:///:memory:"
    )
    assert "source" in meta
    assert "quality" in meta
    assert "embedding" in meta
    assert meta["source"]["tool_type"] == "sql_tool"
    assert len(meta["embedding"]["embedding"]) > 0
