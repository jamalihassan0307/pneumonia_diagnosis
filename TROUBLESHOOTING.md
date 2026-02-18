# Troubleshooting Guide

Common issues and their solutions for the Pneumonia Detection System.

## 🔴 Installation Issues

### Issue: Python not found

**Error:**
```
'python' is not recognized as an internal or external command
```

**Solutions:**
1. Install Python from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart your terminal/PowerShell
4. Verify: `python --version`

Alternative: Try `py` instead of `python`:
```powershell
py --version
py -m pip install -r requirements.txt
```

---

### Issue: pip not working

**Error:**
```
'pip' is not recognized as an internal or external command
```

**Solution:**
Use Python's pip module directly:
```powershell
python -m pip install -r requirements.txt
python -m pip install --upgrade pip
```

---

### Issue: TensorFlow installation fails

**Error:**
```
ERROR: Could not find a version that satisfies the requirement tensorflow
```

**Solutions:**

1. **Check Python version:**
   ```powershell
   python --version
   ```
   TensorFlow 2.15 requires Python 3.8-3.11. If you have Python 3.12+, downgrade or use TensorFlow 2.16+.

2. **Install specific TensorFlow version:**
   ```powershell
   pip install tensorflow==2.15.0 --upgrade
   ```

3. **For Windows, ensure you have Visual C++ Redistributable:**
   Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe

4. **Use TensorFlow CPU version if GPU fails:**
   ```powershell
   pip install tensorflow-cpu==2.15.0
   ```

5. **Update pip and try again:**
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

### Issue: Virtual environment activation fails (PowerShell)

**Error:**
```
cannot be loaded because running scripts is disabled on this system
```

**Solution:**
Enable script execution (run PowerShell as Administrator):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again:
```powershell
venv\Scripts\Activate.ps1
```

Alternative (without changing policy):
```powershell
venv\Scripts\activate.bat
```

---

## 🔴 Model Loading Issues

### Issue: Model file not found

**Error in terminal:**
```
FileNotFoundError: Model file not found at ...\ml_models\mobilenetv2_pneumonia_model.h5
```

**Solutions:**

1. **Verify model file exists:**
   ```powershell
   Test-Path "ml_models\mobilenetv2_pneumonia_model.h5"
   ```
   Should return `True`.

2. **Check file name exactly:**
   - Must be: `mobilenetv2_pneumonia_model.h5`
   - Common mistakes: `model.h5`, `pneumonia_model.h5`, `MobileNetV2.h5`

3. **Create directory if missing:**
   ```powershell
   New-Item -ItemType Directory -Path "ml_models" -Force
   ```

4. **Copy your model:**
   ```powershell
   Copy-Item "path\to\your\model.h5" -Destination "ml_models\mobilenetv2_pneumonia_model.h5"
   ```

---

### Issue: Model fails to load

**Error:**
```
Exception: Failed to load model: ...
```

**Possible Causes & Solutions:**

1. **Corrupted model file:**
   - Re-download or re-train model
   - Verify file size (should be several MB)

2. **Wrong TensorFlow version:**
   - Model was saved with different TensorFlow version
   - Try: `pip install tensorflow==2.15.0` (match training version)

3. **Model format issues:**
   - Ensure model is in Keras `.h5` format
   - If using SavedModel format, convert to `.h5`:
   ```python
   from tensorflow import keras
   model = keras.models.load_model('path/to/saved_model')
   model.save('mobilenetv2_pneumonia_model.h5')
   ```

4. **Memory issues:**
   - Close other applications
   - Restart computer
   - Check available RAM

---

## 🔴 File Upload Issues

### Issue: File upload fails immediately

**Error in browser:**
```
Invalid file type. Please upload a PNG, JPG, or JPEG image.
```

**Solutions:**
1. Check file extension is `.png`, `.jpg`, or `.jpeg`
2. Convert image if needed:
   - Use Paint, GIMP, or online converters
   - Save as PNG or JPEG

---

### Issue: File too large

**Error:**
```
File too large. Maximum size: 16MB
```

**Solutions:**
1. **Compress image:**
   - Use online tools like TinyPNG, CompressJPEG
   - Reduce image dimensions (still needs 224x224 minimum)

2. **Increase upload limit (if needed):**
   Edit `pneumonia_diagnosis/settings.py`:
   ```python
   FILE_UPLOAD_MAX_MEMORY_SIZE = 32 * 1024 * 1024  # 32MB
   DATA_UPLOAD_MAX_MEMORY_SIZE = 32 * 1024 * 1024  # 32MB
   ```

