import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

MOCK_RESPONSE = {
    "explanation": "Fetches all pending orders.",
    "performance_issues": ["Full table scan possible"],
    "erd_description": "Orders table with a Status column.",
    "optimizations": ["Add index on Status column"]
}

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

def test_root():
    res = client.get("/")
    assert res.status_code == 200

def test_invalid_sql_rejected():
    res = client.post("/api/explain", json={"query": "not sql at all"})
    assert res.status_code == 400
    assert "valid SQL" in res.json()["detail"]

def test_multi_statement_rejected():
    res = client.post("/api/explain", json={"query": "SELECT 1; DROP TABLE users;"})
    assert res.status_code == 400

def test_empty_query_rejected():
    res = client.post("/api/explain", json={"query": ""})
    assert res.status_code == 400

def test_query_too_long_rejected():
    res = client.post("/api/explain", json={"query": "SELECT " + "a" * 2001})
    assert res.status_code == 400

@patch("app.routers.explain.explain_query")
def test_valid_query_returns_explanation(mock_gemini):
    import json
    mock_gemini.return_value = json.dumps(MOCK_RESPONSE)
    res = client.post("/api/explain", json={"query": "SELECT * FROM orders WHERE status = 'pending'"})
    assert res.status_code == 200
    body = res.json()
    assert "explanation" in body
    assert "performance_issues" in body
    assert "erd_description" in body
    assert "optimizations" in body

@patch("app.routers.explain.explain_query")
def test_gemini_failure_returns_502(mock_gemini):
    mock_gemini.side_effect = Exception("Gemini API down")
    res = client.post("/api/explain", json={"query": "SELECT * FROM users"})
    assert res.status_code == 502

@patch("app.routers.explain.explain_query")
def test_bad_json_from_gemini_returns_502(mock_gemini):
    mock_gemini.return_value = "this is not json at all"
    res = client.post("/api/explain", json={"query": "SELECT * FROM users"})
    assert res.status_code == 502