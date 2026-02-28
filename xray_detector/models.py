"""
Django Models for Pneumonia Diagnosis System
Follows SDD database schema and SRS requirements
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.utils import timezone
import os


class ModelVersion(models.Model):
    """
    Store information about different model versions
    Supports easy model updates and version tracking
    """
    model_name = models.CharField(max_length=100, unique=True)
    model_path = models.FileField(upload_to='models/')
    version = models.CharField(max_length=50)
    accuracy = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    precision = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    recall = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    f1_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    input_size = models.CharField(max_length=20, default='224x224')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Model Version'
        verbose_name_plural = 'Model Versions'
    
    def __str__(self):
        return f"{self.model_name} v{self.version}"


class XRayImage(models.Model):
    """
    Store uploaded X-ray image metadata and file information
    Based on database schema from SDD
    """
    IMAGE_FORMAT_CHOICES = [
        ('JPEG', 'JPEG'),
        ('PNG', 'PNG'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='xray_images')
    original_filename = models.CharField(max_length=255)
    stored_filename = models.CharField(max_length=255)
    file_path = models.ImageField(
        upload_to='xray_images/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    file_size = models.IntegerField()  # in bytes
    upload_time = models.DateTimeField(auto_now_add=True)
    image_width = models.IntegerField(null=True, blank=True)
    image_height = models.IntegerField(null=True, blank=True)
    format = models.CharField(max_length=10, choices=IMAGE_FORMAT_CHOICES)
    is_preprocessed = models.BooleanField(default=False)
    preprocessing_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-upload_time']
        verbose_name = 'X-Ray Image'
        verbose_name_plural = 'X-Ray Images'
        indexes = [
            models.Index(fields=['user', '-upload_time']),
        ]
    
    def __str__(self):
        return f"{self.original_filename} - {self.user.username}"
    
    def get_file_size_mb(self):
        """Convert file size to MB"""
        return round(self.file_size / (1024 * 1024), 2)


class PredictionResult(models.Model):
    """
    Store AI prediction results for X-ray images
    Contains classification, confidence, and processing metrics
    """
    PREDICTION_CHOICES = [
        ('NORMAL', 'Normal'),
        ('PNEUMONIA', 'Pneumonia'),
    ]
    
    CONFIDENCE_LEVEL_CHOICES = [
        ('HIGH', 'High Confidence (>95%)'),
        ('MODERATE', 'Moderate Confidence (80-95%)'),
        ('LOW', 'Low Confidence (<80%)'),
    ]
    
    image = models.OneToOneField(XRayImage, on_delete=models.CASCADE, related_name='prediction')
    prediction_label = models.CharField(max_length=20, choices=PREDICTION_CHOICES)
    confidence_score = models.DecimalField(
        max_digits=5, 
        decimal_places=4,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    confidence_level = models.CharField(max_length=20, choices=CONFIDENCE_LEVEL_CHOICES)
    processing_time = models.DecimalField(max_digits=8, decimal_places=3)  # in seconds
    created_at = models.DateTimeField(auto_now_add=True)
    model_version = models.ForeignKey(ModelVersion, on_delete=models.SET_NULL, null=True, blank=True)
    raw_predictions = models.TextField()  # JSON string storing both class predictions
    is_archived = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Prediction Result'
        verbose_name_plural = 'Prediction Results'
        indexes = [
            models.Index(fields=['image', '-created_at']),
            models.Index(fields=['prediction_label']),
        ]
    
    def __str__(self):
        return f"{self.prediction_label} - {self.image.original_filename}"
    
    def get_confidence_percentage(self):
        """Return confidence as percentage"""
        return round(float(self.confidence_score) * 100, 2)


class UserHistory(models.Model):
    """
    Basic history log for authenticated users
    Tracks user actions and provides audit trail
    """
    ACTION_CHOICES = [
        ('UPLOAD', 'Image Upload'),
        ('ANALYZE', 'Image Analysis'),
        ('VIEW_RESULT', 'View Result'),
        ('DELETE_RESULT', 'Delete Result'),
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_history')
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    image = models.ForeignKey(XRayImage, on_delete=models.SET_NULL, null=True, blank=True)
    prediction_result = models.ForeignKey(PredictionResult, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    additional_data = models.TextField(blank=True)  # JSON for extra details
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'User History'
        verbose_name_plural = 'User History'
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action_type} - {self.timestamp}"


class SystemConfig(models.Model):
    """
    Store system-wide configuration settings
    Allows runtime configuration without code changes
    """
    config_key = models.CharField(max_length=100, unique=True)
    config_value = models.TextField()
    description = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'System Configuration'
        verbose_name_plural = 'System Configurations'
    
    def __str__(self):
        return f"{self.config_key}"
    
    @classmethod
    def get_config(cls, key, default=None):
        """Get configuration value by key"""
        try:
            config = cls.objects.get(config_key=key)
            return config.config_value
        except cls.DoesNotExist:
            return default


class ProcessingLog(models.Model):
    """
    Log for image processing operations
    Helps track preprocessing steps and troubleshoot issues
    """
    image = models.ForeignKey(XRayImage, on_delete=models.CASCADE, related_name='processing_logs')
    step_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('SUCCESS', 'Success'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
    ])
    message = models.TextField()
    execution_time = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Processing Log'
        verbose_name_plural = 'Processing Logs'
    
    def __str__(self):
        return f"{self.image.original_filename} - {self.step_name}"
