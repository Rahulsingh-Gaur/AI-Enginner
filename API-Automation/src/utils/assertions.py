"""
Custom Assertions for API Testing
"""
import json
from typing import Any, Dict, List, Optional, Union
from jsonschema import validate, ValidationError
import requests

from src.utils.logger import logger


class APIAssertions:
    """Custom assertion helpers for API testing"""
    
    @staticmethod
    def assert_status_code(
        response: requests.Response,
        expected_code: int,
        message: Optional[str] = None
    ):
        """Assert response status code"""
        actual_code = response.status_code
        if actual_code != expected_code:
            error_msg = message or f"Expected status code {expected_code}, got {actual_code}"
            error_msg += f"\nResponse: {response.text[:500]}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"✓ Status code verified: {actual_code}")
    
    @staticmethod
    def assert_status_range(
        response: requests.Response,
        min_code: int = 200,
        max_code: int = 299
    ):
        """Assert status code is within range"""
        actual_code = response.status_code
        if not (min_code <= actual_code <= max_code):
            error_msg = f"Status code {actual_code} not in range [{min_code}, {max_code}]"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"✓ Status code {actual_code} in valid range")
    
    @staticmethod
    def assert_json_schema(response: requests.Response, schema: Dict[str, Any]):
        """Assert response matches JSON schema"""
        try:
            data = response.json()
            validate(instance=data, schema=schema)
            logger.info("✓ JSON schema validation passed")
        except ValidationError as e:
            error_msg = f"JSON schema validation failed: {e.message}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response: {e}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
    
    @staticmethod
    def assert_response_time(
        response: requests.Response,
        max_time_ms: float
    ):
        """Assert response time is within limit"""
        elapsed_ms = response.elapsed.total_seconds() * 1000
        if elapsed_ms > max_time_ms:
            error_msg = f"Response time {elapsed_ms:.2f}ms exceeded limit {max_time_ms}ms"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"✓ Response time {elapsed_ms:.2f}ms within limit")
    
    @staticmethod
    def assert_json_contains(
        response: requests.Response,
        key: str,
        expected_value: Any = None
    ):
        """Assert JSON response contains specific key/value"""
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise AssertionError("Response is not valid JSON")
        
        # Handle nested keys with dot notation (e.g., "data.user.id")
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict):
                if k not in current:
                    raise AssertionError(f"Key '{key}' not found in response")
                current = current[k]
            elif isinstance(current, list) and k.isdigit():
                index = int(k)
                if index >= len(current):
                    raise AssertionError(f"Index {index} out of range for list")
                current = current[index]
            else:
                raise AssertionError(f"Cannot access '{k}' in {type(current)}")
        
        if expected_value is not None:
            if current != expected_value:
                raise AssertionError(
                    f"Expected '{key}' = {expected_value}, got {current}"
                )
        
        logger.info(f"✓ JSON contains key '{key}'")
    
    @staticmethod
    def assert_json_keys_exist(response: requests.Response, keys: List[str]):
        """Assert JSON response contains all specified keys"""
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise AssertionError("Response is not valid JSON")
        
        missing = [k for k in keys if k not in data]
        if missing:
            raise AssertionError(f"Missing keys in response: {missing}")
        
        logger.info(f"✓ All required keys present: {keys}")
    
    @staticmethod
    def assert_header_contains(
        response: requests.Response,
        header: str,
        expected_value: Optional[str] = None
    ):
        """Assert response header exists and optionally matches value"""
        if header not in response.headers:
            raise AssertionError(f"Header '{header}' not found in response")
        
        if expected_value:
            actual_value = response.headers[header]
            if expected_value.lower() not in actual_value.lower():
                raise AssertionError(
                    f"Header '{header}' value '{actual_value}' doesn't contain '{expected_value}'"
                )
        
        logger.info(f"✓ Header '{header}' verified")
    
    @staticmethod
    def assert_content_type(response: requests.Response, expected_type: str = "application/json"):
        """Assert Content-Type header"""
        content_type = response.headers.get("Content-Type", "")
        if expected_type not in content_type:
            raise AssertionError(
                f"Expected Content-Type containing '{expected_type}', got '{content_type}'"
            )
        logger.info(f"✓ Content-Type verified: {content_type}")
    
    @staticmethod
    def assert_list_not_empty(response: requests.Response, key: Optional[str] = None):
        """Assert list in response is not empty"""
        data = response.json()
        
        if key:
            if key not in data:
                raise AssertionError(f"Key '{key}' not found")
            data = data[key]
        
        if not isinstance(data, list):
            raise AssertionError(f"Expected list, got {type(data)}")
        
        if len(data) == 0:
            raise AssertionError("List is empty")
        
        logger.info(f"✓ List contains {len(data)} items")
    
    @staticmethod
    def assert_error_message(
        response: requests.Response,
        expected_message: Optional[str] = None,
        expected_code: Optional[str] = None
    ):
        """Assert error response contains expected message/code"""
        data = response.json()
        
        if expected_message:
            # Check common error fields
            error_fields = ['error', 'message', 'errorMessage', 'detail']
            found = False
            for field in error_fields:
                if field in data:
                    if expected_message.lower() in str(data[field]).lower():
                        found = True
                        break
            
            if not found:
                raise AssertionError(f"Error message '{expected_message}' not found in {data}")
        
        if expected_code:
            code_fields = ['error_code', 'code', 'errorCode']
            found = False
            for field in code_fields:
                if field in data and data[field] == expected_code:
                    found = True
                    break
            
            if not found:
                raise AssertionError(f"Error code '{expected_code}' not found")
        
        logger.info("✓ Error response verified")


# Aliases for convenience
assert_status = APIAssertions.assert_status_code
assert_schema = APIAssertions.assert_json_schema
assert_time = APIAssertions.assert_response_time
assert_contains = APIAssertions.assert_json_contains
assert_keys = APIAssertions.assert_json_keys_exist
