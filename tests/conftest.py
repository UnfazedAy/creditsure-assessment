
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import (
    create_access_token,
    hash_password,
)
from app.db.database import Base, get_db
from app.main import app
from app.models.user import User


@pytest.fixture
def db_session():
    # Separate in-memory SQLite database for each test
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    TestingSession = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    with TestingSession() as session:
        yield session

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    test_client = TestClient(
        app,
        raise_server_exceptions=False,
    )

    try:
        yield test_client
    finally:
        test_client.close()
        app.dependency_overrides.clear()

@pytest.fixture
def user_factory(db_session):
    def create_user(
        email="user@example.com",
        password="SecurePass123!",
        full_name="Test User",
        role="user",
        is_active=True,
        created_at=None,
    ):
        user = User(
            full_name=full_name,
            email=email,
            hashed_password=hash_password(password),
            role=role,
            is_active=is_active,
            created_at=created_at or datetime.now(timezone.utc),
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        return user

    return create_user


@pytest.fixture
def admin_user(user_factory):
    return user_factory(
        email="admin@example.com",
        full_name="Test Admin",
        role="admin",
    )


@pytest.fixture
def normal_user(user_factory):
    return user_factory(
        email="member@example.com",
        full_name="Test Member",
        role="user",
    )


@pytest.fixture
def auth_headers():
    def make_headers(user):
        token = create_access_token(subject=str(user.id))

        return {
            "Authorization": f"Bearer {token}"
        }

    return make_headers
