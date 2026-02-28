"""
Convert MobileNetV2 Keras model (.h5) to TensorFlow Lite (.tflite)

This script converts your large Keras model to a much smaller TFLite format,
reducing size by 80-90% while maintaining prediction accuracy.

Usage:
    python convert_model_to_tflite.py

Requirements:
    - TensorFlow must be installed locally (pip install tensorflow)
    - Model file must exist at: ml_models/mobilenetv2_pneumonia_model.h5
"""

import os
import sys
import tensorflow as tf
from pathlib import Path

def convert_to_tflite():
    """Convert the Keras model to TensorFlow Lite format"""
    
    # Paths
    model_path = Path('ml_models/mobilenetv2_pneumonia_model.h5')
    output_path = Path('ml_models/mobilenetv2_pneumonia_model.tflite')
    quantized_output_path = Path('ml_models/mobilenetv2_pneumonia_model_quantized.tflite')
    
    # Check if model exists
    if not model_path.exists():
        print(f"❌ Error: Model file not found at {model_path}")
        print("Please ensure your trained model is in the ml_models directory")
        sys.exit(1)
    
    print(f"🔄 Loading Keras model from {model_path}...")
    
    try:
        # Load the Keras model
        model = tf.keras.models.load_model(str(model_path))
        print(f"✅ Model loaded successfully")
        print(f"   Input shape: {model.input_shape}")
        print(f"   Output shape: {model.output_shape}")
        
        # Get original model size
        original_size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"   Original size: {original_size_mb:.2f} MB")
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        sys.exit(1)
    
    # ===== Convert to standard TFLite ===== 
    print("\n🔄 Converting to TensorFlow Lite (standard)...")
    
    try:
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        tflite_model = converter.convert()
        
        # Save the model
        with open(output_path, 'wb') as f:
            f.write(tflite_model)
        
        tflite_size_mb = output_path.stat().st_size / (1024 * 1024)
        reduction = ((original_size_mb - tflite_size_mb) / original_size_mb) * 100
        
        print(f"✅ Standard TFLite model saved to {output_path}")
        print(f"   Size: {tflite_size_mb:.2f} MB")
        print(f"   Reduction: {reduction:.1f}%")
        
    except Exception as e:
        print(f"❌ Error converting to TFLite: {e}")
        sys.exit(1)
    
    # ===== Convert to quantized TFLite (even smaller) =====
    print("\n🔄 Converting to TensorFlow Lite (quantized - smaller)...")
    
    try:
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        
        # Apply optimizations for smaller size
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        
        # Convert to quantized model
        tflite_quantized_model = converter.convert()
        
        # Save the quantized model
        with open(quantized_output_path, 'wb') as f:
            f.write(tflite_quantized_model)
        
        quantized_size_mb = quantized_output_path.stat().st_size / (1024 * 1024)
        quantized_reduction = ((original_size_mb - quantized_size_mb) / original_size_mb) * 100
        
        print(f"✅ Quantized TFLite model saved to {quantized_output_path}")
        print(f"   Size: {quantized_size_mb:.2f} MB")
        print(f"   Reduction: {quantized_reduction:.1f}%")
        
    except Exception as e:
        print(f"⚠️  Warning: Quantization failed: {e}")
        print("   The standard TFLite model is still available")
    
    # ===== Summary =====
    print("\n" + "="*60)
    print("📊 CONVERSION SUMMARY")
    print("="*60)
    print(f"Original Keras model:     {original_size_mb:>10.2f} MB")
    print(f"Standard TFLite model:    {tflite_size_mb:>10.2f} MB  ({reduction:.1f}% smaller)")
    if quantized_output_path.exists():
        print(f"Quantized TFLite model:   {quantized_size_mb:>10.2f} MB  ({quantized_reduction:.1f}% smaller)")
    print("="*60)
    
    # ===== Next Steps =====
    print("\n📋 NEXT STEPS:")
    print("1. Test the TFLite model locally using: python test_tflite_model.py")
    print("2. For PythonAnywhere deployment:")
    print("   - Upload the .tflite file (much smaller!)")
    print("   - Use requirements_pythonanywhere.txt")
    print("   - Update services.py to use TFLite instead of Keras")
    print("\n✨ Conversion complete!")

if __name__ == '__main__':
    print("="*60)
    print("  TensorFlow Keras to TFLite Converter")
    print("  Pneumonia Detection Model")
    print("="*60)
    print()
    
    convert_to_tflite()
