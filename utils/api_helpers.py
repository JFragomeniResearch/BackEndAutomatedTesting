from typing import Optional, Dict, Any, Union
import json
from requests import Response
from ..beat import BEAT, TestConfig

class APIHelper:
    """Helper class for API testing operations"""
    
    def __init__(self, beat_instance: BEAT):
        self.beat = beat_instance
    
    def assert_status_code(self, response: Response, expected_code: int) -> None:
        """Assert that the response has the expected status code"""
        assert response.status_code == expected_code, (
            f"Expected status code {expected_code}, but got {response.status_code}. "
            f"Response body: {response.text}"
        )
    
    def assert_json_structure(
        self, 
        response: Response, 
        expected_keys: list
    ) -> None:
        """Verify that JSON response contains all expected keys"""
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            raise AssertionError("Response is not valid JSON")
            
        for key in expected_keys:
            assert key in response_json, f"Expected key '{key}' not found in response"
    
    def get_resource(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Response:
        """Wrapper for GET requests"""
        return self.beat.api_request("GET", endpoint, params=params)
    
    def create_resource(
        self, 
        endpoint: str, 
        data: Dict[str, Any]
    ) -> Response:
        """Wrapper for POST requests"""
        return self.beat.api_request("POST", endpoint, data=data)
    
    def update_resource(
        self, 
        endpoint: str, 
        data: Dict[str, Any]
    ) -> Response:
        """Wrapper for PUT requests"""
        return self.beat.api_request("PUT", endpoint, data=data)
    
    def delete_resource(
        self, 
        endpoint: str
    ) -> Response:
        """Wrapper for DELETE requests"""
        return self.beat.api_request("DELETE", endpoint)
    
    def validate_response_schema(
        self, 
        response: Response, 
        schema: Dict[str, Any]
    ) -> None:
        """
        Validate response against a schema definition
        Schema should be a dictionary defining the expected structure and types
        """
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            raise AssertionError("Response is not valid JSON")
            
        def _validate_type(value: Any, expected_type: Union[type, str]) -> bool:
            if expected_type == "array":
                return isinstance(value, list)
            elif expected_type == "object":
                return isinstance(value, dict)
            return isinstance(value, expected_type)
        
        def _validate_object(obj: Dict, schema_def: Dict) -> None:
            for key, type_def in schema_def.items():
                assert key in obj, f"Missing required key: {key}"
                if isinstance(type_def, dict):
                    assert isinstance(obj[key], dict), f"Expected {key} to be an object"
                    _validate_object(obj[key], type_def)
                else:
                    assert _validate_type(obj[key], type_def), (
                        f"Invalid type for {key}. Expected {type_def}, "
                        f"got {type(obj[key])}"
                    )
        
        _validate_object(response_json, schema) 