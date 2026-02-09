"""
Configuration settings for the automation framework.
Loads settings from environment variables with sensible defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in the config directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings loaded from environment variables."""
    
    # Base URL for the application under test
    BASE_URL = os.getenv("BASE_URL", "https://example.com")
    
    # Browser settings
    BROWSER = os.getenv("BROWSER", "chromium")  # chromium, firefox, webkit
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    SLOW_MO = int(os.getenv("SLOW_MO", "0"))  # Slow motion delay in milliseconds
    
    # Viewport settings
    VIEWPORT_WIDTH = int(os.getenv("VIEWPORT_WIDTH", "1920"))
    VIEWPORT_HEIGHT = int(os.getenv("VIEWPORT_HEIGHT", "1080"))
    
    # Test credentials
    USERNAME = os.getenv("USERNAME", "")
    PASSWORD = os.getenv("PASSWORD", "")

    # KIMI / Eraler API keys (set these in environment or .env, do NOT commit secrets)
    KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
    ERALER_API_KEY = os.getenv("ERALER_API_KEY", "")
    
    # Timeouts (in milliseconds)
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30000"))
    NAVIGATION_TIMEOUT = int(os.getenv("NAVIGATION_TIMEOUT", "30000"))
    
    # Reporting and screenshots
    SCREENSHOT_ON_FAILURE = os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"
    SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "screenshots")
    REPORT_DIR = os.getenv("REPORT_DIR", "reports")
    
    # Test execution
    PARALLEL_WORKERS = int(os.getenv("PARALLEL_WORKERS", "1"))
    RETRY_COUNT = int(os.getenv("RETRY_COUNT", "0"))


# Create a global settings instance
settings = Settings()
