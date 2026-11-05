
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.common import APIResponse, error_responses
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import (
    register_user,
    authenticate_user,
)
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    responses=error_responses(409, 422, 500),
)
def register(
    user_data: UserCreate,
    db: Annotated[Session, Depends(get_db)]
):
    return APIResponse(
        success=True,
        data=register_user(db, user_data),
        detail="User registered successfully",
    )


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    responses=error_responses(400, 401, 403, 422, 500),
)
def login(
    credentials: LoginRequest,
    db: Annotated[Session, Depends(get_db)]
):
    token_pair = authenticate_user(db, credentials)

    return APIResponse(
        success=True,
        data=TokenResponse(
            access_token=token_pair["access_token"],
            refresh_token=token_pair["refresh_token"],
            token_type="bearer",
        ),
        detail="Login successful",
    )


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    responses=error_responses(401, 403, 500),
)
def get_my_profile(
    current_user: Annotated[
        User,
        Depends(get_current_user)
    ]
):
    return APIResponse(
        success=True,
        data=current_user,
        detail="User retrieved successfully",
    )