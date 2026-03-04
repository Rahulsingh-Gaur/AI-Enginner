"""
Configuration Management for API Automation Framework
"""
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = Path(__file__).parent


class Settings:
    """Application settings and configuration"""
    
    # Environment
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # API Credentials (from environment variables)
    API_KEY: Optional[str] = os.getenv("API_KEY")
    API_SECRET: Optional[str] = os.getenv("API_SECRET")
    ACCESS_TOKEN: Optional[str] = os.getenv("ACCESS_TOKEN")
    REFRESH_TOKEN: Optional[str] = os.getenv("REFRESH_TOKEN")
    
    # Test Data
    TEST_DATA_DIR: Path = BASE_DIR / "tests" / "data"
    REPORTS_DIR: Path = BASE_DIR / "reports"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # Test Execution
    PARALLEL_WORKERS: int = int(os.getenv("PARALLEL_WORKERS", "4"))
    TEST_TIMEOUT: int = int(os.getenv("TEST_TIMEOUT", "300"))
    
    # Reporting
    GENERATE_HTML_REPORT: bool = os.getenv("GENERATE_HTML_REPORT", "true").lower() == "true"
    GENERATE_ALLURE_REPORT: bool = os.getenv("GENERATE_ALLURE_REPORT", "false").lower() == "true"
    
    _config_cache: Optional[Dict[str, Any]] = None
    
    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        """Load YAML configuration file"""
        if cls._config_cache is None:
            config_file = CONFIG_DIR / "environments.yaml"
            with open(config_file, 'r') as f:
                cls._config_cache = yaml.safe_load(f)
        return cls._config_cache
    
    @classmethod
    def get_env_config(cls, env: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration for specific environment"""
        config = cls.load_config()
        env = env or cls.ENV
        return config.get("environments", {}).get(env, {})
    
    @classmethod
    def get_api_config(cls) -> Dict[str, Any]:
        """Get API endpoints configuration"""
        config = cls.load_config()
        return config.get("apis", {})
    
    @classmethod
    def get_auth_config(cls) -> Dict[str, Any]:
        """Get authentication configuration"""
        config = cls.load_config()
        return config.get("auth", {})
    
    @classmethod
    def get_base_url(cls, env: Optional[str] = None) -> str:
        """Get base URL for environment"""
        env_config = cls.get_env_config(env)
        return env_config.get("base_url", "")
    
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist"""
        for directory in [cls.TEST_DATA_DIR, cls.REPORTS_DIR, cls.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


# Initialize settings
Settings.ensure_directories()
