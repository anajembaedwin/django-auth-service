from django.http import JsonResponse
from django.core.cache import cache
from django.utils import timezone
import json

class RateLimitMiddleware:
    """
    Custom middleware for API rate limiting.
    Implements sliding window rate limiting using Redis.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check rate limit before processing request
        if self.is_rate_limited(request):
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.',
                'retry_after': 60  # seconds
            }, status=429)
        
        response = self.get_response(request)
        return response
    
    def is_rate_limited(self, request):
        """Check if the request should be rate limited."""
        
        # Get client IP address
        client_ip = self.get_client_ip(request)
        
        # Define rate limits for different endpoints
        rate_limits = {
            '/api/v1/auth/login/': {'limit': 5, 'window': 300},  # 5 attempts per 5 minutes
            '/api/v1/auth/register/': {'limit': 3, 'window': 600},  # 3 attempts per 10 minutes
            '/api/v1/auth/forgot-password/': {'limit': 3, 'window': 600},  # 3 attempts per 10 minutes
            '/api/v1/auth/reset-password/': {'limit': 5, 'window': 300},  # 5 attempts per 5 minutes
        }
        
        # Check if current path needs rate limiting
        for path, config in rate_limits.items():
            if request.path.startswith(path):
                return self.check_rate_limit(client_ip, path, config['limit'], config['window'])
        
        return False
    
    def check_rate_limit(self, client_ip, endpoint, limit, window):
        """Check rate limit for specific client and endpoint."""
        
        cache_key = f"rate_limit:{client_ip}:{endpoint}"
        current_time = timezone.now().timestamp()
        
        # Get existing requests from cache
        requests = cache.get(cache_key, [])
        
        # Remove old requests outside the window
        requests = [req_time for req_time in requests if current_time - req_time < window]
        
        # Check if limit is exceeded
        if len(requests) >= limit:
            return True
        
        # Add current request
        requests.append(current_time)
        
        # Update cache
        cache.set(cache_key, requests, timeout=window)
        
        return False
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR', '0.0.0.0')