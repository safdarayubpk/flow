from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.auth import router as auth_router
from src.api.v1.tasks import router as tasks_router
from src.core.config import settings


def create_app():
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(title="Todo Application API", version="1.0.0")

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Restrict to frontend domain in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # Expose authorization header to allow frontend to access JWT tokens
        expose_headers=["Authorization"],
    )

    # Include API routers
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])

    @app.get("/")
    def read_root():
        return {"message": "Todo Application API"}

    return app


app = create_app()