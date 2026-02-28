"""
URL Configuration for model_service app
Maps URLs to views for pneumonia diagnosis system
"""

from django.urls import path, include
from . import views

app_name = 'model_service'

urlpatterns = [
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard and main views
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('', views.dashboard_view, name='index'),
    
    # Upload and diagnosis
    path('upload/', views.upload_view, name='upload'),
    path('analyze/<int:image_id>/', views.analyze_view, name='analyze'),
    
    # Results
    path('result/<int:result_id>/', views.result_view, name='result'),
    
    # History
    path('history/', views.history_view, name='history'),
    path('delete/<int:result_id>/', views.delete_result_view, name='delete'),
    
    # Legacy API Endpoint
    path('api/diagnose/', views.api_diagnose, name='api_diagnose'),
    
    # REST API Endpoints (Django REST Framework)
    path('api/v1/', include('model_service.api_urls', namespace='api')),
]
