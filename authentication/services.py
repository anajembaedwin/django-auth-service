import secrets
import string
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import User
from django.utils import timezone 

class PasswordResetService:
    """
    Service class to handle password reset functionality
    using Redis for token storage and email notifications.
    """
    
    TOKEN_LENGTH = 32
    TOKEN_EXPIRY_SECONDS = 600  # 10 minutes
    
    @classmethod
    def generate_reset_token(cls):
        """Generate a secure random token for password reset."""
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(cls.TOKEN_LENGTH))
        return token
    
    @classmethod
    def create_password_reset_token(cls, email):
        """
        Create a password reset token and store it in Redis.
        Returns the token if successful, None otherwise.
        """
        try:
            # Check if user exists
            user = User.objects.get(email=email)
            
            # Generate unique token
            token = cls.generate_reset_token()
            
            # Store token in Redis with expiry
            cache_key = f"password_reset_token:{token}"
            cache.set(
                cache_key,
                {
                    'email': email,
                    'user_id': user.id,
                    'created_at': str(timezone.now())
                },
                timeout=cls.TOKEN_EXPIRY_SECONDS
            )
            
            # Send reset email (in production, you'd implement actual email sending)
            cls.send_reset_email(email, token, user.full_name)
            
            return token
            
        except User.DoesNotExist:
            return None
    
    @classmethod
    def validate_reset_token(cls, token):
        """
        Validate a password reset token.
        Returns user email if valid, None otherwise.
        """
        cache_key = f"password_reset_token:{token}"
        token_data = cache.get(cache_key)
        
        if token_data:
            return token_data.get('email')
        return None
    
    @classmethod
    def reset_password(cls, token, new_password):
        """
        Reset user password using the provided token.
        Returns True if successful, False otherwise.
        """
        cache_key = f"password_reset_token:{token}"
        token_data = cache.get(cache_key)
        
        if not token_data:
            return False
        
        try:
            # Get user and update password
            user = User.objects.get(email=token_data['email'])
            user.set_password(new_password)
            user.save()
            
            # Remove token from cache (one-time use)
            cache.delete(cache_key)
            
            return True
            
        except User.DoesNotExist:
            return False
    
    @classmethod
    def send_reset_email(cls, email, token, full_name):
        """
        Send password reset email to user.
        In production, this would use a proper email service.
        """
        # For development, we'll just print the token
        # In production, you'd send an actual email with the reset link
        print(f"\n=== PASSWORD RESET EMAIL ===")
        print(f"To: {email}")
        print(f"Name: {full_name}")
        print(f"Reset Token: {token}")
        print(f"Reset Link: http://localhost:8000/api/v1/auth/reset-password/?token={token}")
        print("============================\n")
        
        # Uncomment below for actual email sending in production
        # subject = "Password Reset Request"
        # message = f"Use this token to reset your password: {token}"
        # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

class TokenService:
    """
    Service class for JWT token management.
    Handles token generation and validation.
    """
    
    @staticmethod
    def get_tokens_for_user(user):
        """Generate JWT tokens for authenticated user."""
        from rest_framework_simplejwt.tokens import RefreshToken
        
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'access_token_lifetime': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
            'refresh_token_lifetime': settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
        }