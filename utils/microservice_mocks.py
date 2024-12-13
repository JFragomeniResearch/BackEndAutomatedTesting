from typing import Optional, Dict, Any, Callable
import json
from unittest.mock import MagicMock
from requests import Response

class MicroserviceMocker:
    """Helper class for mocking microservice responses"""
    
    @staticmethod
    def create_response_mock(
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Response:
        """Create a mocked Response object"""
        response = Response()
        response.status_code = status_code
        
        if json_data is not None:
            response._content = json.dumps(json_data).encode('utf-8')
        
        if headers:
            response.headers.update(headers)
            
        return response
    
    @staticmethod
    def mock_service_call(
        return_value: Any,
        side_effect: Optional[Callable] = None
    ) -> MagicMock:
        """Create a mock for a service call"""
        mock = MagicMock()
        mock.return_value = return_value
        if side_effect:
            mock.side_effect = side_effect
        return mock
    
    @staticmethod
    def create_timeout_mock() -> Callable:
        """Create a mock that simulates a timeout"""
        def timeout_effect(*args, **kwargs):
            raise TimeoutError("Service timeout")
        return timeout_effect
    
    @staticmethod
    def create_connection_error_mock() -> Callable:
        """Create a mock that simulates a connection error"""
        def connection_error_effect(*args, **kwargs):
            raise ConnectionError("Connection failed")
        return connection_error_effect 