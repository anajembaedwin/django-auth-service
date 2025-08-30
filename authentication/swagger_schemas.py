from drf_yasg import openapi

# Common response schemas
success_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
    }
)

error_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
        'errors': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='Field-specific validation errors',
            additional_properties=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING)
            )
        )
    }
)

# User profile schema
user_profile_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
        'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email address'),
        'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='User full name'),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='datetime', description='Account creation timestamp'),
        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format='datetime', description='Last profile update timestamp'),
    }
)

# JWT tokens schema
jwt_tokens_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'access': openapi.Schema(type=openapi.TYPE_STRING, description='JWT access token'),
        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='JWT refresh token'),
        'access_token_lifetime': openapi.Schema(type=openapi.TYPE_INTEGER, description='Access token lifetime in seconds'),
        'refresh_token_lifetime': openapi.Schema(type=openapi.TYPE_INTEGER, description='Refresh token lifetime in seconds'),
    }
)

# Authentication response schema
auth_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
        'user': user_profile_schema,
        'tokens': jwt_tokens_schema,
    }
)

# Health check response schema
health_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['healthy', 'unhealthy'], description='API health status'),
        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Health check message'),
        'database': openapi.Schema(type=openapi.TYPE_STRING, description='Database connection status'),
        'total_users': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total registered users count'),
        'timestamp': openapi.Schema(type=openapi.TYPE_STRING, format='datetime', description='Health check timestamp'),
    }
)

# Password reset request response schema
password_reset_request_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
        'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='Email address'),
        'token': openapi.Schema(type=openapi.TYPE_STRING, description='Reset token (remove in production)'),
    }
)

# Common request body schemas
logout_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['refresh_token'],
    properties={
        'refresh_token': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='JWT refresh token to blacklist',
            example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
        )
    }
)

# Manual parameters
auth_header_parameter = openapi.Parameter(
    'Authorization',
    openapi.IN_HEADER,
    description="JWT access token in format: Bearer <token>",
    type=openapi.TYPE_STRING,
    required=True,
    example="Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
)

# Security requirement for authenticated endpoints
security_requirement = [{'Bearer': []}]