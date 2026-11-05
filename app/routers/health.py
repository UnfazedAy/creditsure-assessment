from fastapi import APIRouter

from app.schemas.common import APIResponse, error_responses
from pydantic import BaseModel

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    service: str


@router.get(
    "/health",
    response_model=APIResponse[HealthResponse],
    responses=error_responses(500),
)
def health_check():
    return APIResponse(
        success=True,
        data=HealthResponse(status="healthy", service="dashboard-api"),
        detail="Service is healthy",
    )