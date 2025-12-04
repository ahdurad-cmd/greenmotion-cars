"""
Caching utilities and decorators
"""
from functools import wraps
from flask import request
from app import cache
import logging

logger = logging.getLogger(__name__)

def cache_key_prefix():
    """Generate cache key prefix based on current user"""
    # Include user-specific info if needed for personalized caching
    return f"view_{request.endpoint}_{request.args.to_dict()}"

def cached(timeout=300, key_prefix=None):
    """
    Caching decorator for view functions
    
    Args:
        timeout: Cache timeout in seconds (default: 300 = 5 minutes)
        key_prefix: Custom cache key prefix (default: auto-generated)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key
            if key_prefix:
                cache_key = f"{key_prefix}_{args}_{kwargs}"
            else:
                cache_key = cache_key_prefix()
            
            # Try to get from cache
            try:
                rv = cache.get(cache_key)
                if rv is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return rv
            except Exception as e:
                logger.warning(f"Cache get failed: {str(e)}")
            
            # Cache miss - execute function
            logger.debug(f"Cache miss: {cache_key}")
            rv = f(*args, **kwargs)
            
            # Store in cache
            try:
                cache.set(cache_key, rv, timeout=timeout)
            except Exception as e:
                logger.warning(f"Cache set failed: {str(e)}")
            
            return rv
        return decorated_function
    return decorator

def invalidate_cache(key_pattern=None):
    """
    Invalidate cache entries
    
    Args:
        key_pattern: Pattern to match cache keys (None = clear all)
    """
    try:
        if key_pattern:
            # For Redis backend, we could use pattern matching
            # For simple backend, just clear all
            cache.clear()
            logger.info(f"Cache cleared for pattern: {key_pattern}")
        else:
            cache.clear()
            logger.info("All cache cleared")
        return True
    except Exception as e:
        logger.error(f"Cache clear failed: {str(e)}")
        return False

def cache_stats():
    """Get cache statistics (if available)"""
    try:
        # This depends on the cache backend
        # For development, we might not have detailed stats
        return {
            'backend': cache.config.get('CACHE_TYPE', 'unknown'),
            'timeout': cache.config.get('CACHE_DEFAULT_TIMEOUT', 300)
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {str(e)}")
        return {}
