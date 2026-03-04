"""
Logging Utility for API Automation Framework
"""
import sys
from pathlib import Path
from loguru import logger as _logger
from config.settings import Settings


def setup_logger(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True
):
    """
    Configure logger with file and console handlers
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
    """
    # Remove default handler
    _logger.remove()
    
    # Console handler with rich formatting
    if log_to_console:
        _logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            level=log_level,
            colorize=True
        )
    
    # File handler
    if log_to_file:
        log_file = Settings.LOGS_DIR / "api_automation_{time:YYYY-MM-DD}.log"
        _logger.add(
            str(log_file),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=log_level,
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )
    
    return _logger


# Create global logger instance
logger = setup_logger(
    log_level="DEBUG" if Settings.DEBUG else "INFO",
    log_to_file=True,
    log_to_console=True
)


class APILogger:
    """Helper class for API request/response logging"""
    
    @staticmethod
    def log_request(method: str, url: str, headers: dict, body=None):
        """Log API request details"""
        logger.debug(f"{'='*50}")
        logger.debug(f"API REQUEST: {method} {url}")
        logger.debug(f"Headers: {headers}")
        if body:
            # Mask sensitive data
            safe_body = APILogger._mask_sensitive_data(body)
            logger.debug(f"Body: {safe_body}")
        logger.debug(f"{'='*50}")
    
    @staticmethod
    def log_response(response, duration: float):
        """Log API response details"""
        logger.debug(f"{'='*50}")
        logger.debug(f"API RESPONSE: {response.status_code} ({duration:.3f}s)")
        logger.debug(f"Headers: {dict(response.headers)}")
        try:
            logger.debug(f"Body: {response.text[:1000]}...")  # Limit output
        except:
            logger.debug(f"Body: <binary content>")
        logger.debug(f"{'='*50}")
    
    @staticmethod
    def _mask_sensitive_data(data):
        """Mask sensitive fields in request body"""
        if not isinstance(data, dict):
            return data
        
        sensitive_fields = ['password', 'token', 'api_key', 'secret', 'authorization']
        masked = data.copy()
        
        for key in masked:
            if any(sf in key.lower() for sf in sensitive_fields):
                masked[key] = '***MASKED***'
        
        return masked
