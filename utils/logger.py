# This file handles logging configuration
# it defines logger setup with file rotation and formatting

import os
from loguru import logger

# Context: this function is used within the application to configure logging
# with file rotation and proper formatting
def setup_logger():
    """Setup loguru logger with file rotation"""
    # Remove default handler
    logger.remove()
    
    # Add console handler with colors
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Add file handler with rotation
    logger.add(
        "logs/bot_{time}.log",
        rotation="10 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )

# Initialize logger
setup_logger()