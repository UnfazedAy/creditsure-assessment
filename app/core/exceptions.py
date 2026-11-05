import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.common import APIErrorResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content=APIErrorResponse(
                success=False,
                detail=exc.detail if isinstance(exc.detail, str) else "Request failed",
            ).model_dump(mode="json", exclude_none=True) | {"data": None},
            headers=exc.headers
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ):
        errors = [
            {
                "field": ".".join(map(str, error["loc"])),
                "message": error["msg"],
            }
            for error in exc.errors()
        ]

        return JSONResponse(
            status_code=422,
            content=APIErrorResponse(
                success=False,
                detail="Request validation failed",
                errors=errors,
            ).model_dump(mode="json", exclude_none=True) | {"data": None},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception
    ):
        logger.error(
            "Unhandled error at %s",
            request.url.path,
            exc_info=(type(exc), exc, exc.__traceback__)
        )

        return JSONResponse(
            status_code=500,
            content=APIErrorResponse(
                success=False,
                detail="Internal server error",
            ).model_dump(mode="json", exclude_none=True) | {"data": None},
        )