---

### Issue: Corrupted image file

**Error:**
```
Invalid or corrupted image file
```

**Solutions:**
1. Try opening image in image viewer first
2. Re-download or obtain new copy of image
3. Convert to PNG format
4. Use different X-ray image

---

## 🔴 Prediction Issues

### Issue: Prediction takes too long (>30 seconds)

**Possible Causes:**
1. First prediction (model loading)
2. Large image file
3. Slow computer/low RAM

**Solutions:**
1. **Wait for first prediction** (model loads once)
2. **Reduce image size:**
   ```powershell
   # Images are resized to 224x224 anyway
   # Use smaller input images
   ```
3. **Close other applications**
4. **Use GPU acceleration** (if available):
   ```powershell
   pip install tensorflow-gpu==2.15.0
   ```

---

### Issue: Predictions always same result

**Example:** Always predicts NORMAL or always PNEUMONIA

**Solutions:**

1. **Check model quality:**
   - Model may not be properly trained
   - Test model separately with known images
   - Retrain if accuracy is low

2. **Verify preprocessing:**
   - Check if images are being preprocessed correctly
   - Add logging in `services.py`:
   ```python
   print(f"Image shape after preprocessing: {img_array.shape}")
   print(f"Pixel value range: {img_array.min()} to {img_array.max()}")
   ```

3. **Adjust prediction threshold:**
   Edit `xray_detector/services.py`:
   ```python
   # Try different threshold
   if raw_score >= 0.3:  # More sensitive to pneumonia
   # or
   if raw_score >= 0.7:  # Less sensitive to pneumonia
   ```

---

### Issue: Prediction returns error

**Error:**
```
Server error: ...
```

**Solutions:**
1. **Check terminal logs** for detailed error
2. **Common fixes:**
   ```powershell
   # Reinstall dependencies
   pip install --force-reinstall tensorflow pillow numpy
   
   # Clear cache
   python manage.py collectstatic --clear --noinput
   
   # Restart server
   # Press Ctrl+C, then:
   python manage.py runserver
   ```

---

## 🔴 Server Issues

### Issue: Port already in use

**Error:**
```
Error: That port is already in use.
```

**Solutions:**

1. **Use different port:**
   ```powershell
   python manage.py runserver 8080
   ```
   Access at: `http://127.0.0.1:8080/`

2. **Kill existing process:**
   ```powershell
   # Find process using port 8000
   netstat -ano | findstr :8000
   
   # Kill process (replace PID with actual number)
   taskkill /PID <PID> /F
   ```

---

### Issue: Server starts but website doesn't load

**Error in browser:**
```
This site can't be reached
```

**Solutions:**

1. **Check server is running:**
   - Look for "Starting development server" message
   - No errors in terminal

2. **Try different URL:**
   - `http://127.0.0.1:8000/`
   - `http://localhost:8000/`

3. **Check firewall:**
   - Windows Firewall may be blocking
   - Allow Python through firewall

4. **Restart server:**
   ```powershell
   # Press Ctrl+C to stop
   python manage.py runserver
   ```

---

### Issue: Static files not loading (CSS not working)

**Symptoms:** Plain HTML without styling

**Solutions:**

1. **Check DEBUG setting:**
   In `pneumonia_diagnosis/settings.py`:
   ```python
   DEBUG = True  # Must be True for development
   ```

2. **Collect static files:**
   ```powershell
   python manage.py collectstatic --noinput
   ```

3. **Clear browser cache:**
   - Press `Ctrl + Shift + Delete`
   - Clear cached images and files
   - Refresh page with `Ctrl + F5`

---

## 🔴 Template Issues

### Issue: Template not found

**Error:**
```
TemplateDoesNotExist at /
xray_detector/index.html
```

**Solutions:**

1. **Check template location:**
   ```powershell
   Test-Path "templates\xray_detector\index.html"
   ```
   Should return `True`.

2. **Verify settings.py:**
   ```python
   TEMPLATES = [
       {
           'DIRS': [BASE_DIR / 'templates'],  # Must be present
           ...
       },
   ]
   ```

3. **Restart server** after adding templates.

---

## 🔴 CSRF Issues

### Issue: CSRF verification failed

**Error in browser console (F12):**
```
Forbidden (403)
CSRF verification failed
```

**Solutions:**

