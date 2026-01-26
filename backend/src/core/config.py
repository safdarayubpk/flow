from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    database_url: str = "sqlite:///./todo_app.db"  # Default for local development
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    environment: str = "development"  # "development" or "production"

    # OpenAI Configuration
    openai_api_key: Optional[str] = None

    # Groq Configuration (free alternative to OpenAI)
    groq_api_key: Optional[str] = None

    # ChatKit Configuration
    chatkit_secret_key: Optional[str] = None

    # Better Auth Configuration
    better_auth_url: str = "http://localhost:3000"

    # CORS Configuration - comma-separated origins
    cors_origins: str = "http://localhost:3000,https://frontend-blue-six-59.vercel.app"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    class Config:
        env_file = ".env"


settings = Settings()