
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.user import User
from app.utils.pagination import get_pagination_meta


def list_users(
    db: Session,
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    is_active: bool | None = None,
    role: str | None = None,
) -> dict:

    stmt = select(User)

    if search and search.strip():
        term = search.strip()

        escaped = (
            term.replace("\\", "\\\\")
                .replace("%", "\\%")
                .replace("_", "\\_")
        )

        pattern = f"%{escaped}%"

        stmt = stmt.where(
            or_(
                User.full_name.ilike(pattern, escape="\\"),
                User.email.ilike(pattern, escape="\\")
            )
        )

    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)

    if role is not None:
        stmt = stmt.where(User.role == role)

    count_stmt = select(func.count()).select_from(
        stmt.order_by(None).subquery()
    )

    total = db.scalar(count_stmt) or 0

    offset = (page - 1) * limit

    stmt = (
        stmt.order_by(User.created_at.desc(), User.id.desc())
            .offset(offset)
            .limit(limit)
    )

    users = db.scalars(stmt).all()

    return {
        "items": users,
        **get_pagination_meta(total, page, limit)
    }


def get_user_by_id(
    db: Session,
    user_id: UUID
) -> User:

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


def update_user_status(
    db: Session,
    user_id: UUID,
    is_active: bool,
    current_admin: User
) -> User:

    user = get_user_by_id(db, user_id)

    if user.id == current_admin.id and not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account"
        )

    user.is_active = is_active

    db.commit()
    db.refresh(user)

    return user
