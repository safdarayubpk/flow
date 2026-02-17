import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dapr.ext.fastapi import DaprApp
from sqlmodel import SQLModel, Session
from src.api.v1.auth import router as auth_router
from src.api.v1.tasks import router as tasks_router
from src.api.v1.chat import router as chat_router
from src.api.v1.tags import router as tags_router
from src.core.config import settings
from src.core.database import engine

# Import models to register them with SQLModel
from src.models.user import User
from src.models.task import Task
from src.models.tag import Tag
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.task_tag_link import TaskTagLink

logger = logging.getLogger(__name__)

# Scheduler interval in seconds (default 60s, configurable via env)
RECURRING_INTERVAL_SECONDS = int(getattr(settings, "recurring_interval_seconds", 60))


def create_db_and_tables():
    """Create database tables on startup and add missing columns for Phase V.1"""
    SQLModel.metadata.create_all(engine)

    # Add missing columns to existing tables (safe ALTER TABLE IF NOT EXISTS)
    from sqlalchemy import text, inspect
    inspector = inspect(engine)

    with engine.connect() as conn:
        # Check and add missing columns to 'task' table
        if inspector.has_table("task"):
            existing_cols = {col["name"] for col in inspector.get_columns("task")}
            migrations = [
                ("priority", "VARCHAR(20)"),
                ("due_date", "TIMESTAMP"),
                ("recurrence_rule", "VARCHAR(200)"),
                ("deleted_at", "TIMESTAMP"),
                ("reminder_enabled", "BOOLEAN DEFAULT FALSE"),
            ]
            for col_name, col_type in migrations:
                if col_name not in existing_cols:
                    conn.execute(text(f'ALTER TABLE task ADD COLUMN {col_name} {col_type}'))
            conn.commit()


async def _recurring_task_loop():
    """Background loop that processes recurring tasks on a fixed interval."""
    from src.services.recurring_service import RecurringService

    while True:
        await asyncio.sleep(RECURRING_INTERVAL_SECONDS)
        try:
            with Session(engine) as session:
                created = RecurringService.process_recurring_tasks(session=session)
                if created:
                    logger.info("Recurring scheduler created %d task(s)", len(created))
        except Exception:
            logger.exception("Recurring task scheduler error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: DB migrations + Dapr setup + recurring-task scheduler. Shutdown: cleanup all."""
    # Phase 1: Database setup
    create_db_and_tables()

    # Phase 2: Dapr subscriptions are registered in create_app() via register_subscriptions()
    logger.info("Dapr subscription handlers active")

    # Phase 3: Background tasks (recurring scheduler continues as safety net per FR-007)
    recurring_scheduler_task = asyncio.create_task(_recurring_task_loop())
    logger.info("Recurring task scheduler started (interval=%ds)", RECURRING_INTERVAL_SECONDS)

    yield

    # Shutdown: Cancel recurring scheduler
    recurring_scheduler_task.cancel()
    try:
        await recurring_scheduler_task
    except asyncio.CancelledError:
        pass
    logger.info("Recurring task scheduler stopped")


def create_app():
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(title="Todo Application API", version="1.0.0", lifespan=lifespan)

    # CORS middleware - specify exact origins when using credentials
    # Note: Cannot use ["*"] with allow_credentials=True
    # Use configuration from settings
    allowed_origins = [origin.strip() for origin in settings.cors_origins.split(",")]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Authorization"],
    )

    # Include API routers
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])
    app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
    app.include_router(tags_router, prefix="/api/v1/tags", tags=["tags"])

    # Import and include Dapr service invocation endpoints
    from src.services.dapr.service_invocation import register_dapr_endpoints
    register_dapr_endpoints(app)

    @app.get("/")
    def read_root():
        return {"message": "Todo Application API"}

    @app.get("/health")
    def health_check():
        """Health check endpoint for deployment monitoring"""
        return {"status": "healthy", "version": "1.0.0"}

    # Initialize DaprApp wrapper and register subscriptions on the SAME app instance
    dapr_app = DaprApp(app)
    from src.services.dapr.subscriptions import register_subscriptions
    register_subscriptions(dapr_app)

    return app


app = create_app()