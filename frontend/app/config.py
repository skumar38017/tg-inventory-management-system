# frontend/app/config.py
import os
import requests
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

def get_base_url():
    """Determine the correct base URL based on environment"""
    if os.getenv('DOCKER_CONTAINER'):
        return os.getenv("BACKEND_URL", "http://host.docker.internal:8000/api/v1/")
    return os.getenv("API_BASE_URL", "http://localhost:8000/api/v1/")

API_BASE_URL = get_base_url()

def make_api_request(method, endpoint, **kwargs):
    """Helper function for making API requests"""
    url = f"{API_BASE_URL}{endpoint}".rstrip('/')
    try:
        logger.debug(f"Attempting API request to: {url}")
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed to {url}: {str(e)}")
        raise