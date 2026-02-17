"""
Django Admin Configuration for Pneumonia Diagnosis System
"""

from django.contrib import admin
from .models import (
    ModelVersion, XRayImage, PredictionResult,
    UserHistory, SystemConfig, ProcessingLog
)


@admin.register(ModelVersion)
class ModelVersionAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'version', 'accuracy', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('model_name', 'version')
    
    fieldsets = (
        ('Model Information', {
            'fields': ('model_name', 'version', 'model_path', 'input_size')
        }),
        ('Performance Metrics', {
            'fields': ('accuracy', 'precision', 'recall', 'f1_score')
        }),
        ('Status', {
            'fields': ('is_active', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(XRayImage)
class XRayImageAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'user', 'format', 'upload_time', 'is_preprocessed')
    list_filter = ('format', 'upload_time', 'is_preprocessed')
    readonly_fields = ('upload_time', 'file_size', 'image_width', 'image_height')
    search_fields = ('original_filename', 'user__username')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'original_filename', 'stored_filename')
        }),
        ('File Details', {
            'fields': ('file_path', 'file_size', 'format')
        }),
        ('Image Properties', {
            'fields': ('image_width', 'image_height')
        }),
        ('Processing', {
            'fields': ('is_preprocessed', 'preprocessing_notes')
        }),
        ('Upload Information', {
            'fields': ('upload_time',),
            'classes': ('collapse',)
        }),
    )


@admin.register(PredictionResult)
class PredictionResultAdmin(admin.ModelAdmin):
    list_display = (
        'image', 'prediction_label', 'confidence_score',
        'confidence_level', 'created_at'
    )
    list_filter = ('prediction_label', 'confidence_level', 'created_at')
    readonly_fields = ('created_at', 'model_version')
    search_fields = ('image__original_filename', 'prediction_label')
    
    fieldsets = (
        ('Image & Result', {
            'fields': ('image', 'prediction_label')
        }),
        ('Confidence Metrics', {
            'fields': ('confidence_score', 'confidence_level')
        }),
        ('Model & Processing', {
            'fields': ('model_version', 'processing_time')
        }),
        ('Additional Information', {
            'fields': ('raw_predictions', 'notes', 'is_archived'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserHistory)
class UserHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'timestamp', 'ip_address')
    list_filter = ('action_type', 'timestamp')
    readonly_fields = ('timestamp',)
    search_fields = ('user__username', 'ip_address')
    
    fieldsets = (
        ('User Action', {
            'fields': ('user', 'action_type', 'timestamp')
        }),
        ('Related Objects', {
            'fields': ('image', 'prediction_result'),
            'classes': ('collapse',)
        }),
        ('Additional Info', {
            'fields': ('ip_address', 'additional_data'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProcessingLog)
class ProcessingLogAdmin(admin.ModelAdmin):
    list_display = ('image', 'step_name', 'status', 'created_at')
    list_filter = ('status', 'step_name', 'created_at')
    readonly_fields = ('created_at',)
    search_fields = ('image__original_filename', 'step_name')
    
    fieldsets = (
        ('Image & Step', {
            'fields': ('image', 'step_name')
        }),
        ('Processing Details', {
            'fields': ('status', 'message')
        }),
        ('Performance', {
            'fields': ('execution_time',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('config_key', 'config_value', 'updated_at')
    readonly_fields = ('updated_at',)
    search_fields = ('config_key',)
    
    fieldsets = (
        ('Configuration', {
            'fields': ('config_key', 'config_value', 'description')
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
