import pytest
from httpx import Response, Request, AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from src.main import app
from src.api.dependencies import get_http_client


@pytest.fixture
def mock_app_http_client():
    mock_client = AsyncMock(spec=AsyncClient)
    return mock_client


def test_get_summary_success(mock_app_http_client: AsyncMock):
    event_id = 1
    mock_response_content = {"id": event_id, "name": "Test Event", "total_cost": 123.45}

    mock_response = Response(
        status_code=200,
        json=mock_response_content,
        request=Request("GET", "http://irrelevant-for-this-mock.com/some/path")
    )
    mock_app_http_client.get.return_value = mock_response

    with TestClient(app) as client:
        original_client = app.state.http_client
        app.state.http_client = mock_app_http_client
        try:
            response = client.get(f"/api/events/{event_id}/summary")

            assert response.status_code == 200
            assert response.json() == {"summary": mock_response_content}
            mock_app_http_client.get.assert_called_once_with(f"/internal/events/{event_id}")
        finally:
            app.state.http_client = original_client


def test_get_summary_raises_for_status(mock_app_http_client: AsyncMock):
    event_id = 999

    mock_external_response = Response(
        status_code=404,
        content=b'{"detail": "External service: Event not found"}',
        request=Request("GET", f"http://mocked-db-handler.example.com/internal/events/{event_id}")
    )
    mock_app_http_client.get.return_value = mock_external_response

    app.dependency_overrides[get_http_client] = lambda: mock_app_http_client

    with TestClient(app) as client:
        try:
            response = client.get(f"/api/events/{event_id}/summary")
            assert response.status_code == 404
            response_json = response.json()
            assert "detail" in response_json
            mock_app_http_client.get.assert_called_once_with(f"/internal/events/{event_id}")
        finally:
            if get_http_client in app.dependency_overrides:
                del app.dependency_overrides[get_http_client]
