"""
TensorFlow Lite-based prediction service for pneumonia detection.
This version uses tflite-runtime or tensorflow.lite instead of full TensorFlow.

ADVANTAGES:
- Smaller footprint: ~20MB for tflite-runtime vs 600MB for TensorFlow
- Suitable for limited storage environments (PythonAnywhere free tier)
- Same prediction accuracy as full TensorFlow
- Faster inference

USAGE:
from xray_detector.services_tflite import predict_pneumonia, validate_image_file
"""

import os
import numpy as np
from PIL import Image
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Global variable to cache the loaded interpreter
_interpreter = None


def get_tflite_interpreter():
    """
    Load and cache the TFLite model interpreter.
    
    Returns:
        TFLite Interpreter object
        
    Raises:
        FileNotFoundError: If model file doesn't exist
        Exception: If model loading fails
    """
    global _interpreter
    
    if _interpreter is None:
        try:
            # Try to import tflite_runtime first (preferred - smaller)
            try:
                import tflite_runtime.interpreter as tflite
                logger.info("Using tflite_runtime for inference")
            except ImportError:
                # Fallback to tensorflow.lite if tflite_runtime not available
                logger.warning("tflite_runtime not found, using tensorflow.lite")
                import tensorflow as tf
                tflite = tf.lite
            
            # Determine model path - prefer quantized
            quantized_model_path = os.path.join(
                settings.ML_MODELS_PATH, 
                'mobilenetv2_pneumonia_model_quantized.tflite'
            )
            standard_model_path = os.path.join(
                settings.ML_MODELS_PATH, 
                'mobilenetv2_pneumonia_model.tflite'
            )
            
            if os.path.exists(quantized_model_path):
                model_path = quantized_model_path
                logger.info("Loading quantized TFLite model (smaller size)")
            elif os.path.exists(standard_model_path):
                model_path = standard_model_path
                logger.info("Loading standard TFLite model")
            else:
                raise FileNotFoundError(
                    f"TFLite model not found at {quantized_model_path} or {standard_model_path}\n"
                    f"Please ensure model files are in {settings.ML_MODELS_PATH}"
                )
            
            logger.info(f"Loading TFLite model from: {model_path}")
            
            # Create interpreter
            _interpreter = tflite.Interpreter(model_path=model_path)
            _interpreter.allocate_tensors()
            
            # Log model details
            input_details = _interpreter.get_input_details()
            output_details = _interpreter.get_output_details()
            logger.info(
                f"TFLite model loaded successfully - "
                f"Input shape: {input_details[0]['shape']}, "
                f"Output shape: {output_details[0]['shape']}"
            )
            
        except ImportError as e:
            logger.error(f"Failed to import TFLite: {str(e)}")
            raise ImportError(
                "Neither tflite_runtime nor tensorflow.lite could be imported. "
                "Please install: pip install tflite-runtime"
            )
        except FileNotFoundError as e:
            logger.error(str(e))
            raise
        except Exception as e:
            logger.error(f"Error loading TFLite model: {str(e)}")
            raise
    
    return _interpreter


def preprocess_image(image_file, target_size=(224, 224)):
    """
    Preprocess image for MobileNetV2 model.
    
    Args:
        image_file: PIL Image or file path
        target_size: Tuple of (width, height)
        
    Returns:
        Preprocessed numpy array
    """
    # Open image if it's a file
    if isinstance(image_file, str):
        img = Image.open(image_file)
    else:
        img = Image.open(image_file)
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize to target size
    img = img.resize(target_size)
    
    # Convert to numpy array and normalize
    img_array = np.array(img, dtype=np.float32)
    img_array = img_array / 255.0  # Normalize to [0, 1]
    
    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array


def predict_with_tflite(image_file):
    """
    Perform pneumonia prediction using TFLite interpreter.
    
    Args:
        image_file: Django UploadedFile or PIL Image
        
    Returns:
        Dictionary with prediction results:
        {
            'status': 'success',
            'prediction': 'PNEUMONIA' or 'NORMAL',
            'confidence': 0.95 (float between 0-1),
            'confidence_percentage': 95.0,
            'all_probabilities': {'NORMAL': 0.05, 'PNEUMONIA': 0.95}
        }
    """
    try:
        # Get interpreter
        interpreter = get_tflite_interpreter()
        
        # Get input/output details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        # Preprocess image
        input_data = preprocess_image(image_file)
        
        # Run inference
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        
        # Get predictions
        output_data = interpreter.get_tensor(output_details[0]['index'])
        predictions = output_data[0]  # Remove batch dimension
        
        # Interpret results (assuming 2 classes: [NORMAL, PNEUMONIA])
        normal_prob = float(predictions[0]) if len(predictions) > 0 else 0.5
        pneumonia_prob = float(predictions[1]) if len(predictions) > 1 else 0.5
        
        # If only one output, assume it's pneumonia probability
        if len(predictions) == 1:
            pneumonia_prob = float(predictions[0])
            normal_prob = 1.0 - pneumonia_prob
        
        # Determine prediction
        if pneumonia_prob > normal_prob:
            prediction = 'PNEUMONIA'
            confidence = pneumonia_prob
        else:
            prediction = 'NORMAL'
            confidence = normal_prob
        
        logger.info(
            f"Prediction: {prediction}, "
            f"Confidence: {confidence:.4f}, "
            f"Normal: {normal_prob:.4f}, "
            f"Pneumonia: {pneumonia_prob:.4f}"
        )
        
        return {
            'status': 'success',
            'prediction': prediction,
            'confidence': confidence,
            'confidence_percentage': confidence * 100,
            'all_probabilities': {
                'NORMAL': normal_prob,
                'PNEUMONIA': pneumonia_prob
            }
        }
        
    except Exception as e:
        logger.error(f"TFLite prediction error: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'message': f'Prediction failed: {str(e)}',
            'prediction': 'UNKNOWN',
            'confidence': 0.0
        }


def predict_pneumonia(image_file):
    """
    Main prediction function - compatible with existing code.
    This is a drop-in replacement for the TensorFlow version.
    
    Args:
        image_file: Uploaded image file object or file path
        
    Returns:
        Dictionary with prediction results
    """
    return predict_with_tflite(image_file)


def validate_image_file(uploaded_file):
    """
    Validate uploaded image file.
    
    Checks:
    - File extension is allowed
    - File size is within limit
    - File is a valid image
    
    Args:
        uploaded_file: Django UploadedFile object
        
    Returns:
        Tuple (is_valid, error_message)
        
    Example:
        (True, None) if valid
        (False, "Invalid file extension") if invalid
    """
    # Check file extension
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    if file_ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        return False, f"Invalid file extension. Allowed: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
    
    # Check file size (16MB limit)
    max_size = 16 * 1024 * 1024  # 16MB in bytes
    if uploaded_file.size > max_size:
        return False, f"File too large. Maximum size: 16MB"
    
    # Try to open image to verify it's valid
    try:
        img = Image.open(uploaded_file)
        img.verify()
        # Reset file pointer after verify
        uploaded_file.seek(0)
        return True, None
    except Exception as e:
        return False, f"Invalid or corrupted image file: {str(e)}"
