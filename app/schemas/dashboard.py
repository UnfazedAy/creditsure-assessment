
from pydantic import BaseModel, Field


class DashboardOverviewResponse(BaseModel):
    total_users: int = Field(ge=0)
    active_users: int = Field(ge=0)
    inactive_users: int = Field(ge=0)
    new_users_this_month: int = Field(ge=0)

