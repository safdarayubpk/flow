from sqlmodel import create_engine, Session
from src.core.config import settings


# Create the database engine
# Only enable SQL logging in development mode
engine = create_engine(settings.database_url, echo=not settings.is_production)


def get_session():
    """
    Generator function that yields a database session.
    This is used as a FastAPI dependency.
    """
    with Session(engine) as session:
        yield session