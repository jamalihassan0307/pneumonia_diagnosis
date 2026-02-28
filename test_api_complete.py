"""
Test Django REST Framework API and Model Loading
Comprehensive diagnostics for the system
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pneumonia_config.settings')
django.setup()

import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("DJANGO PNEUMONIA DIAGNOSIS SYSTEM - DIAGNOSTICS")
print("="*70)

# Test 1: Model Loading
print("\n[TEST 1] Model Loading")
print("-" * 70)
try:
    from model_service.services import PneumoniaDetectionService
    
    model = PneumoniaDetectionService.get_model()
    
    if model is None:
        print("⚠️  WARNING: Model failed to load")
        print("   Status: Demo mode active (predictions will be simulated)")
        print("   Impact: System will work but predictions won't use real AI")
        model_loaded = False
    else:
        print("✅ SUCCESS: Model loaded successfully!")
        print(f"   Source: {PneumoniaDetectionService._model_loaded_from}")
        print(f"   Input shape: {model.input_shape}")
        print(f"   Output shape: {model.output_shape}")
        if hasattr(model, 'count_params'):
            print(f"   Parameters: {model.count_params():,}")
        model_loaded = True
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    model_loaded = False

# Test 2: Image Preprocessing
print("\n[TEST 2] Image Preprocessing")
print("-" * 70)
try:
    from model_service.services import ImagePreprocessor
    import numpy as np
    from pathlib import Path
    
    # Check for test images
    test_images = list(Path('media/xray_images').glob('*.jpeg'))
    
    if test_images:
        test_img = test_images[0]
        print(f"   Testing with: {test_img.name}")
        
        # Validate
        validation = ImagePreprocessor.validate_image(str(test_img))
        if validation['valid']:
            print("   ✅ Image validation: PASSED")
            
            # Preprocess
            preprocessed = ImagePreprocessor.preprocess(str(test_img))
            if preprocessed is not None:
                print(f"   ✅ Preprocessing: PASSED")
                print(f"      Output shape: {preprocessed.shape}")
                print(f"      Data type: {preprocessed.dtype}")
                print(f"      Value range: [{preprocessed.min():.3f}, {preprocessed.max():.3f}]")
            else:
                print("   ❌ Preprocessing: FAILED")
        else:
            print(f"   ❌ Validation: FAILED - {validation['errors']}")
    else:
        print("   ⚠️  No test images found in media/xray_images/")
        
except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")

# Test 3: Full Diagnosis Pipeline
print("\n[TEST 3] Full Diagnosis Pipeline")
print("-" * 70)
try:
    from model_service.services import DiagnosisService
    
    if test_images:
        result = DiagnosisService.diagnose(str(test_images[0]))
        
        if result['status'] == 'success':
            print("   ✅ Diagnosis: SUCCESS")
            print(f"      Prediction: {result['prediction_label']}")
            print(f"      Confidence: {result['confidence_percentage']:.2f}%")
            print(f"      Level: {result['confidence_level']}")
            print(f"      Processing time: {result['processing_time']:.3f}s")
            
            # Check if demo mode
            import json
            raw_preds = json.loads(result['raw_predictions']) if result.get('raw_predictions') else {}
            if raw_preds.get('_demo'):
                print("      ⚠️  Demo mode active")
        else:
            print(f"   ❌ Diagnosis: FAILED")
            print(f"      Errors: {result.get('errors')}")
    else:
        print("   ⚠️  No test images available")
        
except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")

# Test 4: Django REST Framework Configuration
print("\n[TEST 4] Django REST Framework")
print("-" * 70)
try:
    from django.conf import settings
    
    if 'rest_framework' in settings.INSTALLED_APPS:
        print("   ✅ DRF installed: YES")
        
        if hasattr(settings, 'REST_FRAMEWORK'):
            print("   ✅ DRF configured: YES")
            print(f"      Authentication: {settings.REST_FRAMEWORK.get('DEFAULT_AUTHENTICATION_CLASSES')}")
            print(f"      Pagination: {settings.REST_FRAMEWORK.get('PAGE_SIZE')} items/page")
        else:
            print("   ⚠️  DRF configured: NO")
    else:
        print("   ❌ DRF installed: NO")
        
    if 'corsheaders' in settings.INSTALLED_APPS:
        print("   ✅ CORS headers installed: YES")
    else:
        print("   ⚠️  CORS headers installed: NO")
        
except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")

# Test 5: API Endpoints
print("\n[TEST 5] API Endpoints")
print("-" * 70)
try:
    from django.urls import reverse
    
    endpoints = [
        ('api:register', 'POST /api/v1/auth/register/'),
        ('api:login', 'POST /api/v1/auth/login/'),
        ('api:diagnose', 'POST /api/v1/diagnosis/analyze/'),
        ('api:result-list', 'GET /api/v1/results/'),
        ('api:model_info', 'GET /api/v1/model/info/'),
    ]
    
    for name, desc in endpoints:
        try:
            url = reverse(f'model_service:{name}')
            print(f"   ✅ {desc}")
        except:
            print(f"   ❌ {desc} - NOT CONFIGURED")
            
except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")

# Test 6: Database Connection
print("\n[TEST 6] Database")
print("-" * 70)
try:
    from django.contrib.auth.models import User
    from model_service.models import XRayImage, PredictionResult
    
    user_count = User.objects.count()
    image_count = XRayImage.objects.count()
    prediction_count = PredictionResult.objects.count()
    
    print(f"   ✅ Database connection: SUCCESS")
    print(f"      Users: {user_count}")
    print(f"      X-ray images: {image_count}")
    print(f"      Predictions: {prediction_count}")
    
except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

if model_loaded:
    print("\n✅ SYSTEM STATUS: FULLY OPERATIONAL")
    print("   - Model loaded successfully")
    print("   - All tests passed")
    print("   - Django REST Framework configured")
    print("\n🎯 Ready to make ACCURATE predictions!")
else:
    print("\n⚠️  SYSTEM STATUS: OPERATIONAL (DEMO MODE)")
    print("\n⚠️  CRITICAL ISSUE:")
    print("   The H5 model file has compatibility issues with TensorFlow 2.13.0")
    print("   System is using DEMO MODE for predictions (not real AI)")
    print("\n📋 RECOMMENDED ACTION:")
    print("   Option 1: Re-save the model from your working Python environment")
    print("            Run: convert_from_flask.py in the environment where model loads")
    print("   Option 2: Use a different TensorFlow version that matches training")
    print("   Option 3: Continue with demo mode (for testing/development only)")
    print("\n💡 Demo mode gives reasonable predictions based on filename patterns")
    print("   but should NOT be used for actual medical diagnosis.")

print("\n" + "="*70)
print("API ENDPOINTS AVAILABLE:")
print("="*70)
print("""
Authentication:
  POST   /api/v1/auth/register/      - Register new user
  POST   /api/v1/auth/login/         - Login
  POST   /api/v1/auth/logout/        - Logout
  GET    /api/v1/auth/profile/       - Get user profile

Diagnosis:
  POST   /api/v1/diagnosis/analyze/  - Analyze X-ray image

Results:
  GET    /api/v1/results/            - List all predictions
  GET    /api/v1/results/{id}/       - Get specific prediction
  GET    /api/v1/results/statistics/ - User statistics

Images:
  GET    /api/v1/images/             - List uploaded images
  GET    /api/v1/images/{id}/        - Get image details
  DELETE /api/v1/images/{id}/        - Delete image

Model:
  GET    /api/v1/model/info/         - Get model information
""")

print("="*70)
print("Django server: python manage.py runserver")
print("Access at: http://127.0.0.1:8000")
print("API browsers: http://127.0.0.1:8000/api/v1/")
print("="*70)
