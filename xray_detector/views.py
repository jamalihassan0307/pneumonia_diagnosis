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
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        # Form uses password1 and password2 (or password and password_confirm)
        password = request.POST.get('password', '') or request.POST.get('password1', '')
        password = password.strip()
        password_confirm = request.POST.get('password_confirm', '') or request.POST.get('password2', '')
        password_confirm = password_confirm.strip()
        
        # Debug: Log what we're receiving
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Registration attempt - username: '{username}', email: '{email}', password length: {len(password) if password else 0}")
        
        # Validate form - check all fields are provided with more specific messages
        errors = []
        if not username:
            errors.append('Username is required')
        if not email:
            errors.append('Email is required')
        if not password:
            errors.append('Password is required')
        if not password_confirm:
            errors.append('Please confirm your password')
        
        if errors:
            return render(request, 'xray_detector/register.html',
                         {'error': ', '.join(errors)})
        
        # Validate passwords match
        if password != password_confirm:
            return render(request, 'xray_detector/register.html',
                         {'error': 'Passwords do not match'})
        
        # Validate password length
        if len(password) < 8:
            return render(request, 'xray_detector/register.html',
                         {'error': 'Password must be at least 8 characters'})
        
        # Validate email format
        if '@' not in email:
            return render(request, 'xray_detector/register.html',
                         {'error': 'Please enter a valid email address'})
        
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
            logger.error(f"User creation error: {str(e)}")
            return render(request, 'xray_detector/register.html',
                         {'error': f'Error creating account: {str(e)}'})
    
    return render(request, 'xray_detector/register.html')


@login_required(login_url='xray_detector:login')
def dashboard_view(request):
    """Render dashboard page (requires authentication)"""
    # Get all user's prediction results for statistics
    all_results = PredictionResult.objects.filter(
        image__user=request.user
    ).select_related('image')
    
    # Calculate statistics on full queryset
    total_uploads = all_results.count()
    normal_count = all_results.filter(prediction_label='NORMAL').count()
    pneumonia_count = all_results.filter(prediction_label='PNEUMONIA').count()
    
    # Get recent results for history display
    recent_results = all_results.order_by('-created_at')[:10]
    
    # Prepare history data
    history_data = []
    for result in recent_results:
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
    # Get all user's prediction results
    results = PredictionResult.objects.filter(
        image__user=request.user
    ).select_related('image').order_by('-created_at')
    
    # Prepare results data
    results_data = []
    for result in results:
        results_data.append({
            'id': result.id,
            'filename': result.image.original_filename,
            'prediction': result.prediction_label,
            'confidence': result.get_confidence_percentage(),
            'date': result.created_at.strftime('%Y-%m-%d %H:%M'),
            'image_url': result.image.file_path.url if result.image.file_path else '',
            'processing_time': float(result.processing_time),
            'confidence_level': result.confidence_level
        })
    
    context = {
        'results': json.dumps(results_data),
        'username': request.user.username
    }
    
    return render(request, 'xray_detector/results.html', context)


@login_required(login_url='xray_detector:login')
def profile_view(request):
    """View and edit user profile"""
    # Get user stats
    total_uploads = PredictionResult.objects.filter(image__user=request.user).count()
    normal_count = PredictionResult.objects.filter(
        image__user=request.user, 
        prediction_label='NORMAL'
    ).count()
    pneumonia_count = PredictionResult.objects.filter(
        image__user=request.user, 
        prediction_label='PNEUMONIA'
    ).count()
    
    context = {
        'user': request.user,
        'total_uploads': total_uploads,
        'normal_count': normal_count,
        'pneumonia_count': pneumonia_count
    }
    
    return render(request, 'xray_detector/profile.html', context)


@login_required(login_url='xray_detector:login')
def history_view(request):
    """View activity history"""
    # Get user history
    history = UserHistory.objects.filter(
        user=request.user
    ).select_related('image').order_by('-timestamp')
    
    # Prepare history data
    history_data = []
    for item in history:
        history_data.append({
            'id': item.id,
            'action': item.action_type,
            'description': item.get_action_type_display(),
            'filename': item.image.original_filename if item.image else '-',
            'date': item.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'ip_address': item.ip_address or '-'
        })
    
    context = {
        'history': json.dumps(history_data),
        'username': request.user.username
    }
    
    return render(request, 'xray_detector/history.html', context)


@login_required(login_url='xray_detector:login')
def model_info_view(request):
    """View model information and specifications"""
    return render(request, 'xray_detector/model_info.html')


@login_required(login_url='xray_detector:login')
def result_detail_view(request):
    """View detailed result information"""
    from django.shortcuts import get_object_or_404
    
    # Get result ID from query parameter
    result_id = request.GET.get('id')
    if not result_id:
        return redirect('xray_detector:results')
    
    # Fetch the result for the current user only
    result = get_object_or_404(
        PredictionResult,
        id=result_id,
        image__user=request.user
    )
    
    # Parse raw predictions if it's a string
    raw_predictions = result.raw_predictions
    if isinstance(raw_predictions, str):
        try:
            raw_predictions = json.loads(raw_predictions)
        except:
            raw_predictions = {}
    
    # Prepare image data with correct field names from model
    image_data = {
        'id': result.image.id,
        'original_filename': result.image.original_filename,
        'file_path': result.image.file_path.url if result.image.file_path else '',
        'file_size_mb': result.image.get_file_size_mb(),
        'image_format': result.image.format,
        'width': result.image.image_width or 0,
        'height': result.image.image_height or 0,
        'upload_time': result.image.upload_time,
        'is_preprocessed': result.image.is_preprocessed,
    }
    
    # Prepare result data with correct field names
    result_data = {
        'id': result.id,
        'prediction_label': result.prediction_label,
        'confidence_percentage': result.get_confidence_percentage(),
        'confidence_level': result.confidence_level,
        'confidence_score': float(result.confidence_score),
        'processing_time': float(result.processing_time),
        'created_at': result.created_at,
        'model_version': result.model_version.version if result.model_version else 'Default (MobileNetV2)',
    }
    
    # Prepare context
    context = {
        'result': result_data,
        'image': image_data,
        'raw_predictions': raw_predictions,
        'is_pneumonia': result.prediction_label == 'PNEUMONIA'
    }
    
    return render(request, 'xray_detector/result_detail.html', context)


@login_required(login_url='xray_detector:login')
def upload_view(request):
    """Display the upload page for X-ray image analysis"""
    return render(request, 'xray_detector/upload.html')


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


