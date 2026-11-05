
def test_health_check(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "dashboard-api"


def test_unknown_endpoint_returns_404(client):
    response = client.get(
        "/api/v1/endpoint-that-does-not-exist"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
