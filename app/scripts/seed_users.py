from getpass import getpass

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db.database import Base, SessionLocal, engine
from app.models.user import User


SEED_USERS: tuple[tuple[str, str, bool], ...] = (
    ("Amelia Bennett", "amelia.bennett@example.com", True),
    ("Ethan Cole", "ethan.cole@example.com", True),
    ("Sofia Martinez", "sofia.martinez@example.com", False),
    ("Noah Williams", "noah.williams@example.com", True),
    ("Maya Patel", "maya.patel@example.com", True),
    ("Lucas Morgan", "lucas.morgan@example.com", False),
    ("Ava Thompson", "ava.thompson@example.com", True),
    ("Oliver Brooks", "oliver.brooks@example.com", False),
    ("Grace Chen", "grace.chen@example.com", True),
    ("Daniel Rivera", "daniel.rivera@example.com", True),
)


def ensure_demo_seeding_allowed(
    environment: str,
    allow_demo_seeding: bool,
) -> None:
    if environment.strip().casefold() in {"prod", "production"} and not allow_demo_seeding:
        raise RuntimeError(
            "Demo seeding is disabled in production. Set ALLOW_DEMO_SEEDING=true "
            "only if demo data is explicitly intended."
        )


def seed_users(db: Session, password: str) -> tuple[int, int]:
    """Insert missing fictional demo accounts without changing existing rows."""
    if not 8 <= len(password) <= 128:
        raise ValueError("Demo password must be 8-128 characters")

    emails = [email for _, email, _ in SEED_USERS]
    existing_emails = set(
        db.scalars(select(User.email).where(User.email.in_(emails))).all()
    )

    created = 0
    for full_name, email, is_active in SEED_USERS:
        if email in existing_emails:
            continue
        db.add(
            User(
                full_name=full_name,
                email=email,
                hashed_password=hash_password(password),
                role="user",
                is_active=is_active,
            )
        )
        created += 1

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return created, len(SEED_USERS) - created


def _demo_password() -> str:
    if settings.DEMO_USER_PASSWORD is not None:
        return settings.DEMO_USER_PASSWORD

    password = getpass("Password for the fictional demo accounts: ")
    if password != getpass("Confirm demo password: "):
        raise ValueError("Passwords do not match")
    return password


def main() -> None:
    try:
        ensure_demo_seeding_allowed(
            settings.ENVIRONMENT,
            settings.ALLOW_DEMO_SEEDING,
        )
        password = _demo_password()
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            created, skipped = seed_users(db, password)
    except (RuntimeError, ValueError) as exc:
        print(f"Demo seeding failed: {exc}")
        raise SystemExit(1) from exc

    print(
        f"Fictional demo users: created {created}, skipped {skipped} "
        "(existing accounts were not modified)."
    )


if __name__ == "__main__":
    main()
