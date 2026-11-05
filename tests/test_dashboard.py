
from datetime import datetime, timedelta, timezone


def test_dashboard_statistics(
    client,
    admin_user,
    user_factory,
    auth_headers,
):
    now = datetime.now(timezone.utc)

    month_start = datetime(
        now.year,
        now.month,
        1,
        tzinfo=timezone.utc,
    )

    previous_month = month_start - timedelta(days=1)

    user_factory(
        email="active@example.com",
        is_active=True,
        created_at=now,
    )

    user_factory(
        email="inactive@example.com",
        is_active=False,
        created_at=now,
    )

    user_factory(
        email="older@example.com",
        is_active=True,
        created_at=previous_month,
    )

    response = client.get(
        "/api/v1/dashboard/overview",
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_users"] == 4
    assert data["active_users"] == 3
    assert data["inactive_users"] == 1
    assert data["new_users_this_month"] == 3


def test_dashboard_empty_database(
    client,
    db_session,
    admin_user,
    auth_headers,
):
    # The admin account is the only existing user.
    response = client.get(
        "/api/v1/dashboard/overview",
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_users"] == 1
    assert data["active_users"] == 1
    assert data["inactive_users"] == 0


def test_dashboard_requires_authentication(client):
    response = client.get(
        "/api/v1/dashboard/overview"
    )

    assert response.status_code == 401


def test_normal_user_cannot_access_dashboard(
    client,
    normal_user,
    auth_headers,
):
    response = client.get(
        "/api/v1/dashboard/overview",
        headers=auth_headers(normal_user),
    )

    assert response.status_code == 403
