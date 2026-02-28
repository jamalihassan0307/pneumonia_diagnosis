"""Inspect H5 file structure to understand the model architecture"""
import h5py
import json

h5_path = 'model_service/mobilenetv2.h5'

print("="*70)
print("H5 FILE INSPECTION")
print("="*70)

with h5py.File(h5_path, 'r') as f:
    print("\nRoot keys:", list(f.keys()))
    
    if 'model_weights' in f:
        print("\nModel weights structure:")
        def print_structure(name, obj):
            if isinstance(obj, h5py.Group):
                print(f"  Group: {name}")
            elif isinstance(obj, h5py.Dataset):
                print(f"  Dataset: {name}, shape: {obj.shape}")
        
        f['model_weights'].visititems(print_structure)
    
    # Check for model config
    if 'model_config' in f.attrs:
        config_str = f.attrs['model_config']
        if isinstance(config_str, bytes):
            config_str = config_str.decode('utf-8')
        
        config = json.loads(config_str)
        
        print("\n" + "="*70)
        print("MODEL CONFIGURATION")
        print("="*70)
        print(f"\nModel class: {config.get('class_name')}")
        print(f"Backend: {config.get('backend')}")
        
        if 'config' in config:
            model_config = config['config']
            print(f"\nModel name: {model_config.get('name')}")
            
            if 'layers' in model_config:
                print(f"\nTotal layers: {len(model_config['layers'])}")
                print("\nLayer summary:")
                for i, layer in enumerate(model_config['layers'][:10]):  # First 10 layers
                    layer_class = layer.get('class_name', 'Unknown')
                    layer_name = layer.get('config', {}).get('name', 'unnamed')
                    
                    if layer_class == 'InputLayer':
                        batch_shape = layer.get('config', {}).get('batch_shape')
                        print(f"  {i}: {layer_class} '{layer_name}' - batch_shape: {batch_shape}")
                    else:
                        print(f"  {i}: {layer_class} '{layer_name}'")
                
                if len(model_config['layers']) > 10:
                    print(f"  ... ({len(model_config['layers']) - 10} more layers)")
                
                # Show last layer
                last_layer = model_config['layers'][-1]
                print(f"  {len(model_config['layers'])-1}: {last_layer.get('class_name')} '{last_layer.get('config', {}).get('name')}'")
                
                # Check output layer details
                if 'units' in last_layer.get('config', {}):
                    units = last_layer['config']['units']
                    activation = last_layer['config'].get('activation')
                    print(f"      Output: {units} units, activation: {activation}")
