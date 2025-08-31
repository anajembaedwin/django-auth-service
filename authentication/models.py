from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, full_name, password=None, **extra_fields):
        """Create and return a regular user with email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, full_name, password=None, **extra_fields):
        """Create and return a superuser with email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email, full_name, password, **extra_fields)

class User(AbstractUser):
    """
    Custom User model that uses email as the unique identifier
    instead of username for authentication.
    """
    
    # Remove username field and use email instead
    username = None
    
    # User fields
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Required. Enter a valid email address.')
    )
    
    full_name = models.CharField(
        _('full name'),
        max_length=255,
        help_text=_('Enter your full name.')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )
    
    # Make email the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    objects = UserManager()
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    @property
    def get_full_name(self):
        """Return the full name of the user."""
        return self.full_name
    
    def get_short_name(self):
        """Return the short name (first name) of the user."""
        return self.full_name.split(' ')[0] if self.full_name else self.email