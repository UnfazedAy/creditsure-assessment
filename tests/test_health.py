
def test_health_check(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["detail"] == "Service is healthy"
    data = body["data"]
    assert data["status"] == "healthy"
    assert data["service"] == "dashboard-api"


def test_unknown_endpoint_returns_404(client):
    response = client.get(
        "/api/v1/endpoint-that-does-not-exist"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert data["data"] is None
    assert data["detail"] == "Not Found"


def test_docs_and_openapi_include_demo_access_and_bearer_scheme(client):
    docs = client.get("/docs")
    openapi_response = client.get("/openapi.json")

    assert docs.status_code == 200
    assert openapi_response.status_code == 200
    assert openapi_response.json()["info"]["description"].startswith(
        "## Assessment Demo Access"
    )
    assert "admin@credisure.com" in openapi_response.json()["info"]["description"]
    assert "Password123@" in openapi_response.json()["info"]["description"]
    assert (
        openapi_response.json()["components"]["securitySchemes"]["HTTPBearer"]["scheme"]
        == "bearer"
    )

    schema = openapi_response.json()
    login_schema = schema["paths"]["/api/v1/auth/login"]["post"]
    success_schema = login_schema["responses"]["200"]["content"]["application/json"]["schema"]
    assert success_schema["$ref"].endswith("APIResponse_TokenResponse_")
    assert "APIErrorResponse" in schema["components"]["schemas"]
    assert schema["paths"]["/api/v1/dashboard/overview"]["get"]["security"] == [
        {"HTTPBearer": []}
    ]
    assert (
        "WWW-Authenticate"
        in schema["paths"]["/api/v1/dashboard/overview"]["get"]["responses"]["401"]["headers"]
    )
    assert (
        schema["paths"]["/api/v1/auth/register"]["post"]["responses"]["201"]
        ["content"]["application/json"]["schema"]["$ref"]
        .endswith("APIResponse_UserResponse_")
    )
