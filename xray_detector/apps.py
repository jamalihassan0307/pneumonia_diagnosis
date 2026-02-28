from django.apps import AppConfig


class XrayDetectorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'xray_detector'
    verbose_name = 'X-Ray Pneumonia Detector'
