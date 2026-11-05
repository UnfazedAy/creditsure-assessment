
import logging
from time import perf_counter

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        start_time = perf_counter()

        response = await call_next(request)

        duration = (perf_counter() - start_time) * 1000

        logger.info(
            "%s %s - %s - %.2fms",
            request.method,
            request.url.path,
            response.status_code,
            duration
        )

        response.headers["X-Process-Time"] = (
            f"{duration / 1000:.4f}"
        )

        return response
