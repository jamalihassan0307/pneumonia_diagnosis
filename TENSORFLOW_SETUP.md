# TensorFlow Installation Guide

## Problem
You're seeing the error: `'NoneType' object has no attribute 'keras'`

This means **TensorFlow is not installed** in your Python environment.

## Solution

### Option 1: Using Python 3.11 or Earlier (Recommended)
TensorFlow 2.13.0+ requires Python ≤ 3.11 for full compatibility.

```bash
# Install TensorFlow for CPU (no GPU)
pip install tensorflow==2.13.0

# Or install with wheel (if above fails)
pip install --only-binary :all: tensorflow==2.13.0
```

### Option 2: Using Latest TensorFlow (Python 3.12+)
If you're using Python 3.12 or later, install the latest version:

```bash
pip install tensorflow
```

### Option 3: Using Conda (Alternative)
If pip installation fails, use Conda:

```bash
# Create new environment with Python 3.11
conda create -n pneumonia-env python=3.11

# Activate environment
conda activate pneumonia-env

# Install all dependencies
conda install tensorflow django pillow numpy pandas

# If in project directory:
pip install -r requirements.txt
```

### Option 4: Install Without GPU Support (Lightweight)
For CPU-only usage (lighter installation):

```bash
pip install tensorflow-cpu
```

---

## Verification

After installation, verify TensorFlow works:

```bash
python -c "import tensorflow as tf; print(f'TensorFlow {tf.__version__} successfully installed!')"
```

Expected output:
```
TensorFlow 2.13.0 successfully installed!
```

---

## If Installation Fails

### Check Your Python Version
```bash
python --version
```

- **Python 3.11 or earlier**: Install `tensorflow==2.13.0`
- **Python 3.12+**: Install just `tensorflow` (latest version)

### Clear pip cache
```bash
pip cache purge
pip install --force-reinstall tensorflow
```

### Common Issues

**Issue**: `No module named 'tensorflow_toolz'`
- **Solution**: Update pip first
- ```bash
  pip install --upgrade pip setuptools wheel
  pip install tensorflow
  ```

**Issue**: `ModuleNotFoundError: No module named 'tensorflow'` persists
- **Solution**: You may have multiple Python installations
- ```bash
  # Find which python you're using
  which python  # or: where python (Windows)
  
  # Use full path to install
  C:/path/to/python.exe -m pip install tensorflow
  ```

---

## After Installation

Once TensorFlow is installed, restart Django:

```bash
# Stop the current server (Ctrl+C)

# Start Django again
python manage.py runserver
```

Then try uploading an X-ray image again. The diagnosis should work!

---

## What Gets Installed?

Installing TensorFlow also installs:
- NumPy (numerical computing)
- Protobuf (data serialization)
- H5py (HDF5 file support - essential for loading .h5 models)
- gast, opt_einsum, tensornetwork (support libraries)

These are all required for the pneumonia detection system to work.

---

## Help & Support

If you still have issues:

1. **Check Django logs** in the terminal where you ran `python manage.py runserver`
2. **Check file location**: Ensure `model_service/mobilenetv2.h5` exists
3. **Reinstall cleanly**:
   ```bash
   pip uninstall tensorflow -y
   pip install tensorflow
   ```

---

**Last Updated**: February 17, 2026
