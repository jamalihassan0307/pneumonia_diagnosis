"""
Convert old H5 model to TensorFlow SavedModel format
This uses compatibility layers to load the old model and resave it
"""
import tensorflow as tf
import numpy as np
from pathlib import Path

print("TensorFlow version:", tf.__version__)

old_h5_path = "model_service/mobilenetv2.h5"
output_dir = "model_service/mobilenetv2_saved_model"

print(f"\nConverting {old_h5_path} to SavedModel format...")

# Try multiple loading strategies
model = None

# Strategy 1: Load with warnings ignored
print("\n[1] Trying standard load_model...")
try:
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = tf.keras.models.load_model(old_h5_path, compile=False)
    print("✓ Success!")
except Exception as e:
    print(f"✗ Failed: {e}")

# Strategy 2: Disable eager execution and try compat mode
if model is None:
    print("\n[2] Trying with tf.compat.v1...")
    try:
        # Try loading in compatibility mode
        tf.compat.v1.disable_eager_execution()
        with tf.compat.v1.Session() as sess:
            from tensorflow.python.keras._impl.keras.models import load_model as v1_load
            model = v1_load(old_h5_path, compile=False)
        tf.compat.v1.enable_eager_execution()
        print("✓ Success!")
    except Exception as e:
        print(f"✗ Failed: {e}")
        try:
            tf.compat.v1.enable_eager_execution()
        except:
            pass

# Strategy 3: Load with custom deserialization
if model is None:
    print("\n[3] Trying custom deserialization...")
    try:
        import h5py
        import json
        
        # Read and manually fix the config
        with h5py.File(old_h5_path, 'r') as f:
            config_str = f.attrs['model_config']
            if isinstance(config_str, bytes):
                config_str = config_str.decode('utf-8')
            
            config = json.loads(config_str)
            
            # Simplify dtype configs
            def fix_dtype(layer_config):
                if 'dtype' in layer_config and isinstance(layer_config['dtype'], dict):
                    layer_config['dtype'] = 'float32'
                if 'batch_shape' in layer_config:
                    batch_shape = layer_config.pop('batch_shape')
                    if batch_shape and len(batch_shape) > 1:
                        layer_config['input_shape'] = tuple(batch_shape[1:])
                return layer_config
            
            # Fix all layers
            if 'config' in config and 'layers' in config['config']:
                for layer in config['config']['layers']:
                    if 'config' in layer:
                        layer['config'] = fix_dtype(layer['config'])
            
            # Try loading with fixed config
            model = tf.keras.models.model_from_json(json.dumps(config))
            model.load_weights(old_h5_path)
            print("✓ Success!")
    except Exception as e:
        print(f"✗ Failed: {e}")

if model is None:
    print("\n❌ All loading strategies failed. Cannot convert model.")
    print("\nSUGGESTION: The model needs to be re-exported from the training environment")
    print("with: model.save('mobilenetv2_new.h5', save_format='h5') or model.export('mobilenetv2_saved_model')")
    exit(1)

# Model loaded successfully - now convert it
print(f"\n✓ Model loaded successfully!")
print(f"  Input shape: {model.input_shape}")
print(f"  Output shape: {model.output_shape}")

# Test the model works
print("\nTesting model inference...")
test_input = np.random.random((1, 224, 224, 1)).astype(np.float32)
test_output = model.predict(test_input, verbose=0)
print(f"✓ Test prediction shape: {test_output.shape}")
print(f"✓ Test prediction value: {test_output[0][0]:.4f}")

# Save as SavedModel
print(f"\nSaving to {output_dir}...")
model.save(output_dir, save_format='tf')
print("✓ Saved as TensorFlow SavedModel")

# Also save as new H5
new_h5_path = "model_service/mobilenetv2_converted.h5"
print(f"\nSaving to {new_h5_path}...")
model.save(new_h5_path, save_format='h5')
print("✓ Saved as H5")

print("\n" + "="*70)
print("CONVERSION COMPLETE")
print("="*70)
print(f"\nYou can now use:")
print(f"  - SavedModel: {output_dir}")
print(f"  - H5 file: {new_h5_path}")
print("\nBoth should work with TensorFlow 2.13.0")
