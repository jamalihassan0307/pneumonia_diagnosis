"""
Views for X-Ray pneumonia detection.
Handles GET requests for the upload form and POST requests for image processing.
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
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
    """Handle login page and authentication"""
    if request.user.is_authenticated:
        return redirect('xray_detector:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('xray_detector:dashboard')
        else:
            return render(request, 'xray_detector/login.html', 
                         {'error': 'Invalid username or password'})
    
    return render(request, 'xray_detector/login.html')


def register_view(request):
    """Handle registration page and new user creation"""
    if request.user.is_authenticated:
        return redirect('xray_detector:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validate form
        if password != password_confirm:
            return render(request, 'xray_detector/register.html',
                         {'error': 'Passwords do not match'})
        
        if len(password) < 8:
            return render(request, 'xray_detector/register.html',
                         {'error': 'Password must be at least 8 characters'})
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'xray_detector/register.html',
                         {'error': 'Username already exists'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'xray_detector/register.html',
                         {'error': 'Email already registered'})
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            # Log the user in
            login(request, user)
            return redirect('xray_detector:dashboard')
        except Exception as e:
            return render(request, 'xray_detector/register.html',
                         {'error': 'Error creating account'})
    
    return render(request, 'xray_detector/register.html')


@login_required(login_url='xray_detector:login')
def dashboard_view(request):
    """Render dashboard page (requires authentication)"""
    # Get user's prediction results
    results = PredictionResult.objects.filter(
        image__user=request.user
    ).select_related('image').order_by('-created_at')[:10]
    
    # Calculate statistics
    total_uploads = results.count()
    normal_count = results.filter(prediction_label='NORMAL').count()
    pneumonia_count = results.filter(prediction_label='PNEUMONIA').count()
    
    # Prepare history data
    history_data = []
    for result in results:
        history_data.append({
            'filename': result.image.original_filename,
            'prediction': result.prediction_label,
            'confidence': result.get_confidence_percentage(),
            'date': result.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    context = {
        'total_uploads': total_uploads,
        'total_analyzed': total_uploads,
        'normal_count': normal_count,
        'pneumonia_count': pneumonia_count,
        'history': history_data,
        'username': request.user.username
    }
    
    return render(request, 'xray_detector/dashboard.html', context)


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


def logout_view(request):
    """Logout user and redirect to login page"""
    logout(request)
    return redirect('xray_detector:login')


