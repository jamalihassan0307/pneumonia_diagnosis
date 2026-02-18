#!/usr/bin/env python
"""
Comprehensive Model Diagnostic and Testing Script
Tests the pneumonia diagnosis model against real X-ray images
and diagnoses why predictions may be incorrect
"""

import os
import sys
import django
from pathlib import Path
import numpy as np
from PIL import Image
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pneumonia_config.settings')
django.setup()

from model_service.services import DiagnosisService, PneumoniaDetectionService, ImagePreprocessor

def analyze_model():
    """Analyze the loaded model architecture and training info"""
    print("\n" + "="*70)
    print("MODEL ARCHITECTURE ANALYSIS")
    print("="*70)
    
    model = PneumoniaDetectionService.get_model()
    
    if model is None:
        print("❌ Model failed to load")
        return False
    
    print(f"\nModel Type: {type(model).__name__}")
    print(f"Input Shape: {model.input_shape}")
    print(f"Output Shape: {model.output_shape}")
    print(f"Total Parameters: {model.count_params():,}")
    print(f"Layers: {len(model.layers)}")
    
    # Check if it's a loaded H5 file or auto-created model
    print("\nModel Source Analysis:")
    if 'imagenet' in str(model.name).lower():
        print("⚠️  WARNING: This is a fresh MobileNetV2 (ImageNet weights)")
        print("   → NOT trained on pneumonia data")
        print("   → Will give INCORRECT predictions")
    
    print("\nRecommendation: Use the trained H5 model file instead")
    return True

def test_on_real_image(image_path):
    """Test the model on a real X-ray image"""
    print("\n" + "="*70)
    print(f"TESTING ON REAL IMAGE: {Path(image_path).name}")
    print("="*70)
    
    # Check if file exists
    if not Path(image_path).exists():
        print(f"❌ Image not found: {image_path}")
        return False
    
    # Get image info
    img = Image.open(image_path)
    print(f"\nImage Properties:")
    print(f"  Size: {img.size}")
    print(f"  Mode: {img.mode}")
    print(f"  Format: {img.format}")
    
    # Analyze filename
    filename = Path(image_path).stem
    print(f"\nFilename Analysis:")
    print(f"  Filename: {Path(image_path).name}")
    
    if 'bacteria' in filename.lower() or 'pneumonia' in filename.lower():
        print(f"  Expected: PNEUMONIA ← Should predict this")
    elif 'normal' in filename.lower():
        print(f"  Expected: NORMAL ← Should predict this")
    else:
        print(f"  Expected: UNKNOWN (based on filename)")
    
    # Run diagnosis
    print(f"\nRunning diagnosis...")
    result = DiagnosisService.diagnose(image_path)
    
    if result['status'] != 'success':
        print(f"❌ Diagnosis failed: {result['errors']}")
        return False
    
    # Print results
    pred = result['prediction']
    print(f"\n{'─'*70}")
    print(f"PREDICTION RESULT:")
    print(f"{'─'*70}")
    print(f"Predicted Class:     {pred['label']}")
    print(f"Confidence:          {pred['confidence_percentage']:.2f}%")
    print(f"Confidence Level:    {pred['confidence_level']}")
    print(f"Processing Time:     {result['total_time']:.3f}s")
    print(f"Raw Predictions:     {pred['raw_predictions']}")
    
    # Check if prediction seems reasonable
    print(f"\n{'─'*70}")
    
    if 'bacteria' in filename.lower():
        if pred['label'] == 'PNEUMONIA':
            print("✅ CORRECT: File shows bacteria, predicted PNEUMONIA")
            return True
        else:
            print("❌ WRONG: File shows bacteria (PNEUMONIA expected), but predicted NORMAL")
            print("   → Model is NOT trained on pneumonia data!")
            return False
    elif 'normal' in filename.lower():
        if pred['label'] == 'NORMAL':
            print("✅ CORRECT: File shows normal, predicted NORMAL")
            return True
        else:
            print("❌ WRONG: File shows normal, but predicted PNEUMONIA")
            return False
    
    return True

def check_h5_file():
    """Check the original H5 model file"""
    print("\n" + "="*70)
    print("ORIGINAL H5 MODEL FILE ANALYSIS")
    print("="*70)
    
    h5_path = Path('model_service/mobilenetv2.h5')
    
    if not h5_path.exists():
        print(f"❌ H5 file not found: {h5_path}")
        return False
    
    print(f"\nFile: {h5_path}")
    print(f"Size: {h5_path.stat().st_size / (1024*1024):.2f} MB")
    print(f"Status: File exists")
    
    # Try to read H5 structure
    try:
        import h5py
        with h5py.File(str(h5_path), 'r') as f:
            print(f"\nH5 File Structure:")
            print(f"  Root keys: {list(f.keys())}")
            
            if 'model_config' in f.attrs:
                config = json.loads(f.attrs['model_config'])
                print(f"  Has model_config: Yes")
                print(f"  Config size: {len(str(config))} bytes")
            
            if 'model_weights' in f:
                print(f"  Has model_weights: Yes")
            
            if 'training_config' in f.attrs:
                print(f"  Has training_config: Yes")
        
        print(f"\n✓ H5 file is valid and readable")
        return True
        
    except Exception as e:
        print(f"\n❌ Error reading H5 file: {e}")
        return False

def main():
    """Run all diagnostics"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "PNEUMONIA DIAGNOSIS MODEL - COMPREHENSIVE DIAGNOSTIC".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    # 1. Analyze model
    analyze_model()
    
    # 2. Check H5 file
    check_h5_file()
    
    # 3. Test on the specific image
    test_image = Path('media/xray_images/person23_bacteria_89.jpeg')
    if test_image.exists():
        test_on_real_image(str(test_image))
    else:
        print(f"\n⚠️  Test image not found: {test_image}")
        print("   Checking for similar images...")
        
        xray_dir = Path('media/xray_images')
        if xray_dir.exists():
            images = list(xray_dir.glob('*.jpeg'))[:1]
            if images:
                test_on_real_image(str(images[0]))
    
    # 4. Summary
    print("\n" + "="*70)
    print("DIAGNOSTIC SUMMARY")
    print("="*70)
    print("""
The current model appears to be a generic MobileNetV2 (ImageNet weights).
This model is NOT trained on pneumonia X-ray data.

ISSUE: 
  • Auto-created model because original H5 file had compatibility issues
  • Generic model gives wrong predictions on medical data
  • Files named "bacteria" are predicted as "NORMAL"

SOLUTION OPTIONS:

1. Fix Original H5 File (RECOMMENDED)
   ✓ Try converting to SavedModel format
   ✓ Try loading with TensorFlow compatibility options
   ✓ Manually rebuild from weights if possible

2. Retrain Model
   ✓ Get training data (pneumonia vs normal X-rays)
   ✓ Fine-tune MobileNetV2 on medical data
   ✓ Save in modern format (SavedModel, not H5)

3. Quick Fix
   ✓ Use demo mode (realistic predictions without AI)
   ✓ Acknowledge in UI that real model needs fixing
""")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    main()
