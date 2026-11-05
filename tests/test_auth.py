
def test_register_user(client):
    payload = {
        "full_name": "John Doe",
        "email": "john@example.com",
        "password": "SecurePass123!",
    }

    response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["full_name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["role"] == "user"
    assert data["is_active"] is True

    # UUID should be returned
    from uuid import UUID
    assert UUID(data["id"])

    # Password and hash must never be exposed
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client, normal_user):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Another Member",
            "email": "member@example.com",
            "password": "SecurePass123!",
        },
    )

    assert response.status_code == 409


def test_register_invalid_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "John Doe",
            "email": "not-an-email",
            "password": "SecurePass123!",
        },
    )

    assert response.status_code == 422


def test_register_short_password(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "John Doe",
            "email": "john@example.com",
            "password": "123",
        },
    )

    assert response.status_code == 422


def test_login_success(client, normal_user):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "member@example.com",
            "password": "SecurePass123!",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, normal_user):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "member@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "missing@example.com",
            "password": "SecurePass123!",
        },
    )

    assert response.status_code == 401


def test_inactive_user_cannot_login(client, user_factory):
    user_factory(
        email="inactive@example.com",
        is_active=False,
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "inactive@example.com",
            "password": "SecurePass123!",
        },
    )

    assert response.status_code == 403


def test_get_current_user(
    client,
    normal_user,
    auth_headers,
):
    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers(normal_user),
    )

    assert response.status_code == 200
    assert response.json()["id"] == str(normal_user.id)
    assert response.json()["email"] == normal_user.email


def test_get_current_user_without_token(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_get_current_user_invalid_token(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": "Bearer invalid-token"
        },
    )

    assert response.status_code == 401


def test_inactive_user_cannot_access_profile(
    client,
    user_factory,
    auth_headers,
):
    user = user_factory(
        email="disabled@example.com",
        is_active=False,
    )

    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers(user),
    )

    assert response.status_code == 403
