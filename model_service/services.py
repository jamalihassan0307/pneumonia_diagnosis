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
import logging
import h5py

logger = logging.getLogger(__name__)

# Try to import TensorFlow and OpenCV, but gracefully handle if not available
try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    tf = None
    TENSORFLOW_AVAILABLE = False
    logger.warning("TensorFlow not installed. Install with: pip install tensorflow")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    CV2_AVAILABLE = False
    logger.debug("OpenCV not installed. Will use PIL as fallback.")

from django.core.files.base import ContentFile
from django.utils import timezone
from io import BytesIO

from .models import PredictionResult, XRayImage, ModelVersion, ProcessingLog


class DemoModeHelper:
    """
    Demo mode prediction when TensorFlow is not available
    Provides realistic predictions for testing without TensorFlow
    
    IMPORTANT: This is NOT AI prediction. This is demo mode only.
    Install TensorFlow for actual pneumonia detection.
    """
    @staticmethod
    def get_demo_prediction(image_path):
        """
        Generate more realistic demo predictions based on image analysis
        NOT actual AI - for demonstration only
        """
        try:
            # Load image to analyze
            img = Image.open(image_path)
            img_array = np.array(img.convert('RGB'), dtype=np.float32)
            
            # Analyze image properties (NOT AI prediction)
            img_mean = np.mean(img_array)
            img_std = np.std(img_array)
            img_entropy = float(np.max(img_array) - np.min(img_array))
            
            # Create pseudo-random but deterministic predictions
            # based on image properties (NOT actual model output)
            np.random.seed(hash(image_path) % (2**32))
            
            # Generate varied predictions (not stuck at 61%)
            base_value = 0.4 + (img_mean / 512.0)
            pneumonia_prob = np.clip(base_value + np.random.uniform(-0.15, 0.35), 0.2, 0.95)
            normal_prob = 1.0 - pneumonia_prob
            
            # Determine label
            if pneumonia_prob > 0.5:
                label = 'PNEUMONIA'
                confidence = pneumonia_prob
            else:
                label = 'NORMAL'
                confidence = normal_prob
            
            # Confidence level
            confidence_pct = confidence * 100
            if confidence_pct >= 95:
                confidence_level = 'HIGH'
            elif confidence_pct >= 80:
                confidence_level = 'MODERATE'
            elif confidence_pct >= 70:
                confidence_level = 'MODERATE'
            else:
                confidence_level = 'LOW'
            
            return {
                'status': 'success',
                'prediction_label': label,
                'confidence_score': float(confidence),
                'confidence_percentage': float(confidence_pct),
                'confidence_level': confidence_level,
                'confidence_normal': float(normal_prob),
                'confidence_pneumonia': float(pneumonia_prob),
                'processing_time': 0.02,
                'raw_predictions': {
                    'NORMAL': float(normal_prob),
                    'PNEUMONIA': float(pneumonia_prob),
                    '_demo': True  # Mark as demo mode
                },
                'demo_mode': True,
                'warning': "⚠️ DEMO MODE: Not actual AI prediction. Install TensorFlow for real detection."
            }
        except Exception as e:
            logger.error(f"Demo prediction error: {str(e)}")
            return {
                'status': 'error',
                'error': f"Demo prediction failed: {str(e)}",
                'processing_time': 0
            }


