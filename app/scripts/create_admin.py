from getpass import getpass

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db.database import Base, SessionLocal, engine
from app.models.user import User
from app.schemas.user import UserCreate


def create_admin(
    db: Session,
    full_name: str,
    email: str,
    password: str,
) -> bool:
    """Create an admin, or leave an existing account unchanged."""
    data = UserCreate(
        full_name=full_name.strip(),
        email=email.strip().lower(),
        password=password,
    )
    normalized_email = str(data.email)

    existing = db.scalar(
        select(User).where(User.email == normalized_email)
    )
    if existing is not None:
        if existing.role != "admin":
            raise ValueError(
                "The email belongs to a non-admin account; refusing to change its role"
            )
        return False

    admin = User(
        full_name=data.full_name,
        email=normalized_email,
        hashed_password=hash_password(data.password),
        role="admin",
        is_active=True,
    )
    db.add(admin)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return True


def _admin_credentials() -> tuple[str, str, str]:
    configured = (
        settings.ADMIN_FULL_NAME,
        settings.ADMIN_EMAIL,
        settings.ADMIN_PASSWORD,
    )
    if any(value is not None for value in configured):
        full_name, email, password = configured
        if (
            full_name is None
            or not full_name.strip()
            or email is None
            or not email.strip()
            or password is None
            or not password.strip()
        ):
            raise ValueError(
                "Set ADMIN_FULL_NAME, ADMIN_EMAIL, and ADMIN_PASSWORD together"
            )
        return full_name, email, password

    full_name = input("Admin full name: ").strip()
    email = input("Admin email: ").strip()
    password = getpass("Admin password: ")
    if password != getpass("Confirm admin password: "):
        raise ValueError("Passwords do not match")
    return full_name, email, password


def main() -> None:
    try:
        credentials = _admin_credentials()
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            created = create_admin(db, *credentials)
    except ValidationError as exc:
        messages = "; ".join(
            error["msg"] for error in exc.errors(include_input=False)
        )
        print(f"Admin setup failed: {messages}")
        raise SystemExit(1) from exc
    except ValueError as exc:
        print(f"Admin setup failed: {exc}")
        raise SystemExit(1) from exc

    if created:
        print("Administrator created successfully.")
    else:
        print("Administrator already exists; no changes were made.")


if __name__ == "__main__":
    main()
