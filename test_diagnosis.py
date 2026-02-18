#!/usr/bin/env python
"""
Test script to verify the diagnosis pipeline works end-to-end
"""

import os
import sys
import django
from pathlib import Path
from PIL import Image
import numpy as np

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pneumonia_config.settings')
django.setup()

from model_service.services import DiagnosisService, ImagePreprocessor

def test_diagnosis():
    """Test the complete diagnosis pipeline"""
    
    # Create a test X-ray image
    print('Creating test X-ray image...')
    test_image_path = Path('test_xray_sample.jpg')
    
    # Create a simple grayscale test image
    test_img_array = np.random.randint(50, 200, (224, 224), dtype=np.uint8)
    test_img = Image.fromarray(test_img_array, mode='L')
    test_img.save(str(test_image_path))
    print(f'✓ Test image created at {test_image_path}')
    
    # Test diagnosis pipeline
    print('\nRunning diagnosis pipeline...')
    result = DiagnosisService.diagnose(str(test_image_path))
    
    if result['status'] == 'success':
        print('\n' + '='*60)
        print('✅ DIAGNOSIS SUCCESSFUL')
        print('='*60)
        pred = result['prediction']
        print('Prediction: {}'.format(pred['label']))
        print('Confidence: {:.2f}%'.format(pred['confidence_percentage']))
        print('Confidence Level: {}'.format(pred['confidence_level']))
        print('Processing Time: {:.3f}s'.format(result['total_time']))
        print('='*60)
        
        # Clean up
        test_image_path.unlink()
        return True
    else:
        print('❌ Error: {}'.format(result['errors']))
        # Clean up
        if test_image_path.exists():
            test_image_path.unlink()
        return False

if __name__ == '__main__':
    success = test_diagnosis()
    sys.exit(0 if success else 1)
