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
    XRayImageViewSet, PredictionResultViewSet, UserHistoryViewSet
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'users', UserRegistrationView, basename='user')
router.register(r'images', XRayImageViewSet, basename='xray-image')
router.register(r'results', PredictionResultViewSet, basename='prediction-result')
router.register(r'history', UserHistoryViewSet, basename='user-history')

app_name = 'api'

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Authentication
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    path('auth/login/', CustomAuthToken.as_view(), name='api_login'),
    path('auth/logout/', LogoutView.as_view({'post': 'logout'}), name='api_logout'),
    
    # Swagger/OpenAPI Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
