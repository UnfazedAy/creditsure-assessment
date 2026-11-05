import pytest
from sqlalchemy import func, select

from app.core.security import verify_password
from app.models.user import User
from app.scripts.create_admin import create_admin
from app.scripts.seed_users import (
    SEED_USERS,
    ensure_demo_seeding_allowed,
    seed_users,
)


def test_seed_users_creates_ten_argon2_regular_accounts(db_session):
    created, skipped = seed_users(db_session, "AssessmentDemo123!")

    users = db_session.scalars(
        select(User).where(
            User.email.in_([email for _, email, _ in SEED_USERS])
        )
    ).all()

    assert (created, skipped) == (10, 0)
    assert len(users) == 10
    assert {user.role for user in users} == {"user"}
    assert {user.is_active for user in users} == {True, False}
    assert all(user.email.endswith("@example.com") for user in users)
    assert all(user.hashed_password.startswith("$argon2id$") for user in users)
    assert all(
        verify_password("AssessmentDemo123!", user.hashed_password)
        for user in users
    )


def test_seed_users_is_idempotent_and_preserves_existing_accounts(
    db_session,
    user_factory,
):
    existing = user_factory(
        email="amelia.bennett@example.com",
        full_name="Existing Admin",
        role="admin",
        is_active=False,
    )
    unrelated = user_factory(
        email="unrelated@example.net",
        full_name="Unrelated User",
        role="admin",
        is_active=False,
    )
    existing_hash = existing.hashed_password
    unrelated_hash = unrelated.hashed_password

    assert seed_users(db_session, "AssessmentDemo123!") == (9, 1)
    assert seed_users(db_session, "DifferentDemo123!") == (0, 10)
    assert db_session.scalar(select(func.count()).select_from(User)) == 11

    db_session.refresh(existing)
    db_session.refresh(unrelated)
    assert existing.role == "admin"
    assert existing.is_active is False
    assert existing.hashed_password == existing_hash
    assert unrelated.role == "admin"
    assert unrelated.is_active is False
    assert unrelated.hashed_password == unrelated_hash


def test_admin_provisioning_is_idempotent_and_authenticates(
    client,
    db_session,
):
    assert create_admin(
        db_session,
        "Assessment Admin",
        "admin@example.com",
        "AssessmentAdmin123!",
    ) is True
    assert create_admin(
        db_session,
        "Changed Name",
        "admin@example.com",
        "DifferentPassword123!",
    ) is False

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "AssessmentAdmin123!",
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token"]
    overview = client.get(
        "/api/v1/dashboard/overview",
        headers={
            "Authorization": f"Bearer {response.json()['access_token']}",
        },
    )
    assert overview.status_code == 200

    admin = db_session.scalar(
        select(User).where(User.email == "admin@example.com")
    )
    assert admin is not None
    assert admin.role == "admin"
    assert admin.is_active is True
    assert verify_password("AssessmentAdmin123!", admin.hashed_password)


def test_admin_provisioning_does_not_promote_existing_user(
    db_session,
    user_factory,
):
    user = user_factory(email="member@example.com")

    with pytest.raises(ValueError, match="non-admin"):
        create_admin(
            db_session,
            "Member",
            "member@example.com",
            "AssessmentAdmin123!",
        )

    db_session.refresh(user)
    assert user.role == "user"


def test_demo_seeding_requires_explicit_production_enablement():
    with pytest.raises(RuntimeError, match="ALLOW_DEMO_SEEDING"):
        ensure_demo_seeding_allowed("production", False)

    ensure_demo_seeding_allowed("production", True)
