"""
URL configuration for xray_detector app.
"""

from django.urls import path
from . import views

app_name = 'xray_detector'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('results/', views.results_view, name='results'),
]

