from sqlmodel import create_engine, Session
from src.core.config import settings


# Create the database engine
# Only enable SQL logging in development mode
# pool_pre_ping: verify connections before use (handles Neon pooler dropping idle connections)
# pool_recycle: discard connections older than 300s to avoid stale SSL connections
engine = create_engine(
    settings.database_url,
    echo=not settings.is_production,
    pool_pre_ping=True,
    pool_recycle=300,
)


def get_session():
    """
    Generator function that yields a database session.
    This is used as a FastAPI dependency.
    """
    with Session(engine) as session:
        yield session