from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI Schema Configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Django Auth Service API",
        default_version='v1.0.0',
        description="""
        A comprehensive authentication service built with Django REST Framework.
        
        ## Features
        - User registration and authentication
        - JWT token-based security
        - Password reset functionality with Redis
        - Rate limiting for security
        - PostgreSQL database integration
        
        ## Authentication
        This API uses JWT (JSON Web Token) authentication. To access protected endpoints:
        1. Obtain tokens by registering or logging in
        2. Include the access token in the Authorization header: `Bearer <access_token>`
        
        ## Rate Limiting
        - Login: 5 attempts per 5 minutes
        - Registration: 3 attempts per 10 minutes  
        - Password Reset: 3 attempts per 10 minutes
        """,
        terms_of_service="https://www.billstation.com/terms/",
        contact=openapi.Contact(email="support@billstation.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[]
)

def health_check(request):
    """Health check endpoint for deployment verification"""
    return JsonResponse({
        'status': 'healthy',
        'message': 'Django Auth Service is running successfully'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('authentication.urls')),
    path('health/', health_check, name='health_check'),
    
    # Swagger/OpenAPI Documentation URLs
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='api-docs-home'),
]