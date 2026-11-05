from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.database import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise auth_error

    try:
        payload = decode_token(credentials.credentials)
    except ValueError:
        raise auth_error

    if payload.get("type") != "access":
        raise auth_error

    subject = payload.get("sub")
    if not isinstance(subject, str):
        raise auth_error

    try:
        user_id = UUID(subject)
    except ValueError:
        raise auth_error

    user = db.scalar(select(User).where(User.id == user_id))

    if user is None:
        raise auth_error

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    return user

def require_admin(
    current_user: Annotated[
        User,
        Depends(get_current_user)
    ]
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user
