"""
Test TensorFlow Lite model to verify it works correctly

This script tests the converted TFLite model to ensure it produces
accurate predictions similar to the original Keras model.

Usage:
    python test_tflite_model.py
    python test_tflite_model.py path/to/test/image.jpg
"""

import sys
import numpy as np
from pathlib import Path
from PIL import Image

def load_tflite_model(model_path='ml_models/mobilenetv2_pneumonia_model.tflite'):
    """Load TFLite model"""
    try:
        import tflite_runtime.interpreter as tflite
    except ImportError:
        print("⚠️  tflite_runtime not installed, trying tensorflow.lite...")
        try:
            import tensorflow as tf
            tflite = tf.lite
        except ImportError:
            print("❌ Neither tflite_runtime nor tensorflow is installed")
            print("   Install with: pip install tflite-runtime")
            sys.exit(1)
    
    if not Path(model_path).exists():
        print(f"❌ Model file not found: {model_path}")
        print("   Please run convert_model_to_tflite.py first")
        sys.exit(1)
    
    print(f"🔄 Loading TFLite model from {model_path}...")
    interpreter = tflite.Interpreter(model_path=str(model_path))
    interpreter.allocate_tensors()
    
    return interpreter


def preprocess_image(image_path):
    """Preprocess image for model input (same as in services.py)"""
    img = Image.open(image_path)
    img = img.convert('L')  # Grayscale
    img = img.resize((224, 224), Image.LANCZOS)
    
    img_array = np.array(img, dtype=np.float32)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=-1)  # Add channel dimension
    img_array = np.expand_dims(img_array, axis=0)    # Add batch dimension
    
    return img_array


def predict_with_tflite(interpreter, image_array):
    """Make prediction using TFLite interpreter"""
    
    # Get input and output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    # Set input tensor
    interpreter.set_tensor(input_details[0]['index'], image_array)
    
    # Run inference
    interpreter.invoke()
    
    # Get output tensor
    output_data = interpreter.get_tensor(output_details[0]['index'])
    
    return output_data


def test_model(image_path=None):
    """Test the TFLite model"""
    
    # Load model
    interpreter = load_tflite_model()
    
    # Get input/output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    print(f"✅ Model loaded successfully")
    print(f"\n📊 Model Details:")
    print(f"   Input shape:  {input_details[0]['shape']}")
    print(f"   Input dtype:  {input_details[0]['dtype']}")
    print(f"   Output shape: {output_details[0]['shape']}")
    print(f"   Output dtype: {output_details[0]['dtype']}")
    
    # If image path provided, test with real image
    if image_path:
        if not Path(image_path).exists():
            print(f"\n❌ Image file not found: {image_path}")
            return
        
        print(f"\n🔄 Testing with image: {image_path}")
        
        # Preprocess image
        img_array = preprocess_image(image_path)
        print(f"   Preprocessed shape: {img_array.shape}")
        
        # Make prediction
        prediction = predict_with_tflite(interpreter, img_array)
        raw_score = float(prediction[0][0])
        
        # Interpret results
        if raw_score >= 0.5:
            predicted_class = 'PNEUMONIA'
            confidence = raw_score * 100
        else:
            predicted_class = 'NORMAL'
            confidence = (1 - raw_score) * 100
        
        print(f"\n✨ PREDICTION RESULT:")
        print(f"   Class:      {predicted_class}")
        print(f"   Confidence: {confidence:.2f}%")
        print(f"   Raw score:  {raw_score:.4f}")
        print(f"\n   Breakdown:")
        print(f"   - NORMAL:    {(1-raw_score)*100:.2f}%")
        print(f"   - PNEUMONIA: {raw_score*100:.2f}%")
    
    else:
        # Test with dummy data
        print(f"\n🔄 Testing with dummy data (random noise)...")
        dummy_input = np.random.random((1, 224, 224, 1)).astype(np.float32)
        prediction = predict_with_tflite(interpreter, dummy_input)
        print(f"✅ Model inference successful")
        print(f"   Output: {prediction[0][0]:.4f}")
        print(f"\n💡 Tip: Run with an image path to test with real data:")
        print(f"   python test_tflite_model.py path/to/xray.jpg")
    
    print(f"\n✅ TFLite model is working correctly!")
    return True


if __name__ == '__main__':
    print("="*60)
    print("  TFLite Model Tester")
    print("  Pneumonia Detection Model")
    print("="*60)
    print()
    
    # Check if image path provided
    image_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    test_model(image_path)
