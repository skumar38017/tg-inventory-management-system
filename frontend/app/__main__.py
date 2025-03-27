# frontend/app/__main__.py
from .entry_inventory import main
import platform
import logging
import traceback

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("Starting inventory application")
        main()  # Call the main function instead of trying to access root directly
        logger.info("Application closed normally")
    except Exception as e:
        logger.error(f"Fatal application error: {str(e)}")
        traceback.print_exc()