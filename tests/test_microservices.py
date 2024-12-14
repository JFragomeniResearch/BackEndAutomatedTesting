import pytest
from beat import BEAT, TestConfig
from utils.microservice_mocks import MicroserviceMocker
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
def mock_service():
    """Fixture to create MicroserviceMocker instance"""
    return MicroserviceMocker()

class TestMicroserviceIntegration:
    """Test suite for microservice integration"""

    def test_successful_service_response(self, mock_service, monkeypatch):
        """Test successful microservice response"""
        mock_response = mock_service.create_response_mock(
            status_code=200,
            json_data={"status": "success", "data": {"id": 1, "name": "Test"}}
        )
        
        # Mock the requests.get method
        monkeypatch.setattr(requests, "get", 
            mock_service.mock_service_call(return_value=mock_response))
        
        # Make request
        response = requests.get("https://microservice.example.com/api/resource")
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_service_timeout(self, mock_service, monkeypatch):
        """Test microservice timeout handling"""
        # Mock timeout behavior
        monkeypatch.setattr(requests, "get", 
            mock_service.mock_service_call(
                side_effect=mock_service.create_timeout_mock()
            ))
        
        with pytest.raises(TimeoutError):
            requests.get("https://microservice.example.com/api/resource")

    def test_service_connection_error(self, mock_service, monkeypatch):
        """Test microservice connection error handling"""
        # Mock connection error
        monkeypatch.setattr(requests, "get", 
            mock_service.mock_service_call(
                side_effect=mock_service.create_connection_error_mock()
            ))
        
        with pytest.raises(ConnectionError):
            requests.get("https://microservice.example.com/api/resource")

    def test_service_error_response(self, mock_service, monkeypatch):
        """Test microservice error response handling"""
        mock_response = mock_service.create_response_mock(
            status_code=500,
            json_data={"status": "error", "message": "Internal Server Error"}
        )
        
        monkeypatch.setattr(requests, "get", 
            mock_service.mock_service_call(return_value=mock_response))
        
        response = requests.get("https://microservice.example.com/api/resource")
        
        assert response.status_code == 500
        assert response.json()["status"] == "error"

    @pytest.mark.parametrize("status_code,expected_data", [
        (200, {"status": "success"}),
        (400, {"status": "error", "type": "validation"}),
        (500, {"status": "error", "type": "server"})
    ])
    def test_various_response_scenarios(self, mock_service, monkeypatch, 
                                      status_code, expected_data):
        """Test different response scenarios from microservice"""
        mock_response = mock_service.create_response_mock(
            status_code=status_code,
            json_data=expected_data
        )
        
        monkeypatch.setattr(requests, "get", 
            mock_service.mock_service_call(return_value=mock_response))
        
        response = requests.get("https://microservice.example.com/api/resource")
        
        assert response.status_code == status_code
        assert response.json()["status"] == expected_data["status"]