1. **Ensure CSRF middleware is enabled:**
   In `settings.py`:
   ```python
   MIDDLEWARE = [
       ...
       'django.middleware.csrf.CsrfViewMiddleware',  # Must be present
       ...
   ]
   ```

2. **Check template has CSRF token:**
   Template includes CSRF token handling in JavaScript (already implemented).

3. **Clear cookies:**
   - Browser settings → Clear browsing data → Cookies
   - Refresh page

4. **Disable CSRF for testing ONLY:**
   In `views.py` (NOT recommended for production):
   ```python
   from django.views.decorators.csrf import csrf_exempt
   
   @csrf_exempt  # Only for testing!
   def index(request):
       ...
   ```

---

## 🔴 Browser Issues

### Issue: Upload/preview not working

**Symptoms:**
- Can't select file
- Preview doesn't show
- Button clicks do nothing

**Solutions:**

1. **Check browser console (F12):**
   - Look for JavaScript errors
   - Note any error messages

2. **Try different browser:**
   - Chrome (recommended)
   - Firefox
   - Edge

3. **Disable browser extensions:**
   - Ad blockers may interfere
   - Try incognito/private mode

4. **Clear browser cache:**
   - `Ctrl + Shift + Delete`
   - Clear cached files
   - Refresh with `Ctrl + F5`

---

## 🔴 Permission Issues

### Issue: Can't create directories/files

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

1. **Run terminal as Administrator:**
   - Right-click PowerShell
   - "Run as administrator"

2. **Check folder permissions:**
   ```powershell
   # Make sure you have write access to project folder
   icacls "e:\uni projects\ML\pneumonia diagnosis(updated)\attiq_pneumonia_project\Pneumonia_digonosis"
   ```

3. **Use different location:**
   - Copy project to `C:\Projects\Pneumonia_digonosis`
   - Avoid long paths with spaces

---

## 🔴 Performance Issues

### Issue: Application is slow

**Symptoms:**
- Pages load slowly
- Predictions take >10 seconds
- Server response delayed

**Solutions:**

1. **Check system resources:**
   ```powershell
   # Task Manager: Ctrl+Shift+Esc
   # Check CPU, RAM, Disk usage
   ```

2. **Close unnecessary applications:**
   - Browser tabs
   - Other Python processes
   - Heavy applications

3. **Optimize model loading:**
   Model is cached after first load. First prediction is slower.

4. **Use smaller images:**
   - Images are resized to 224x224
   - Upload smaller files

5. **Upgrade hardware:**
   - More RAM (8GB+ recommended)
   - SSD instead of HDD
   - Better CPU

---

## 🔴 Windows-Specific Issues

### Issue: Long path names error

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory
```

**Solution:**
Enable long path support in Windows:

1. **Registry edit** (run as Administrator):
   ```powershell
   reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f
   ```

2. **Or move project closer to root:**
   ```powershell
   # Instead of: e:\uni projects\ML\pneumonia diagnosis(updated)\...
   # Use: C:\Projects\Pneumonia_digonosis
   ```

3. **Restart computer** after registry change.

---

## 📧 Getting Help

If you're still experiencing issues:

1. **Check terminal logs:**
   - Copy error messages
   - Note what triggers the error

2. **Check browser console (F12):**
   - Note any JavaScript errors
   - Check Network tab for failed requests

3. **Verify setup:**
   - Go through setup instructions again
   - Ensure all steps completed

4. **System information:**
   ```powershell
   python --version
   pip list
   systeminfo
   ```

5. **Test with minimal setup:**
   - Fresh virtual environment
   - Clean installation
   - Different test image

---

## ✅ Quick Fixes Checklist

Try these in order:

- [ ] Restart development server (`Ctrl+C`, then `python manage.py runserver`)
- [ ] Restart terminal/PowerShell
- [ ] Clear browser cache (`Ctrl+Shift+Delete`)
- [ ] Refresh page (`Ctrl+F5`)
- [ ] Check model file exists (`Test-Path "ml_models\mobilenetv2_pneumonia_model.h5"`)
- [ ] Verify virtual environment activated (`(venv)` in prompt)
- [ ] Check terminal for error messages
- [ ] Try different image file
- [ ] Try different browser
- [ ] Restart computer

---

## 🎯 Still Need Help?

Document your issue with:
1. What you're trying to do
2. What happens instead
3. Complete error message
4. System information (Python version, OS)
5. Steps already tried

This will help diagnose and resolve the issue quickly.
