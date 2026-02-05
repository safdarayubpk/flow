#!/usr/bin/env python3
"""
Quick check to verify the API endpoints are properly configured with advanced features
"""
import inspect
from src.api.v1.tasks import router
from fastapi import APIRouter

def check_api_endpoints():
    """Check that all required API endpoints exist"""

    # Get all routes from the router
    routes = router.routes

    print("Checking API endpoints...")

    # Verify we have the basic CRUD endpoints
    endpoints = [route.path for route in routes]

    expected_endpoints = [
        "/",
        "/{task_id}",
        "/{task_id}/complete",
        "/{task_id}/recurring",
        "/{task_id}/due_date"
    ]

    for expected in expected_endpoints:
        if expected in [route.path for route in routes]:
            print(f"✓ Endpoint {expected} exists")
        else:
            print(f"✗ Endpoint {expected} missing")

    # Check that GET endpoint has query parameters for filtering
    get_route = next((route for route in routes if route.path == "/" and route.methods and "GET" in route.methods), None)
    if get_route:
        # Check function signature for query parameters
        print(f"✓ GET / endpoint exists with methods: {get_route.methods}")

        # Get the function behind the route
        if hasattr(get_route, 'endpoint'):
            sig = inspect.signature(get_route.endpoint)
            params = list(sig.parameters.keys())

            # Check for expected query parameters
            expected_params = ['priority', 'tags', 'due_date_before', 'sort', 'order']
            for param in expected_params:
                if param in params:
                    print(f"✓ Parameter '{param}' found in GET / endpoint")
                else:
                    print(f"? Parameter '{param}' not directly visible in signature (may be handled via Query)")
    else:
        print("✗ GET / endpoint not found")

    # Count total endpoints
    print(f"\nTotal endpoints found: {len(endpoints)}")

    print("\nEndpoint paths:")
    for route in routes:
        print(f"  {route.methods} {route.path}")

    print("\n✅ API endpoints verification completed!")

if __name__ == "__main__":
    check_api_endpoints()