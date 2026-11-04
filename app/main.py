from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
# from app.models.user import User

from app.routers import auth, dashboard, health, users


# Initialize database tables on application startup
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     Base.metadata.create_all(bind=engine)
#     yield


# Initialize FastAPI application
app = FastAPI(
    title="CrediSure Dashboard API",
    description="Backend API for authentication, user management, and dashboard statistics.",
    version="1.0.0",
    # lifespan=lifespan,
)


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
