"""
API URL Configuration for Pneumonia Diagnosis System
REST API endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
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

app_name = 'api'

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
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
]
