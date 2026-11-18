import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.services.gemini_service import explain_query
from app.utils.sql_validator import is_valid_sql

client = TestClient(app)

def test_missing_query_field_returns_422():
    res = client.post("/api/explain", json={})
    assert res.status_code == 422

def test_nonexistent_endpoint_returns_404():
    res = client.get("/api/nonexistent")
    assert res.status_code == 404

def test_sql_validator_complex_queries():
    query_with_join = """
    SELECT u.id, u.name, o.total 
    FROM users u 
    INNER JOIN orders o ON u.id = o.user_id 
    WHERE o.status = 'completed'
    """
    assert is_valid_sql(query_with_join) is True

def test_sql_validator_with_comments():
    query_with_comments = """
    -- Fetch active accounts
    SELECT id, username, email FROM accounts WHERE is_active = 1
    """
    assert is_valid_sql(query_with_comments) is True

def test_sql_validator_boundary_lengths():
    assert is_valid_sql("SELECT " + "x" * 1990) is True
    assert is_valid_sql("SELECT " + "x" * 2005) is False

def test_sql_validator_whitespace_only():
    assert is_valid_sql("     \n\t   ") is False

@patch("app.services.gemini_service.client")
def test_explain_query_strips_markdown_fences(mock_client):
    mock_response = MagicMock()
    mock_response.text = '```json\n{"explanation": "ok", "performance_issues": [], "erd_description": "none", "optimizations": []}\n```'
    mock_client.models.generate_content.return_value = mock_response

    result = explain_query("SELECT * FROM products")
    assert result.startswith("{")
    assert result.endswith("}")
    assert "explanation" in result
