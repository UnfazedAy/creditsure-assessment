
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_token_pair,
)
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate


def register_user(db: Session, user_data: UserCreate) -> User:
    email = str(user_data.email).strip().lower()
    full_name = user_data.full_name.strip()

    if len(full_name) < 2:
        raise HTTPException(
            status_code=422,
            detail="Full name must contain at least 2 characters"
        )

    if email == "":
        raise HTTPException(
            status_code=422,
            detail="Email must not be empty"
        )

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )

    new_user = User(
        full_name=full_name,
        email=email,
        hashed_password=hash_password(user_data.password),
        role="user",
        is_active=True,
    )

    db.add(new_user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )

    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, credentials: LoginRequest) -> str:
    email = str(credentials.email).strip().lower()
    if not email or not credentials.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password must be provided"
        )

    user = db.scalar(
        select(User).where(User.email == email)
    )

    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user:
        raise invalid_credentials

    if not verify_password(
        credentials.password,
        user.hashed_password
    ):
        raise invalid_credentials

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    return create_token_pair(
        subject=str(user.id),
        extra_claims={"role": user.role}
    )
