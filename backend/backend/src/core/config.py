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

    # Kafka Configuration (Phase V.2 - Event-Driven Architecture - reference for Dapr)
    kafka_bootstrap_servers: Optional[str] = None  # e.g., "localhost:9092" - Dapr pubsub component uses this
    kafka_topic: str = "todo-events"

    # Dapr Configuration (Phase V.3 - Dapr Microservices & Pub/Sub)
    dapr_pubsub_name: str = "kafka-pubsub"  # Dapr pubsub component name (defined in backend/components/)
    dapr_app_id: str = "todo-backend"       # Dapr app ID for service invocation
    dapr_enabled: bool = True               # Enable/disable Dapr integration (for graceful degradation)

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    class Config:
        env_file = ".env"


settings = Settings()