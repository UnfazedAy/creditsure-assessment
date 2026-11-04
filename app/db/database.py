from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# Database configuration
DATABASE_URL = "sqlite:///./test.db"  # Replace with your actual database URL
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()