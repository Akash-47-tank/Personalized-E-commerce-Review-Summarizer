from loguru import logger
import sys
import os
from datetime import datetime

class Logger:
    @staticmethod
    def setup_logger():
        """Set up logger configuration with rotation and formatting."""
        try:
            # Create logs directory if it doesn't exist
            if not os.path.exists("logs"):
                os.makedirs("logs")

            # Generate log filename with timestamp
            log_filename = f"logs/app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

            # Remove any existing logger configurations
            logger.remove()

            # Add console output
            logger.add(
                sys.stdout,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                level="INFO"
            )

            # Add file output with rotation
            logger.add(
                log_filename,
                rotation="500 MB",  # Create new file after 500MB
                retention="10 days",  # Keep logs for 10 days
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                level="DEBUG"
            )

            logger.info("Logger initialized successfully")
            return logger

        except Exception as e:
            print(f"Error setting up logger: {str(e)}")
            raise

# Initialize logger
app_logger = Logger.setup_logger()
