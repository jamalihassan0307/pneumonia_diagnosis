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


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ============================================================================
# AUTHENTICATION VIEWSETS & VIEWS
# ============================================================================

class CustomAuthToken(ObtainAuthToken):
    """Custom auth token view with user data"""
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })


class LogoutView(viewsets.ViewSet):
    """Logout view"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout user and delete token"""
        request.user.auth_token.delete()
        return Response({
            'status': 'success',
            'message': 'Logout successful'
        })


class UserRegistrationView(viewsets.ModelViewSet):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Register new user"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.create(user=user)
            return Response({
                'status': 'success',
                'message': 'User registered successfully',
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail(request, user_id):
    """Get user details"""
    user = get_object_or_404(User, id=user_id)
    if user != request.user and not request.user.is_staff:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    return Response(UserSerializer(user).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password"""
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    if not user.check_password(old_password):
        return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.save()
    return Response({'status': 'success', 'message': 'Password changed successfully'})


# ============================================================================
# X-RAY IMAGE UPLOAD & ANALYSIS
# ============================================================================

class XRayImageViewSet(viewsets.ModelViewSet):
    """Upload and manage X-ray images"""
    serializer_class = XRayImageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_queryset(self):
        """Get images for current user"""
        return XRayImage.objects.filter(user=self.request.user).order_by('-uploaded_at')
    
    @action(detail=False, methods=['post'], parser_classes=(MultiPartParser, FormParser))
    def upload(self, request):
        """Upload X-ray image and perform diagnosis"""
        start_time = time.time()
        
        # Validate image
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({
                'status': 'error',
                'message': 'No image provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file
        is_valid, error_msg = validate_image_file(image_file)
        if not is_valid:
            return Response({
                'status': 'error',
                'message': error_msg
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Save image to database
            img = Image.open(image_file)
            width, height = img.size
            format_type = img.format or 'JPEG'
            
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
            
            # Create history log
            UserHistory.objects.create(
                user=request.user,
                action_type='UPLOAD',
                image=xray_image,
                timestamp=timezone.now(),
                ip_address=get_client_ip(request)
            )
            
            # Perform diagnosis
            prediction_result = predict_pneumonia(image_file)
            
            # Save prediction result
            processing_time = time.time() - start_time
            
            prediction = PredictionResult.objects.create(
                image=xray_image,
                model_version=ModelVersion.objects.filter(is_active=True).first(),
                prediction_label=prediction_result.get('prediction', 'UNKNOWN'),
                confidence_score=prediction_result.get('confidence', 0.0),
                confidence_level='HIGH' if prediction_result.get('confidence', 0) > 0.8 else 'MEDIUM' if prediction_result.get('confidence', 0) > 0.5 else 'LOW',
                processing_time=processing_time,
                raw_predictions=json.dumps(prediction_result)
            )
            
            # Log analysis
            UserHistory.objects.create(
                user=request.user,
                action_type='ANALYZE',
                image=xray_image,
                prediction_result=prediction,
                timestamp=timezone.now(),
                ip_address=get_client_ip(request)
            )
            
            return Response({
                'status': 'success',
                'result_id': prediction.id,
                'image_id': xray_image.id,
                'prediction': prediction.prediction_label,
                'confidence': float(prediction.confidence_score),
                'confidence_percentage': prediction.get_confidence_percentage(),
                'confidence_level': prediction.confidence_level,
                'processing_time': round(processing_time, 2)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Upload/diagnosis error: {str(e)}", exc_info=True)
            return Response({
                'status': 'error',
                'message': f'Analysis failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# PREDICTION RESULTS
# ============================================================================

class PredictionResultViewSet(viewsets.ReadOnlyModelViewSet):
    """View prediction results"""
    serializer_class = PredictionResultSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Get predictions for current user"""
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
        """Use detailed serializer for retrieve"""
        if self.action == 'retrieve':
            return PredictionResultDetailSerializer
        return self.serializer_class
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get user's prediction statistics"""
        queryset = self.get_queryset()
        
        total = queryset.count()
        pneumonia = queryset.filter(prediction_label='PNEUMONIA').count()
        normal = queryset.filter(prediction_label='NORMAL').count()
        
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
# USER HISTORY
# ============================================================================

class UserHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """View user activity history"""
    serializer_class = UserHistorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Get history for current user"""
        return UserHistory.objects.filter(
            user=self.request.user
        ).order_by('-timestamp')


# ============================================================================
# MODEL VERSION
# ============================================================================

class ModelVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """View available model versions"""
    queryset = ModelVersion.objects.all()
    serializer_class = ModelVersionSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get currently active model version"""
        model = ModelVersion.objects.filter(is_active=True).first()
        if model:
            return Response(ModelVersionSerializer(model).data)
        return Response({'error': 'No active model'}, status=status.HTTP_404_NOT_FOUND)
