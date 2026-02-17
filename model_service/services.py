"""
AI Processing & Inference Service
Handles image preprocessing and CNN model inference
"""

import os
import json
import time
import numpy as np
from pathlib import Path
from PIL import Image

try:
    import tensorflow as tf
except ImportError:
    tf = None

from django.core.files.base import ContentFile
from django.utils import timezone
from io import BytesIO

from .models import PredictionResult, XRayImage, ModelVersion, ProcessingLog


class ImagePreprocessor:
    """
    Handles preprocessing of uploaded X-ray images
    Normalizes images to model input requirements
    """
    
    DEFAULT_SIZE = (224, 224)
    # ImageNet normalization values
    MEAN = np.array([0.485, 0.456, 0.406])
    STD = np.array([0.229, 0.224, 0.225])
    
    @staticmethod
    def preprocess_image(image_path, target_size=DEFAULT_SIZE):
        """
        Preprocess a single image for model inference
        
        Args:
            image_path: Path to image file
            target_size: Tuple (height, width) for resizing
            
        Returns:
            Preprocessed image array ready for model
            
        Algorithm from SDD Section 5.2.1
        """
        try:
            start_time = time.time()
            
            # Load image
            img = Image.open(image_path)
            
            # Convert to RGB if grayscale
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize image
            img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
            
            # Convert to numpy array
            img_array = np.array(img_resized, dtype=np.float32)
            
            # Normalize to [0, 1]
            img_normalized = img_array / 255.0
            
            # Apply ImageNet normalization
            img_normalized = (img_normalized - ImagePreprocessor.MEAN) / ImagePreprocessor.STD
            
            # Add batch dimension
            img_batch = np.expand_dims(img_normalized, axis=0)
            
            elapsed = time.time() - start_time
            
            return {
                'status': 'success',
                'data': img_batch,
                'processing_time': elapsed,
                'original_shape': np.array(img).shape,
                'processed_shape': img_batch.shape
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': 0
            }
    
    @staticmethod
    def validate_image(image_path, max_size_mb=10):
        """
        Validate image before preprocessing
        
        Args:
            image_path: Path to image file
            max_size_mb: Maximum file size in MB
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        
        # Check file exists
        if not os.path.exists(image_path):
            errors.append("Image file not found")
            return {'valid': False, 'errors': errors}
        
        # Check file size
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            errors.append(f"File size ({file_size_mb:.2f}MB) exceeds limit ({max_size_mb}MB)")
        
        # Check file format
        try:
            img = Image.open(image_path)
            if img.format not in ['JPEG', 'PNG', 'JPG']:
                errors.append(f"Unsupported format: {img.format}")
        except Exception as e:
            errors.append(f"Invalid image file: {str(e)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'file_size_mb': file_size_mb
        }


class PneumoniaDetectionService:
    """
    CNN Model Service for Pneumonia Detection
    Loads model and performs inference
    
    Algorithm from SDD Section 5.2.2
    """
    
    _model = None
    _model_path = None
    
    @classmethod
    def get_model(cls, force_reload=False):
        """
        Load and cache the pre-trained model
        
        Args:
            force_reload: Force reloading even if cached
            
        Returns:
            Loaded TensorFlow model
        """
        if cls._model is None or force_reload:
            try:
                # Get model path from model_service directory
                model_dir = Path(__file__).parent
                model_path = model_dir / 'mobilenetv2.h5'
                
                if not model_path.exists():
                    raise FileNotFoundError(f"Model not found at {model_path}")
                
                cls._model = tf.keras.models.load_model(str(model_path))
                cls._model_path = str(model_path)
                
            except Exception as e:
                raise RuntimeError(f"Failed to load model: {str(e)}")
        
        return cls._model
    
    @classmethod
    def predict(cls, preprocessed_image):
        """
        Perform pneumonia detection on preprocessed image
        
        Args:
            preprocessed_image: Preprocessed image array (batch)
            
        Returns:
            Dictionary with prediction results
        """
        try:
            start_time = time.time()
            
            # Load model
            model = cls.get_model()
            
            # Perform inference
            predictions = model.predict(preprocessed_image, verbose=0)
            
            # Get prediction details
            confidence_normal = float(predictions[0][0])
            confidence_pneumonia = float(predictions[0][1])
            
            # Determine label
            if confidence_pneumonia > confidence_normal:
                label = 'PNEUMONIA'
                confidence = confidence_pneumonia
            else:
                label = 'NORMAL'
                confidence = confidence_normal
            
            elapsed = time.time() - start_time
            
            # Determine confidence level
            confidence_pct = confidence * 100
            if confidence_pct >= 95:
                confidence_level = 'HIGH'
            elif confidence_pct >= 80:
                confidence_level = 'MODERATE'
            else:
                confidence_level = 'LOW'
            
            return {
                'status': 'success',
                'prediction_label': label,
                'confidence_score': confidence,
                'confidence_percentage': confidence_pct,
                'confidence_level': confidence_level,
                'confidence_normal': confidence_normal,
                'confidence_pneumonia': confidence_pneumonia,
                'processing_time': elapsed,
                'raw_predictions': {
                    'NORMAL': float(predictions[0][0]),
                    'PNEUMONIA': float(predictions[0][1])
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': 0
            }


class DiagnosisService:
    """
    High-level service combining preprocessing and inference
    Main entry point for pneumonia diagnosis
    """
    
    @staticmethod
    def diagnose(image_path):
        """
        Complete diagnosis workflow: preprocess -> predict
        
        Args:
            image_path: Path to X-ray image
            
        Returns:
            Complete diagnosis result with all details
        """
        result = {
            'status': 'error',
            'errors': []
        }
        
        try:
            # Validate image
            validation = ImagePreprocessor.validate_image(image_path)
            if not validation['valid']:
                result['errors'] = validation['errors']
                return result
            
            # Preprocess image
            preprocess_result = ImagePreprocessor.preprocess_image(image_path)
            if preprocess_result['status'] != 'success':
                result['errors'].append(f"Preprocessing failed: {preprocess_result.get('error')}")
                return result
            
            # Predict
            prediction_result = PneumoniaDetectionService.predict(preprocess_result['data'])
            if prediction_result['status'] != 'success':
                result['errors'].append(f"Prediction failed: {prediction_result.get('error')}")
                return result
            
            # Combine results
            result['status'] = 'success'
            result['preprocessing_time'] = preprocess_result['processing_time']
            result['prediction_time'] = prediction_result['processing_time']
            result['total_time'] = result['preprocessing_time'] + result['prediction_time']
            result['prediction'] = {
                'label': prediction_result['prediction_label'],
                'confidence': prediction_result['confidence_score'],
                'confidence_percentage': prediction_result['confidence_percentage'],
                'confidence_level': prediction_result['confidence_level'],
                'raw_predictions': prediction_result['raw_predictions']
            }
            
            return result
            
        except Exception as e:
            result['errors'].append(str(e))
            return result
    
    @staticmethod
    def save_prediction_result(xray_image, diagnosis_result):
        """
        Save diagnosis result to database
        
        Args:
            xray_image: XRayImage instance
            diagnosis_result: Result from diagnose()
            
        Returns:
            PredictionResult instance or None
        """
        try:
            if diagnosis_result['status'] != 'success':
                return None
            
            prediction = diagnosis_result['prediction']
            
            # Get active model version
            try:
                model_version = ModelVersion.objects.get(is_active=True)
            except ModelVersion.DoesNotExist:
                model_version = None
            
            # Create prediction result
            result = PredictionResult.objects.create(
                image=xray_image,
                prediction_label=prediction['label'],
                confidence_score=prediction['confidence'],
                confidence_level=prediction['confidence_level'],
                processing_time=diagnosis_result['total_time'],
                model_version=model_version,
                raw_predictions=json.dumps(prediction['raw_predictions']),
                created_at=timezone.now()
            )
            
            # Log successful processing
            ProcessingLog.objects.create(
                image=xray_image,
                step_name='Model Inference',
                status='SUCCESS',
                message=f"Prediction: {prediction['label']} (Confidence: {prediction['confidence_percentage']:.2f}%)",
                execution_time=diagnosis_result['total_time']
            )
            
            return result
            
        except Exception as e:
            ProcessingLog.objects.create(
                image=xray_image,
                step_name='Save Result',
                status='ERROR',
                message=str(e)
            )
            return None
