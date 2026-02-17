"""
Views for Pneumonia Diagnosis System
Handles user requests for diagnosis, history, and results
"""

import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone

from .models import XRayImage, PredictionResult, UserHistory, ModelVersion, ProcessingLog
from .services import DiagnosisService

logger = logging.getLogger(__name__)


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def register_view(request):
    """
    User registration for medical professionals
    FR-1: User Account Management
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        errors = []
        
        # Validation
        if not all([username, email, password, password_confirm]):
            errors.append('All fields are required')
        
        if password != password_confirm:
            errors.append('Passwords do not match')
        
        if len(password) < 8:
            errors.append('Password must be at least 8 characters')
        
        if User.objects.filter(username=username).exists():
            errors.append('Username already exists')
        
        if User.objects.filter(email=email).exists():
            errors.append('Email already exists')
        
        if errors:
            return render(request, 'register.html', {'errors': errors})
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Log action
            UserHistory.objects.create(
                user=user,
                action_type='LOGIN',
                timestamp=timezone.now(),
                ip_address=get_client_ip(request)
            )
            
            # Auto-login after registration
            login(request, user)
            return redirect('model_service:dashboard')
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            errors.append('Registration failed. Please try again.')
            return render(request, 'register.html', {'errors': errors})
    
    return render(request, 'register.html')


def login_view(request):
    """
    User login for medical professionals
    FR-1: User Account Management
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        errors = []
        
        if not all([username, password]):
            errors.append('Username and password are required')
        else:
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Log action
                UserHistory.objects.create(
                    user=user,
                    action_type='LOGIN',
                    timestamp=timezone.now(),
                    ip_address=get_client_ip(request)
                )
                
                return redirect('model_service:dashboard')
            else:
                errors.append('Invalid username or password')
        
        return render(request, 'login.html', {'errors': errors})
    
    return render(request, 'login.html')


@login_required(login_url='model_service:login')
def logout_view(request):
    """User logout"""
    # Log action
    UserHistory.objects.create(
        user=request.user,
        action_type='LOGOUT',
        timestamp=timezone.now(),
        ip_address=get_client_ip(request)
    )
    
    logout(request)
    return redirect('model_service:login')


# ============================================================================
# MAIN DASHBOARD VIEWS
# ============================================================================

@login_required(login_url='model_service:login')
def dashboard_view(request):
    """
    Main dashboard showing user's recent predictions and statistics
    """
    user = request.user
    
    # Get user's recent predictions
    recent_predictions = PredictionResult.objects.filter(
        image__user=user
    ).select_related('image', 'model_version').order_by('-created_at')[:5]
    
    # Calculate statistics
    total_predictions = PredictionResult.objects.filter(image__user=user).count()
    pneumonia_count = PredictionResult.objects.filter(
        image__user=user,
        prediction_label='PNEUMONIA'
    ).count()
    normal_count = PredictionResult.objects.filter(
        image__user=user,
        prediction_label='NORMAL'
    ).count()
    
    # Average confidence
    all_predictions = PredictionResult.objects.filter(image__user=user)
    avg_confidence = 0
    if all_predictions.exists():
        avg_confidence = float(all_predictions.aggregate(
            avg=__import__('django.db.models', fromlist=['Avg']).Avg('confidence_score')
        )['avg'] or 0) * 100
    
    context = {
        'total_predictions': total_predictions,
        'pneumonia_count': pneumonia_count,
        'normal_count': normal_count,
        'avg_confidence': round(avg_confidence, 2),
        'recent_predictions': recent_predictions,
    }
    
    return render(request, 'dashboard.html', context)


# ============================================================================
# IMAGE UPLOAD & DIAGNOSIS VIEWS
# ============================================================================

@login_required(login_url='model_service:login')
def upload_view(request):
    """
    Image upload interface
    FR-2: Chest X-Ray Image Upload
    """
    if request.method == 'POST':
        if 'image' not in request.FILES:
            return render(request, 'upload.html', 
                        {'error': 'No image file provided'})
        
        image_file = request.FILES['image']
        
        # Validate file
        if image_file.size > 10 * 1024 * 1024:  # 10 MB limit
            return render(request, 'upload.html',
                        {'error': 'File size exceeds 10 MB limit'})
        
        if image_file.content_type not in ['image/jpeg', 'image/png']:
            return render(request, 'upload.html',
                        {'error': 'Only JPEG and PNG formats are supported'})
        
        try:
            # Create XRayImage record
            from PIL import Image
            from django.core.files.storage import default_storage
            
            # Save file temporarily
            file_name = f"{request.user.id}_{timezone.now().timestamp()}_{image_file.name}"
            file_path = f"xray_images/{file_name}"
            
            # Save and get dimensions
            img = Image.open(image_file)
            width, height = img.size
            format_type = 'PNG' if img.format == 'PNG' else 'JPEG'
            
            xray_image = XRayImage.objects.create(
                user=request.user,
                original_filename=image_file.name,
                stored_filename=file_name,
                file_path=image_file,
                file_size=image_file.size,
                image_width=width,
                image_height=height,
                format=format_type
            )
            
            # Log action
            UserHistory.objects.create(
                user=request.user,
                action_type='UPLOAD',
                image=xray_image,
                timestamp=timezone.now(),
                ip_address=get_client_ip(request)
            )
            
            # Perform diagnosis
            return redirect('model_service:analyze', image_id=xray_image.id)
            
        except Exception as e:
            logger.error(f"Image upload error: {str(e)}")
            return render(request, 'upload.html',
                        {'error': 'Failed to process image'})
    
    return render(request, 'upload.html')


