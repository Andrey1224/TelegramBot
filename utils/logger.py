# This file handles logging configuration and retry decorators
# it defines logger setup and telegram_retry decorator

import sys
import os
from datetime import datetime
from loguru import logger
import functools
import asyncio
from telegram.error import NetworkError, TimedOut, RetryAfter

# Context: this function is used within the application to setup logging
# with file rotation and proper formatting
def setup_logging():
    """Setup logging configuration with file rotation"""
    # Remove default handler
    logger.remove()
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Generate timestamp for log filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pid = os.getpid()
    log_filename = f"logs/bot_{timestamp}_{pid}.log"
    
    # Console handler with colors
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # File handler with rotation
    logger.add(
        log_filename,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    logger.info("Logging setup complete. Log file: %s", log_filename)

# Context: this decorator is used within the application to add retry logic
# for Telegram API calls that may fail due to network issues
def telegram_retry(max_retries=3, base_delay=1.0, max_delay=60.0, total_timeout=300.0):
    """Decorator to add retry logic for Telegram API calls"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            import time
            from telegram.error import Forbidden
            
            start_time = time.time()
            last_exception = None
            
            for attempt in range(max_retries):
                # Check total timeout
                if time.time() - start_time > total_timeout:
                    logger.error("Total timeout exceeded for %s after %s seconds", 
                               func.__name__, total_timeout)
                    break
                
                try:
                    return await func(*args, **kwargs)
                except Forbidden as e:
                    # User blocked the bot - log and skip retry
                    logger.warning("User blocked bot in %s: %s - skipping retries", 
                                 func.__name__, str(e))
                    raise  # Don't retry Forbidden errors
                except RetryAfter as e:
                    # Telegram rate limiting - wait the specified time
                    retry_after = e.retry_after
                    if isinstance(retry_after, (int, float)):
                        wait_time = min(float(retry_after), max_delay)
                    else:
                        wait_time = min(60.0, max_delay)  # Default fallback
                    
                    # Check if waiting would exceed total timeout
                    if time.time() - start_time + wait_time > total_timeout:
                        logger.error("Would exceed total timeout waiting for rate limit in %s", 
                                   func.__name__)
                        break
                    
                    logger.warning("Rate limited by Telegram, waiting %s seconds (attempt %d/%d)", 
                                 wait_time, attempt + 1, max_retries)
                    await asyncio.sleep(wait_time)
                    last_exception = e
                except (NetworkError, TimedOut) as e:
                    # Network issues - exponential backoff
                    if attempt == max_retries - 1:
                        break
                    
                    wait_time = min(base_delay * (2 ** attempt), max_delay)
                    
                    # Check if waiting would exceed total timeout
                    if time.time() - start_time + wait_time > total_timeout:
                        logger.error("Would exceed total timeout waiting for network retry in %s", 
                                   func.__name__)
                        break
                    
                    logger.warning("Network error: %s, retrying in %s seconds (attempt %d/%d)", 
                                 str(e), wait_time, attempt + 1, max_retries)
                    await asyncio.sleep(wait_time)
                    last_exception = e
                except Exception as e:
                    # Other exceptions - don't retry
                    logger.error("Non-retryable error in %s: %s", func.__name__, str(e))
                    raise
            
            # All retries exhausted
            elapsed = time.time() - start_time
            if last_exception:
                logger.error("All retries exhausted for %s after %s seconds, last error: %s", 
                           func.__name__, elapsed, str(last_exception))
                raise last_exception
            else:
                logger.error("All retries exhausted for %s after %s seconds with no recorded exception", 
                           func.__name__, elapsed)
                raise RuntimeError(f"All retries exhausted for {func.__name__}")
        
        return wrapper
    return decorator

# Context: this function is used within the application to parse and validate
# user input amounts with support for various formats (spaces, commas, etc.)
def parse_amount(amount_str: str) -> tuple[int, str]:
    """
    Parse amount string and return (amount, error_message)
    Returns (0, error_message) if parsing fails
    """
    if not amount_str:
        return 0, "Сума не може бути порожньою"
    
    # Remove common formatting
    cleaned = amount_str.strip()
    
    # Remove emojis and special characters (keep only digits, spaces, commas, dots)
    import re
    cleaned = re.sub(r'[^\d\s,.-]', '', cleaned)
    
    # Handle common formats
    # "12 345,67" -> "12345.67"
    # "12,345.67" -> "12345.67"  
    # "12 345" -> "12345"
    # "12.345" (European style) -> "12345"
    
    if ',' in cleaned and '.' in cleaned:
        # Both comma and dot - determine which is decimal separator
        comma_pos = cleaned.rfind(',')
        dot_pos = cleaned.rfind('.')
        
        if comma_pos > dot_pos:
            # Comma is decimal separator: "1.234,56"
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            # Dot is decimal separator: "1,234.56"
            cleaned = cleaned.replace(',', '')
    elif ',' in cleaned:
        # Only comma - could be thousands separator or decimal
        parts = cleaned.split(',')
        if len(parts) == 2 and len(parts[1]) <= 2:
            # Likely decimal separator: "1234,56"
            cleaned = cleaned.replace(',', '.')
        else:
            # Likely thousands separator: "1,234,567"
            cleaned = cleaned.replace(',', '')
    
    # Remove spaces (thousands separator)
    cleaned = cleaned.replace(' ', '')
    
    if not cleaned:
        return 0, "Некоректний формат суми"
    
    try:
        # Try to parse as float first
        amount_float = float(cleaned)
        
        if amount_float < 0:
            return 0, "Сума не може бути від'ємною"
        
        if amount_float > 1_000_000_000:  # 1 billion limit
            return 0, "Сума занадто велика (максимум 1 млрд)"
        
        # Convert to integer (assuming amounts are in base currency units)
        amount_int = int(round(amount_float))
        
        return amount_int, ""
        
    except ValueError:
        return 0, f"Некоректний формат суми: '{amount_str}'"

# Initialize logging
setup_logging()