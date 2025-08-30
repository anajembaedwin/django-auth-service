from functools import wraps
from django.http import JsonResponse
from django.core.cache import cache
from django.utils import timezone

def rate_limit(max_requests=10, time_window=60):
    """
    Decorator for rate limiting API views.
    
    Args:
        max_requests (int): Maximum number of requests allowed
        time_window (int): Time window in seconds
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get client identifier
            client_ip = get_client_ip(request)
            cache_key = f"rate_limit:{view_func.__name__}:{client_ip}"
            
            # Get current request count
            current_requests = cache.get(cache_key, [])
            current_time = timezone.now().timestamp()
            
            # Remove old requests outside time window
            current_requests = [
                req_time for req_time in current_requests 
                if current_time - req_time < time_window
            ]
            
            # Check if limit exceeded
            if len(current_requests) >= max_requests:
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {max_requests} requests per {time_window} seconds',
                    'retry_after': time_window
                }, status=429)
            
            # Add current request
            current_requests.append(current_time)
            cache.set(cache_key, current_requests, timeout=time_window)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR', '0.0.0.0')