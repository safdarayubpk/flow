from sqlmodel import create_engine, Session
from src.core.config import settings


# Create the database engine with connection pooling settings
# These settings help with external database connections (like Neon PostgreSQL)
# that may drop SSL connections unexpectedly
engine = create_engine(
    settings.database_url,
    echo=not settings.is_production,
    pool_pre_ping=True,  # Verify connection before using (handles dropped connections)
    pool_recycle=300,    # Recycle connections every 5 minutes
    pool_size=5,         # Number of connections to keep in the pool
    max_overflow=10,     # Max additional connections beyond pool_size
    connect_args={
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    } if "postgresql" in settings.database_url else {}
)


def get_session():
    """
    Generator function that yields a database session.
    This is used as a FastAPI dependency.
    """
    with Session(engine) as session:
        yield session