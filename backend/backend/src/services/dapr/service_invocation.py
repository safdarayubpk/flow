"""
Dapr service invocation endpoints for the Todo application.

Implements the dapr-invocation-pattern skill with:
- Health check endpoint accessible via Dapr service invocation
- Event counters for observability
- User context propagation support
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter

logger = logging.getLogger(__name__)

# In-memory event counters for observability (reset on app restart)
# These would be replaced with a persistent store in production
publish_counter = 0
subscription_counter = 0


router = APIRouter(prefix="/api/dapr", tags=["dapr-service-invocation"])


@router.get("/health")
async def dapr_health_endpoint() -> Dict[str, Any]:
    """
    Health check endpoint accessible via Dapr service invocation.

    Can be called via:
    - Direct HTTP: /api/dapr/health
    - Dapr service invocation: dapr invoke --app-id todo-backend --method api/dapr/health
    - Dapr sidecar: http://localhost:3500/v1.0/invoke/todo-backend/method/api/dapr/health

    Returns health status with event counters and subscription info.
    """
    global publish_counter, subscription_counter

    # Note: In a real implementation, these would be actual counters
    # For now, we're not tracking actual events in this endpoint for simplicity
    # The counters would be incremented in publisher and subscription handlers

    health_info = {
        "status": "healthy",
        "app_id": "todo-backend",
        "dapr_enabled": True,
        "pubsub_component": "kafka-pubsub",
        "subscriptions_active": 2,  # notification + recurring
        "publish_counter": publish_counter,
        "subscription_counter": subscription_counter,
        "features": ["pubsub", "service_invocation", "user_isolation"],
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }

    logger.info("Dapr health endpoint called, returning status: %s", health_info["status"])

    return health_info


@router.post("/increment-publish-counter")
async def increment_publish_counter_endpoint() -> Dict[str, Any]:
    """
    Helper endpoint to increment the publish counter (for testing).
    In a real app, this would be done automatically in the publisher.
    """
    global publish_counter
    publish_counter += 1
    return {"publish_counter": publish_counter}


@router.post("/increment-subscription-counter")
async def increment_subscription_counter_endpoint() -> Dict[str, Any]:
    """
    Helper endpoint to increment the subscription counter (for testing).
    In a real app, this would be done automatically in the subscription handlers.
    """
    global subscription_counter
    subscription_counter += 1
    return {"subscription_counter": subscription_counter}


# Register the router endpoints
def register_dapr_endpoints(app):
    """
    Register Dapr service invocation endpoints with the FastAPI app.
    This is called from main.py to make the endpoints available.
    """
    app.include_router(router)


__all__ = ["register_dapr_endpoints", "router"]