# Django Auth Service - API Documentation

## Interactive Documentation

### Swagger UI (Recommended)
- **Local Development**: `http://localhost:8000/swagger/`
- **Production**: `https://your-app.render.com/swagger/`

### ReDoc Alternative
- **Local Development**: `http://localhost:8000/redoc/`
- **Production**: `https://your-app.render.com/redoc/`

## Quick Start with Swagger

1. **Access Swagger UI**: Navigate to the Swagger URL above
2. **Try Authentication**: Use the "Try it out" feature on registration/login endpoints
3. **Test Protected Endpoints**: 
   - First register/login to get a JWT token
   - Click "Authorize" button in Swagger UI
   - Enter: `Bearer <your_access_token>`
   - Now you can test protected endpoints

## Authentication Flow

### Step 1: Register or Login
```bash
# Register new user
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "full_name": "John Doe",
    "password": "SecurePassword123",
    "password_confirm": "SecurePassword123"
  }'
```

### Step 2: Use JWT Tokens
```bash
# Access protected endpoints
curl -X GET http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer <access_token_from_step_1>"
```

## API Endpoints Summary

| Method | Endpoint | Description | Auth | Rate Limit |
|--------|----------|-------------|------|------------|
| `POST` | `/register/` | User registration | ❌ | 3/10min |
| `POST` | `/login/` | User login | ❌ | 5/5min |
| `POST` | `/logout/` | User logout | ✅ | - |
| `GET` | `/profile/` | Get user profile | ✅ | - |
| `POST` | `/forgot-password/` | Request password reset | ❌ | 3/10min |
| `POST` | `/reset-password/` | Reset password with token | ❌ | 5/5min |
| `GET` | `/health/` | API health check | ❌ | - |

## Security Features

### Rate Limiting
- **Registration**: 3 attempts per 10 minutes per IP
- **Login**: 5 attempts per 5 minutes per IP  
- **Password Reset**: 3 requests per 10 minutes per IP
- **Reset Confirmation**: 5 attempts per 5 minutes per IP

### JWT Security
- **Access Token**: 60 minutes lifetime (configurable)
- **Refresh Token**: 7 days lifetime (configurable)
- **Token Rotation**: New refresh token on each use
- **Blacklisting**: Tokens invalidated on logout

### Password Security
- **Minimum Length**: 8 characters
- **Django Validators**: Common password checking
- **Secure Storage**: bcrypt hashing
- **Reset Tokens**: 10-minute expiry, single use

## Testing with Swagger UI

### 1. Test User Registration
1. Go to `/swagger/` 
2. Find "Authentication" section
3. Click on `POST /register/`
4. Click "Try it out"
5. Fill in the example data:
   ```json
   {
     "email": "test@example.com",
     "full_name": "Test User",
     "password": "TestPassword123",
     "password_confirm": "TestPassword123"
   }
   ```
6. Click "Execute"
7. Copy the `access` token from the response

### 2. Test Protected Endpoints
1. Click the "Authorize" button at the top
2. Enter: `Bearer <your_access_token>`
3. Click "Authorize"
4. Now try the `GET /profile/` endpoint

### 3. Test Password Reset Flow
1. Use `POST /forgot-password/` with your email
2. Check console logs for the reset token (in development)
3. Use the token in `POST /reset-password/`

## Frontend Integration

### JavaScript Example
```javascript
// Register user
const registerUser = async (userData) => {
  const response = await fetch('/api/v1/auth/register/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData)
  });
  
  if (response.ok) {
    const data = await response.json();
    // Store tokens in secure storage
    localStorage.setItem('access_token', data.tokens.access);
    localStorage.setItem('refresh_token', data.tokens.refresh);
    return data.user;
  }
  
  throw new Error('Registration failed');
};

// Make authenticated requests
const fetchProfile = async () => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('/api/v1/auth/profile/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (response.ok) {
    return await response.json();
  }
  
  throw new Error('Failed to fetch profile');
};
```

## Detailed API Reference

### 1. User Registration
**Endpoint**: `POST /api/v1/auth/register/`  
**Access**: Public  
**Rate Limit**: 3 attempts per 10 minutes

