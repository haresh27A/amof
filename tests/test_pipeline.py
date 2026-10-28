"""
Integration Tests for End-to-End AMORA API Pipeline
Component Tag: [A. Integration Tests]
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from database.session import init_db, SessionLocal
from datasets.demo_data import populate_demo_sources

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    init_db()
    db = SessionLocal()
    try:
        populate_demo_sources(db)
    finally:
        db.close()

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

def test_list_sources_endpoint():
    response = client.get("/sources")
    assert response.status_code == 200
    sources = response.json()
    assert isinstance(sources, list)
    assert len(sources) > 0

def test_query_endpoint_full_pipeline():
    payload = {
        "query": "What is the current inventory stock quantity of Quantum X Laptop?",
        "mode": "weighted",
        "top_k": 3
    }
    response = client.post("/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["retrieval_required"] == True
    assert "retrieval_query" in data
    assert len(data["selected_sources"]) > 0
    assert "final_answer" in data
    assert data["tokens"] > 0
    assert data["amora_efficiency_score"] > 0.0

def test_amora_rank_only_endpoint():
    payload = {
        "query": "What does the company return policy say about unopened merchandise?",
        "mode": "weighted",
        "top_k": 3
    }
    response = client.post("/amora/rank", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "selected_sources" in data
    assert "weights" in data
