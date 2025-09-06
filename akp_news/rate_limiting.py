"""
Rate limiting utilities for AKP News application
"""
import hashlib
import logging
from functools import wraps
from typing import Optional

from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Rate limiting implementation using Django cache
    """
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60, key_prefix: str = 'rate_limit'):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.key_prefix = key_prefix
    
    def get_client_ip(self, request) -> str:
        """
        Get client IP address from request
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip
    
    def get_cache_key(self, identifier: str) -> str:
        """
        Generate cache key for rate limiting
        """
        key_hash = hashlib.md5(identifier.encode()).hexdigest()
        return f"{self.key_prefix}:{key_hash}"
    
    def is_rate_limited(self, request, identifier: Optional[str] = None) -> tuple[bool, dict]:
        """
        Check if request should be rate limited
        
        Returns:
            tuple: (is_limited, info_dict)
        """
        if identifier is None:
            identifier = self.get_client_ip(request)
        
        cache_key = self.get_cache_key(identifier)
        
        # Get current request count and timestamp
        cache_data = cache.get(cache_key, {'count': 0, 'reset_time': timezone.now()})
        
        current_time = timezone.now()
        reset_time = cache_data['reset_time']
        
        # Reset counter if window has passed
        if (current_time - reset_time).total_seconds() >= self.window_seconds:
            cache_data = {'count': 1, 'reset_time': current_time}
            cache.set(cache_key, cache_data, self.window_seconds)
            
            return False, {
                'requests_remaining': self.max_requests - 1,
                'reset_time': current_time.isoformat(),
                'window_seconds': self.window_seconds
            }
        
        # Increment counter
        cache_data['count'] += 1
        
        # Check if limit exceeded
        if cache_data['count'] > self.max_requests:
            # Update cache with current count
            cache.set(cache_key, cache_data, self.window_seconds)
            
            remaining_time = self.window_seconds - (current_time - reset_time).total_seconds()
            
            logger.warning(
                f"Rate limit exceeded for {identifier}. "
                f"Count: {cache_data['count']}/{self.max_requests}. "
                f"Reset in: {remaining_time:.0f}s"
            )
            
            return True, {
                'requests_remaining': 0,
                'reset_time': reset_time.isoformat(),
                'window_seconds': self.window_seconds,
                'retry_after': max(1, int(remaining_time))
            }
        
        # Update cache with new count
        cache.set(cache_key, cache_data, self.window_seconds)
        
        return False, {
            'requests_remaining': self.max_requests - cache_data['count'],
            'reset_time': reset_time.isoformat(),
            'window_seconds': self.window_seconds
        }

# Predefined rate limiters for different use cases
search_rate_limiter = RateLimiter(max_requests=30, window_seconds=60, key_prefix='search_limit')
api_rate_limiter = RateLimiter(max_requests=100, window_seconds=60, key_prefix='api_limit')
strict_rate_limiter = RateLimiter(max_requests=10, window_seconds=60, key_prefix='strict_limit')

def rate_limit(limiter: RateLimiter = api_rate_limiter, identifier_func=None):
    """
    Decorator for rate limiting views
    
    Args:
        limiter: RateLimiter instance to use
        identifier_func: Optional function to generate custom identifier
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Generate identifier
            if identifier_func:
                identifier = identifier_func(request)
            else:
                identifier = limiter.get_client_ip(request)
            
            # Check rate limit
            is_limited, info = limiter.is_rate_limited(request, identifier)
            
            if is_limited:
                response_data = {
                    'error': 'Rate limit exceeded',
                    'message': 'Too many requests. Please try again later.',
                    'retry_after': info.get('retry_after', 60)
                }
                
                response = JsonResponse(response_data, status=429)
                response['Retry-After'] = str(info.get('retry_after', 60))
                response['X-RateLimit-Limit'] = str(limiter.max_requests)
                response['X-RateLimit-Remaining'] = '0'
                response['X-RateLimit-Reset'] = info.get('reset_time', '')
                
                return response
            
            # Add rate limit headers to successful responses
            response = view_func(request, *args, **kwargs)
            
            if hasattr(response, '__setitem__'):  # Check if response supports headers
                response['X-RateLimit-Limit'] = str(limiter.max_requests)
                response['X-RateLimit-Remaining'] = str(info.get('requests_remaining', 0))
                response['X-RateLimit-Reset'] = info.get('reset_time', '')
            
            return response
        
        return wrapper
    return decorator

# Convenience decorators
search_rate_limit = lambda f: rate_limit(search_rate_limiter)(f)
api_rate_limit = lambda f: rate_limit(api_rate_limiter)(f)
strict_rate_limit = lambda f: rate_limit(strict_rate_limiter)(f)
