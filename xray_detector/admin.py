"""
Django Admin Interface for Pneumonia Diagnosis System
Provides management interface for medical professionals and administrators
"""

from django.contrib import admin
from .models import ModelVersion, XRayImage, PredictionResult, UserHistory, SystemConfig, ProcessingLog


@admin.register(ModelVersion)
class ModelVersionAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'version', 'accuracy', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['model_name', 'version']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Model Information', {
            'fields': ('model_name', 'version', 'model_path', 'description')
        }),
        ('Performance Metrics', {
            'fields': ('accuracy', 'precision', 'recall', 'f1_score', 'input_size')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(XRayImage)
class XRayImageAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'user', 'format', 'upload_time', 'get_file_size_mb']
    list_filter = ['format', 'upload_time', 'is_preprocessed']
    search_fields = ['original_filename', 'user__username']
    readonly_fields = ['stored_filename', 'upload_time', 'file_size']
    fieldsets = (
        ('File Information', {
            'fields': ('original_filename', 'stored_filename', 'file_path', 'format')
        }),
        ('Upload Details', {
            'fields': ('user', 'file_size', 'upload_time')
        }),
        ('Image Metadata', {
            'fields': ('image_width', 'image_height')
        }),
        ('Processing', {
            'fields': ('is_preprocessed', 'preprocessing_notes')
        }),
    )


@admin.register(PredictionResult)
class PredictionResultAdmin(admin.ModelAdmin):
    list_display = ['image', 'prediction_label', 'confidence_level', 'get_confidence_percentage', 'created_at']
    list_filter = ['prediction_label', 'confidence_level', 'created_at']
    search_fields = ['image__original_filename']
    readonly_fields = ['created_at', 'processing_time']
    fieldsets = (
        ('Image & Prediction', {
            'fields': ('image', 'prediction_label')
        }),
        ('Confidence', {
            'fields': ('confidence_score', 'confidence_level')
        }),
        ('Model Information', {
            'fields': ('model_version', 'processing_time')
        }),
        ('Additional Data', {
            'fields': ('raw_predictions', 'notes', 'is_archived')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserHistory)
class UserHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'timestamp', 'ip_address']
    list_filter = ['action_type', 'timestamp', 'user']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['timestamp']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'timestamp')
        }),
        ('Action Details', {
            'fields': ('action_type', 'ip_address')
        }),
        ('Related Data', {
            'fields': ('image', 'prediction_result')
        }),
        ('Additional Data', {
            'fields': ('additional_data',)
        }),
    )


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ['config_key', 'config_value', 'updated_at']
    search_fields = ['config_key']
    readonly_fields = ['updated_at']


@admin.register(ProcessingLog)
class ProcessingLogAdmin(admin.ModelAdmin):
    list_display = ['image', 'step_name', 'status', 'execution_time', 'created_at']
    list_filter = ['status', 'step_name', 'created_at']
    search_fields = ['image__original_filename', 'step_name']
    readonly_fields = ['created_at']

