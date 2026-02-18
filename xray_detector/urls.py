"""
URL configuration for xray_detector app.
"""

from django.urls import path
from . import views

app_name = 'xray_detector'

urlpatterns = [
    path('', views.index, name='index'),
]
