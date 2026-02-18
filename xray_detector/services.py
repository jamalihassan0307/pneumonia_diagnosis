"""
Prediction service for pneumonia detection using MobileNetV2 model.
Handles model loading, image preprocessing, and prediction.
"""

import os
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Global variable to cache the loaded model
_model = None


def get_model():
    """
    Load and cache the MobileNetV2 model.
    The model is loaded once and reused for all predictions.
    
    Returns:
        Loaded Keras model
        
    Raises:
        FileNotFoundError: If model file doesn't exist
        Exception: If model loading fails
    """
    global _model
    
    if _model is None:
        try:
            model_path = os.path.join(settings.ML_MODELS_PATH, 'mobilenetv2_pneumonia_model.h5')
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(
                    f"Model file not found at {model_path}. "
                    f"Please place your trained MobileNetV2 model at this location."
                )
            
            logger.info(f"Loading model from {model_path}")
            _model = load_model(model_path)
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise Exception(f"Failed to load model: {str(e)}")
    
    return _model


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
        image_file: Uploaded image file object
        
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
        raise Exception(f"Failed to preprocess image: {str(e)}")


def predict_pneumonia(image_file):
    """
    Predict pneumonia from chest X-ray image.
    
    Args:
        image_file: Uploaded image file object
        
    Returns:
        Dictionary containing:
        - success (bool): Whether prediction was successful
        - predicted_class (str): 'NORMAL' or 'PNEUMONIA'
        - confidence (float): Confidence percentage (0-100)
        - raw_score (float): Raw prediction score (0-1)
        - error (str, optional): Error message if prediction failed
        
    Example:
        {
            'success': True,
            'predicted_class': 'PNEUMONIA',
            'confidence': 92.5,
            'raw_score': 0.925
        }
    """
    try:
        # Load model
        model = get_model()
        
        # Preprocess image
        processed_image = preprocess_image(image_file)
        
        # Make prediction
        prediction = model.predict(processed_image, verbose=0)
        
        # Extract prediction score
        # Assuming binary classification: 0 = NORMAL, 1 = PNEUMONIA
        raw_score = float(prediction[0][0])
        
        # Determine class and confidence
        if raw_score >= 0.5:
            predicted_class = 'PNEUMONIA'
            confidence = raw_score * 100
        else:
            predicted_class = 'NORMAL'
            confidence = (1 - raw_score) * 100
        
        logger.info(
            f"Prediction successful: {predicted_class} "
            f"(confidence: {confidence:.2f}%, raw_score: {raw_score:.4f})"
        )
        
        return {
            'success': True,
            'predicted_class': predicted_class,
            'confidence': round(confidence, 2),
            'raw_score': round(raw_score, 4)
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


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
