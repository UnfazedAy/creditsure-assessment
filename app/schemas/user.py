
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, UUID4

class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: UUID4
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserStatusUpdate(BaseModel):
    is_active: bool


class PaginatedUsersResponse(BaseModel):
    items: list[UserResponse]

    total: int = Field(ge=0)
    page: int = Field(ge=1)
    limit: int = Field(ge=1)
    total_pages: int = Field(ge=0)

    has_next: bool
    has_previous: bool
