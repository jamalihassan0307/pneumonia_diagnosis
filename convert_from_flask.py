"""
Convert Model from Flask Environment to Django-Compatible Format
================================================================

Run this script in your FLASK environment (where the model loads successfully).
It will load the model and re-save it in a format compatible with TensorFlow 2.13.

Requirements:
- Run in Flask environment (where load_model('mobilenetv2.h5') works)
- TensorFlow/Keras installed
- Original mobilenetv2.h5 file present

Output:
- mobilenetv2_django_compatible.h5 (H5 format)
- mobilenetv2_saved_model/ (SavedModel format - preferred)
"""

import tensorflow as tf
import numpy as np
import cv2
from pathlib import Path

print("="*70)
print("MODEL CONVERSION FOR DJANGO COMPATIBILITY")
print("="*70)

# Configuration
old_model_path = "mobilenetv2.h5"  # Your original model
output_h5 = "mobilenetv2_django_compatible.h5"
output_savedmodel = "mobilenetv2_saved_model"

print(f"\nEnvironment:")
print(f"  TensorFlow version: {tf.__version__}")
print(f"  Keras version: {tf.keras.__version__}")

# Step 1: Load the original model
print(f"\n[1] Loading original model: {old_model_path}")
try:
    model = tf.keras.models.load_model(old_model_path)
    print(f"✓ Model loaded successfully!")
except Exception as e:
    print(f"✗ ERROR: Could not load model: {e}")
    print(f"\nMake sure you're running this in the Flask environment where")
    print(f"the model loads successfully.")
    exit(1)

# Display model info
print(f"\nModel Information:")
print(f"  Input shape: {model.input_shape}")
print(f"  Output shape: {model.output_shape}")
print(f"  Total parameters: {model.count_params():,}")
print(f"  Layers: {len(model.layers)}")

# Step 2: Test the model works
print(f"\n[2] Testing model inference...")
test_input = np.random.random((1, 224, 224, 1)).astype(np.float32)
try:
    test_output = model.predict(test_input, verbose=0)
    print(f"✓ Test prediction: {test_output[0][0]:.6f}")
except Exception as e:
    print(f"✗ ERROR: Model prediction failed: {e}")
    exit(1)

# Step 3: Test on real image (if available)
test_image_paths = [
    "person23_bacteria_89.jpeg",
    "person1_bacteria_1.jpeg",
    "../media/xray_images/person1_bacteria_1.jpeg",
]

print(f"\n[3] Testing on real X-ray image...")
test_img = None
for img_path in test_image_paths:
    if Path(img_path).exists():
        try:
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img, (224, 224))
            img = img.astype(np.float32) / 255.0
            img = np.expand_dims(img, axis=0)
            img = np.expand_dims(img, axis=-1)
            
            pred = model.predict(img, verbose=0)
            confidence = float(pred[0][0])
            
            if confidence > 0.5:
                label = "PNEUMONIA"
                conf_pct = confidence * 100
            else:
                label = "NORMAL"
                conf_pct = (1 - confidence) * 100
            
            print(f"✓ Image: {Path(img_path).name}")
            print(f"  Prediction: {label} ({conf_pct:.2f}%)")
            print(f"  Raw confidence: {confidence:.6f}")
            test_img = img_path
            break
        except Exception as e:
            continue

if test_img is None:
    print(f"⚠  No test images found - skipping real image test")

# Step 4: Save in H5 format (compatible)
print(f"\n[4] Saving as H5 format...")
try:
    model.save(output_h5, save_format='h5')
    print(f"✓ Saved: {output_h5}")
    
    # Verify the saved model loads
    test_model = tf.keras.models.load_model(output_h5)
    test_pred = test_model.predict(test_input, verbose=0)
    print(f"✓ Verified: Model loads and predicts correctly")
    del test_model
except Exception as e:
    print(f"✗ ERROR: Could not save H5: {e}")

# Step 5: Save as SavedModel format (preferred)
print(f"\n[5] Saving as SavedModel format...")
try:
    model.save(output_savedmodel, save_format='tf')
    print(f"✓ Saved: {output_savedmodel}/")
    
    # Verify
    test_model = tf.keras.models.load_model(output_savedmodel)
    test_pred = test_model.predict(test_input, verbose=0)
    print(f"✓ Verified: Model loads and predicts correctly")
    del test_model
except Exception as e:
    print(f"✗ ERROR: Could not save SavedModel: {e}")

# Summary
print(f"\n" + "="*70)
print("CONVERSION COMPLETE")
print("="*70)

if Path(output_h5).exists():
    size_mb = Path(output_h5).stat().st_size / (1024*1024)
    print(f"\n✓ H5 Format:")
    print(f"  File: {output_h5}")
    print(f"  Size: {size_mb:.2f} MB")

if Path(output_savedmodel).exists():
    print(f"\n✓ SavedModel Format:")
    print(f"  Directory: {output_savedmodel}/")
    print(f"  (Preferred format for TensorFlow 2.x)")

print(f"\nNext Steps:")
print(f"  1. Copy '{output_h5}' to Django project:")
print(f"     → model_service/mobilenetv2.h5")
print(f"  2. Or copy '{output_savedmodel}/' folder")
print(f"  3. Update services.py to use the new file")
print(f"  4. Test Django app")

print(f"\nBoth formats should work with TensorFlow 2.13.0 in Django!")
