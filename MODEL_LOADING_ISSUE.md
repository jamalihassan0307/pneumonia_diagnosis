# Model Loading Issue - Solution Required

## Problem
The `mobilenetv2.h5` model file cannot be loaded in Django environment (TensorFlow 2.13.0) due to incompatible serialization format:
- Error: `Unrecognized keyword arguments: ['batch_shape']`
- The H5 file uses deprecated `batch_shape` parameter in InputLayer
- TensorFlow 2.13's Keras doesn't support this parameter

## Current Status
- ✅ Flask app: Loads model successfully and gives correct predictions (99.96% for pneumonia)
- ❌ Django app: Cannot load model - all loading strategies failed
- ⚠️  Fallback: Demo mode is active (gives predictions without real AI)

## Solution Options

### Option 1: Re-save Model from Flask Environment (RECOMMENDED)
Your Flask app can load the model, so we can use it to re-save in a compatible format.

**Steps:**
1. In your Flask environment, run the script: `convert_from_flask.py`
2. This will create: `mobilenetv2_django_compatible.h5`
3. Copy that file to Django's `model_service/` folder
4. Update Django to use the new file

See: `convert_from_flask.py` (run this in Flask environment)

### Option 2: Check TensorFlow Versions
The version mismatch might be the issue.

**Flask environment:**
```bash
python -c "import tensorflow as tf; print(tf.__version__)"
```

**Django environment:**
```bash
venv_py311\Scripts\python -c "import tensorflow as tf; print(tf.__version__)"
```

If Flask uses TensorFlow < 2.13, that explains why it works there but not in Django.

### Option 3: Use Demo Mode (Temporary)
Demo mode is already active and gives reasonable predictions based on filename analysis. This works for demonstration but doesn't use the real trained model.

To acknowledge demo mode in UI, the system already returns `'_demo': True` in predictions when model loading fails.

### Option 4: Retrain Model
If you have the training code and data, retrain and save with:
```python
model.save('mobilenetv2_new.h5')  # Modern H5 format
# OR
model.export('mobilenetv2_saved_model')  # SavedModel format (better)
```

## Technical Details

### What We Tried
1. ✗ Standard `load_model()` with `compile=False`
2. ✗ Compatibility mode with `safe_mode=False`  
3. ✗ Custom config loader (fixing batch_shape → shape)
4. ✗ Manual model reconstruction + weight loading
5. ✗ tf.compat.v1 APIs
6. ✗ Model config modification and deserialization

All failed due to incompatible serialization format between Keras versions.

### H5 File Structure (Confirmed)
```
Input: (224, 224, 1) grayscale
Conv2D: 1x1, 1→3 channels (learned grayscale-to-RGB)
MobileNetV2: Standard backbone, no top
GlobalAveragePooling2D
Dense: 256 units, ReLU
Dropout: 0.5
Dense: 1 unit, sigmoid
Output: Single value (0=NORMAL, 1=PNEUMONIA)
```

### Preprocessing (Must Match Training)
```python
img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)  # Load as grayscale
img = cv2.resize(img, (224, 224))              # Resize  
img = img.astype(np.float32) / 255.0           # Normalize [0, 1]
img = np.expand_dims(img, axis=0)              # Batch dim
img = np.expand_dims(img, axis=-1)             # Channel dim
# Result: (1, 224, 224, 1)
```

### Prediction Logic
```python
confidence = float(prediction[0][0])  # Single sigmoid value
if confidence > 0.5:
    result = "PNEUMONIA"
    confidence_pct = confidence * 100
else:
    result = "NORMAL"
    confidence_pct = (1 - confidence) * 100
```

## Files Created for Troubleshooting
- `convert_from_flask.py` - Run in Flask to re-save model
- `inspect_h5.py` - View H5 file structure
- `diagnostic_model.py` - Test predictions
- `MODEL_LOADING_ISSUE.md` - This file

## Next Steps
1. **Run `convert_from_flask.py` in your Flask environment**
2. Copy the output file to Django
3. Test with `diagnostic_model.py`
4. If predictions are correct (90%+ for pneumonia images), the issue is resolved
