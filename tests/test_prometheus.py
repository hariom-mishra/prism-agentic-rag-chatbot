import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio

async def test_metrics_endpoint(client: AsyncClient):
    # Hit the test/root endpoint to generate some request metrics
    response = await client.get("/")
    assert response.status_code == 200
    
    # Verify the metrics endpoint returns 200 and has the Prometheus text format content
    metrics_response = await client.get("/metrics")
    assert metrics_response.status_code == 200
    assert "text/plain" in metrics_response.headers.get("content-type", "")
    assert "# HELP" in metrics_response.text
    assert "http_requests" in metrics_response.text or "http_request" in metrics_response.text
