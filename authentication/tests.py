from django.test import TestCase
from django.contrib.auth import authenticate
from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import User
from .services import PasswordResetService, TokenService
import json

class UserModelTest(TestCase):
    """Test cases for the custom User model."""
    
    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'email': 'testuser@example.com',
            'full_name': 'Test User',
            'password': 'testpassword123'
        }
    
    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.full_name, self.user_data['full_name'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            full_name='Admin User',
            password='adminpassword123'
        )
        
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
    
    def test_user_string_representation(self):
        """Test the string representation of user."""
        user = User.objects.create_user(**self.user_data)
        expected_str = f"{self.user_data['full_name']} ({self.user_data['email']})"
        self.assertEqual(str(user), expected_str)
    
    def test_user_authentication_with_email(self):
        """Test that users can authenticate with email instead of username."""
        user = User.objects.create_user(**self.user_data)
        authenticated_user = authenticate(
            username=self.user_data['email'],
            password=self.user_data['password']
        )
        self.assertEqual(authenticated_user, user)

class PasswordResetServiceTest(TestCase):
    """Test cases for the PasswordResetService."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='testuser@example.com',
            full_name='Test User',
            password='testpassword123'
        )
        # Clear cache before each test
        cache.clear()
    
    def test_generate_reset_token(self):
        """Test reset token generation."""
        token = PasswordResetService.generate_reset_token()
        self.assertEqual(len(token), 32)
        self.assertTrue(token.isalnum())
    
    def test_create_password_reset_token(self):
        """Test creating a password reset token."""
        token = PasswordResetService.create_password_reset_token(self.user.email)
        self.assertIsNotNone(token)
        self.assertEqual(len(token), 32)
    
    def test_validate_reset_token(self):
        """Test validating a reset token."""
        token = PasswordResetService.create_password_reset_token(self.user.email)
        validated_email = PasswordResetService.validate_reset_token(token)
        self.assertEqual(validated_email, self.user.email)
    
    def test_validate_invalid_token(self):
        """Test validating an invalid token."""
        invalid_token = "invalid_token_12345"
        validated_email = PasswordResetService.validate_reset_token(invalid_token)
        self.assertIsNone(validated_email)
    
    def test_reset_password_success(self):
        """Test successful password reset."""
        token = PasswordResetService.create_password_reset_token(self.user.email)
        new_password = "newpassword456"
        
        result = PasswordResetService.reset_password(token, new_password)
        self.assertTrue(result)
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
    
    def test_reset_password_invalid_token(self):
        """Test password reset with invalid token."""
        result = PasswordResetService.reset_password("invalid_token", "newpassword")
        self.assertFalse(result)

class TokenServiceTest(TestCase):
    """Test cases for the TokenService."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='testuser@example.com',
            full_name='Test User',
            password='testpassword123'
        )
    
    def test_get_tokens_for_user(self):
        """Test JWT token generation for user."""
        tokens = TokenService.get_tokens_for_user(self.user)
        
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        self.assertIn('access_token_lifetime', tokens)
        self.assertIn('refresh_token_lifetime', tokens)
        
        # Verify tokens are strings
        self.assertIsInstance(tokens['access'], str)
        self.assertIsInstance(tokens['refresh'], str)

class AuthenticationAPITest(APITestCase):
    """Test cases for authentication API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.register_url = reverse('authentication:register')
        self.login_url = reverse('authentication:login')
        self.logout_url = reverse('authentication:logout')
        self.profile_url = reverse('authentication:profile')
        self.forgot_password_url = reverse('authentication:forgot_password')
        self.reset_password_url = reverse('authentication:reset_password')
        self.health_url = reverse('authentication:health_check')
        
        self.user_data = {
            'email': 'testuser@example.com',
            'full_name': 'Test User',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123'
        }
        
        # Clear cache before each test
        cache.clear()
    
    def test_user_registration_success(self):
        """Test successful user registration."""
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['email'], self.user_data['email'])
    
    def test_user_registration_invalid_data(self):
        """Test user registration with invalid data."""
        invalid_data = {
            'email': 'invalid-email',
            'full_name': '',
            'password': '123',
            'password_confirm': '456'
        }
        
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)
    
    def test_user_login_success(self):
        """Test successful user login."""
        # First register a user
        User.objects.create_user(
            email=self.user_data['email'],
            full_name=self.user_data['full_name'],
            password=self.user_data['password']
        )
        
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
    
    def test_user_login_invalid_credentials(self):
        """Test user login with invalid credentials."""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_user_profile_authenticated(self):
        """Test getting user profile with valid authentication."""
        # Create user and get tokens
        user = User.objects.create_user(
            email=self.user_data['email'],
            full_name=self.user_data['full_name'],
            password=self.user_data['password']
        )
        tokens = TokenService.get_tokens_for_user(user)
        
        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], user.email)
    
    def test_get_user_profile_unauthenticated(self):
        """Test getting user profile without authentication."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_forgot_password_success(self):
        """Test successful forgot password request."""
        # Create user
        User.objects.create_user(
            email=self.user_data['email'],
            full_name=self.user_data['full_name'],
            password=self.user_data['password']
        )
        
        forgot_data = {'email': self.user_data['email']}
        response = self.client.post(self.forgot_password_url, forgot_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
    
    def test_forgot_password_invalid_email(self):
        """Test forgot password with invalid email."""
        forgot_data = {'email': 'nonexistent@example.com'}
        response = self.client.post(self.forgot_password_url, forgot_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_reset_password_success(self):
        """Test successful password reset."""
        # Create user
        user = User.objects.create_user(
            email=self.user_data['email'],
            full_name=self.user_data['full_name'],
            password=self.user_data['password']
        )
        
        # Generate reset token
        token = PasswordResetService.create_password_reset_token(user.email)
        
        reset_data = {
            'token': token,
            'new_password': 'newpassword456',
            'new_password_confirm': 'newpassword456'
        }
        
        response = self.client.post(self.reset_password_url, reset_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_reset_password_invalid_token(self):
        """Test password reset with invalid token."""
        reset_data = {
            'token': 'invalid_token',
            'new_password': 'newpassword456',
            'new_password_confirm': 'newpassword456'
        }
        
        response = self.client.post(self.reset_password_url, reset_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_health_check(self):
        """Test API health check endpoint."""
        response = self.client.get(self.health_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertIn('total_users', response.data)