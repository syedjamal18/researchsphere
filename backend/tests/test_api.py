from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def sample_paper():
    """Return sample paper data for testing."""
    return {
        "arxiv_id": "2601.12345",
        "title": "Testing Scientific Paper Search",
        "authors": ["Author One", "Author Two"],
        "abstract": "This is a sample abstract for automated testing.",
        "published": "2026-01-01T00:00:00Z",
        "updated": "2026-01-02T00:00:00Z",
        "abstract_url": "https://arxiv.org/abs/2601.12345",
        "pdf_url": "https://arxiv.org/pdf/2601.12345",
    }


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch("backend.app.main.search_arxiv")
def test_search_success(mock_search_arxiv):
    mock_search_arxiv.return_value = [sample_paper()]

    response = client.get(
        "/api/search",
        params={"q": "machine learning", "limit": 5},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "machine learning"
    assert data["count"] == 1
    assert len(data["results"]) == 1
    assert data["results"][0]["title"] == "Testing Scientific Paper Search"

    mock_search_arxiv.assert_called_once_with(
        "machine learning",
        max_results=5,
    )


def test_search_rejects_missing_query():
    response = client.get("/api/search")

    assert response.status_code == 422


def test_search_rejects_invalid_limit():
    response = client.get(
        "/api/search",
        params={"q": "machine learning", "limit": 10},
    )

    assert response.status_code == 422


def test_search_rejects_whitespace_query():
    response = client.get(
        "/api/search",
        params={"q": "   ", "limit": 5},
    )

    assert response.status_code == 400
    assert "empty" in response.json()["detail"]


@patch("backend.app.main.search_arxiv")
def test_search_handles_arxiv_failure(mock_search_arxiv):
    mock_search_arxiv.side_effect = Exception("Simulated connection failure")

    response = client.get(
        "/api/search",
        params={"q": "machine learning", "limit": 5},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "Unable to retrieve papers from arXiv. Please try again."
    )