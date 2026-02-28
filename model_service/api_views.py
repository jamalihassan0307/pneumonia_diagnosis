"""
Django REST Framework API Views for Pneumonia Diagnosis System
Modern, high-performance API endpoints
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q

from .models import XRayImage, PredictionResult, UserHistory, ModelVersion
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    XRayImageSerializer, XRayImageUploadSerializer,
    PredictionResultSerializer, PredictionResultDetailSerializer,
    DiagnosisRequestSerializer, DiagnosisResponseSerializer,
    UserHistorySerializer, ModelVersionSerializer
)
from .services import DiagnosisService

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API results"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# ============================================================================
# AUTHENTICATION API ENDPOINTS
# ============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    """
    Register a new user
    
    POST /api/auth/register/
    {
        "username": "doctor123",
        "email": "doctor@hospital.com",
        "password": "securepass123",
        "password_confirm": "securepass123"
    }
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Log registration
        UserHistory.objects.create(
            user=user,
            action_type='REGISTER',
            timestamp=timezone.now(),
            ip_address=get_client_ip(request)
        )
        
        return Response({
            'status': 'success',
            'message': 'User registered successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'status': 'error',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """
    Login user
    
    POST /api/auth/login/
    {
        "username": "doctor123",
        "password": "securepass123"
    }
    """
    from django.contrib.auth import authenticate, login
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'status': 'error',
            'message': 'Username and password required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        
        # Log login
        UserHistory.objects.create(
            user=user,
            action_type='LOGIN',
            timestamp=timezone.now(),
            ip_address=get_client_ip(request)
        )
        
        return Response({
            'status': 'success',
            'message': 'Login successful',
            'user': UserSerializer(user).data
        })
    
    return Response({
        'status': 'error',
        'message': 'Invalid credentials'
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """
    Logout user
    
    POST /api/auth/logout/
    """
    from django.contrib.auth import logout
    
    # Log logout
    UserHistory.objects.create(
        user=request.user,
        action_type='LOGOUT',
        timestamp=timezone.now(),
        ip_address=get_client_ip(request)
    )
    
    logout(request)
    
    return Response({
        'status': 'success',
        'message': 'Logout successful'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_user_profile(request):
    """
    Get current user profile
    
    GET /api/auth/profile/
    """
    return Response({
        'status': 'success',
        'user': UserSerializer(request.user).data
    })


# ============================================================================
# PNEUMONIA DIAGNOSIS API ENDPOINTS
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_diagnose_pneumonia(request):
    """
    Perform pneumonia diagnosis on uploaded X-ray image
    
    POST /api/diagnosis/analyze/
    Content-Type: multipart/form-data
    
    Parameters:
        image (file): X-ray image (JPEG/PNG, max 10MB)
    
    Returns:
        {
            "status": "success",
            "result_id": 123,
            "prediction": "PNEUMONIA",
            "confidence": 0.9856,
            "confidence_percentage": 98.56,
            "confidence_level": "HIGH",
            "processing_time": 0.45,
            "is_demo_mode": false
        }
    """
    # Validate request
    serializer = DiagnosisRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    image_file = serializer.validated_data['image']
    
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
        
        # Log upload
        UserHistory.objects.create(
            user=request.user,
            action_type='UPLOAD',
            image=xray_image,
            timestamp=timezone.now(),
            ip_address=get_client_ip(request)
        )
        
        # Perform diagnosis
        image_path = xray_image.file_path.path
        diagnosis_result = DiagnosisService.diagnose(image_path)
        
        if diagnosis_result['status'] != 'success':
            return Response({
                'status': 'error',
                'message': 'Analysis failed',
                'errors': diagnosis_result.get('errors', [])
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Save prediction
        prediction = DiagnosisService.save_prediction_result(xray_image, diagnosis_result)
        
        if prediction is None:
            return Response({
                'status': 'error',
                'message': 'Failed to save prediction result'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Log analysis
        UserHistory.objects.create(
            user=request.user,
            action_type='ANALYZE',
            image=xray_image,
            prediction_result=prediction,
            timestamp=timezone.now(),
            ip_address=get_client_ip(request)
        )
        
        # Check if demo mode
        import json
        raw_preds = json.loads(prediction.raw_predictions) if prediction.raw_predictions else {}
        is_demo = raw_preds.get('_demo', False)
        
        response_data = {
            'status': 'success',
            'result_id': prediction.id,
            'prediction': prediction.prediction_label,
            'confidence': float(prediction.confidence_score),
            'confidence_percentage': prediction.get_confidence_percentage(),
            'confidence_level': prediction.confidence_level,
            'processing_time': prediction.processing_time,
            'is_demo_mode': is_demo,
            'image_id': xray_image.id
        }
        
        if is_demo:
            response_data['warning'] = 'Model loading failed. Using demo mode for predictions.'
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"API diagnosis error: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'Diagnosis failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# PREDICTION RESULTS API ENDPOINTS
# ============================================================================

class PredictionResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing prediction results
    
    GET /api/results/          - List all predictions
    GET /api/results/{id}/     - Get specific prediction detail
    """
    serializer_class = PredictionResultSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter predictions by current user"""
        queryset = PredictionResult.objects.filter(
            image__user=self.request.user
        ).select_related('image', 'model_version').order_by('-created_at')
        
        # Filter by label
        label = self.request.query_params.get('label')
        if label in ['NORMAL', 'PNEUMONIA']:
            queryset = queryset.filter(prediction_label=label)
        
        # Search by filename
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(image__original_filename__icontains=search)
            )
        
        return queryset
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action"""
        if self.action == 'retrieve':
            return PredictionResultDetailSerializer
        return self.serializer_class
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get user's prediction statistics
        
        GET /api/results/statistics/
        """
        queryset = self.get_queryset()
        
        total = queryset.count()
        pneumonia = queryset.filter(prediction_label='PNEUMONIA').count()
        normal = queryset.filter(prediction_label='NORMAL').count()
        
        # Average confidence
        from django.db.models import Avg
        avg_conf = queryset.aggregate(avg=Avg('confidence_score'))['avg']
        avg_confidence = float(avg_conf * 100) if avg_conf else 0
        
        return Response({
            'status': 'success',
            'statistics': {
                'total_predictions': total,
                'pneumonia_count': pneumonia,
                'normal_count': normal,
                'average_confidence': round(avg_confidence, 2)
            }
        })


# ============================================================================
# X-RAY IMAGE API ENDPOINTS
# ============================================================================

class XRayImageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing uploaded X-ray images
    
    GET /api/images/          - List all images
    GET /api/images/{id}/     - Get specific image detail
    DELETE /api/images/{id}/  - Delete image and prediction
    """
    serializer_class = XRayImageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter images by current user"""
        return XRayImage.objects.filter(
            user=self.request.user
        ).order_by('-uploaded_at')
    
    def destroy(self, request, *args, **kwargs):
        """Delete image and associated prediction"""
        instance = self.get_object()
        
        # Log deletion
        UserHistory.objects.create(
            user=request.user,
            action_type='DELETE_IMAGE',
            image=instance,
            timestamp=timezone.now(),
            ip_address=get_client_ip(request)
        )
        
        # Delete file
        if instance.file_path:
            instance.file_path.delete()
        
        self.perform_destroy(instance)
        
        return Response({
            'status': 'success',
            'message': 'Image and prediction deleted successfully'
        }, status=status.HTTP_200_OK)


# ============================================================================
# MODEL INFO API ENDPOINTS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_model_info(request):
    """
    Get information about the current ML model
    
    GET /api/model/info/
    """
    from .services import PneumoniaDetectionService
    
    try:
        model = PneumoniaDetectionService.get_model()
        
        if model is None:
            return Response({
                'status': 'warning',
                'message': 'Model not loaded - using demo mode',
                'model_loaded': False,
                'demo_mode': True
            })
        
        return Response({
            'status': 'success',
            'model_loaded': True,
            'demo_mode': False,
            'model_info': {
                'input_shape': str(model.input_shape),
                'output_shape': str(model.output_shape),
                'total_parameters': model.count_params() if hasattr(model, 'count_params') else None,
                'source': PneumoniaDetectionService._model_loaded_from
            }
        })
    except Exception as e:
        logger.error(f"Model info error: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
