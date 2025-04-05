#  frontend/app/config.py
import os
import requests


# Set logging
import logging  
# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)


#  url for the API
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1/")
REQUEST_TIMEOUT = 10


def make_api_request(method, endpoint, **kwargs):
    """Helper function for making API requests"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        response = requests.request(
            method,
            url,
            timeout=REQUEST_TIMEOUT,
            **kwargs
        )
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed to {url}: {str(e)}")
        raise