
from uuid import uuid4


def test_admin_can_list_users(
    client,
    admin_user,
    normal_user,
    auth_headers,
):
    response = client.get(
        "/api/v1/users",
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["detail"] == "Users retrieved successfully"
    data = body["data"]

    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_normal_user_cannot_list_users(
    client,
    normal_user,
    auth_headers,
):
    response = client.get(
        "/api/v1/users",
        headers=auth_headers(normal_user),
    )

    assert response.status_code == 403
    assert response.json()["success"] is False
    assert response.json()["data"] is None
    assert response.json()["detail"] == "Admin access required"


def test_unauthenticated_user_cannot_list_users(client):
    response = client.get("/api/v1/users")

    assert response.status_code == 401
    assert response.json()["success"] is False
    assert response.json()["data"] is None
    assert response.headers["www-authenticate"] == "Bearer"


def test_search_users(
    client,
    admin_user,
    user_factory,
    auth_headers,
):
    user_factory(
        email="john@example.com",
        full_name="John Doe",
    )

    user_factory(
        email="jane@example.com",
        full_name="Jane Smith",
    )

    response = client.get(
        "/api/v1/users",
        params={"search": "john"},
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["detail"] == "Users retrieved successfully"
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["email"] == "john@example.com"


def test_search_is_case_insensitive(
    client,
    admin_user,
    user_factory,
    auth_headers,
):
    user_factory(
        email="john@example.com",
        full_name="John Doe",
    )

    response = client.get(
        "/api/v1/users",
        params={"search": "JOHN"},
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["total"] == 1


def test_filter_active_users(
    client,
    admin_user,
    user_factory,
    auth_headers,
):
    user_factory(
        email="active@example.com",
        is_active=True,
    )

    user_factory(
        email="inactive@example.com",
        is_active=False,
    )

    response = client.get(
        "/api/v1/users",
        params={"is_active": "true"},
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    data = body["data"]

    # Admin + active user
    assert data["total"] == 2

    assert all(
        user["is_active"] is True
        for user in data["items"]
    )


def test_filter_inactive_users(
    client,
    admin_user,
    user_factory,
    auth_headers,
):
    user_factory(
        email="inactive@example.com",
        is_active=False,
    )

    response = client.get(
        "/api/v1/users",
        params={"is_active": "false"},
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["total"] == 1
    assert response.json()["data"]["items"][0]["is_active"] is False


def test_filter_by_role(
    client,
    admin_user,
    normal_user,
    auth_headers,
):
    response = client.get(
        "/api/v1/users",
        params={"role": "admin"},
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["total"] == 1
    assert response.json()["data"]["items"][0]["role"] == "admin"


def test_pagination(
    client,
    admin_user,
    user_factory,
    auth_headers,
):
    for index in range(12):
        user_factory(
            email=f"user{index}@example.com"
        )

    response = client.get(
        "/api/v1/users",
        params={"page": 2, "limit": 5},
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    data = body["data"]

    # 12 regular users + admin
    assert data["total"] == 13
    assert data["page"] == 2
    assert data["limit"] == 5
    assert data["total_pages"] == 3
    assert len(data["items"]) == 5
    assert data["has_next"] is True
    assert data["has_previous"] is True


def test_invalid_pagination(
    client,
    admin_user,
    auth_headers,
):
    response = client.get(
        "/api/v1/users",
        params={"page": 0, "limit": 10},
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 422
    assert response.json()["success"] is False
    assert response.json()["data"] is None
    assert response.json()["errors"]


def test_get_user_by_uuid(
    client,
    admin_user,
    normal_user,
    auth_headers,
):
    response = client.get(
        f"/api/v1/users/{normal_user.id}",
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["detail"] == "User retrieved successfully"
    assert response.json()["data"]["id"] == str(normal_user.id)


def test_get_user_invalid_uuid(
    client,
    admin_user,
    auth_headers,
):
    response = client.get(
        "/api/v1/users/not-a-valid-uuid",
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 422
    assert response.json()["success"] is False
    assert response.json()["data"] is None


def test_get_nonexistent_user(
    client,
    admin_user,
    auth_headers,
):
    response = client.get(
        f"/api/v1/users/{uuid4()}",
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 404
    assert response.json()["success"] is False
    assert response.json()["data"] is None
    assert response.json()["detail"] == "User not found"


def test_admin_can_deactivate_user(
    client,
    admin_user,
    normal_user,
    auth_headers,
):
    response = client.patch(
        f"/api/v1/users/{normal_user.id}",
        json={"is_active": False},
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["detail"] == "User updated successfully"
    assert response.json()["data"]["is_active"] is False


def test_admin_cannot_deactivate_self(
    client,
    admin_user,
    auth_headers,
):
    response = client.patch(
        f"/api/v1/users/{admin_user.id}",
        json={"is_active": False},
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["data"] is None
    assert response.json()["detail"] == "You cannot deactivate your own account"


def test_normal_user_cannot_update_user(
    client,
    normal_user,
    admin_user,
    auth_headers,
):
    response = client.patch(
        f"/api/v1/users/{admin_user.id}",
        json={"is_active": False},
        headers=auth_headers(normal_user),
    )

    assert response.status_code == 403
    assert response.json()["success"] is False
    assert response.json()["data"] is None
