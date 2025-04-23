# frontend/app/config.py
import os
import sys
import requests
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables from .env file"""
    try:
        # Try to load from current directory (development)
        env_path = Path('.') / '.env'
        
        # For PyInstaller bundle
        if getattr(sys, 'frozen', False):
            env_path = Path(sys._MEIPASS) / '.env'
            if not env_path.exists():
                env_path = Path(os.path.dirname(sys.executable)) / '.env'
        
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            logger.info(f"Loaded environment from: {env_path}")
        else:
            logger.warning(f"No .env file found at {env_path}. Using system environment variables.")
    except Exception as e:
        logger.error(f"Error loading environment: {str(e)}")

# Load environment variables
load_environment()

def get_base_url():
    """Determine the correct base URL based on environment"""
    if os.getenv('DOCKER_CONTAINER'):
        return os.getenv("BACKEND_URL", "http://host.docker.internal:8000/api/v1/")
    return os.getenv("API_BASE_URL", "http://localhost:8000/api/v1/")

API_BASE_URL = get_base_url()
TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))  # Default 30 seconds timeout

def make_api_request(method, endpoint, **kwargs):
    """Helper function for making API requests"""
    url = f"{API_BASE_URL}{endpoint}".rstrip('/')
    
    # Set default timeout if not provided
    if 'timeout' not in kwargs:
        kwargs['timeout'] = TIMEOUT
    
    try:
        logger.debug(f"Making {method} request to: {url}")
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.Timeout:
        logger.error(f"Request timed out after {TIMEOUT} seconds: {url}")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed to {url}: {str(e)}")
        raise

# Configuration validation
if not API_BASE_URL:
    logger.error("API_BASE_URL is not configured. Please set it in .env file")
    raise ValueError("API_BASE_URL is required")

logger.info(f"API configuration loaded. Base URL: {API_BASE_URL}")