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
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_view, name='upload'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('results/', views.results_view, name='results'),
    path('profile/', views.profile_view, name='profile'),
    path('history/', views.history_view, name='history'),
    path('model-info/', views.model_info_view, name='model_info'),
    path('result-detail/', views.result_detail_view, name='result_detail'),
]

