"""
Views for X-Ray pneumonia detection.
Handles GET requests for the upload form and POST requests for image processing.
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .services import predict_pneumonia, validate_image_file
from .models import UserHistory, XRayImage, PredictionResult, ModelVersion
import logging
import time
import json
import os

logger = logging.getLogger(__name__)


def login_view(request):
    """Render login page - redirects to dashboard if already authenticated"""
    if request.user.is_authenticated:
        return redirect('xray_detector:dashboard')
    return render(request, 'xray_detector/login.html')


def register_view(request):
    """Render registration page - redirects to dashboard if already authenticated"""
    if request.user.is_authenticated:
        return redirect('xray_detector:dashboard')
    return render(request, 'xray_detector/register.html')


@login_required(login_url='xray_detector:login')
def dashboard_view(request):
    """Render dashboard page (requires authentication)"""
    return render(request, 'xray_detector/dashboard.html')


@login_required(login_url='xray_detector:login')
def results_view(request):
    """View prediction results and history"""
    return render(request, 'xray_detector/results.html')


@login_required(login_url='xray_detector:login')
def profile_view(request):
    """View and edit user profile"""
    return render(request, 'xray_detector/profile.html')


@login_required(login_url='xray_detector:login')
def history_view(request):
    """View activity history"""
    return render(request, 'xray_detector/history.html')


@login_required(login_url='xray_detector:login')
def model_info_view(request):
    """View model information and specifications"""
    return render(request, 'xray_detector/model_info.html')


@login_required(login_url='xray_detector:login')
def result_detail_view(request):
    """View detailed result information"""
    return render(request, 'xray_detector/result_detail.html')


def index(request):
    """
    Home page view - redirects to dashboard if authenticated, login otherwise.
    """
    if request.user.is_authenticated:
        return redirect('xray_detector:dashboard')
    return redirect('xray_detector:login')


