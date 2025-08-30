from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for the User model.
    Displays user information in a clean, organized format.
    """
    
    # Fields to display in the user list
    list_display = [
        'email', 
        'full_name', 
        'is_active', 
        'is_staff', 
        'created_at'
    ]
    
    # Fields to filter by in the admin sidebar
    list_filter = [
        'is_active', 
        'is_staff', 
        'is_superuser', 
        'created_at'
    ]
    
    # Fields to search by
    search_fields = ['email', 'full_name']
    
    # Default ordering
    ordering = ['-created_at']
    
    # Fields to display when viewing/editing a user
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Personal info'), {
            'fields': ('full_name',)
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'created_at', 'updated_at'),
        }),
    )
    
    # Fields to display when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2'),
        }),
    )
    
    # Read-only fields
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    
    # Remove username from the admin since we use email
    filter_horizontal = ('groups', 'user_permissions',)