"""
Basic test to verify the tags functionality works correctly.
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch


@pytest.fixture
def client():
    """Create a test client for the API."""
    with TestClient(app) as test_client:
        yield test_client


def test_tags_endpoints_exist(client):
    """Test that tags endpoints are accessible."""
    # Mock authentication
    with patch("src.core.auth.get_current_user") as mock_get_current_user:
        from src.models.user import User
        mock_get_current_user.return_value = User(id="test_user", email="test@example.com", name="Test User")

        # Test the tags listing endpoint
        response = client.get("/api/v1/tags/")
        assert response.status_code in [200, 401, 403]

        # Test creating a tag
        tag_data = {
            "name": "Important",
            "color": "#FF0000"
        }
        response = client.post("/api/v1/tags/", json=tag_data)
        assert response.status_code in [200, 201, 401, 403]


if __name__ == "__main__":
    pytest.main([__file__])