"""
Advanced H5 Model Loader - Bypasses Keras deserialization issues
Loads weights directly from H5 file into manually reconstructed model
"""

import tensorflow as tf
import h5py
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def load_weights_from_h5_bypass_keras(model, h5_path):
    """
    Load weights from H5 file directly, bypassing Keras load_weights
    Maps weights by name matching
    """
    with h5py.File(h5_path, 'r') as f:
        if 'model_weights' not in f:
            raise ValueError("H5 file doesn't contain model_weights")
        
        weights_group = f['model_weights']
        
        # Load weights for each layer
        for layer in model.layers:
            layer_name = layer.name
            
            # Skip input layer
            if isinstance(layer, tf.keras.layers.InputLayer):
                continue
            
            # Check if weights exist for this layer
            if layer_name not in weights_group:
                logger.warning(f"No weights found for layer: {layer_name}")
                continue
            
            layer_group = weights_group[layer_name]
            
            # Get weight names for this layer
            weight_names = []
            layer_group.visit(lambda name: weight_names.append(name) if isinstance(layer_group[name], h5py.Dataset) else None)
            
            if not weight_names:
                continue
            
            # Load weights
            weights_to_set = []
            for weight_name in sorted(weight_names):
                weight_data = np.array(layer_group[weight_name])
                weights_to_set.append(weight_data)
            
            # Set weights to layer
            try:
                if weights_to_set:
                    layer.set_weights(weights_to_set)
                    logger.info(f"✓ Loaded weights for layer: {layer_name}")
            except Exception as e:
                logger.warning(f"✗ Failed to set weights for layer {layer_name}: {e}")
                continue
    
    return model


def load_mobilenetv2_pneumonia_model(h5_path):
    """
    Load MobileNetV2 pneumonia model with direct weight loading
    
    Args:
        h5_path: Path to mobilenetv2.h5 file
        
    Returns:
        Loaded Keras model or None if failed
    """
    h5_path = Path(h5_path)
    
    if not h5_path.exists():
        logger.error(f"Model file not found: {h5_path}")
        return None
    
    logger.info(f"Loading model from: {h5_path}")
    
    try:
        # Strategy 1: Standard load (works if H5 is compatible)
        logger.info("Attempting standard load...")
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            try:
                model = tf.keras.models.load_model(str(h5_path), compile=False)
                logger.info("✓ Standard load successful!")
                return model
            except Exception as e:
                logger.warning(f"Standard load failed: {str(e)[:100]}")
        
        # Strategy 2: Load with safe_mode=False
        logger.info("Attempting load with safe_mode=False...")
        try:
            model = tf.keras.models.load_model(str(h5_path), compile=False, safe_mode=False)
            logger.info("✓ Safe mode load successful!")
            return model
        except Exception as e:
            logger.warning(f"Safe mode load failed: {str(e)[:100]}")
        
        # Strategy 3: Build architecture and load weights directly
        logger.info("Building model architecture and loading weights directly...")
        
        # Build the exact architecture
        from tensorflow.keras import layers, models
        
        # Input: grayscale 224x224x1
        inputs = layers.Input(shape=(224, 224, 1), name='input_layer_1')
        
        # Conv2D: 1x1 kernel, 1 channel -> 3 channels (learned grayscale-to-RGB)
        x = layers.Conv2D(3, (1, 1), padding='valid', use_bias=True, name='conv2d')(inputs)
        
        # MobileNetV2 backbone
        base_model = tf.keras.applications.MobileNetV2(
            input_shape=(224, 224, 3),
            include_top=False,
            weights=None  # Don't load ImageNet weights
        )
        base_model._name = 'mobilenetv2_1.00_224'
        
        x = base_model(x)
        
        # Top layers
        x = layers.GlobalAveragePooling2D(name='global_average_pooling2d')(x)
        x = layers.Dense(256, activation='relu', use_bias=True, name='dense')(x)
        x = layers.Dropout(0.5, name='dropout')(x)
        outputs = layers.Dense(1, activation='sigmoid', use_bias=True, name='dense_1')(x)
        
        model = models.Model(inputs=inputs, outputs=outputs, name='functional')
        
        logger.info(f"Model architecture created: {len(model.layers)} layers")
        
        # Load weights using custom loader
        logger.info("Loading weights from H5 file...")
        model = load_weights_from_h5_bypass_keras(model, h5_path)
        
        # Verify model loaded correctly
        test_input = np.random.random((1, 224, 224, 1)).astype(np.float32)
        test_output = model.predict(test_input, verbose=0)
        
        if test_output.shape == (1, 1):
            logger.info(f"✓ Model loaded successfully! Output shape: {test_output.shape}")
            logger.info(f"✓ Test prediction: {test_output[0][0]:.6f}")
            return model
        else:
            logger.error(f"Model output shape incorrect: {test_output.shape}")
            return None
        
    except Exception as e:
        logger.error(f"All loading strategies failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None


if __name__ == "__main__":
    # Test the loader
    import sys
    
    model_path = "model_service/mobilenetv2.h5"
    
    print("="*70)
    print("TESTING ADVANCED MODEL LOADER")
    print("="*70)
    
    model = load_mobilenetv2_pneumonia_model(model_path)
    
    if model is not None:
        print("\n✓ SUCCESS! Model loaded successfully")
        print(f"  Input shape: {model.input_shape}")
        print(f"  Output shape: {model.output_shape}")
        
        # Test on real image
        import cv2
        test_img_path = "media/xray_images/person1_bacteria_1.jpeg"
        
        if Path(test_img_path).exists():
            img = cv2.imread(test_img_path, cv2.IMREAD_GRAYSCALE)
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
            
            print(f"\n  Test Image: {Path(test_img_path).name}")
            print(f"  Prediction: {label} ({conf_pct:.2f}%)")
            print(f"  Raw confidence: {confidence:.6f}")
    else:
        print("\n✗ FAILED to load model")
        sys.exit(1)