**Request Body**:
```json
{
    "email": "user@example.com",
    "full_name": "John Doe",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
}
```

**Success Response** (201):
```json
{
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
```

### 2. User Login
**Endpoint**: `POST /api/v1/auth/login/`  
**Access**: Public  
**Rate Limit**: 5 attempts per 5 minutes

**Request Body**:
```json
{
    "email": "user@example.com",
    "password": "securepassword123"
}
```

**Success Response** (200):
```json
{
    "message": "Login successful",
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
```

### 3. Request Password Reset
**Endpoint**: `POST /api/v1/auth/forgot-password/`  
**Access**: Public  
**Rate Limit**: 3 attempts per 10 minutes

**Request Body**:
```json
{
    "email": "user@example.com"
}
```

**Success Response** (200):
```json
{
    "message": "Password reset token sent to your email",
    "email": "user@example.com",
    "token": "AbCd1234EfGh5678IjKl9012MnOp3456"
}
```

### 4. Reset Password
**Endpoint**: `POST /api/v1/auth/reset-password/`  
**Access**: Public  
**Rate Limit**: 5 attempts per 5 minutes

**Request Body**:
```json
{
    "token": "AbCd1234EfGh5678IjKl9012MnOp3456",
    "new_password": "newsecurepassword456",
    "new_password_confirm": "newsecurepassword456"
}
```

**Success Response** (200):
```json
{
    "message": "Password reset successful"
}
```

### 5. Get User Profile
**Endpoint**: `GET /api/v1/auth/profile/`  
**Access**: Authenticated  
**Headers**: `Authorization: Bearer <access_token>`

**Success Response** (200):
```json
{
    "message": "User profile retrieved successfully",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "full_name": "John Doe",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }
}
```

### 6. User Logout
**Endpoint**: `POST /api/v1/auth/logout/`  
**Access**: Authenticated  
**Headers**: `Authorization: Bearer <access_token>`

**Request Body**:
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Success Response** (200):
```json
{
    "message": "Logout successful"
}
```

### 7. API Health Check
**Endpoint**: `GET /api/v1/auth/health/`  
**Access**: Public

**Success Response** (200):
```json
{
    "status": "healthy",
    "message": "Authentication API is running successfully",
    "database": "connected",
    "total_users": 25,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## Error Responses

### 400 Bad Request
```json
{
    "message": "Validation failed",
    "errors": {
        "email": ["This field is required."],
        "password": ["This field is required."]
    }
}
```

### 401 Unauthorized
```json
{
    "detail": "Given token not valid for any token type",
    "code": "token_not_valid",
    "messages": [
        {
            "token_class": "AccessToken",
            "token_type": "access",
            "message": "Token is invalid or expired"
        }
    ]
}
```

### 429 Rate Limited
```json
{
    "error": "Rate limit exceeded",
    "message": "Too many requests. Please try again later.",
    "retry_after": 60
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
    "status": "error",
    "message": "Internal server error occurred",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## Development Tools

### Swagger Specification
- **JSON Format**: `http://localhost:8000/swagger.json`
- **YAML Format**: `http://localhost:8000/swagger.yaml`

### Postman Collection
Generate a Postman collection from the OpenAPI spec:
1. Open Postman
2. Click Import > Link
3. Enter: `http://localhost:8000/swagger.json`
4. Import as Collection

## Common Issues & Solutions

### Authentication Issues
```json
{
  "detail": "Given token not valid for any token type"
}
```
**Solution**: Check token format is `Bearer <token>` with space after Bearer

### Rate Limiting
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```
**Solution**: Wait for the retry_after seconds or use different IP

### Password Reset
**Issue**: Not receiving reset emails  
**Solution**: In development, check console logs for the reset token

### CORS Issues
**Issue**: Browser blocking requests from frontend  
**Solution**: Add your frontend URL to `CORS_ALLOWED_ORIGINS` in settings

## Support

- **Swagger UI Issues**: Check browser console for JavaScript errors
- **API Questions**: Test endpoints in Swagger UI first
- **Authentication Problems**: Verify JWT token format and expiry
- **Rate Limiting**: Check IP address and wait for rate limit reset