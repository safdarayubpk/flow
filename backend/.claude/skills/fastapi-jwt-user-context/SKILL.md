---
name: fastapi-jwt-user-context
description: provide fastapi jwt dependency, current_user from jwt, protected endpoint auth, fastapi jwt verification with shared secret
---

# FastAPI JWT User Context

## Overview

This skill provides FastAPI JWT authentication patterns for extracting current_user context from JWT tokens. It implements secure token verification using shared secrets from BETTER_AUTH_SECRET environment variable, ensuring proper user context isolation and protected endpoint authorization.

## JWT Dependency Pattern

### Core JWT Dependency Function
Use the FastAPI Depends() pattern to extract current_user from JWT tokens:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
import os

security = HTTPBearer()

class CurrentUser(BaseModel):
    user_id: str
    email: str
    name: str = None

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)) -> CurrentUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Get the shared secret from environment variable
    SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
    if not SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication system not properly configured"
        )

    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")

        if user_id is None or email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Return Pydantic model with user context
    return CurrentUser(user_id=user_id, email=email)
```

## Protected Endpoint Implementation

### Basic Protected Endpoint
Use the dependency in your route definitions:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/protected-endpoint")
async def protected_route(current_user: CurrentUser = Depends(get_current_user)):
    return {
        "message": f"Hello {current_user.email}",
        "user_id": current_user.user_id
    }
```

### User Context Validation
For endpoints requiring user context matching (e.g., user-specific data):

```python
@app.get("/api/{user_id}/tasks")
async def get_user_tasks(
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    # Validate that requested user_id matches authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot access another user's data"
        )

    # Return user's tasks
    return {"tasks": [], "user_id": current_user.user_id}
```

## Error Handling Standards

### JWT Verification Errors
Always raise appropriate HTTP exceptions:

- **HTTPException(401)**: For missing/invalid tokens, failed verification
- **HTTPException(403)**: For user context mismatches or insufficient permissions
- **HTTPException(500)**: For missing or misconfigured secrets

### Environment Configuration
Ensure the BETTER_AUTH_SECRET environment variable is set:

```python
import os

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
if not SECRET_KEY:
    raise RuntimeError("BETTER_AUTH_SECRET environment variable is required")
```

## Library Recommendations

### Primary Libraries
- **python-jose**: For JWT decoding and verification
- **PyJWT**: Alternative JWT library with similar functionality

### Installation
```bash
pip install python-jose[cryptography]
# or
pip install PyJWT
```

## Security Best Practices

### Token Verification
- Always verify tokens against the shared secret
- Use HS256 algorithm for symmetric encryption
- Validate required claims (user_id, email)
- Never trust unverified tokens

### Secret Management
- Store secrets in environment variables (BETTER_AUTH_SECRET)
- Use secure secret management in production
- Rotate secrets periodically

### Dependency Injection
- Use FastAPI's Depends() for clean dependency injection
- Return Pydantic models for type safety
- Include at minimum user_id and email in current_user context

## Common Usage Patterns

### With Better Auth Integration
When integrating with Better Auth for frontend authentication:

```python
# In your frontend, attach the JWT token to API requests:
# Authorization: Bearer <jwt_token>

# Backend automatically extracts user context via dependency
@app.post("/api/{user_id}/tasks")
async def create_task(
    user_id: str,
    task_data: dict,
    current_user: CurrentUser = Depends(get_current_user)
):
    # Validate user context
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Process task creation for authenticated user
    return {"task_id": 123, "status": "created"}
```

## Validation Checklist

Before implementing JWT authentication:
- [ ] BETTER_AUTH_SECRET environment variable configured
- [ ] python-jose or PyJWT installed
- [ ] get_current_user dependency function created
- [ ] Protected endpoints use Depends(get_current_user)
- [ ] Proper HTTP exception handling implemented
- [ ] User context validation applied where needed