"""
API URL Configuration for Pneumonia Diagnosis System
<<<<<<< HEAD:model_service/api_urls.py
Modern REST API endpoints
=======
REST API endpoints
>>>>>>> 78d89b9f51d0fdbbd388483cf17b5a8558c3e832:xray_detector/api_urls.py
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
<<<<<<< HEAD:model_service/api_urls.py
from . import api_views

# Create DRF router
router = DefaultRouter()
router.register(r'results', api_views.PredictionResultViewSet, basename='result')
router.register(r'images', api_views.XRayImageViewSet, basename='image')
=======
from rest_framework.authtoken.views import obtain_auth_token
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .api_views import (
    UserRegistrationView, CustomAuthToken, LogoutView,
    XRayImageViewSet, PredictionResultViewSet, UserHistoryViewSet,
    ModelVersionViewSet, user_detail, change_password
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'users', UserRegistrationView, basename='user')
router.register(r'images', XRayImageViewSet, basename='xray-image')
router.register(r'results', PredictionResultViewSet, basename='prediction-result')
router.register(r'history', UserHistoryViewSet, basename='user-history')
router.register(r'model-versions', ModelVersionViewSet, basename='model-version')
>>>>>>> 78d89b9f51d0fdbbd388483cf17b5a8558c3e832:xray_detector/api_urls.py

app_name = 'api'

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
<<<<<<< HEAD:model_service/api_urls.py
    # Authentication Endpoints
    path('auth/register/', api_views.api_register, name='register'),
    path('auth/login/', api_views.api_login, name='login'),
    path('auth/logout/', api_views.api_logout, name='logout'),
    path('auth/profile/', api_views.api_user_profile, name='profile'),
    
    # Diagnosis Endpoints
    path('diagnosis/analyze/', api_views.api_diagnose_pneumonia, name='diagnose'),
    
    # Model Info Endpoints
    path('model/info/', api_views.api_model_info, name='model_info'),
=======
    # Authentication
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    path('auth/login/', CustomAuthToken.as_view(), name='api_login'),
    path('auth/logout/', LogoutView.as_view({'post': 'logout'}), name='api_logout'),
    
    # User endpoints
    path('users/<int:user_id>/', user_detail, name='user_detail'),
    path('change-password/', change_password, name='change_password'),
    
    # Swagger/OpenAPI Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
>>>>>>> 78d89b9f51d0fdbbd388483cf17b5a8558c3e832:xray_detector/api_urls.py
]
