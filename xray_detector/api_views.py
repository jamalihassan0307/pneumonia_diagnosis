"""
API Views for Pneumonia Diagnosis System
REST API endpoints for authentication, image upload, analysis, and history
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import time
import json
import os

from .models import XRayImage, PredictionResult, UserHistory, ModelVersion, ProcessingLog
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    XRayImageSerializer, XRayImageUploadSerializer,
    PredictionResultSerializer, PredictionResultDetailSerializer,
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


class PredictionResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View prediction results
    GET /api/results/ - List all results for user
    GET /api/results/{id}/ - Get specific result
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PredictionResultDetailSerializer
    
    def get_queryset(self):
        """Return results for current user only"""
        return PredictionResult.objects.filter(image__user=self.request.user)
    
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
    View model information (public access)
    GET /api/model-versions/ - List available models
    GET /api/model-versions/{id}/ - Get specific model
    """
    queryset = ModelVersion.objects.all()
    serializer_class = ModelVersionSerializer
    permission_classes = [permissions.AllowAny]


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
