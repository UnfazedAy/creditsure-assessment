import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.db.database import Base, engine
from app.middleware.request_logging import RequestLoggingMiddleware
from app.routers import auth, dashboard, health, users


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


API_DESCRIPTION = """
## Assessment Demo Access

This API is deployed for the CrediSure backend assessment and uses fictional
demonstration records.

- **Login endpoint:** `POST /api/v1/auth/login`
- **Demo email:** `admin@credisure.com`
- **Demo password:** `Password123@`

In Swagger, call the login endpoint with these credentials. Copy
`data.access_token` from the response, click **Authorize**, and paste the token
into the HTTP Bearer field. Swagger adds the `Bearer` prefix when sending
protected requests.

> These credentials are for this assessment only.

## API

The backend provides authentication, administrative user management, and
dashboard statistics. Successful and error responses use a consistent
`success`, `data`, and `detail` envelope.
"""


# Initialize database tables on application startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=API_DESCRIPTION.strip(),
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

register_exception_handlers(app)

app.add_middleware(RequestLoggingMiddleware)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routers
app.include_router(
    health.router,
    prefix="/api/v1",
)

app.include_router(
    auth.router,
    prefix="/api/v1",
)

app.include_router(
    users.router,
    prefix="/api/v1",
)

app.include_router(
    dashboard.router,
    prefix="/api/v1"
)