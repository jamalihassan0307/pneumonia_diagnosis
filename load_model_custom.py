"""
Custom model loader that handles batch_shape parameter in old H5 files
"""
import tensorflow as tf
import json
import h5py
from pathlib import Path


def custom_input_layer(**kwargs):
    """Wrapper for InputLayer that converts batch_shape to shape"""
    if 'batch_shape' in kwargs:
        batch_shape = kwargs.pop('batch_shape')
        if batch_shape and len(batch_shape) > 1:
            kwargs['shape'] = tuple(batch_shape[1:])
    return tf.keras.layers.InputLayer(**kwargs)


def load_model_with_batch_shape_fix(model_path):
    """
    Load H5 model that uses deprecated batch_shape parameter
    
    Args:
        model_path: Path to .h5 file
        
    Returns:
        Loaded Keras model
    """
    model_path = Path(model_path)
    
    # Read model config
    with h5py.File(str(model_path), 'r') as f:
        config_str = f.attrs['model_config']
        if isinstance(config_str, bytes):
            config_str = config_str.decode('utf-8')
    
    config = json.loads(config_str)
    
    # Create model from config with custom InputLayer
    custom_objects = {'InputLayer': custom_input_layer}
    
    try:
        model = tf.keras.models.model_from_config(config, custom_objects=custom_objects)
    except Exception as e:
        print(f"model_from_config failed: {e}")
        #  Fallback: modify config to replace batch_shape with shape
        if 'config' in config and 'layers' in config['config']:
            for layer in config['config']['layers']:
                if layer.get('class_name') == 'InputLayer':
                    layer_config = layer.get('config', {})
                    if 'batch_shape' in layer_config:
                        batch_shape = layer_config.pop('batch_shape')
                        if batch_shape and len(batch_shape) > 1:
                            layer_config['shape'] = tuple(batch_shape[1:])
        
        model = tf.keras.models.model_from_json(json.dumps(config))
    
    #  Load weights
    model.load_weights(str(model_path))
    
    print(f"✓ Model loaded successfully")
    print(f"  Input shape: {model.input_shape}")
    print(f"  Output shape: {model.output_shape}")
    
    return model


if __name__ == "__main__":
    # Test loading
    model_path = "model_service/mobilenetv2.h5"
    model = load_model_with_batch_shape_fix(model_path)
    
    # Test prediction on sample input
    import numpy as np
    import cv2
    
    # Load test image (grayscale)
    img_path = "media/xray_images/person1_bacteria_1.jpeg"
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (224, 224))
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)
    img = np.expand_dims(img, axis=-1)
    
    print(f"\nTest image shape: {img.shape}")
    
    # Predict
    pred = model.predict(img, verbose=0)
    confidence = float(pred[0][0])
    
    if confidence > 0.5:
        label = "PNEUMONIA"
        conf_pct = confidence * 100
    else:
        label = "NORMAL"
        conf_pct = (1 - confidence) * 100
    
    print(f"\nPrediction: {label} ({conf_pct:.2f}%)")
