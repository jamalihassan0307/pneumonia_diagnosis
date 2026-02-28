"""
Management command to set up initial data for Pneumonia Diagnosis System
Run: python manage.py setup_initial_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from xray_detector.models import ModelVersion, SystemConfig


class Command(BaseCommand):
    help = 'Set up initial data for Pneumonia Diagnosis System'

    def handle(self, *args, **options):
        # Create default model version
        if not ModelVersion.objects.exists():
            ModelVersion.objects.create(
                model_name='MobileNetV2',
                model_path='models/mobilenetv2_pneumonia_model.h5',
                version='1.0.0',
                accuracy=0.9450,
                precision=0.9320,
                recall=0.9560,
                f1_score=0.9438,
                input_size='224x224',
                is_active=True,
                description='Pre-trained MobileNetV2 model for pneumonia detection'
            )
            self.stdout.write(self.style.SUCCESS('Created default ModelVersion'))

        # Create system configurations
        configs = [
            ('MAX_FILE_SIZE', '16777216', 'Maximum file size in bytes (16MB)'),
            ('PREDICTION_CONFIDENCE_THRESHOLD', '0.5', 'Threshold for pneumonia prediction'),
            ('SESSION_TIMEOUT', '3600', 'Session timeout in seconds'),
            ('ENABLE_HISTORY_LOGGING', 'true', 'Enable user activity logging'),
        ]
        
        for key, value, description in configs:
            SystemConfig.objects.get_or_create(
                config_key=key,
                defaults={'config_value': value, 'description': description}
            )
        
        self.stdout.write(self.style.SUCCESS('Created system configurations'))
        self.stdout.write(self.style.SUCCESS('Initial data setup completed successfully!'))
