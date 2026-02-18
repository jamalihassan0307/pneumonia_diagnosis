#!/usr/bin/env python
"""
Rebuild model by creating fresh architecture and loading weights only
This avoids config serialization issues entirely
"""

import tensorflow as tf
import h5py
import json
from pathlib import Path
import shutil

print("\n" + "=" * 70)
print("REBUILDING MODEL - LOADING WEIGHTS ONLY")
print("=" * 70 + "\n")

model_path = Path("model_service/mobilenetv2.h5")
backup_path = Path("model_service/mobilenetv2_backup.h5")

try:
    # Step 1: Determine input shape from model config
    print("1. Analyzing original model...")
    with h5py.File(str(model_path), 'r') as f:
        if 'model_config' in f.attrs:
            config_str = f.attrs['model_config']
            if isinstance(config_str, bytes):
                config_str = config_str.decode('utf-8')
            config = json.loads(config_str)
            
            # Find input shape from config
            input_shape = None
            if 'config' in config and 'layers' in config['config']:
                first_layer = config['config']['layers'][0]
                if 'config' in first_layer:
                    layer_config = first_layer['config']
                    if 'batch_shape' in layer_config:
                        batch_shape = layer_config['batch_shape']
                        input_shape = tuple(batch_shape[1:])  # Remove batch dimension
                        print(f"   Found input shape from config: {input_shape}")
            
            if input_shape is None:
                print("   ⚠️ Could not determine input shape, using default (224, 224, 3)")
                input_shape = (224, 224, 3)
        else:
            print("   ⚠️ No model config found, using default input shape (224, 224, 3)")
            input_shape = (224, 224, 3)
    
    print(f"   Model input shape will be: {input_shape}")
    
    # Step 2: Create fresh model with MobileNetV2 architecture
    print("\n2. Creating fresh MobileNetV2 model...")
    
    # Handle grayscale input by converting to 3 channels
    if input_shape[2] == 1:
        print("   Creating grayscale-to-RGB conversion layer...")
        # Input layer for grayscale
        input_layer = tf.keras.layers.Input(shape=input_shape, name='grayscale_input')
        
        # Convert 1 channel to 3 channels by repeating
        x = tf.keras.layers.Lambda(
            lambda img: tf.repeat(img, 3, axis=-1),
            name='grayscale_to_rgb'
        )(input_layer)
        
        # Create MobileNetV2 with RGB input
        base_model = tf.keras.applications.MobileNetV2(
            input_shape=(input_shape[0], input_shape[1], 3),
            include_top=False,
            weights='imagenet',
            input_tensor=x
        )
        
        model_input = input_layer
    else:
        # RGB input - use directly
        base_model = tf.keras.applications.MobileNetV2(
            input_shape=input_shape,
            include_top=False,
            weights='imagenet'
        )
        model_input = base_model.input
    
    # Add classification head (2 classes: NORMAL, PNEUMONIA)
    x = tf.keras.layers.GlobalAveragePooling2D()(base_model.output)
    x = tf.keras.layers.Dense(128, activation='relu')(x)
    x = tf.keras.layers.Dropout(0.5)(x)
    predictions = tf.keras.layers.Dense(2, activation='softmax', name='predictions')(x)
    
    model = tf.keras.Model(inputs=model_input, outputs=predictions)
    print(f"   ✓ Fresh model created")
    print(f"   Input: {model.input_shape}")
    print(f"   Output: {model.output_shape}")
    print(f"   Total layers: {len(model.layers)}")
    
    # Step 3: Try to load weights from original model
    print("\n3. Loading weights from original model...")
    try:
        model.load_weights(str(model_path), by_name=True, skip_mismatch=True)
        print("   ✓ Weights loaded successfully (by name, ignoring mismatches)")
    except Exception as e:
        print(f"   ⚠️ Could not load all weights: {e}")
        print("   Model will use ImageNet base weights + random classification head")
    
    # Step 4: Compile model
    print("\n4. Compiling model...")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    print("   ✓ Model compiled")
    
    # Step 5: Backup and save
    print("\n5. Saving rebuilt model...")
    
    # Backup original if not already done
    if not backup_path.exists():
        shutil.copy(model_path, backup_path)
        print(f"   ✓ Original backed up to {backup_path}")
    else:
        print(f"   ℹ Backup already exists at {backup_path}")
    
    # Save new model
    model.save(str(model_path), save_format='h5')
    print(f"   ✓ Rebuilt model saved to {model_path}")
    
    # Step 6: Verify loading
    print("\n6. Verifying rebuilt model loads correctly...")
    test_model = tf.keras.models.load_model(str(model_path))
    print(f"   ✓ Model loads successfully!")
    print(f"   Input: {test_model.input_shape}")
    print(f"   Output: {test_model.output_shape}")
    
    print("\n" + "=" * 70)
    print("✅ MODEL REBUILD SUCCESSFUL!")
    print("=" * 70)
    print(f"\nNOTE: The model now uses:")
    print(f"  - MobileNetV2 base with ImageNet weights")
    print(f"  - Original weights where compatible")
    print(f"  - Input shape: {input_shape}")
    print(f"  - Output: 2 classes (NORMAL, PNEUMONIA)")
    print(f"\n⚠️  IMPORTANT: Model accuracy may differ from original.")
    print(f"   Consider retraining on your dataset for best results.")
    print("\n" + "=" * 70 + "\n")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print(f"\nIf this fails, the system will continue to work in demo mode.")
    exit(1)
