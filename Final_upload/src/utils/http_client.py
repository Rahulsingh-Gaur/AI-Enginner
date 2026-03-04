"""
HTTP Client with retry logic, authentication, and logging
"""
import time
import requests
from typing import Dict, Any, Optional, Callable
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import Settings
from src.utils.logger import logger, APILogger


class HTTPClient:
    """
    Robust HTTP client for API automation with:
    - Automatic retries
    - Request/response logging
    - Session management
    - Authentication handling
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 30,
        retry_attempts: int = 3,
        headers: Optional[Dict[str, str]] = None
    ):
        self.base_url = base_url or Settings.get_base_url()
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.session = requests.Session()
        
        # Set default headers
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "API-Automation-Framework/1.0"
        }
        if headers:
            default_headers.update(headers)
        self.session.headers.update(default_headers)
        
        # Configure retries
        self._setup_retries()
        
        # Authentication
        self._auth_token: Optional[str] = None
        self._auth_callback: Optional[Callable] = None
    
    def _setup_retries(self):
        """Configure retry strategy"""
        retry_strategy = Retry(
            total=self.retry_attempts,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def set_auth_token(self, token: str):
        """Set bearer token for authentication"""
        self._auth_token = token
        self.session.headers["Authorization"] = f"Bearer {token}"
    
    def set_api_key(self, api_key: str, header_name: str = "X-API-Key"):
        """Set API key authentication"""
        self.session.headers[header_name] = api_key
    
    def set_basic_auth(self, username: str, password: str):
        """Set basic authentication"""
        self.session.auth = (username, password)
    
    def set_auth_callback(self, callback: Callable):
        """Set callback function to refresh authentication"""
        self._auth_callback = callback
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """Make HTTP request with logging and error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Prepare request
        headers = kwargs.pop('headers', {})
        json_data = kwargs.pop('json', None)
        params = kwargs.pop('params', None)
        files = kwargs.pop('files', None)
        data = kwargs.pop('data', None)
        
        # Merge headers
        request_headers = {**self.session.headers, **headers}
        
        # Log request
        APILogger.log_request(method, url, request_headers, json_data or data)
        
        # Make request
        start_time = time.time()
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=request_headers,
                json=json_data,
                params=params,
                files=files,
                data=data,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            
        except requests.exceptions.HTTPError as e:
            # Handle 401 - Try to refresh token if callback is set
            if response.status_code == 401 and self._auth_callback:
                logger.warning("Token expired, attempting refresh...")
                self._auth_callback()
                # Retry request
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    json=json_data,
                    params=params,
                    timeout=self.timeout,
                    **kwargs
                )
                response.raise_for_status()
            else:
                raise
        
        duration = time.time() - start_time
        APILogger.log_response(response, duration)
        
        return response
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """Make GET request"""
        return self._make_request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """Make POST request"""
        return self._make_request("POST", endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """Make PUT request"""
        return self._make_request("PUT", endpoint, **kwargs)
    
    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        """Make PATCH request"""
        return self._make_request("PATCH", endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make DELETE request"""
        return self._make_request("DELETE", endpoint, **kwargs)
    
    def close(self):
        """Close session"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
