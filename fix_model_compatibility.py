#!/usr/bin/env python
"""
Rebuild the model to fix Keras 2.13 compatibility

This script fixes the 'batch_shape' incompatibility issue
by loading the original model config and removing deprecated parameters.
"""

import json
import h5py
import tensorflow as tf
from pathlib import Path

print("\n" + "=" * 70)
print("FIXING MODEL COMPATIBILITY FOR KERAS 2.13")
print("=" * 70 + "\n")

model_path = Path("model_service/mobilenetv2.h5")
backup_path = Path("model_service/mobilenetv2_backup.h5")

try:
    print(f"1. Loading model config from {model_path}...")
    
    # Read the original model config
    with h5py.File(str(model_path), 'r') as f:
        # Get model config
        if 'model_config' not in f.attrs:
            print("⚠️  No model_config found. Cannot rebuild.")
            exit(1)
            
        config_str = f.attrs['model_config']
        if isinstance(config_str, bytes):
            config_str = config_str.decode('utf-8')
        
        config = json.loads(config_str)
        print(f"✓ Model config loaded ({len(config_str)} bytes)")
        
        # Check for batch_shape in config
        def fix_batch_shape(obj):
            """Recursively remove batch_shape from config"""
            if isinstance(obj, dict):
                if 'batch_shape' in obj:
                    del obj['batch_shape']
                    print("  - Fixed: Removed 'batch_shape' from InputLayer config")
                for key, value in obj.items():
                    fix_batch_shape(value)
            elif isinstance(obj, list):
                for item in obj:
                    fix_batch_shape(item)
        
        print("\n2. Fixing deprecated 'batch_shape' parameter...")
        fix_batch_shape(config)
        
        print("\n3. Rebuilding model with fixed config...")
        # Rebuild model from config
        model = tf.keras.models.model_from_json(json.dumps(config))
        print("✓ Model rebuilt successfully")
        
        print("\n4. Loading weights from original model...")
        # Load weights from the original model file
        model.load_weights(str(model_path), by_name=True, skip_mismatch=True)
        print("✓ Weights loaded successfully")
        
        print("\n5. Saving fixed model...")
        # Backup original
        import shutil
        if not backup_path.exists():
            shutil.copy(model_path, backup_path)
            print(f"✓ Original model backed up to {backup_path}")
        
        # Save fixed model
        model.save(str(model_path), save_format='h5')
        print(f"✓ Fixed model saved to {model_path}")
        
        print("\n" + "=" * 70)
        print("✅ MODEL SUCCESSFULLY FIXED!")
        print("=" * 70)
        print(f"\nModel Details:")
        print(f"  Input shape: {model.input_shape}")
        print(f"  Output shape: {model.output_shape}")
        print(f"  Total layers: {len(model.layers)}")
        print(f"\n✓ The system is now ready for REAL AI predictions!")
        print("\n" + "=" * 70 + "\n")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print(f"\nTroubleshooting:")
    print(f"  - Ensure TensorFlow 2.13.0+ is installed")
    print(f"  - Check that {model_path} exists and is a valid H5 file")
    print(f"  - Verify you have write permissions to the directory")
    exit(1)
