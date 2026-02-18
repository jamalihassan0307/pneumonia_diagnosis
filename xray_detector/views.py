"""
Views for X-Ray pneumonia detection.
Handles GET requests for the upload form and POST requests for image processing.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .services import predict_pneumonia, validate_image_file
from .models import UserHistory, XRayImage, PredictionResult
import logging
import time
import json

logger = logging.getLogger(__name__)


def login_view(request):
    """Render login page"""
    if request.user.is_authenticated:
        return render(request, 'xray_detector/login.html')
    return render(request, 'xray_detector/login.html')


def register_view(request):
    """Render registration page"""
    if request.user.is_authenticated:
        return render(request, 'xray_detector/register.html')
    return render(request, 'xray_detector/register.html')


def dashboard_view(request):
    """Render dashboard page (requires authentication)"""
    if not request.user.is_authenticated:
        return render(request, 'xray_detector/dashboard.html')
    return render(request, 'xray_detector/dashboard.html')


def results_view(request):
    """View prediction results and history"""
    if not request.user.is_authenticated:
        return render(request, 'xray_detector/results.html')
    return render(request, 'xray_detector/results.html')


@ensure_csrf_cookie
def index(request):
    """
    Main view for pneumonia detection.
    
    GET: Display the upload form
    POST: Process uploaded image and return prediction results
    
    Returns:
        GET: Rendered HTML template
        POST: JSON response with prediction results or error
    """
    if request.method == 'GET':
        # Display upload form
        return render(request, 'xray_detector/index.html')
    
    elif request.method == 'POST':
        # Process uploaded image
        try:
            # Check if file was uploaded
            if 'xray_image' not in request.FILES:
                return JsonResponse({
                    'success': False,
                    'error': 'No image file provided. Please select an X-ray image.'
                }, status=400)
            
            uploaded_file = request.FILES['xray_image']
            
            # Validate file
            is_valid, error_message = validate_image_file(uploaded_file)
            if not is_valid:
                return JsonResponse({
                    'success': False,
                    'error': error_message
                }, status=400)
            
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file temporarily
            file_name = uploaded_file.name
            file_path = os.path.join(upload_dir, file_name)
            
            # Save the uploaded file
            saved_path = default_storage.save(file_path, ContentFile(uploaded_file.read()))
            logger.info(f"File saved temporarily at: {saved_path}")
            
            try:
                # Reset file pointer for prediction
                uploaded_file.seek(0)
                
                # Make prediction
                start_time = time.time()
                result = predict_pneumonia(uploaded_file)
                processing_time = time.time() - start_time
                
                # Check if prediction was successful
                if not result.get('success'):
                    return JsonResponse({
                        'success': False,
                        'error': result.get('error', 'Prediction failed')
                    }, status=500)
                
                # Return successful prediction
                response_data = {
                    'success': True,
                    'predicted_class': result['predicted_class'],
                    'confidence': result['confidence'],
                    'raw_score': result['raw_score'],
                    'processing_time': round(processing_time, 3)
                }
                
                logger.info(f"Prediction successful: {response_data}")
                return JsonResponse(response_data)
                
            finally:
                # Delete temporary file
                try:
                    if default_storage.exists(saved_path):
                        default_storage.delete(saved_path)
                        logger.info(f"Temporary file deleted: {saved_path}")
                except Exception as e:
                    logger.error(f"Error deleting temporary file: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Server error: {str(e)}'
            }, status=500)
    
    else:
        # Method not allowed
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed'
        }, status=405)

