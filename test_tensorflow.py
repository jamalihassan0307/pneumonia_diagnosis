#!/usr/bin/env python
"""Test TensorFlow installation and model loading"""

import sys
try:
    import tensorflow as tf
    print(f"✅ TensorFlow {tf.__version__} INSTALLED")
    print(f"✅ Keras available: {hasattr(tf, 'keras')}")
    print(f"✅ Python: {sys.version}")
    
    # Test model loading
    try:
        model_path = "model_service/mobilenetv2.h5"
        model = tf.keras.models.load_model(model_path)
        print(f"✅ Model loaded successfully from {model_path}")
        print(f"   Input shape: {model.input_shape}")
        print(f"   Output shape: {model.output_shape}")
    except Exception as e:
        print(f"⚠️ Model load error: {e}")
        
except ModuleNotFoundError as e:
    print(f"❌ TensorFlow NOT installed: {e}")
    sys.exit(1)
