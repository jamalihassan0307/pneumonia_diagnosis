"""
Django REST Framework API Views for Pneumonia Diagnosis System
REST API endpoints for authentication, image upload, analysis, and history
"""

import logging
import json
import time
import os
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import Q, Avg
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image

from .models import XRayImage, PredictionResult, UserHistory, ModelVersion
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    XRayImageSerializer, XRayImageUploadSerializer,
    PredictionResultSerializer, PredictionResultDetailSerializer,
    DiagnosisRequestSerializer, DiagnosisResponseSerializer,
    UserHistorySerializer, ModelVersionSerializer
)
from .services_tflite import predict_pneumonia, validate_image_file

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
=======
    UserHistorySerializer, ModelVersionSerializer
)
from .services import predict_pneumonia, validate_image_file
from .permissions import IsAuthenticated


class UserRegistrationView(viewsets.ModelViewSet):
    """
    User registration endpoint
    POST /api/users/register/
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Register new user"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomAuthToken(ObtainAuthToken):
    """
    Custom token auth view
    POST /api/auth/login/
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = token.user
        
        # Log login action
        ip_address = self.get_client_ip(request)
        UserHistory.objects.create(
            user=user,
            action_type='LOGIN',
            ip_address=ip_address
        )
        
        return Response({
            'token': response.data['token'],
            'user': UserSerializer(user).data
        })
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(viewsets.ViewSet):
    """
    User logout endpoint
    POST /api/auth/logout/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout user and delete token"""
        ip_address = self.get_client_ip(request)
        UserHistory.objects.create(
            user=request.user,
            action_type='LOGOUT',
            ip_address=ip_address
        )
        request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class XRayImageViewSet(viewsets.ModelViewSet):
    """
    X-Ray Image upload and management
    GET /api/images/ - List user's images
    POST /api/images/ - Upload new image
    """
    serializer_class = XRayImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return images for current user only"""
        return XRayImage.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Save image with current user"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload and analyze X-ray image"""
        try:
            if 'image' not in request.FILES:
                return Response(
                    {'error': 'No image file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            uploaded_file = request.FILES['image']
            
            # Validate file
            is_valid, error_message = validate_image_file(uploaded_file)
            if not is_valid:
                return Response(
                    {'error': error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create uploads directory
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save image to database
            original_name = uploaded_file.name
            stored_name = f"{int(time.time())}_{original_name}"
            
            xray_image = XRayImage.objects.create(
                user=request.user,
                original_filename=original_name,
                stored_filename=stored_name,
                file_path=uploaded_file,
                file_size=uploaded_file.size,
                format='JPEG' if original_name.lower().endswith('jpg') or original_name.lower().endswith('jpeg') else 'PNG'
            )
            
            # Log upload action
            ip_address = self.get_client_ip(request)
            UserHistory.objects.create(
                user=request.user,
                action_type='UPLOAD',
                image=xray_image,
                ip_address=ip_address
            )
            
            # Analyze image
            start_time = time.time()
            uploaded_file.seek(0)
            prediction_result = predict_pneumonia(uploaded_file)
            processing_time = time.time() - start_time
            
            if not prediction_result.get('success'):
                return Response(
                    {'error': prediction_result.get('error', 'Prediction failed')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Determine confidence level
            confidence = prediction_result['confidence'] / 100
            if confidence > 0.95:
                confidence_level = 'HIGH'
            elif confidence > 0.80:
                confidence_level = 'MODERATE'
            else:
                confidence_level = 'LOW'
            
            # Save prediction result
            prediction = PredictionResult.objects.create(
                image=xray_image,
                prediction_label=prediction_result['predicted_class'],
                confidence_score=confidence,
                confidence_level=confidence_level,
                processing_time=processing_time,
                raw_predictions=json.dumps({
                    'normal': float(1 - confidence),
                    'pneumonia': float(confidence)
                })
            )
            
            # Log analysis action
            UserHistory.objects.create(
                user=request.user,
                action_type='ANALYZE',
                image=xray_image,
                prediction_result=prediction,
                ip_address=ip_address
            )
            
            # Clean up temporary file
            try:
                uploaded_file.seek(0)
                if default_storage.exists(xray_image.file_path.name):
                    pass  # Keep the file in media folder
            except Exception as e:
                pass
            
            return Response({
                'status': 'success',
                'image_id': xray_image.id,
                'result_id': prediction.id,
                'prediction': prediction_result['predicted_class'],
                'confidence': prediction_result['confidence'],
                'confidence_level': confidence_level,
                'processing_time': round(processing_time, 3)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PredictionResultViewSet(viewsets.ModelViewSet):
    """
    View and delete prediction results
    GET /api/results/ - List all results for user
    GET /api/results/{id}/ - Get specific result
    DELETE /api/results/{id}/ - Delete specific result
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PredictionResultDetailSerializer
    
    def get_queryset(self):
        """Return results for current user only"""
        return PredictionResult.objects.filter(image__user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """Delete prediction result"""
        prediction = self.get_object()
        image = prediction.image
        
        # Delete files from storage if they exist
        if image.file_path:
            try:
                if default_storage.exists(image.file_path.name):
                    default_storage.delete(image.file_path.name)
            except:
                pass
        
        # Delete database records
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None):
        """Get detailed prediction result"""
        prediction = self.get_object()
        serializer = PredictionResultDetailSerializer(prediction)
        return Response(serializer.data)


class UserHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View user activity history
    GET /api/history/ - List user history
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserHistorySerializer
    
    def get_queryset(self):
        """Return history for current user only"""
        return UserHistory.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get history summary"""
        user_history = self.get_queryset()
        summary = {
            'total_uploads': user_history.filter(action_type='UPLOAD').count(),
            'total_analyses': user_history.filter(action_type='ANALYZE').count(),
            'total_views': user_history.filter(action_type='VIEW_RESULT').count(),
            'last_activity': user_history.first().timestamp if user_history.exists() else None
        }
        return Response(summary)


class ModelVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View model information
    GET /api/model-versions/ - List available models
    GET /api/model-versions/{id}/ - Get specific model
    """
    queryset = ModelVersion.objects.all()
    serializer_class = ModelVersionSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def user_detail(request, user_id):
    """
    Get or update user details
    GET /api/users/{id}/ - Get user details
    PUT /api/users/{id}/ - Update user details
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user is updating their own profile
    if request.user.id != user.id:
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        data = request.data
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """
    Change user password
    POST /api/change-password/
    """
    user = request.user
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    
    if not user.check_password(current_password):
        return Response(
            {'error': 'Current password is incorrect'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.set_password(new_password)
    user.save()
    
    # Invalidate current token and create new one
    try:
        user.auth_token.delete()
    except:
        pass
    
    token, created = Token.objects.get_or_create(user=user)
    
    return Response({
        'message': 'Password changed successfully',
        'token': token.key
    })
>>>>>>> 78d89b9f51d0fdbbd388483cf17b5a8558c3e832:xray_detector/api_views.py