class ImagePreprocessor:
    """
    Handles preprocessing of uploaded X-ray images
    MATCHES EXACTLY the Flask app preprocessing for correct predictions
    """
    
    DEFAULT_SIZE = (224, 224)
    
    @staticmethod
    def preprocess_image(image_path, target_size=DEFAULT_SIZE):
        """
        Preprocess image EXACTLY like the working Flask application
        
        Args:
            image_path: Path to image file
            target_size: Tuple (height, width) for resizing
            
        Returns:
            Preprocessed image array ready for model (1, 224, 224, 1)
            
        IMPORTANT: This MUST match the Flask app preprocessing exactly:
        1. Read as grayscale
        2. Resize to 224x224
        3. Normalize to [0, 1] by dividing by 255
        4. Add batch and channel dimensions
        """
        try:
            start_time = time.time()
            
            # Read image using OpenCV (same as Flask app)
            try:
                import cv2
                # Read image in grayscale
                img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
                
                if img is None:
                    raise ValueError("Could not read image with OpenCV")
                
                # Resize to 224x224
                img = cv2.resize(img, target_size)
                
            except ImportError:
                # Fallback to PIL if OpenCV not available
                img_pil = Image.open(image_path)
                
                # Convert to grayscale
                if img_pil.mode != 'L':
                    img_pil = img_pil.convert('L')
                
                # Resize
                img_pil = img_pil.resize(target_size, Image.Resampling.LANCZOS)
                
                # Convert to numpy
                img = np.array(img_pil)
            
            # Normalize to [0, 1] (EXACTLY like Flask app)
            img = img.astype(np.float32) / 255.0
            
            # Add batch and channel dimensions (EXACTLY like Flask app)
            img = np.expand_dims(img, axis=0)      # Add batch dimension: (224, 224) -> (1, 224, 224)
            img = np.expand_dims(img, axis=-1)     # Add channel dimension: (1, 224, 224) -> (1, 224, 224, 1)
            
            elapsed = time.time() - start_time
            
            return {
                'status': 'success',
                'data': img,
                'processing_time': elapsed,
                'original_shape': img.shape,
                'processed_shape': img.shape
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': 0
            }

    @staticmethod
    def preprocess(image_path, target_size=DEFAULT_SIZE):
        """Backward-compatible alias for preprocess_image."""
        return ImagePreprocessor.preprocess_image(image_path, target_size)
    
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
    _model_loaded_from = None  # Track which model source we're using
    
    @classmethod
    def get_model(cls, force_reload=False):
        """
        Load the EXACT trained model from H5 file (like Flask app)
        
        Args:
            force_reload: Force reloading even if cached
            
        Returns:
            Loaded TensorFlow model with grayscale input (1, 224, 224, 1)
            
        IMPORTANT: Must load the exact trained model, not create a new one
        """
        if cls._model is None or force_reload:
            try:
                # Check if TensorFlow is available
                if not TENSORFLOW_AVAILABLE or tf is None:
                    logger.warning("TensorFlow not available, model loading skipped")
                    return None
                
                # Get model path from model_service directory
                model_dir = Path(__file__).parent
                model_path = model_dir / 'mobilenetv2.h5'
                
                if not model_path.exists():
                    logger.warning(f"Model not found at {model_path}, using demo mode")
                    return None
                
                logger.info(f"Loading trained model from {model_path}")
                
                # Try loading with compile=False to avoid optimizer issues
                try:
                    # Use legacy Keras API for better compatibility with old H5 files
                    import warnings
                    warnings.filterwarnings('ignore')
                    cls._model = tf.keras.models.load_model(str(model_path), compile=False)
                    cls._model_loaded_from = "H5_TRAINED_MODEL"
                    logger.info("✓ Trained model loaded successfully (input: grayscale 224x224x1)")
                    
                except Exception as load_error:
                    # Try with custom object to handle batch_shape parameter
                    logger.warning(f"Standard load failed: {str(load_error)[:80]}...")
                    logger.info("Trying custom loader to fix batch_shape issue...")
                    
                    try:
                        # Read and modify the model config to remove batch_shape
                        import json
                        import h5py
                        
                        with h5py.File(str(model_path), 'r') as f:
                            if 'model_config' in f.attrs:
                                config_str = f.attrs['model_config']
                                if isinstance(config_str, bytes):
                                    config_str = config_str.decode('utf-8')
                                
                                config = json.loads(config_str)
                                
                                # Replace batch_shape with shape in all InputLayers
                                if 'config' in config and 'layers' in config['config']:
                                    for layer in config['config']['layers']:
                                        if layer.get('class_name') == 'InputLayer':
                                            layer_config = layer.get('config', {})
                                            if 'batch_shape' in layer_config:
                                                batch_shape = layer_config.pop('batch_shape')
                                                if batch_shape and len(batch_shape) > 1:
                                                    layer_config['shape'] = batch_shape[1:]
                                
                                # Create model from modified config
                                cls._model = tf.keras.models.model_from_json(json.dumps(config))
                                
                                # Load weights into the model
                                cls._model.load_weights(str(model_path))
                                
                                cls._model_loaded_from = "H5_FIXED_CONFIG"
                                logger.info("✓ Model loaded with fixed config (batch_shape -> shape)")
                                
                    except Exception as custom_error:
                        logger.warning(f"Custom loader failed: {str(custom_error)[:80]}...")
                        logger.info("Trying compatibility mode with safe_mode=False...")
                        
                        try:
                            cls._model = tf.keras.models.load_model(
                                str(model_path), 
                                compile=False,
                                safe_mode=False
                            )
                            cls._model_loaded_from = "H5_COMPAT_MODE"
                            logger.info("✓ Model loaded with compatibility mode")
                            
                        except Exception as compat_error:
                            # Last resort: reconstruct exact H5 architecture and load weights
                            logger.warning(f"Compatibility mode failed: {str(compat_error)[:80]}...")
                            logger.info("Reconstructing exact model architecture from H5 file...")
                            
                            try:
                                from tensorflow.keras import layers, models
                                
                                # Exact architecture from H5 inspection:
                                # 1. Input: (224, 224, 1) grayscale
                                # 2. Conv2D: 1x1 to convert grayscale -> 3 channels  
                                # 3. MobileNetV2 backbone
                                # 4. GlobalAveragePooling2D
                                # 5. Dense 256
                                # 6. Dropout 
                                # 7. Dense 1 sigmoid
                                
                                inputs = layers.Input(shape=(224, 224, 1), name='input_layer_1')
                                
                                # Learned grayscale-to-RGB conversion (1x1 conv)
                                x = layers.Conv2D(3, (1, 1), padding='same', name='conv2d')(inputs)
                                
                                # MobileNetV2 backbone (matches 'mobilenetv2_1.00_224' in H5)
                                base_model = tf.keras.applications.MobileNetV2(
                                    input_shape=(224, 224, 3),
                                    include_top=False,
                                    weights=None  # Will load from H5 file
                                )
                                # Rename to match H5 structure
                                base_model._name = 'mobilenetv2_1.00_224'
                                
                                x = base_model(x)
                                x = layers.GlobalAveragePooling2D(name='global_average_pooling2d')(x)
                                x = layers.Dense(256, activation='relu', name='dense')(x)
                                x = layers.Dropout(0.5, name='dropout')(x)
                                
                                # Single sigmoid output (0=NORMAL, 1=PNEUMONIA)
                                outputs = layers.Dense(1, activation='sigmoid', name='dense_1')(x)
                                
                                cls._model = models.Model(inputs=inputs, outputs=outputs, name='functional')
                                
                                # Load ALL weights from H5 file
                                cls._model.load_weights(str(model_path))
                                cls._model_loaded_from = "H5_RECONSTRUCTED"
                                logger.info("✓ Exact model architecture reconstructed, all weights loaded")
                                
                            except Exception as final_error:
                                logger.error(f"All loading strategies failed: {str(final_error)}")
                                cls._model = None
                                return None
                
                cls._model_path = str(model_path)
                logger.info(f"Model source: {cls._model_loaded_from}")
                logger.info(f"Model input shape: {cls._model.input_shape}")
                logger.info(f"Model output shape: {cls._model.output_shape}")
                
                return cls._model
                
            except Exception as e:
                logger.error(f"Unexpected error during model loading: {str(e)}")
                cls._model = None
                return None
        
        return cls._model
    
    @staticmethod
    def _extract_model_info(model_path):
        """Extract model information from H5 file"""
        try:
            with h5py.File(str(model_path), 'r') as f:
                if 'model_config' in f.attrs:
                    config_str = f.attrs['model_config']
                    if isinstance(config_str, bytes):
                        config_str = config_str.decode('utf-8')
                    
                    config = json.loads(config_str)
                    
                    # Extract input shape from config
                    if 'config' in config and 'layers' in config['config']:
                        for layer in config['config']['layers']:
                            if layer.get('class_name') == 'InputLayer':
                                batch_shape = layer.get('config', {}).get('batch_shape')
                                if batch_shape:
                                    return {
                                        'input_shape': tuple(batch_shape[1:]),
                                        'config': config
                                    }
            return None
        except Exception as e:
            logger.debug(f"Could not extract model info: {e}")
            return None
    
    @staticmethod
    def _create_pneumonia_model(input_shape=(224, 224, 1)):
        """Create a pneumonia detection model for given input shape"""
        try:
            inputs = tf.keras.Input(shape=input_shape)
            
            # If grayscale, convert to RGB for MobileNetV2
            if input_shape[-1] == 1:
                x = tf.keras.layers.Lambda(
                    lambda img: tf.image.grayscale_to_rgb(img)
                )(inputs)
            else:
                x = inputs
            
            # MobileNetV2 base
            base_model = tf.keras.applications.MobileNetV2(
                input_shape=(224, 224, 3),
                include_top=False,
                weights='imagenet'
            )
            base_model.trainable = False
            
            x = base_model(x, training=False)
            x = tf.keras.layers.GlobalAveragePooling2D()(x)
            x = tf.keras.layers.Dense(256, activation='relu')(x)
            x = tf.keras.layers.Dropout(0.2)(x)
            outputs = tf.keras.layers.Dense(2, activation='softmax')(x)
            
            model = tf.keras.Model(inputs=inputs, outputs=outputs)
            logger.info(f"Created pneumonia model with input shape {input_shape}")
            return model
        
        except Exception as e:
            logger.error(f"Failed to create pneumonia model: {e}")
            return None
    
    @staticmethod
    def _create_simple_grayscale_cnn():
        """
        Create a simple CNN model for grayscale input (224, 224, 1)
        This is used as fallback when H5 file won't load
        Output: Single sigmoid value (like the trained model)
        """
        try:
            from tensorflow.keras import layers, models
            
            model = models.Sequential([
                # Input layer
                layers.Input(shape=(224, 224, 1)),
                
                # Conv block 1
                layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
                layers.MaxPooling2D((2, 2)),
                
                # Conv block 2
                layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
                layers.MaxPooling2D((2, 2)),
                
                # Conv block 3
                layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
                layers.MaxPooling2D((2, 2)),
                
                # Dense layers
                layers.Flatten(),
                layers.Dense(256, activation='relu'),
                layers.Dropout(0.5),
                layers.Dense(128, activation='relu'),
                layers.Dropout(0.5),
                
                # Output: single sigmoid (0=NORMAL, 1=PNEUMONIA)
                layers.Dense(1, activation='sigmoid')
            ])
            
            logger.info("Created fallback grayscale CNN model")
            return model
        
        except Exception as e:
            logger.error(f"Failed to create fallback CNN: {e}")
            return None
    
    @classmethod
    def predict(cls, preprocessed_image):
        """
        Perform inference on preprocessed image using loaded model
        Matches Flask app prediction logic EXACTLY
        """
        try:
            start_time = time.time()
            model = cls.get_model()
            
            # If model loading failed, use demo mode
            if model is None:
                logger.info("Model load failed, will use demo mode for predictions")
                return None
            
            # Perform inference
            predictions = model.predict(preprocessed_image, verbose=0)
            
            # CRITICAL: Match Flask app prediction logic EXACTLY
            # The model outputs a single value (sigmoid), not 2-class softmax
            confidence = float(predictions[0][0])
            
            # Determine class based on Flask app logic
            if confidence > 0.5:
                label = 'PNEUMONIA'
                confidence_score = confidence
                confidence_pct = confidence * 100
            else:
                label = 'NORMAL'
                confidence_score = 1 - confidence
                confidence_pct = (1 - confidence) * 100
            
            elapsed = time.time() - start_time
            
            # Determine confidence level
            if confidence_pct >= 95:
                confidence_level = 'HIGH'
            elif confidence_pct >= 80:
                confidence_level = 'MODERATE'
            else:
                confidence_level = 'LOW'
            
            return {
                'status': 'success',
                'prediction_label': label,
                'confidence_score': confidence_score,
                'confidence_percentage': confidence_pct,
                'confidence_level': confidence_level,
                'confidence_normal': 1 - confidence if label == 'NORMAL' else confidence,
                'confidence_pneumonia': confidence if label == 'PNEUMONIA' else 1 - confidence,
                'processing_time': elapsed,
                'raw_predictions': {
                    'raw_score': confidence,
                    'NORMAL': 1 - confidence,
                    'PNEUMONIA': confidence
                }
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return None  # Will use demo mode


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
            
            # Try real prediction first
            prediction_result = PneumoniaDetectionService.predict(preprocess_result['data'])
            
            # If real prediction fails or TensorFlow unavailable, use demo mode
            if prediction_result is None or prediction_result.get('status') != 'success':
                logger.warning("Using demo mode for prediction (TensorFlow not available)")
                prediction_result = DemoModeHelper.get_demo_prediction(image_path)
            
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

            # Flat fields for compatibility with older callers/tests
            result['prediction_label'] = prediction_result['prediction_label']
            result['confidence_score'] = prediction_result['confidence_score']
            result['confidence_percentage'] = prediction_result['confidence_percentage']
            result['confidence_level'] = prediction_result['confidence_level']
            result['raw_predictions'] = prediction_result['raw_predictions']
            
            # Add demo mode note if applicable
            if prediction_result.get('demo_mode'):
                result['demo_mode'] = True
                result['note'] = "⚠️ DEMO MODE: Install TensorFlow for actual AI predictions. See TENSORFLOW_SETUP.md"
            
            return result
            
        except Exception as e:
            logger.error(f"Diagnosis error: {str(e)}")
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
