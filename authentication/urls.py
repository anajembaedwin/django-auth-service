from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    
    # Password reset endpoints
    path('forgot-password/', views.request_password_reset, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    
    # User profile endpoints
    path('profile/', views.get_user_profile, name='profile'),
    
    # Health check endpoint
    path('health/', views.api_health_check, name='health_check'),
]