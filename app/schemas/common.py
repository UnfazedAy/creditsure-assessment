from typing import Generic, Literal, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: Literal[True]
    data: T
    detail: str


class ValidationFieldError(BaseModel):
    field: str
    message: str


class APIErrorResponse(BaseModel):
    success: Literal[False]
    data: None = None
    detail: str
    errors: list[ValidationFieldError] | None = None


_ERROR_DESCRIPTIONS = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    409: "Conflict",
    422: "Validation Error",
    500: "Internal Server Error",
}


def error_responses(*status_codes: int) -> dict[int, dict[str, object]]:
    responses = {
        status_code: {
            "model": APIErrorResponse,
            "description": _ERROR_DESCRIPTIONS[status_code],
        }
        for status_code in status_codes
    }
    if 401 in responses:
        responses[401]["headers"] = {
            "WWW-Authenticate": {
                "description": "Bearer authentication challenge",
                "schema": {"type": "string"},
            }
        }
    return responses