@login_required(login_url='model_service:login')
def analyze_view(request, image_id):
    """
    Perform diagnosis on uploaded image
    FR-3: Image Preprocessing
    FR-4: Pneumonia Prediction
    """
    xray_image = get_object_or_404(XRayImage, id=image_id, user=request.user)
    
    # Check if already analyzed
    if hasattr(xray_image, 'prediction'):
        return redirect('model_service:result', result_id=xray_image.prediction.id)
    
    try:
        # Perform diagnosis
        image_path = xray_image.file_path.path
        diagnosis_result = DiagnosisService.diagnose(image_path)
        
        if diagnosis_result['status'] == 'error':
            logger.warning(f"Diagnosis failed for image {image_id}: {diagnosis_result['errors']}")
            return render(request, 'error.html',
                        {'error': 'Analysis failed: ' + ', '.join(diagnosis_result['errors'])})
        
        # Save prediction result
        prediction = DiagnosisService.save_prediction_result(xray_image, diagnosis_result)
        
        if prediction is None:
            return render(request, 'error.html',
                        {'error': 'Failed to save analysis result'})
        
        # Log action
        UserHistory.objects.create(
            user=request.user,
            action_type='ANALYZE',
            image=xray_image,
            prediction_result=prediction,
            timestamp=timezone.now(),
            ip_address=get_client_ip(request)
        )
        
        return redirect('model_service:result', result_id=prediction.id)
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return render(request, 'error.html',
                    {'error': 'An error occurred during analysis'})


# ============================================================================
# RESULT DISPLAY VIEWS
# ============================================================================

@login_required(login_url='model_service:login')
def result_view(request, result_id):
    """
    Display prediction result
    FR-5: Result Display
    """
    prediction = get_object_or_404(
        PredictionResult,
        id=result_id,
        image__user=request.user
    )
    
    # Log action
    UserHistory.objects.create(
        user=request.user,
        action_type='VIEW_RESULT',
        prediction_result=prediction,
        timestamp=timezone.now(),
        ip_address=get_client_ip(request)
    )
    
    # Parse raw predictions
    raw_predictions = json.loads(prediction.raw_predictions) if prediction.raw_predictions else {}
    
    # Check if demo mode
    demo_mode = False
    if isinstance(raw_predictions, dict):
        demo_mode = raw_predictions.get('_demo', False)
    
    context = {
        'result': prediction,
        'confidence_percentage': prediction.get_confidence_percentage(),
        'raw_predictions': raw_predictions,
        'demo_mode': demo_mode,
    }
    
    return render(request, 'result.html', context)


# ============================================================================
# HISTORY VIEWS
# ============================================================================

@login_required(login_url='model_service:login')
def history_view(request):
    """
    Display user's prediction history
    FR-6: Result History
    """
    user = request.user
    
    # Get all predictions with filtering options
    predictions = PredictionResult.objects.filter(
        image__user=user
    ).select_related('image', 'model_version').order_by('-created_at')
    
    # Filter by label if specified
    label_filter = request.GET.get('label')
    if label_filter in ['NORMAL', 'PNEUMONIA']:
        predictions = predictions.filter(prediction_label=label_filter)
    
    # Search by filename
    search_query = request.GET.get('search')
    if search_query:
        predictions = predictions.filter(
            image__original_filename__icontains=search_query
        )
    
    # Pagination
    paginator = Paginator(predictions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'predictions': page_obj.object_list,
        'label_filter': label_filter,
        'search_query': search_query,
    }
    
    return render(request, 'history.html', context)


@login_required(login_url='model_service:login')
@require_http_methods(["POST"])
def delete_result_view(request, result_id):
    """Delete a prediction result"""
    prediction = get_object_or_404(
        PredictionResult,
        id=result_id,
        image__user=request.user
    )
    
    image = prediction.image
    
    # Log action
    UserHistory.objects.create(
        user=request.user,
        action_type='DELETE_RESULT',
        prediction_result=prediction,
        timestamp=timezone.now(),
        ip_address=get_client_ip(request)
    )
    
    # Delete related files
    if image.file_path:
        image.file_path.delete()
    
    image.delete()
    
    return redirect('model_service:history')


# ============================================================================
# API ENDPOINTS
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def api_diagnose(request):
    """
    API endpoint for pneumonia diagnosis
    Accepts image upload and returns prediction
    """
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    
    if 'image' not in request.FILES:
        return JsonResponse({'status': 'error', 'message': 'No image provided'}, status=400)
    
    image_file = request.FILES['image']
    
    try:
        # Create XRayImage record
        from PIL import Image
        
        img = Image.open(image_file)
        width, height = img.size
        format_type = 'PNG' if img.format == 'PNG' else 'JPEG'
        
        xray_image = XRayImage.objects.create(
            user=request.user,
            original_filename=image_file.name,
            stored_filename=f"{request.user.id}_{timezone.now().timestamp()}_{image_file.name}",
            file_path=image_file,
            file_size=image_file.size,
            image_width=width,
            image_height=height,
            format=format_type
        )
        
        # Perform diagnosis
        image_path = xray_image.file_path.path
        diagnosis_result = DiagnosisService.diagnose(image_path)
        
        if diagnosis_result['status'] != 'success':
            return JsonResponse({
                'status': 'error',
                'message': 'Analysis failed',
                'errors': diagnosis_result['errors']
            }, status=400)
        
        # Save prediction
        prediction = DiagnosisService.save_prediction_result(xray_image, diagnosis_result)
        
        if prediction is None:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to save result'
            }, status=500)
        
        return JsonResponse({
            'status': 'success',
            'result_id': prediction.id,
            'prediction': prediction.prediction_label,
            'confidence': float(prediction.confidence_score),
            'confidence_percentage': prediction.get_confidence_percentage(),
            'confidence_level': prediction.confidence_level,
        })
        
    except Exception as e:
        logger.error(f"API diagnosis error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
