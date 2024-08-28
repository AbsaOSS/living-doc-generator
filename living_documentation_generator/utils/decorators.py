import logging

from typing import Callable, Optional, Any
from functools import wraps

from living_documentation_generator.utils.github_rate_limiter import GithubRateLimiter

logger = logging.getLogger(__name__)


def debug_log_decorator(method: Callable) -> Callable:
    """
    Decorator to add debug logging for a method call.
    """
    @wraps(method)
    def wrapped(*args, **kwargs) -> Optional[Any]:
        logger.debug("Calling method %s with args: %s and kwargs: %s.", method.__name__, args, kwargs)
        result = method(*args, **kwargs)
        logger.debug("Method %s returned %s.", method.__name__, result)
        return result
    return wrapped


def safe_call_decorator(rate_limiter: GithubRateLimiter):
    """
    Decorator factory to create a rate-limited safe call function.
    """
    def decorator(method: Callable) -> Callable:
        # Note: Keep log decorator first to log correct method name.
        @debug_log_decorator
        @wraps(method)
        @rate_limiter
        def wrapped(*args, **kwargs) -> Optional[Any]:
            try:
                return method(*args, **kwargs)
            except (ValueError, TypeError) as e:
                logger.error("Error calling %s: %s", method.__name__, e, exc_info=True)
                return None
        return wrapped
    return decorator
