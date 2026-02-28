"""
TensorFlow Lite-based prediction service for pneumonia detection.
This version uses tflite-runtime instead of full TensorFlow.

ADVANTAGES:
- Much smaller: ~20MB vs 600MB for TensorFlow
- Perfect for limited storage environments (PythonAnywhere free tier)
- Same prediction accuracy as full TensorFlow
- Faster inference on CPU-only servers

USAGE:
Replace the import in your views:
    from xray_detector.services_tflite import predict_pneumonia
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
    The interpreter is loaded once and reused for all predictions.
    
    Returns:
        TFLite Interpreter object
        
    Raises:
        FileNotFoundError: If model file doesn't exist
        ImportError: If tflite_runtime is not installed
        Exception: If model loading fails
    """
    global _interpreter
    
    if _interpreter is None:
        try:
            # Try to import tflite_runtime first (smaller, preferred)
            try:
                import tflite_runtime.interpreter as tflite
            except ImportError:
                # Fallback to tensorflow.lite if tflite_runtime not available
                logger.warning("tflite_runtime not found, falling back to tensorflow.lite")
                import tensorflow as tf
                tflite = tf.lite
            
            # Determine model path - try standard first for better compatibility
            standard_model_path = os.path.join(
                settings.ML_MODELS_PATH, 
                'mobilenetv2_pneumonia_model.tflite'
            )
            quantized_model_path = os.path.join(
                settings.ML_MODELS_PATH, 
                'mobilenetv2_pneumonia_model_quantized.tflite'
            )
            
            if os.path.exists(standard_model_path):
                model_path = standard_model_path
                logger.info("Using standard TFLite model (better compatibility)")
            elif os.path.exists(quantized_model_path):
                model_path = quantized_model_path
                logger.info("Using quantized TFLite model (smaller size)")
            else:
                raise FileNotFoundError(
                    f"TFLite model file not found. Please convert your model first:\n"
                    f"  Run: python convert_model_to_tflite.py\n"
                    f"  Expected locations:\n"
                    f"    - {quantized_model_path}\n"
                    f"    - {standard_model_path}"
                )
            
            logger.info(f"Loading TFLite model from {model_path}")
            
            # Create interpreter and allocate tensors
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
            logger.error(
                f"Failed to import TFLite runtime: {str(e)}\n"
                f"Please install: pip install tflite-runtime"
            )
            raise ImportError(
                "tflite_runtime is not installed. "
                "Install with: pip install tflite-runtime"
            ) from e
        except Exception as e:
            logger.error(f"Error loading TFLite model: {str(e)}")
            raise Exception(f"Failed to load TFLite model: {str(e)}") from e
    
    return _interpreter


def preprocess_image(image_file):
    """
    Preprocess the uploaded image for model prediction.
    
    Steps:
    1. Open image using PIL
    2. Convert to grayscale
    3. Resize to 224x224
    4. Normalize pixel values to [0, 1]
    5. Add channel dimension (1 channel for grayscale)
    6. Add batch dimension
    
    Args:
        image_file: Uploaded image file object or file path
        
    Returns:
        Preprocessed numpy array ready for model input
        Shape: (1, 224, 224, 1) for grayscale model
        
    Raises:
        Exception: If image processing fails
    """
    try:
        # Open image
        img = Image.open(image_file)
        
        # Convert to grayscale (L mode)
        img = img.convert('L')
        
        # Resize to 224x224
        img = img.resize((224, 224), Image.LANCZOS)
        
        # Convert to numpy array
        img_array = np.array(img, dtype=np.float32)
        
        # Normalize pixel values to [0, 1]
        img_array = img_array / 255.0
        
        # Add channel dimension (grayscale has 1 channel)
        img_array = np.expand_dims(img_array, axis=-1)
        
        # Add batch dimension
        # Final shape: (1, 224, 224, 1) for grayscale model
        img_array = np.expand_dims(img_array, axis=0)
        
        logger.info(f"Image preprocessed successfully. Shape: {img_array.shape}")
        return img_array
        
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        raise Exception(f"Failed to preprocess image: {str(e)}") from e


def predict_with_tflite(image_file):
    """
    Make prediction using TensorFlow Lite model.
    
    Args:
        image_file: Uploaded image file object or file path
        
    Returns:
        Dictionary with prediction results:
        {
            'predicted_class': 'PNEUMONIA' or 'NORMAL',
            'confidence': float (0-100),
            'raw_score': float (0-1),
            'confidence_normal': float (0-100),
            'confidence_pneumonia': float (0-100)
        }
        
    Raises:
        Exception: If prediction fails
    """
    try:
        # Load interpreter
        interpreter = get_tflite_interpreter()
        
        # Preprocess image
        processed_image = preprocess_image(image_file)
        
        # Get input and output details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        # Set the input tensor
        interpreter.set_tensor(input_details[0]['index'], processed_image)
        
        # Run inference
        interpreter.invoke()
        
        # Get the output tensor
        prediction = interpreter.get_tensor(output_details[0]['index'])
        
        # Extract prediction score
        raw_score = float(prediction[0][0])
        
        # Calculate confidences for both classes
        confidence_pneumonia = raw_score * 100
        confidence_normal = (1 - raw_score) * 100
        
        # Determine class and confidence
        if raw_score >= 0.5:
            predicted_class = 'PNEUMONIA'
            confidence = confidence_pneumonia
        else:
            predicted_class = 'NORMAL'
            confidence = confidence_normal
        
        result = {
            'predicted_class': predicted_class,
            'confidence': round(confidence, 2),
            'raw_score': round(raw_score, 4),
            'confidence_normal': round(confidence_normal, 2),
            'confidence_pneumonia': round(confidence_pneumonia, 2)
        }
        
        logger.info(
            f"TFLite prediction: {predicted_class} "
            f"(confidence: {confidence:.2f}%, raw_score: {raw_score:.4f})"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"TFLite prediction error: {str(e)}")
        raise Exception(f"Prediction failed: {str(e)}") from e


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


# For backwards compatibility
predict_pneumonia_with_tflite = predict_with_tflite


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
