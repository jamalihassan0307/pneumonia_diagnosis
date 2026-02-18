# Setup Instructions

Complete step-by-step guide to set up the Pneumonia Detection System.

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.8 or higher** installed
  - Check: `python --version`
  - Download from: https://www.python.org/downloads/
  
- **pip** (Python package installer)
  - Check: `pip --version`
  - Usually comes with Python
  
- **Trained MobileNetV2 model** (.h5 file)
  - Your pneumonia detection model
  - Should be trained on chest X-ray images
  - Binary classification (NORMAL vs PNEUMONIA)

## 🔧 Step-by-Step Setup

### Step 1: Navigate to Project Directory

Open PowerShell or Command Prompt and navigate to the project folder:

```powershell
cd "e:\uni projects\ML\pneumonia diagnosis(updated)\attiq_pneumonia_project\Pneumonia_digonosis"
```

### Step 2: Create Virtual Environment (Recommended)

A virtual environment keeps dependencies isolated:

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
venv\Scripts\Activate.ps1

# On Windows Command Prompt:
venv\Scripts\activate.bat

# On macOS/Linux:
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt when activated.

### Step 3: Install Dependencies

Install all required Python packages:

```powershell
pip install -r requirements.txt
```

This installs:
- Django 4.2.7
- TensorFlow 2.15.0
- Pillow 10.1.0
- NumPy 1.26.2

**Note:** TensorFlow installation may take several minutes.

### Step 4: Create Required Directories

Create the necessary folders:

```powershell
# Create media directory for uploads
New-Item -ItemType Directory -Path "media\uploads" -Force

# Create ml_models directory
New-Item -ItemType Directory -Path "ml_models" -Force
```

### Step 5: Add Your Trained Model

**CRITICAL STEP:**

1. Locate your trained MobileNetV2 model file (should be a `.h5` file)
2. Rename it to: `mobilenetv2_pneumonia_model.h5`
3. Copy it to: `ml_models/mobilenetv2_pneumonia_model.h5`

**Windows PowerShell command:**
```powershell
# Example - adjust the source path to your model location
Copy-Item "path\to\your\model.h5" -Destination "ml_models\mobilenetv2_pneumonia_model.h5"
```

**Verify the model is in place:**
```powershell
Test-Path "ml_models\mobilenetv2_pneumonia_model.h5"
# Should return: True
```

### Step 6: Run Database Migrations

Initialize the Django database:

```powershell
python manage.py migrate
```

Expected output:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

### Step 7: Create Admin User (Optional)

Create a superuser to access Django admin panel:

```powershell
python manage.py createsuperuser
```

Follow the prompts:
- Username: (choose a username)
- Email: (your email, optional)
- Password: (choose a secure password)

### Step 8: Collect Static Files (Optional for Development)

```powershell
python manage.py collectstatic --noinput
```

### Step 9: Start Development Server

Launch the application:

```powershell
python manage.py runserver
```

Expected output:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
February 18, 2026 - 10:30:00
Django version 4.2.7, using settings 'pneumonia_diagnosis.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Step 10: Access the Application

Open your web browser and navigate to:

```
http://127.0.0.1:8000/
```

or

```
http://localhost:8000/
```

You should see the Pneumonia Detection interface!

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Virtual environment activated
- [ ] All dependencies installed (no errors during pip install)
- [ ] Model file exists at `ml_models/mobilenetv2_pneumonia_model.h5`
- [ ] Database migrations completed successfully
- [ ] Development server starts without errors
- [ ] Website loads at http://127.0.0.1:8000/
- [ ] Can upload an image (test with any X-ray image)
- [ ] Model loads without errors (check terminal for logs)
- [ ] Prediction returns results

## 🧪 Test the Application

1. **Test with a sample X-ray image:**
   - Use a chest X-ray image (PNG, JPG, or JPEG)
   - Maximum size: 16MB
   - Can be NORMAL or PNEUMONIA

2. **Upload process:**
   - Drag & drop or click "Choose File"
   - Preview should appear
   - Click "Analyze X-Ray"
   - Wait for results (may take 5-10 seconds on first run)

3. **Check results:**
   - Should show NORMAL (green) or PNEUMONIA (red)
   - Confidence percentage displayed
   - No errors in browser console (F12)

## 🔄 Daily Usage

### Starting the Server

```powershell
# 1. Navigate to project
cd "e:\uni projects\ML\pneumonia diagnosis(updated)\attiq_pneumonia_project\Pneumonia_digonosis"

# 2. Activate virtual environment
venv\Scripts\Activate.ps1

# 3. Start server
python manage.py runserver
```

### Stopping the Server

Press `Ctrl + C` in the terminal where the server is running.

### Deactivating Virtual Environment

```powershell
deactivate
```

## 🌐 Access from Other Devices (Same Network)

To access from other devices on your network:

1. **Find your IP address:**
   ```powershell
   ipconfig
   # Look for IPv4 Address (e.g., 192.168.1.100)
   ```

2. **Start server on all interfaces:**
   ```powershell
   python manage.py runserver 0.0.0.0:8000
   ```

3. **Access from other devices:**
   ```
   http://YOUR_IP_ADDRESS:8000/
   # Example: http://192.168.1.100:8000/
   ```

## 📊 Checking Logs

Monitor the terminal where the server is running. You'll see:

- HTTP requests (GET, POST)
- Model loading status
- Prediction results
- Any errors or warnings

Example logs:
```
[18/Feb/2026 10:35:21] "GET / HTTP/1.1" 200 12345
Loading model from ...\ml_models\mobilenetv2_pneumonia_model.h5
Model loaded successfully
Image preprocessed successfully. Shape: (1, 224, 224, 3)
Prediction successful: PNEUMONIA (confidence: 92.50%, raw_score: 0.9250)
[18/Feb/2026 10:35:35] "POST / HTTP/1.1" 200 98
```

## 🐛 Troubleshooting Setup Issues

If you encounter issues during setup, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for solutions.

Common setup problems:
- Python not found → Install Python and add to PATH
- pip not working → Use `python -m pip` instead of `pip`
- TensorFlow installation fails → Check Python version (must be 3.8-3.11)
- Model not loading → Verify file path and file integrity
- Port already in use → Use different port: `python manage.py runserver 8080`

## 🎉 Success!

If everything works, you're ready to use the Pneumonia Detection System!

For any issues, refer to the troubleshooting guide or check the error messages in your terminal.
