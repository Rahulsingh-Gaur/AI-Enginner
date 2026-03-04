"""
Base API Client with common functionality
"""
from typing import Dict, Any, Optional, TypeVar, Type
from pydantic import BaseModel
import requests

from src.utils.http_client import HTTPClient
from src.utils.logger import logger
from config.settings import Settings

T = TypeVar('T', bound=BaseModel)


class BaseAPIClient:
    """
    Base class for all API clients
    Provides common functionality for authentication, error handling, etc.
    """
    
    def __init__(
        self,
        http_client: Optional[HTTPClient] = None,
        base_url: Optional[str] = None
    ):
        self.http = http_client or HTTPClient(base_url=base_url)
        self._authenticate()
    
    def _authenticate(self):
        """
        Authenticate the client based on settings
        Override this method for custom authentication
        """
        auth_config = Settings.get_auth_config()
        auth_type = auth_config.get("type", "bearer")
        
        if auth_type == "bearer" and Settings.ACCESS_TOKEN:
            self.http.set_auth_token(Settings.ACCESS_TOKEN)
            logger.info("Authenticated with Bearer token")
            
        elif auth_type == "api_key" and Settings.API_KEY:
            header_name = auth_config.get("api_key_header", "X-API-Key")
            self.http.set_api_key(Settings.API_KEY, header_name)
            logger.info(f"Authenticated with API Key ({header_name})")
            
        elif auth_type == "basic":
            # Implement basic auth if needed
            pass
            
        elif auth_type == "oauth2":
            # Implement OAuth2 flow if needed
            pass
    
    def _handle_response(
        self,
        response: requests.Response,
        model_class: Optional[Type[T]] = None
    ) -> Any:
        """
        Handle API response and optionally parse to model
        
        Args:
            response: HTTP response
            model_class: Pydantic model class to parse response
            
        Returns:
            Parsed model or raw response
        """
        try:
            data = response.json()
        except ValueError:
            return response
        
        if model_class:
            try:
                if isinstance(data, list):
                    return [model_class.model_validate(item) for item in data]
                return model_class.model_validate(data)
            except Exception as e:
                logger.error(f"Failed to parse response: {e}")
                logger.debug(f"Response data: {data}")
                raise
        
        return data
    
    def _build_url(self, path: str, **kwargs) -> str:
        """Build URL with path parameters"""
        return path.format(**kwargs)
    
    def close(self):
        """Close HTTP client"""
        self.http.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
