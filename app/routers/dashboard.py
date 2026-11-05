
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import require_admin
from app.models.user import User
from app.schemas.common import APIResponse, error_responses
from app.schemas.dashboard import DashboardOverviewResponse
from app.services.dashboard_service import get_dashboard_overview


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

DbSession = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[User, Depends(require_admin)]


@router.get(
    "/overview",
    response_model=APIResponse[DashboardOverviewResponse],
    responses=error_responses(401, 403, 500),
)
def dashboard_overview(
    db: DbSession,
    admin: AdminUser
):
    return APIResponse(
        success=True,
        data=get_dashboard_overview(db),
        detail="Dashboard overview retrieved successfully",
    )
