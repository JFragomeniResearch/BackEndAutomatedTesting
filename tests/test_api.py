import pytest
from beat import BEAT, TestConfig
from utils.api_helpers import APIHelper
from unittest.mock import Mock
import requests

@pytest.fixture
def beat_framework():
    """Fixture to create BEAT instance with test configuration"""
    config = TestConfig(
        api_base_url="https://api.example.com",
        db_connection_string="sqlite:///test.db",
        auth_token="test_token"
    )
    return BEAT(config)

@pytest.fixture
def api_helper(beat_framework):
    """Fixture to create APIHelper instance"""
    return APIHelper(beat_framework)

@pytest.fixture
def mock_requests(monkeypatch):
    """Mock requests for API tests"""
    def mock_response(*args, **kwargs):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": 1, "name": "Test User"}
        return mock_resp
    
    monkeypatch.setattr(requests, "request", mock_response)
    return mock_response

class TestAPIEndpoints:
    """Test suite for API endpoints"""

    def test_successful_get_request(self, api_helper, mock_requests):
        """Test successful GET request"""
        response = api_helper.get_resource("users/1")
        assert response.status_code == 200

    def test_create_resource(self, api_helper):
        """Test POST request to create a resource"""
        test_data = {
            "name": "Test User",
            "email": "test@example.com"
        }
        response = api_helper.create_resource("users", test_data)
        api_helper.assert_status_code(response, 201)
        
        # Verify response contains created resource
        response_data = response.json()
        assert response_data["name"] == test_data["name"]
        assert response_data["email"] == test_data["email"]

    def test_invalid_endpoint(self, api_helper):
        """Test request to invalid endpoint returns 404"""
        response = api_helper.get_resource("nonexistent")
        api_helper.assert_status_code(response, 404)

    def test_schema_validation(self, api_helper):
        """Test response schema validation"""
        expected_schema = {
            "id": int,
            "name": str,
            "email": str,
            "address": {
                "street": str,
                "city": str,
                "zipcode": str
            }
        }
        
        response = api_helper.get_resource("users/1")
        api_helper.validate_response_schema(response, expected_schema)

    @pytest.mark.parametrize("user_id,expected_status", [
        ("1", 200),
        ("999", 404),
        ("invalid", 400)
    ])
    def test_get_user_scenarios(self, api_helper, user_id, expected_status):
        """Test different scenarios for getting user details"""
        response = api_helper.get_resource(f"users/{user_id}")
        api_helper.assert_status_code(response, expected_status)
