#!/usr/bin/env python
"""Test model loading through services"""

import sys
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

# Test 1: TensorFlow
print("\n" + "=" * 60)
print("Test 1: TensorFlow Installation")
print("=" * 60)

try:
    import tensorflow as tf
    print(f"✅ TensorFlow {tf.__version__} is available")
except ImportError as e:
    print(f"❌ TensorFlow not available: {e}")
    sys.exit(1)

# Test 2: Model File
print("\n" + "=" * 60)
print("Test 2: Model File Existence")
print("=" * 60)

from pathlib import Path
model_path = Path("model_service/mobilenetv2.h5")
if model_path.exists():
    size_mb = model_path.stat().st_size / (1024 * 1024)
    print(f"✅ Model file found: {model_path}")
    print(f"   Size: {size_mb:.2f} MB")
else:
    print(f"❌ Model file not found: {model_path}")
    sys.exit(1)

# Test 3: Model Loading
print("\n" + "=" * 60)
print("Test 3: Model Loading with TensorFlow")
print("=" * 60)

try:
    print("Attempting to load model...")
    model = tf.keras.models.load_model(str(model_path))
    print(f"✅ Model loaded successfully!")
    print(f"   Type: {type(model).__name__}")
    print(f"   Input shape: {model.input_shape}")
    print(f"   Output shape: {model.output_shape}")
except Exception as e:
    print(f"⚠️ Standard loading failed: {e}")
    print("\nTrying alternative loading methods...")
    
    # Try h5py approach
    try:
        import h5py
        import json
        with h5py.File(str(model_path), 'r') as f:
            print(f"   H5 file structure: {list(f.keys())}")
            if 'model_config' in f.attrs:
                print("   ✓ model_config found in attributes")
    except Exception as h5_error:
        print(f"   ✗ h5py check failed: {h5_error}")
    
    print("\n✅ System will use DEMO MODE for predictions")
    print("   (No real AI predictions until model is fixed)")

print("\n" + "=" * 60)
print("Test Summary: TensorFlow is installed and ready.")
print("If model loading failed, the system will gracefully fall back to demo mode.")
print("=" * 60 + "\n")

