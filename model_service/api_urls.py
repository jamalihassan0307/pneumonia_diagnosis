"""
API URL Configuration for Pneumonia Diagnosis System
Modern REST API endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# Create DRF router
router = DefaultRouter()
router.register(r'results', api_views.PredictionResultViewSet, basename='result')
router.register(r'images', api_views.XRayImageViewSet, basename='image')

app_name = 'api'

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Authentication Endpoints
    path('auth/register/', api_views.api_register, name='register'),
    path('auth/login/', api_views.api_login, name='login'),
    path('auth/logout/', api_views.api_logout, name='logout'),
    path('auth/profile/', api_views.api_user_profile, name='profile'),
    
    # Diagnosis Endpoints
    path('diagnosis/analyze/', api_views.api_diagnose_pneumonia, name='diagnose'),
    
    # Model Info Endpoints
    path('model/info/', api_views.api_model_info, name='model_info'),
]
