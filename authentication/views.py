from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserProfileSerializer
)
from .services import PasswordResetService, TokenService
from .decorators import rate_limit

# Swagger response examples
user_response_example = {
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "full_name": "John Doe",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access_token_lifetime": 3600,
        "refresh_token_lifetime": 604800
    }
}

error_response_example = {
    "message": "Registration failed",
    "errors": {
        "email": ["This field is required."],
        "password": ["This field is required."]
    }
}

@swagger_auto_schema(
    method='post',
    operation_summary="Register a new user",
    operation_description="""
    Create a new user account with email, full name, and password.
    
    ## Requirements:
    - Valid email address (will be used for login)
    - Full name (at least 2 characters)
    - Strong password (min 8 chars, not too common)
    - Password confirmation must match
    
    ## Rate Limiting:
    - 3 attempts per 10 minutes per IP address
    
    ## Returns:
    - User profile information
    - JWT access and refresh tokens for immediate login
    """,
    request_body=UserRegistrationSerializer,
    responses={
        201: openapi.Response(
            description="User registered successfully",
            examples={
                "application/json": user_response_example
            }
        ),
        400: openapi.Response(
            description="Registration failed - validation errors",
            examples={
                "application/json": error_response_example
            }
        )
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
@rate_limit(max_requests=3, time_window=600)  # 3 attempts per 10 minutes
def register_user(request):
    """
    User Registration Endpoint
    
    Accepts: POST /api/v1/auth/register/
    Body: {
        "email": "user@example.com",
        "full_name": "John Doe",
        "password": "securepassword123",
        "password_confirm": "securepassword123"
    }
    
    Returns: User profile data and JWT tokens
    """
    
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        # Create new user
        user = serializer.save()
        
        # Generate JWT tokens
        tokens = TokenService.get_tokens_for_user(user)
        
        # Prepare user profile data
        user_profile = UserProfileSerializer(user).data
        
        return Response({
            'message': 'User registered successfully',
            'user': user_profile,
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'message': 'Registration failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="User login",
    operation_description="""
    Authenticate user with email and password.
    
    ## Authentication:
    - Use email address as username
    - Account must be active
    
    ## Rate Limiting:
    - 5 attempts per 5 minutes per IP address
    
    ## Returns:
    - User profile information
    - JWT access and refresh tokens
    - Token lifetime information
    """,
    request_body=UserLoginSerializer,
    responses={
        200: openapi.Response(
            description="Login successful",
            examples={
                "application/json": user_response_example
            }
        ),
        400: openapi.Response(
            description="Login failed - invalid credentials",
            examples={
                "application/json": {
                    "message": "Login failed",
                    "errors": {
                        "non_field_errors": ["Invalid email or password."]
                    }
                }
            }
        )
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
@rate_limit(max_requests=5, time_window=300)  # 5 attempts per 5 minutes
def login_user(request):
    """
    User Login Endpoint
    
    Accepts: POST /api/v1/auth/login/
    Body: {
        "email": "user@example.com",
        "password": "securepassword123"
    }
    
    Returns: User profile data and JWT tokens
    """
    
    serializer = UserLoginSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        tokens = TokenService.get_tokens_for_user(user)
        
        # Prepare user profile data
        user_profile = UserProfileSerializer(user).data
        
        # Update last login
        user.last_login = timezone.now()
        user.save()
        
        return Response({
            'message': 'Login successful',
            'user': user_profile,
            'tokens': tokens
        }, status=status.HTTP_200_OK)
    
    return Response({
        'message': 'Login failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="Request password reset",
    operation_description="""
    Request a password reset token for the given email address.
    
    ## Process:
    1. Validates email exists in system
    2. Generates secure reset token
    3. Stores token in Redis with 10-minute expiry
    4. Sends token via email (in development, printed to console)
    
    ## Rate Limiting:
    - 3 attempts per 10 minutes per IP address
    
    ## Security:
    - Tokens expire after 10 minutes
    - One-time use only
    - Secure random generation
    """,
    request_body=PasswordResetRequestSerializer,
    responses={
        200: openapi.Response(
            description="Reset token sent successfully",
            examples={
                "application/json": {
                    "message": "Password reset token sent to your email",
                    "email": "user@example.com",
                    "token": "AbCd1234EfGh5678IjKl9012MnOp3456"
                }
            }
        ),
        400: openapi.Response(
            description="Invalid email address",
            examples={
                "application/json": {
                    "message": "Invalid email address",
                    "errors": {
                        "email": ["No user found with this email address."]
                    }
                }
            }
        )
    },
    tags=['Password Reset']
)
@api_view(['POST'])
@permission_classes([AllowAny])
@rate_limit(max_requests=3, time_window=600)  # 3 attempts per 10 minutes
def request_password_reset(request):
    """
    Password Reset Request Endpoint
    
    Accepts: POST /api/v1/auth/forgot-password/
    Body: {
        "email": "user@example.com"
    }
    
    Returns: Success message and sends reset token to email
    """
    
    serializer = PasswordResetRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        # Generate and send reset token
        token = PasswordResetService.create_password_reset_token(email)
        
        if token:
            return Response({
                'message': 'Password reset token sent to your email',
                'email': email,
                'token': token  # Remove this in production for security
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Failed to generate reset token',
                'errors': {'email': ['User not found']}
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'message': 'Invalid email address',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="Reset password with token",
    operation_description="""
    Reset user password using a valid reset token.
    
    ## Requirements:
    - Valid reset token (from forgot-password endpoint)
    - Strong new password
    - Password confirmation must match
    
    ## Process:
    1. Validates reset token from Redis
    2. Validates new password strength
    3. Updates user password
    4. Removes token from Redis (one-time use)
    
    ## Security:
    - Tokens are single-use only
    - Strong password validation enforced
    - Automatic token cleanup after use
    """,
    request_body=PasswordResetConfirmSerializer,
    responses={
        200: openapi.Response(
            description="Password reset successful",
            examples={
                "application/json": {
                    "message": "Password reset successful"
                }
            }
        ),
        400: openapi.Response(
            description="Reset failed - invalid token or data",
            examples={
                "application/json": {
                    "message": "Password reset failed",
                    "errors": {
                        "token": ["Invalid or expired token"]
                    }
                }
            }
        )
    },
    tags=['Password Reset']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """
    Password Reset Confirmation Endpoint
    
    Accepts: POST /api/v1/auth/reset-password/
    Body: {
        "token": "reset_token_from_email",
        "new_password": "newsecurepassword123",
        "new_password_confirm": "newsecurepassword123"
    }
    
    Returns: Success message
    """
    
    serializer = PasswordResetConfirmSerializer(data=request.data)
    
    if serializer.is_valid():
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        # Validate token and reset password
        if PasswordResetService.reset_password(token, new_password):
            return Response({
                'message': 'Password reset successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Password reset failed',
                'errors': {'token': ['Invalid or expired token']}
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'message': 'Invalid data provided',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    operation_summary="Get user profile",
    operation_description="""
    Retrieve authenticated user's profile information.
    
    ## Authentication Required:
    - Include JWT access token in Authorization header
    - Format: `Authorization: Bearer <access_token>`
    
    ## Returns:
    - User ID, email, full name
    - Account creation and last update timestamps
    """,
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="JWT access token",
            type=openapi.TYPE_STRING,
            required=True,
            format="Bearer <token>"
        )
    ],
    responses={
        200: openapi.Response(
            description="Profile retrieved successfully",
            examples={
                "application/json": {
                    "message": "User profile retrieved successfully",
                    "user": {
                        "id": 1,
                        "email": "user@example.com",
                        "full_name": "John Doe",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        ),
        401: openapi.Response(
            description="Authentication required",
            examples={
                "application/json": {
                    "detail": "Given token not valid for any token type"
                }
            }
        )
    },
    tags=['User Profile']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Get User Profile Endpoint
    
    Accepts: GET /api/v1/auth/profile/
    Headers: Authorization: Bearer <access_token>
    
    Returns: User profile data
    """
    
    user_profile = UserProfileSerializer(request.user).data
    
    return Response({
        'message': 'User profile retrieved successfully',
        'user': user_profile
    }, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='post',
    operation_summary="User logout",
    operation_description="""
    Logout user by blacklisting their refresh token.
    
    ## Authentication Required:
    - Include JWT access token in Authorization header
    - Include refresh token in request body
    
    ## Process:
    1. Validates refresh token
    2. Adds token to blacklist
    3. Prevents token reuse
    
    ## Security:
    - Invalidates refresh token immediately
    - Access token remains valid until expiry
    - Recommended to clear tokens from client storage
    """,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['refresh_token'],
        properties={
            'refresh_token': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='JWT refresh token to blacklist'
            )
        }
    ),
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="JWT access token",
            type=openapi.TYPE_STRING,
            required=True,
            format="Bearer <token>"
        )
    ],
    responses={
        200: openapi.Response(
            description="Logout successful",
            examples={
                "application/json": {
                    "message": "Logout successful"
                }
            }
        ),
        400: openapi.Response(
            description="Invalid refresh token",
            examples={
                "application/json": {
                    "message": "Logout failed",
                    "errors": {
                        "refresh_token": ["Invalid token"]
                    }
                }
            }
        ),
        401: openapi.Response(
            description="Authentication required"
        )
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    User Logout Endpoint
    
    Accepts: POST /api/v1/auth/logout/
    Headers: Authorization: Bearer <access_token>
    Body: {
        "refresh_token": "refresh_token_to_blacklist"
    }
    
    Returns: Success message
    """
    
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'message': 'Logout failed',
            'errors': {'refresh_token': ['Invalid token']}
        }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    operation_summary="API health check",
    operation_description="""
    Check the health status of the authentication API.
    
    ## Returns:
    - API status (healthy/unhealthy)
    - Database connectivity status
    - Total number of registered users
    - Current timestamp
    
    ## Use Cases:
    - Deployment verification
    - Load balancer health checks
    - Monitoring and alerting
    """,
    responses={
        200: openapi.Response(
            description="API is healthy",
            examples={
                "application/json": {
                    "status": "healthy",
                    "message": "Authentication API is running successfully",
                    "database": "connected",
                    "total_users": 25,
                    "timestamp": "2024-01-15T10:30:00Z"
                }
            }
        ),
        500: openapi.Response(
            description="API is unhealthy",
            examples={
                "application/json": {
                    "status": "unhealthy",
                    "message": "Database connection failed",
                    "error": "Connection refused",
                    "timestamp": "2024-01-15T10:30:00Z"
                }
            }
        )
    },
    tags=['Health Check']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def api_health_check(request):
    """
    API Health Check Endpoint
    
    Accepts: GET /api/v1/auth/health/
    
    Returns: API status and database connectivity
    """
    
    try:
        # Test database connectivity
        user_count = User.objects.count()
        
        return Response({
            'status': 'healthy',
            'message': 'Authentication API is running successfully',
            'database': 'connected',
            'total_users': user_count,
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'message': 'Database connection failed',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)