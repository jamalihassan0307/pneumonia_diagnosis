"""
Django REST Framework Serializers for Pneumonia Diagnosis System
Handles API data serialization/deserialization
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import XRayImage, PredictionResult, UserHistory, ModelVersion
<<<<<<< HEAD:model_service/serializers.py
=======
import json
>>>>>>> 78d89b9f51d0fdbbd388483cf17b5a8558c3e832:xray_detector/serializers.py


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
<<<<<<< HEAD:model_service/serializers.py
        fields = ['id', 'username', 'email', 'date_joined']
=======
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
>>>>>>> 78d89b9f51d0fdbbd388483cf17b5a8558c3e832:xray_detector/serializers.py
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
<<<<<<< HEAD:model_service/serializers.py
        fields = ['username', 'email', 'password', 'password_confirm']
=======
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
>>>>>>> 78d89b9f51d0fdbbd388483cf17b5a8558c3e832:xray_detector/serializers.py
    
    def validate(self, data):
        """Validate passwords match"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords must match"})
        return data
    
    def create(self, validated_data):
        """Create user with hashed password"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
<<<<<<< HEAD:model_service/serializers.py
=======
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
>>>>>>> 78d89b9f51d0fdbbd388483cf17b5a8558c3e832:xray_detector/serializers.py
            password=validated_data['password']
        )
        return user


class ModelVersionSerializer(serializers.ModelSerializer):
    """Serializer for ModelVersion"""
    
    class Meta:
        model = ModelVersion
<<<<<<< HEAD:model_service/serializers.py
        fields = ['id', 'version', 'description', 'accuracy', 'training_date', 'is_active']
        read_only_fields = ['id']
=======
        fields = ['id', 'model_name', 'version', 'description', 'accuracy', 'precision', 'recall', 'f1_score', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
>>>>>>> 78d89b9f51d0fdbbd388483cf17b5a8558c3e832:xray_detector/serializers.py


class XRayImageSerializer(serializers.ModelSerializer):
    """Serializer for XRayImage model"""
    user = UserSerializer(read_only=True)
<<<<<<< HEAD:model_service/serializers.py
=======
    file_size_mb = serializers.SerializerMethodField()
>>>>>>> 78d89b9f51d0fdbbd388483cf17b5a8558c3e832:xray_detector/serializers.py
    
    class Meta:
        model = XRayImage
        fields = [
            'id', 'user', 'original_filename', 'stored_filename',
<<<<<<< HEAD:model_service/serializers.py
            'file_path', 'file_size', 'image_width', 'image_height',
            'format', 'uploaded_at'
        ]
        read_only_fields = ['id', 'stored_filename', 'uploaded_at']
=======
            'file_path', 'file_size', 'file_size_mb', 'image_width', 'image_height',
            'format', 'upload_time', 'is_preprocessed'
        ]
        read_only_fields = ['id', 'stored_filename', 'upload_time', 'file_size', 'image_width', 'image_height']
    
    def get_file_size_mb(self, obj):
        return obj.get_file_size_mb()
>>>>>>> 78d89b9f51d0fdbbd388483cf17b5a8558c3e832:xray_detector/serializers.py


class XRayImageUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading X-ray images"""
    image = serializers.ImageField(write_only=True)
    
    class Meta:
        model = XRayImage
        fields = ['image']
    
    def validate_image(self, value):
        """Validate uploaded image"""
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Image size exceeds 10 MB limit")
        
        # Check format
        if value.content_type not in ['image/jpeg', 'image/png']:
            raise serializers.ValidationError("Only JPEG and PNG formats are supported")
        
        return value


class PredictionResultSerializer(serializers.ModelSerializer):
    """Serializer for PredictionResult model"""
    image = XRayImageSerializer(read_only=True)
    model_version = ModelVersionSerializer(read_only=True)
    confidence_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = PredictionResult
        fields = [
            'id', 'image', 'model_version', 'prediction_label',
            'confidence_score', 'confidence_percentage', 'confidence_level',
<<<<<<< HEAD:model_service/serializers.py
            'processing_time', 'raw_predictions', 'created_at'
=======
            'processing_time', 'created_at'
>>>>>>> 78d89b9f51d0fdbbd388483cf17b5a8558c3e832:xray_detector/serializers.py
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_confidence_percentage(self, obj):
        """Get confidence as percentage"""
        return obj.get_confidence_percentage()


class PredictionResultDetailSerializer(PredictionResultSerializer):
    """Detailed serializer with parsed raw predictions"""
    raw_predictions_parsed = serializers.SerializerMethodField()
<<<<<<< HEAD:model_service/serializers.py
    is_demo_mode = serializers.SerializerMethodField()
    
    class Meta(PredictionResultSerializer.Meta):
        fields = PredictionResultSerializer.Meta.fields + [
            'raw_predictions_parsed', 'is_demo_mode'
        ]
    
    def get_raw_predictions_parsed(self, obj):
        """Parse raw predictions JSON"""
        import json
=======
    
    class Meta(PredictionResultSerializer.Meta):
        fields = PredictionResultSerializer.Meta.fields + ['raw_predictions_parsed']
    
    def get_raw_predictions_parsed(self, obj):
        """Parse raw predictions JSON"""
>>>>>>> 78d89b9f51d0fdbbd388483cf17b5a8558c3e832:xray_detector/serializers.py
        try:
            return json.loads(obj.raw_predictions) if obj.raw_predictions else {}
        except:
            return {}
<<<<<<< HEAD:model_service/serializers.py
    
    def get_is_demo_mode(self, obj):
        """Check if prediction was made in demo mode"""
        raw_preds = self.get_raw_predictions_parsed(obj)
        return raw_preds.get('_demo', False)
=======
>>>>>>> 78d89b9f51d0fdbbd388483cf17b5a8558c3e832:xray_detector/serializers.py


class DiagnosisRequestSerializer(serializers.Serializer):
    """Serializer for diagnosis API request"""
    image = serializers.ImageField()
    
    def validate_image(self, value):
        """Validate uploaded image"""
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Image size exceeds 10 MB limit")
        
        if value.content_type not in ['image/jpeg', 'image/png']:
            raise serializers.ValidationError("Only JPEG and PNG formats are supported")
        
        return value


class DiagnosisResponseSerializer(serializers.Serializer):
    """Serializer for diagnosis API response"""
    status = serializers.ChoiceField(choices=['success', 'error'])
    result_id = serializers.IntegerField(required=False)
    prediction = serializers.CharField(required=False)
    confidence = serializers.FloatField(required=False)
    confidence_percentage = serializers.FloatField(required=False)
    confidence_level = serializers.CharField(required=False)
    processing_time = serializers.FloatField(required=False)
<<<<<<< HEAD:model_service/serializers.py
    is_demo_mode = serializers.BooleanField(required=False)
=======
>>>>>>> 78d89b9f51d0fdbbd388483cf17b5a8558c3e832:xray_detector/serializers.py
    message = serializers.CharField(required=False)
    errors = serializers.ListField(child=serializers.CharField(), required=False)


class UserHistorySerializer(serializers.ModelSerializer):
    """Serializer for UserHistory model"""
    user = UserSerializer(read_only=True)
    image = XRayImageSerializer(read_only=True)
    prediction_result = PredictionResultSerializer(read_only=True)
    
    class Meta:
        model = UserHistory
        fields = [
            'id', 'user', 'action_type', 'timestamp',
            'ip_address', 'image', 'prediction_result'
        ]
        read_only_fields = ['id', 'timestamp']
