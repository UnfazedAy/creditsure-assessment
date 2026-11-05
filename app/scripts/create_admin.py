
from getpass import getpass

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.user import User


def main():
    full_name = input("Admin name: ").strip()
    email = input("Admin email: ").strip().lower()
    password = getpass("Admin password: ")
    confirm_password = getpass("Confirm password: ")

    if password != confirm_password:
        raise ValueError("Passwords do not match")

    if len(full_name) < 2:
        raise ValueError("Admin name must be at least 2 characters")

    if not email or "@" not in email:
        raise ValueError("Provide a valid admin email")

    if not 8 <= len(password) <= 128:
        raise ValueError("Password must be 8-128 characters")

    db = SessionLocal()

    try:
        existing = db.scalar(
            select(User).where(User.email == email)
        )

        if existing:
            raise ValueError("This email is already registered")

        admin = User(
            full_name=full_name,
            email=email,
            hashed_password=hash_password(password),
            role="admin",
            is_active=True
        )

        db.add(admin)
        db.commit()

        print("Admin created successfully!")

    except IntegrityError:
        db.rollback()
        print("Admin email already exists")
    finally:
        db.close()


if __name__ == "__main__":
    main()
