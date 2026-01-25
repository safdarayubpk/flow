from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from src.api.v1.auth import router as auth_router
from src.api.v1.tasks import router as tasks_router
from src.api.v1.chat import router as chat_router
from src.core.config import settings
from src.core.database import engine

# Import models to register them with SQLModel
from src.models.user import User
from src.models.task import Task
from src.models.conversation import Conversation
from src.models.message import Message


def create_db_and_tables():
    """Create database tables on startup"""
    SQLModel.metadata.create_all(engine)


def create_app():
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(title="Todo Application API", version="1.0.0")

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

    @app.on_event("startup")
    def on_startup():
        """Create database tables on startup"""
        create_db_and_tables()

    @app.get("/")
    def read_root():
        return {"message": "Todo Application API"}

    return app


app = create_app()