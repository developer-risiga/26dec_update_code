# src/utils/production_error_handler.py
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)

class ProductionErrorHandler:
    def __init__(self):
        self.error_count = 0
        self.max_errors = 100
    
    def retry_on_failure(self, max_retries=3, delay=1):
        """Retry decorator for production"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_retries - 1:
                            logger.error(f"❌ All retries failed for {func.__name__}: {e}")
                            raise
                        logger.warning(f"🔄 Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}")
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                return None
            return wrapper
        return decorator
    
    def graceful_fallback(self, fallback_value=None):
        """Graceful fallback decorator"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"⚠️ {func.__name__} failed, using fallback: {e}")
                    return fallback_value
            return wrapper
        return decorator

# Global error handler
production_error_handler = ProductionErrorHandler()