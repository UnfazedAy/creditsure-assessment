
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import require_admin
from app.models.user import User
from app.schemas.common import APIResponse, error_responses
from app.schemas.user import (
    PaginatedUsersResponse,
    UserResponse,
    UserStatusUpdate,
)
from app.services.user_service import (
    get_user_by_id,
    list_users,
    update_user_status,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

DbSession = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[User, Depends(require_admin)]


@router.get(
    "",
    response_model=APIResponse[PaginatedUsersResponse],
    responses=error_responses(401, 403, 422, 500),
)
def get_users(
    db: DbSession,
    admin: AdminUser,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    search: Annotated[
        str | None,
        Query(max_length=100)
    ] = None,
    is_active: bool | None = None,
    role: Literal["user", "admin"] | None = None
):
    return APIResponse(
        success=True,
        data=list_users(
            db=db,
            page=page,
            limit=limit,
            search=search,
            is_active=is_active,
            role=role,
        ),
        detail="Users retrieved successfully",
    )


@router.get(
    "/{user_id}",
    response_model=APIResponse[UserResponse],
    responses=error_responses(401, 403, 404, 422, 500),
)
def get_user(
    user_id: UUID,
    db: DbSession,
    admin: AdminUser
):
    return APIResponse(
        success=True,
        data=get_user_by_id(db, user_id),
        detail="User retrieved successfully",
    )


@router.patch(
    "/{user_id}",
    response_model=APIResponse[UserResponse],
    responses=error_responses(400, 401, 403, 404, 422, 500),
)
def update_user(
    user_id: UUID,
    user_data: UserStatusUpdate,
    db: DbSession,
    admin: AdminUser
):
    return APIResponse(
        success=True,
        data=update_user_status(
            db=db,
            user_id=user_id,
            is_active=user_data.is_active,
            current_admin=admin,
        ),
        detail="User updated successfully",
    )
