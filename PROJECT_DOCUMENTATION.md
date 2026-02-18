# 🏥 Pneumonia Detection System - Complete Project Documentation

> **AI-Powered Chest X-Ray Analysis using Django and MobileNetV2**  
> Version 1.0 | Last Updated: February 18, 2026

---

## 📑 Table of Contents

1. [Project Overview](#project-overview)
2. [Features & Capabilities](#features--capabilities)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Quick Start Guide](#quick-start-guide)
6. [Detailed Setup Instructions](#detailed-setup-instructions)
7. [Troubleshooting Guide](#troubleshooting-guide)
8. [Design & Styling](#design--styling)
9. [Usage Instructions](#usage-instructions)
10. [API Reference](#api-reference)
11. [Model Information](#model-information)
12. [Deployment Guide](#deployment-guide)
13. [Maintenance & Updates](#maintenance--updates)

---

## 📋 Project Overview

### About the System

The Pneumonia Detection System is a modern, web-based medical diagnostic tool that leverages deep learning to analyze chest X-ray images. Built with Django framework and powered by a MobileNetV2 neural network, the system provides rapid, accurate pneumonia detection with real-time results.

### Key Highlights

- **Purpose**: Automated pneumonia detection from chest X-ray images
- **Target Users**: Healthcare professionals, medical researchers, diagnostic centers
- **Technology**: Django web framework + TensorFlow MobileNetV2 deep learning model
- **Accuracy**: High-precision binary classification (NORMAL vs PNEUMONIA)
- **Deployment**: Development-ready with production deployment guidelines

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Interface (Django)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Upload     │  │   Preview    │  │   Results    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Django Backend (REST API)                       │
│  ┌──────────────────────────────────────────────┐          │
│  │  • File Validation                           │          │
│  │  • Image Preprocessing                       │          │
│  │  • Model Loading & Caching                   │          │
│  │  • Prediction Service                        │          │
│  └──────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│        MobileNetV2 Model (TensorFlow/Keras)                 │
│  ┌──────────────────────────────────────────────┐          │
│  │  Input: 224x224x3 (RGB image)                │          │
│  │  Output: Score 0-1 (probability)             │          │
│  │  Threshold: 0.5 (configurable)               │          │
│  └──────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Features & Capabilities

### Core Features

- ✅ **Modern Responsive UI** - Clean, medical-themed interface optimized for all devices
- ✅ **Drag & Drop Upload** - Intuitive file upload with drag-and-drop support
- ✅ **Real-Time Preview** - Instant image preview before analysis
- ✅ **AJAX Analysis** - No page reload, smooth user experience
- ✅ **Confidence Display** - Visual confidence percentage with progress bar
- ✅ **File Validation** - Comprehensive validation (type, size, integrity)
- ✅ **Auto Cleanup** - Temporary files automatically deleted after processing
- ✅ **Mobile Friendly** - Fully responsive design for mobile devices
- ✅ **User Authentication** - Secure login/registration system
- ✅ **History Tracking** - View and manage past diagnoses

### Advanced Features

- 🔒 **Security**: CSRF protection, file validation, secure sessions
- 📊 **Dashboard**: User statistics and quick access to recent results
- 👤 **Profile Management**: User account management and settings
- 📈 **Results History**: Searchable, filterable diagnostic history
- 📱 **API Ready**: RESTful API for third-party integrations
- 🎨 **Customizable**: Easy theme and configuration customization
- ⚡ **Performance**: Model caching for fast predictions
- 📝 **Logging**: Comprehensive error and activity logging

---

## 🛠 Technology Stack

### Backend

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.8-3.11 | Core programming language |
| **Django** | 4.2.7 | Web framework |
| **Django REST Framework** | 3.14.0 | API development |
| **TensorFlow** | 2.15.0 | Deep learning framework |
| **Keras** | (included) | Model interface |

### Machine Learning

| Component | Details |
|-----------|---------|
| **Model Architecture** | MobileNetV2 |
| **Task** | Binary Classification |
| **Input Size** | 224x224x3 (RGB) |
| **Classes** | NORMAL, PNEUMONIA |
| **Format** | Keras .h5 file |

### Frontend

| Technology | Purpose |
|-----------|---------|
| **HTML5** | Structure |
| **CSS3** | Styling (no framework dependencies) |
| **JavaScript** | Interactivity (vanilla JS) |
| **AJAX** | Asynchronous requests |

### Additional Libraries

```python
Pillow==10.1.0          # Image processing
NumPy>=1.24.0,<2.0.0    # Numerical operations
gunicorn==21.2.0        # WSGI server (production)
whitenoise==6.6.0       # Static file serving
python-dotenv==1.0.0    # Environment variables
django-cors-headers     # CORS support
drf-spectacular         # API documentation
```

---

## 📁 Project Structure

```
Pneumonia_digonosis/
│
├── 📄 manage.py                    # Django management script
├── 📄 requirements.txt             # Python dependencies
├── 📄 activate_env.bat             # Quick environment activation
├── 📄 db.sqlite3                   # SQLite database
├── 📄 .gitignore                   # Git ignore rules
│
├── 📁 pneumonia_diagnosis/         # Main Django project
│   ├── __init__.py
│   ├── settings.py                 # Configuration settings
│   ├── urls.py                     # Main URL routing
│   ├── asgi.py                     # ASGI configuration
│   └── wsgi.py                     # WSGI configuration
│
├── 📁 xray_detector/               # Main application
│   ├── __init__.py
│   ├── admin.py                    # Admin interface configuration
│   ├── apps.py                     # App configuration
│   ├── models.py                   # Database models
│   ├── views.py                    # Web views
│   ├── api_views.py                # REST API views
│   ├── serializers.py              # API serializers
│   ├── services.py                 # Prediction service
│   ├── permissions.py              # Custom permissions
│   ├── urls.py                     # App URL routing
│   ├── api_urls.py                 # API URL routing
│   ├── migrations/                 # Database migrations
│   └── management/                 # Custom management commands
│       └── commands/
│           └── setup_initial_data.py
│
├── 📁 templates/                   # HTML templates
│   ├── base.html                   # Base template
│   └── xray_detector/
│       ├── index.html              # Landing page
│       ├── login.html              # Login page
│       ├── register.html           # Registration page
│       ├── dashboard.html          # User dashboard
│       ├── results.html            # Results list
│       ├── result_detail.html      # Single result view
│       ├── history.html            # Diagnosis history
│       ├── profile.html            # User profile
│       └── model_info.html         # Model information
│
├── 📁 static/                      # Static files
│   ├── css/
│   │   ├── base.css                # Base styles
│   │   ├── dashboard.css           # Dashboard styles
│   │   ├── history.css             # History page styles
│   │   ├── profile.css             # Profile page styles
│   │   ├── results.css             # Results page styles
│   │   ├── result_detail.css       # Detail page styles
│   │   └── model_info.css          # Model info styles
│   └── js/
│       └── base.js                 # Base JavaScript
│
├── 📁 media/                       # User-uploaded files
│   ├── uploads/                    # Temporary uploads
│   └── xray_images/                # Stored X-ray images
│       └── YYYY/MM/DD/             # Date-organized storage
│
├── 📁 ml_models/                   # Machine learning models
│   └── mobilenetv2_pneumonia_model.h5  # ⚠️ Place your model here!
│
└── 📁 venv_py311/                  # Virtual environment
    ├── Scripts/                    # Activation scripts
    ├── Lib/                        # Python libraries
    └── pyvenv.cfg                  # Virtual env configuration
```

---

## 🚀 Quick Start Guide

### Prerequisites Checklist

- [ ] **Python 3.8-3.11** installed (check: `python --version`)
- [ ] **pip** package manager available (check: `pip --version`)
- [ ] **Trained MobileNetV2 model** file (.h5 format)
- [ ] **8GB+ RAM** recommended for smooth operation
- [ ] **Windows/Linux/macOS** operating system

### 5-Minute Setup (For Experienced Users)

```powershell
# 1. Navigate to project directory
cd "e:\uni projects\ML\pneumonia diagnosis(updated)\attiq_pneumonia_project\Pneumonia_digonosis"

# 2. Activate virtual environment (Windows)
.\activate_env.bat
# OR
venv_py311\Scripts\activate.bat

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your model to ml_models/mobilenetv2_pneumonia_model.h5

# 5. Run migrations
python manage.py migrate

# 6. Start server
python manage.py runserver

# 7. Open browser → http://127.0.0.1:8000/
```

### First-Time Setup Tips

**For Python 3.14 Users:**
- TensorFlow 2.15 requires Python 3.8-3.11
- Use the provided `venv_py311` virtual environment

**For PowerShell Users:**
- If activation fails, use: `.\activate_env.bat`
- OR run: `Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process`

**For Linux/Mac Users:**
```bash
source venv/bin/activate
```

---

## 📖 Detailed Setup Instructions

### Step 1: Verify Python Installation

```powershell
# Check Python version
python --version
# Should show: Python 3.8.x to 3.11.x

# Check pip
pip --version

# If 'python' not found, try:
py --version
```

**Download Python:**
- Visit: https://www.python.org/downloads/
- ⚠️ **Important**: Check "Add Python to PATH" during installation

### Step 2: Navigate to Project Directory

```powershell
# Windows PowerShell
cd "e:\uni projects\ML\pneumonia diagnosis(updated)\attiq_pneumonia_project\Pneumonia_digonosis"

# Verify you're in the right place
ls
# Should see: manage.py, requirements.txt, etc.
```

### Step 3: Create and Activate Virtual Environment

**Why Virtual Environment?**
- Isolates project dependencies
- Prevents conflicts with other Python projects
- Matches specific Python version requirements

**Windows - PowerShell:**
```powershell
# Create virtual environment (if not exists)
python -m venv venv_py311

# Activate - Option 1: Batch file (EASIEST)
.\activate_env.bat

# Activate - Option 2: PowerShell script
venv_py311\Scripts\Activate.ps1

# Activate - Option 3: CMD script
venv_py311\Scripts\activate.bat

# Verify activation (should see (venv_py311) in prompt)
# (venv_py311) PS C:\...>
```

**Windows - Command Prompt:**
```cmd
python -m venv venv_py311
venv_py311\Scripts\activate.bat
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**PowerShell Execution Policy Issue?**
```powershell
# Option 1: One-time bypass
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Option 2: Permanent fix (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 4: Install Dependencies

```powershell
# Ensure virtual environment is activated
# You should see (venv_py311) or (venv) in your prompt

# Upgrade pip first (recommended)
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

**Installation Time:**
- Usually takes 5-10 minutes
- TensorFlow is the largest package (~500MB)

**Troubleshooting Installation:**

If TensorFlow fails:
```powershell
# Check Python version compatibility
python --version  # Must be 3.8-3.11

# Try specific version
pip install tensorflow==2.15.0

# Or use CPU-only version
pip install tensorflow-cpu==2.15.0
```

If individual packages fail:
```powershell
# Install one by one
pip install Django==4.2.7
pip install djangorestframework==3.14.0
pip install Pillow>=10.1.0
pip install numpy>=1.24.0,<2.0.0
pip install tensorflow>=2.15.0,<2.18.0
```

### Step 5: Add Your Trained Model

**CRITICAL STEP - System won't work without this!**

1. **Locate your model file:**
   - Should be a `.h5` file (Keras format)
   - Typical size: 50-200MB
   - Trained on chest X-ray images

2. **Create ml_models directory** (if doesn't exist):
   ```powershell
   New-Item -ItemType Directory -Path "ml_models" -Force
   ```

3. **Copy and rename your model:**
   ```powershell
   # Replace "path\to\your\model.h5" with actual path
   Copy-Item "path\to\your\trained_model.h5" -Destination "ml_models\mobilenetv2_pneumonia_model.h5"
   ```

4. **Verify model placement:**
   ```powershell
   Test-Path "ml_models\mobilenetv2_pneumonia_model.h5"
   # Should return: True
   
   # Check file size
   (Get-Item "ml_models\mobilenetv2_pneumonia_model.h5").Length / 1MB
   # Should show model size in MB
   ```

**Model Requirements:**
- **Format**: Keras .h5 file
- **Input shape**: 224x224x3 (RGB images)
- **Output**: Single value 0-1 (sigmoid activation)
- **Classes**: 0 = NORMAL, 1 = PNEUMONIA (or vice versa)

### Step 6: Initialize Database

```powershell
# Run database migrations
python manage.py migrate

# Expected output:
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, sessions, xray_detector
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   ...
```

**Creates:**
- `db.sqlite3` file (SQLite database)
- Tables for users, sessions, diagnosis history, etc.

### Step 7: Create Admin User (Optional)

```powershell
# Create superuser account
python manage.py createsuperuser

# Follow prompts:
# Username: admin
# Email: admin@example.com (optional)
# Password: ******** (minimum 8 characters)
```

**Benefits:**
- Access Django admin panel at `/admin/`
- Manage users, view logs, system configuration
- Database inspection and management

### Step 8: Start Development Server

```powershell
# Start the server
python manage.py runserver

# Expected output:
# Watching for file changes with StatReloader
# Performing system checks...
# 
# System check identified no issues (0 silenced).
# February 18, 2026 - 10:30:00
# Django version 4.2.7, using settings 'pneumonia_diagnosis.settings'
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CTRL-BREAK.
```

**Server Options:**
```powershell
# Run on different port
python manage.py runserver 8080

# Allow external access (same network)
python manage.py runserver 0.0.0.0:8000

# Run in background (not recommended for development)
# Use gunicorn for production instead
```

### Step 9: Access the Application

**Open your web browser and visit:**
- `http://127.0.0.1:8000/` (local)
- `http://localhost:8000/` (local)
- `http://YOUR_IP:8000/` (network access)

**What you should see:**
- Clean, purple-gradient themed interface
- "Pneumonia Detection System" heading
- Upload area for X-ray images
- Login/Register options

### Step 10: Test the System

1. **Create an account:**
   - Click "Register"
   - Fill in username, email, password
   - Click "Register"

2. **Login:**
   - Enter credentials
   - Access dashboard

3. **Upload test X-ray:**
   - Drag & drop or click "Choose File"
   - Select a chest X-ray image (PNG/JPG)
   - Preview should appear

4. **Analyze:**
   - Click "Analyze X-Ray"
   - Wait 5-10 seconds (first prediction loads model)
   - View results

**Expected Results:**
- Result badge: "NORMAL" (green) or "PNEUMONIA" (red)
- Confidence percentage with visual bar
- Option to analyze another image

---

## 🐛 Troubleshooting Guide

### Common Installation Issues

#### Problem: Python not found

**Error:**
```
'python' is not recognized as an internal or external command
```

**Solutions:**
1. Install Python from https://www.python.org/downloads/
2. During installation, **check "Add Python to PATH"**
3. Restart terminal/PowerShell
4. Try `py` instead of `python`:
   ```powershell
   py --version
   py -m pip install -r requirements.txt
   ```

#### Problem: pip not working

**Error:**
```
'pip' is not recognized as an internal or external command
```

**Solution:**
```powershell
# Use pip as module
python -m pip install -r requirements.txt

# Upgrade pip
python -m pip install --upgrade pip
```

#### Problem: TensorFlow installation fails

**Error:**
```
ERROR: Could not find a version that satisfies the requirement tensorflow
```

**Root Causes & Fixes:**

1. **Wrong Python version:**
   ```powershell
   python --version
   # TensorFlow 2.15 requires Python 3.8-3.11
   # If 3.12+, use venv_py311 or downgrade Python
   ```

2. **Install specific version:**
   ```powershell
   pip install tensorflow==2.15.0 --upgrade
   ```

3. **Windows: Missing Visual C++ Redistributable:**
   - Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Install and restart

4. **Use CPU-only version:**
   ```powershell
   pip install tensorflow-cpu==2.15.0
   ```

#### Problem: Virtual environment won't activate (PowerShell)

**Error:**
```
cannot be loaded because running scripts is disabled on this system
```

**Solutions:**

**Option 1: Use batch file** (easiest)
```powershell
.\activate_env.bat
```

**Option 2: Temporary bypass**
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
venv_py311\Scripts\Activate.ps1
```

**Option 3: Permanent fix** (run PowerShell as Administrator)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Model Loading Issues

#### Problem: Model file not found

**Error in terminal:**
```
FileNotFoundError: Model file not found at ...\ml_models\mobilenetv2_pneumonia_model.h5
```

**Troubleshooting Steps:**

1. **Verify file exists:**
   ```powershell
   Test-Path "ml_models\mobilenetv2_pneumonia_model.h5"
   ```

2. **Check exact filename:**
   - Must be: `mobilenetv2_pneumonia_model.h5`
   - Common mistakes: `model.h5`, `pneumonia.h5`, `MobileNetV2.h5`

3. **Check file location:**
   ```powershell
   # Should be in project root
   Get-ChildItem ml_models\*.h5
   ```

4. **Verify file size:**
   ```powershell
   (Get-Item "ml_models\mobilenetv2_pneumonia_model.h5").Length / 1MB
   # Should show size in MB (typically 50-200MB)
   ```

#### Problem: Model fails to load

**Error:**
```
Exception: Failed to load model: ...
```

**Possible Causes:**

1. **Corrupted file:**
   - Re-download or re-export model
   - Check MD5/SHA hash if available

2. **Version mismatch:**
   - Model saved with different TensorFlow version
   - Try matching TensorFlow version used during training

3. **Wrong format:**
   - Ensure model is Keras .h5 format
   - Convert SavedModel to .h5 if needed:
   ```python
   from tensorflow import keras
   model = keras.models.load_model('path/to/saved_model')
   model.save('mobilenetv2_pneumonia_model.h5')
   ```

4. **Insufficient memory:**
   - Close other applications
   - Restart computer
   - Check available RAM (8GB+ recommended)

### File Upload Issues

#### Problem: File type rejected

**Error:**
```
Invalid file type. Please upload a PNG, JPG, or JPEG image.
```

**Solutions:**
- Convert image to PNG, JPG, or JPEG format
- Use Paint, GIMP, or online converters
- Check file extension in properties

#### Problem: File too large

**Error:**
```
File too large. Maximum size: 16MB
```

**Solutions:**

1. **Compress image:**
   - Use online tools: TinyPNG, CompressJPEG
   - Use image editors: Photoshop, GIMP

2. **Increase limit** (if needed):
   Edit `pneumonia_diagnosis/settings.py`:
   ```python
   FILE_UPLOAD_MAX_MEMORY_SIZE = 32 * 1024 * 1024  # 32MB
   DATA_UPLOAD_MAX_MEMORY_SIZE = 32 * 1024 * 1024
   ```

#### Problem: Corrupted image

**Error:**
```
Invalid or corrupted image file
```

**Solutions:**
- Open image in viewer to verify
- Re-download or obtain new copy
- Convert to PNG format
- Try different X-ray image

### Server Issues

#### Problem: Port already in use

**Error:**
```
Error: That port is already in use.
```

**Solutions:**

**Option 1: Use different port**
```powershell
python manage.py runserver 8080
# Access at: http://127.0.0.1:8080/
```

**Option 2: Kill existing process**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace <PID> with actual number)
taskkill /PID <PID> /F
```

#### Problem: Server starts but can't connect

**Error in browser:**
```
This site can't be reached
```

**Troubleshooting:**

1. **Check server is running:**
   - Look for "Starting development server" message
   - No errors in terminal

2. **Try different URLs:**
   - `http://127.0.0.1:8000/`
   - `http://localhost:8000/`
   - `http://0.0.0.0:8000/`

3. **Check firewall:**
   - Windows Firewall may block Python
   - Add Python to allowed apps

4. **Restart server:**
   ```powershell
   # Press Ctrl+C to stop
   python manage.py runserver
   ```

### Browser Issues

#### Problem: Styles not loading (plain HTML)

**Symptoms:** Page displays without colors/styling

**Solutions:**

1. **Check DEBUG mode:**
   In `settings.py`:
   ```python
   DEBUG = True  # Must be True for development
   ```

2. **Collect static files:**
   ```powershell
   python manage.py collectstatic --noinput
   ```

3. **Clear browser cache:**
   - Press `Ctrl + Shift + Delete`
   - Select "Cached images and files"
   - Clear and refresh (`Ctrl + F5`)

4. **Check browser console:**
   - Press F12 → Console tab
   - Look for 404 errors on CSS files

#### Problem: Upload button not working

**Symptoms:**
- Can't select file
- No preview
- Buttons don't respond

**Solutions:**

1. **Check JavaScript errors:**
   - Press F12 → Console
   - Note any error messages

2. **Try different browser:**
   - Chrome (recommended)
   - Firefox
   - Edge

3. **Disable extensions:**
   - Ad blockers may interfere
   - Try incognito/private mode

4. **Clear cache:**
   - `Ctrl + Shift + Delete`
   - Refresh: `Ctrl + F5`

### Performance Issues

#### Problem: Predictions are very slow

**Symptoms:**
- Takes >30 seconds per prediction
- System becomes unresponsive

**Solutions:**

1. **First prediction is always slower:**
   - Model loads on first use
   - Subsequent predictions are faster (~2-5 seconds)

2. **Reduce image size:**
   - Images are resized to 224x224 anyway
   - Upload smaller files

3. **Close other applications:**
   - Free up RAM
   - Close browser tabs

4. **Check system resources:**
   - Task Manager: Ctrl+Shift+Esc
   - Monitor CPU, RAM usage

5. **Upgrade hardware:**
   - 8GB+ RAM recommended
   - SSD instead of HDD
   - Multi-core CPU

### Quick Fixes Checklist

Try these in order when something goes wrong:

1. [ ] Restart server: `Ctrl+C`, then `python manage.py runserver`
2. [ ] Clear browser cache: `Ctrl+Shift+Delete`
3. [ ] Refresh page: `Ctrl+F5`
4. [ ] Restart terminal/PowerShell
5. [ ] Check model file exists
6. [ ] Check virtual environment activated: `(venv_py311)` in prompt
7. [ ] Review terminal for error messages
8. [ ] Try different test image
9. [ ] Try different browser
10. [ ] Restart computer

---

## 🎨 Design & Styling

### Color Scheme

The application uses a cohesive, medical-themed color palette:

#### Primary Colors

| Color | Hex Code | Usage |
|-------|----------|-------|
| **Primary Purple** | `#667eea` | Primary buttons, links, branding |
| **Secondary Purple** | `#764ba2` | Gradients, hover states |
| **Background** | `#f5f7fa` | Page background |
| **Card Background** | `#ffffff` | Content cards |
| **Text Primary** | `#333333` | Main text |
| **Text Muted** | `#999999` | Secondary text |

#### Gradient Combinations

```css
/* Primary Gradient (Purple) */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Success Gradient (Green - Normal Result) */
background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);

/* Danger Gradient (Red - Pneumonia Result) */
background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
```

#### Semantic Colors

| Purpose | Background | Text | Border |
|---------|-----------|------|--------|
| **Success** | `#c8e6c9` | `#2e7d32` | `#2e7d32` |
| **Danger/Error** | `#ffcdd2` | `#c62828` | `#c62828` |
| **Warning** | `#fff9c4` | `#f57f17` | `#f57f17` |
| **Info** | `#bbdefb` | `#1565c0` | `#1565c0` |

### Typography

```css
/* Font Family */
font-family: 'Segoe UI', Arial, Helvetica, sans-serif;

/* Font Sizes */
H1: 36px / Bold
H2: 22px / Bold
H3: 18px / Bold
Body: 14px / Regular
Small: 12px / Regular

/* Font Weights */
Regular: 400
Medium: 500
Semi-bold: 600
Bold: 700
```

### Component Styles

#### Buttons

```css
/* Primary Button */
.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 25px;
    border-radius: 25px;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.6);
}

/* Secondary Button */
.btn-secondary {
    background: #f0f0f0;
    color: #333;
    padding: 12px 25px;
    border-radius: 25px;
}

/* Success Button */
.btn-success {
    background: #10b981;
    color: white;
    border-radius: 25px;
}

/* Danger Button */
.btn-danger {
    background: #ffcdd2;
    color: #c62828;
    border-radius: 25px;
}
```

#### Cards

```css
.card {
    background: white;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.card:hover {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}
```

#### Upload Area

```css
.upload-area {
    border: 3px dashed #667eea;
    border-radius: 15px;
    padding: 40px 20px;
    background: #f8f9ff;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
}

.upload-area:hover {
    background: #f0f2ff;
    border-color: #764ba2;
}

.upload-area.dragover {
    background: #e8ebff;
    border-color: #764ba2;
    transform: scale(1.02);
}
```

#### Results Display

```css
/* Normal Result */
.result-area.normal {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    color: white;
    padding: 30px;
    border-radius: 15px;
    text-align: center;
}

/* Pneumonia Result */
.result-area.pneumonia {
    background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    color: white;
    padding: 30px;
    border-radius: 15px;
    text-align: center;
}

/* Result Badge */
.result-badge {
    font-size: 36px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
}

/* Confidence Bar */
.confidence-bar-container {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 25px;
    height: 30px;
    overflow: hidden;
}

.confidence-bar {
    background: white;
    height: 100%;
    border-radius: 25px;
    transition: width 1s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
}
```

#### Navigation Bar

```css
.navbar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    height: 70px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    position: fixed;
    width: 100%;
    top: 0;
    z-index: 100;
}

.nav-link {
    color: white;
    padding: 8px 15px;
    border-radius: 6px;
    transition: all 0.3s ease;
    font-weight: 500;
}

.nav-link:hover {
    background: rgba(255, 255, 255, 0.2);
}

.nav-link.active {
    background: rgba(255, 255, 255, 0.3);
}
```

#### Badges

```css
/* Success Badge (Normal) */
.badge.normal {
    background: #c8e6c9;
    color: #2e7d32;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

/* Danger Badge (Pneumonia) */
.badge.pneumonia {
    background: #ffcdd2;
    color: #c62828;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}
```

### Animations

```css
/* Spinner Animation */
@keyframes spin {
    0% { 
        transform: rotate(0deg); 
    }
    100% { 
        transform: rotate(360deg); 
    }
}

.spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #667eea;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    animation: spin 1s linear infinite;
}

/* Fade In */
@keyframes fadeIn {
    from { 
        opacity: 0; 
        transform: translateY(20px); 
    }
    to { 
        opacity: 1; 
        transform: translateY(0); 
    }
}

/* Button Hover Effect */
.btn:hover {
    transform: translateY(-2px);
    transition: all 0.3s ease;
}
```

### Responsive Design

```css
/* Tablet (768px and below) */
@media (max-width: 768px) {
    .navbar {
        flex-wrap: wrap;
        height: auto;
    }
    
    .main-container {
        padding: 10px;
    }
    
    .card {
        padding: 20px;
    }
    
    .stats-grid {
        grid-template-columns: 1fr 1fr;
    }
}

/* Mobile (480px and below) */
@media (max-width: 480px) {
    .logo {
        font-size: 20px;
    }
    
    .nav-link {
        padding: 6px 10px;
        font-size: 12px;
    }
    
    .btn {
        padding: 10px 15px;
        font-size: 12px;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .result-badge {
        font-size: 24px;
    }
}
```

### Customization Guide

#### Change Primary Color

Find and replace in CSS files:
```css
/* Old */
#667eea and #764ba2

/* New (example: Blue theme) */
#4e73df and #224abe

/* Update gradients: */
background: linear-gradient(135deg, #4e73df 0%, #224abe 100%);
```

#### Change Result Colors

Edit in `dashboard.css` and `results.css`:
```css
/* Normal (Green → Blue) */
.result-area.normal {
    background: linear-gradient(135deg, #4e73df 0%, #2c5aa0 100%);
}

/* Pneumonia (Red → Orange) */
.result-area.pneumonia {
    background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
}
```

#### Adjust Fonts

Edit in `base.css`:
```css
body {
    font-family: 'Your Font', Arial, sans-serif;
}

/* Or use Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

body {
    font-family: 'Poppins', sans-serif;
}
```

---

## 📱 Usage Instructions

### For End Users

#### Creating an Account

1. Click **"Register"** on homepage
2. Fill in:
   - Username (unique)
   - Email address
   - Password (minimum 8 characters)
   - Confirm password
3. Click **"Register"**
4. Redirected to login page

#### Logging In

1. Enter username and password
2. Click **"Login"**
3. Access dashboard

#### Uploading and Analyzing X-Ray

1. From dashboard, locate **"Upload Chest X-Ray"** section
2. **Upload image:**
   - **Drag & Drop**: Drag image file onto upload area
   - **Click**: Click "Choose File" button and select image
3. Supported formats: PNG, JPG, JPEG (max 16MB)
4. **Preview**: Image preview appears automatically
5. Click **"Analyze X-Ray"** button
6. **Wait**: Processing takes 5-10 seconds
7. **View results:**
   - **NORMAL** (green background): No pneumonia detected
   - **PNEUMONIA** (red background): Pneumonia detected
   - Confidence percentage displayed with visual bar

#### Viewing Results History

1. Click **"History"** in navigation
2. View list of past diagnoses
3. Filter by:
   - Date range
   - Result type (Normal/Pneumonia)
   - Confidence level
4. Click on result to view details

#### Managing Profile

1. Click **"Profile"** in navigation
2. **View** tab: See account information
3. **Edit** tab: Update name, email
4. **Security** tab: Change password

#### Viewing Model Information

1. Click **"Model Info"** in navigation
2. View:
   - Model architecture details
   - Performance metrics
   - Training information
   - Usage guidelines

### For Developers

#### API Endpoints

**Authentication:**
```http
POST /api/register/
POST /api/login/
POST /api/logout/
```

**Image Analysis:**
```http
POST /api/images/
GET /api/images/{id}/
GET /api/images/
```

**Results:**
```http
GET /api/results/
GET /api/results/{id}/
DELETE /api/results/{id}/
```

**User:**
```http
GET /api/users/me/
PUT /api/users/me/
POST /api/users/change-password/
```

#### Example API Usage

**Upload and Analyze:**
```python
import requests

# Login
response = requests.post('http://localhost:8000/api/login/', {
    'username': 'user',
    'password': 'password'
})
token = response.json()['token']

# Upload image
headers = {'Authorization': f'Token {token}'}
files = {'image': open('xray.jpg', 'rb')}
response = requests.post(
    'http://localhost:8000/api/images/',
    files=files,
    headers=headers
)

# Get result
result = response.json()
print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']}%")
```

**JavaScript (AJAX):**
```javascript
// Upload with AJAX
const formData = new FormData();
formData.append('image', fileInput.files[0]);

fetch('/api/images/', {
    method: 'POST',
    headers: {
        'Authorization': 'Token ' + token,
        'X-CSRFToken': csrfToken
    },
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Result:', data.prediction);
    console.log('Confidence:', data.confidence);
});
```

---

## 🔌 API Reference

### Authentication Endpoints

#### Register User

```http
POST /api/register/
```

**Request Body:**
```json
{
    "username": "string",
    "email": "string",
    "password": "string",
    "password_confirm": "string",
    "first_name": "string (optional)",
    "last_name": "string (optional)"
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

#### Login

```http
POST /api/login/
```

**Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```

**Response (200 OK):**
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
}
```

#### Logout

```http
POST /api/logout/
```

**Headers:**
```
Authorization: Token YOUR_TOKEN_HERE
```

**Response (200 OK):**
```json
{
    "message": "Successfully logged out"
}
```

### Image & Prediction Endpoints

#### Upload and Analyze Image

```http
POST /api/images/
```

**Headers:**
```
Authorization: Token YOUR_TOKEN_HERE
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
image: <file>
patient_name: <string> (optional)
patient_age: <int> (optional)
notes: <string> (optional)
```

**Response (201 Created):**
```json
{
    "id": 1,
    "image": "/media/xray_images/2026/02/18/image.jpg",
    "uploaded_at": "2026-02-18T10:30:00Z",
    "result": {
        "id": 1,
        "predicted_class": "PNEUMONIA",
        "confidence": 92.5,
        "raw_score": 0.925,
        "created_at": "2026-02-18T10:30:05Z"
    }
}
```

#### Get All Images

```http
GET /api/images/
```

**Query Parameters:**
```
?page=1
&page_size=10
&ordering=-uploaded_at
```

**Response (200 OK):**
```json
{
    "count": 50,
    "next": "http://localhost:8000/api/images/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "image": "/media/xray_images/2026/02/18/image.jpg",
            "uploaded_at": "2026-02-18T10:30:00Z",
            "result": { ... }
        },
        ...
    ]
}
```

#### Get Single Image

```http
GET /api/images/{id}/
```

**Response (200 OK):**
```json
{
    "id": 1,
    "image": "/media/xray_images/2026/02/18/image.jpg",
    "uploaded_at": "2026-02-18T10:30:00Z",
    "file_size": 1024000,
    "result": {
        "id": 1,
        "predicted_class": "PNEUMONIA",
        "confidence": 92.5,
        "raw_score": 0.925,
        "processing_time": 2.5,
        "created_at": "2026-02-18T10:30:05Z"
    }
}
```

### Result Endpoints

#### Get All Results

```http
GET /api/results/
```

**Query Parameters:**
```
?predicted_class=NORMAL
&confidence_min=80
&confidence_max=100
&date_from=2026-02-01
&date_to=2026-02-18
&ordering=-created_at
```

**Response (200 OK):**
```json
{
    "count": 25,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "xray_image": {...},
            "predicted_class": "NORMAL",
            "confidence": 95.2,
            "created_at": "2026-02-18T10:30:00Z"
        },
        ...
    ]
}
```

#### Get Single Result

```http
GET /api/results/{id}/
```

#### Delete Result

```http
DELETE /api/results/{id}/
```

**Response (204 No Content)**

### User Endpoints

#### Get Current User

```http
GET /api/users/me/
```

**Headers:**
```
Authorization: Token YOUR_TOKEN_HERE
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2026-01-15T08:00:00Z",
    "total_scans": 25,
    "normal_count": 15,
    "pneumonia_count": 10
}
```

#### Update User Profile

```http
PUT /api/users/me/
PATCH /api/users/me/
```

**Request Body:**
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "email": "newemail@example.com"
}
```

#### Change Password

```http
POST /api/users/change-password/
```

**Request Body:**
```json
{
    "old_password": "string",
    "new_password": "string",
    "new_password_confirm": "string"
}
```

**Response (200 OK):**
```json
{
    "message": "Password changed successfully"
}
```

### Error Responses

#### 400 Bad Request
```json
{
    "error": "Invalid file type",
    "detail": "Only PNG, JPG, and JPEG files are allowed"
}
```

#### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### 404 Not Found
```json
{
    "detail": "Not found."
}
```

#### 500 Internal Server Error
```json
{
    "error": "Prediction failed",
    "detail": "Model loading error"
}
```

---

## 🧠 Model Information

### Architecture Details

**Model Type:** MobileNetV2 - Convolutional Neural Network

**Base Architecture:**
- Designed by Google for mobile and embedded vision applications
- Efficient architecture with depth-wise separable convolutions
- Optimized for speed and accuracy balance

**Specifications:**

| Parameter | Value |
|-----------|-------|
| **Input Shape** | 224x224x3 (RGB image) |
| **Output Shape** | 1 (Single probability value) |
| **Activation** | Sigmoid (binary classification) |
| **Parameters** | ~3.5 million (typical) |
| **Model Size** | 50-200 MB (.h5 file) |

### Input Requirements

**Image Format:**
- **File types**: PNG, JPG, JPEG
- **Color mode**: RGB (3 channels)
- **Size**: Resized to 224x224 pixels automatically
- **Max upload**: 16MB
- **Normalization**: 0-1 range (divides by 255)

**Preprocessing Pipeline:**
```python
1. Load image from file
2. Convert to RGB (if needed)
3. Resize to 224x224
4. Convert to array
5. Normalize: pixel_value / 255.0
6. Expand dims: (1, 224, 224, 3)
7. Feed to model
```

### Output Interpretation

**Raw Score:**
- Float value between 0.0 and 1.0
- Represents model's confidence

**Classification Threshold:**
- **< 0.5**: NORMAL (No pneumonia)
- **≥ 0.5**: PNEUMONIA (Pneumonia detected)

**Confidence Calculation:**
```python
# For NORMAL prediction
if raw_score < 0.5:
    confidence = (1 - raw_score) * 100

# For PNEUMONIA prediction
else:
    confidence = raw_score * 100
```

**Example:**

| Raw Score | Prediction | Confidence |
|-----------|-----------|-----------|
| 0.12 | NORMAL | 88.0% |
| 0.35 | NORMAL | 65.0% |
| 0.52 | PNEUMONIA | 52.0% |
| 0.87 | PNEUMONIA | 87.0% |
| 0.95 | PNEUMONIA | 95.0% |

### Performance Considerations

**First Prediction:**
- **Time**: 10-15 seconds
- **Reason**: Model loading from disk
- **Subsequent**: 2-5 seconds (model cached)

**Hardware Requirements:**
- **Minimum RAM**: 4GB
- **Recommended RAM**: 8GB+
- **CPU**: Multi-core processor recommended
- **GPU**: Optional (requires tensorflow-gpu)

**Optimization Tips:**
1. Model is cached after first load
2. Use smaller input images (resized automatically)
3. Close unnecessary applications
4. Consider GPU acceleration for production

### Model Training (For Reference)

**If you're training your own model, ensure:**

1. **Dataset:**
   - Chest X-ray images
   - Labeled: NORMAL vs PNEUMONIA
   - Balanced classes or weighted loss

2. **Training:**
   - Transfer learning from ImageNet weights
   - Fine-tune top layers
   - Use data augmentation

3. **Validation:**
   - Separate validation set
   - Calculate accuracy, precision, recall, F1

4. **Export:**
   ```python
   model.save('mobilenetv2_pneumonia_model.h5')
   ```

### Medical Disclaimer

⚠️ **Important:**
- This is a diagnostic support tool
- NOT a replacement for professional medical diagnosis
- Results should be reviewed by qualified healthcare professionals
- Used for educational and research purposes
- Clinical validation required before medical use

---

## 🚀 Deployment Guide

### Production Deployment Checklist

#### Pre-Deployment

- [ ] **Security configured** (see Security Changes below)
- [ ] **Environment variables** set up
- [ ] **Database migrated** (PostgreSQL recommended)
- [ ] **Static files collected**
- [ ] **Model file uploaded** to server
- [ ] **Dependencies installed**
- [ ] **Testing completed** on staging environment
- [ ] **Backups configured**
- [ ] **Monitoring setup**
- [ ] **SSL certificate** installed
- [ ] **Domain configured**

### Security Changes (CRITICAL)

#### 1. Settings.py Modifications

```python
# pneumonia_diagnosis/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

# Allowed hosts
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',')
# Example: DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database - Use PostgreSQL in production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# HTTPS Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

#### 2. Generate New Secret Key

```powershell
# Generate new secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Copy output to .env file
```

#### 3. Environment Variables

Create `.env` file (DON'T commit to git):

```ini
# .env
DJANGO_SECRET_KEY=your-new-secret-key-here-abc123xyz
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=pneumonia_db
DB_USER=db_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=5432

# Other
MEDIA_URL=/media/
STATIC_URL=/static/
```

### Deployment Options

#### Option 1: Cloud Platform as a Service

**Heroku:**

1. **Create `Procfile`:**
   ```
   web: gunicorn pneumonia_diagnosis.wsgi --log-file -
   ```

2. **Create `runtime.txt`:**
   ```
   python-3.11.0
   ```

3. **Deploy:**
   ```bash
   heroku create your-app-name
   heroku config:set DJANGO_SECRET_KEY='your-secret-key'
   heroku config:set DJANGO_DEBUG=False
   git push heroku main
   heroku run python manage.py migrate
   ```

**AWS Elastic Beanstalk, Google App Engine, Azure App Service:**
- Similar process with platform-specific configuration
- Follow respective platform documentation

#### Option 2: Virtual Private Server (VPS)

**Providers:** DigitalOcean, Linode, AWS EC2, Vultr

**Step-by-Step Setup:**

1. **Provision Server:**
   - Ubuntu 22.04 LTS recommended
   - 2GB+ RAM minimum
   - SSH access configured

2. **Initial Server Setup:**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install dependencies
   sudo apt install python3-pip python3-venv nginx postgresql -y
   
   # Install supervisor (process management)
   sudo apt install supervisor -y
   ```

3. **Setup Project:**
   ```bash
   # Create project directory
   sudo mkdir -p /var/www/pneumonia_diagnosis
   sudo chown $USER:$USER /var/www/pneumonia_diagnosis
   
   # Clone or upload project
   cd /var/www/pneumonia_diagnosis
   # (upload your project files)
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install gunicorn psycopg2-binary
   ```

4. **Configure PostgreSQL:**
   ```bash
   sudo -u postgres psql
   ```
   ```sql
   CREATE DATABASE pneumonia_db;
   CREATE USER db_user WITH PASSWORD 'secure_password';
   ALTER ROLE db_user SET client_encoding TO 'utf8';
   ALTER ROLE db_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE db_user SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE pneumonia_db TO db_user;
   \q
   ```

5. **Run Migrations:**
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

6. **Configure Gunicorn:**
   
   Create `/var/www/pneumonia_diagnosis/gunicorn_start.sh`:
   ```bash
   #!/bin/bash
   
   NAME="pneumonia_diagnosis"
   DJANGODIR=/var/www/pneumonia_diagnosis
   SOCKFILE=/var/www/pneumonia_diagnosis/gunicorn.sock
   USER=www-data
   GROUP=www-data
   NUM_WORKERS=3
   DJANGO_SETTINGS_MODULE=pneumonia_diagnosis.settings
   DJANGO_WSGI_MODULE=pneumonia_diagnosis.wsgi
   
   cd $DJANGODIR
   source venv/bin/activate
   
   export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
   
   exec venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
     --name $NAME \
     --workers $NUM_WORKERS \
     --user=$USER --group=$GROUP \
     --bind=unix:$SOCKFILE \
     --log-level=info \
     --log-file=-
   ```
   
   Make executable:
   ```bash
   chmod +x gunicorn_start.sh
   ```

7. **Configure Supervisor:**
   
   Create `/etc/supervisor/conf.d/pneumonia_diagnosis.conf`:
   ```ini
   [program:pneumonia_diagnosis]
   command=/var/www/pneumonia_diagnosis/gunicorn_start.sh
   user=www-data
   autostart=true
   autorestart=true
   redirect_stderr=true
   stdout_logfile=/var/log/pneumonia_diagnosis.log
   ```
   
   Start service:
   ```bash
   sudo supervisorctl reread
   sudo supervisorctl update
   sudo supervisorctl start pneumonia_diagnosis
   ```

8. **Configure Nginx:**
   
   Create `/etc/nginx/sites-available/pneumonia_diagnosis`:
   ```nginx
   upstream pneumonia_app {
       server unix:/var/www/pneumonia_diagnosis/gunicorn.sock fail_timeout=0;
   }
   
   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;
       
       client_max_body_size 20M;
       
       location /static/ {
           alias /var/www/pneumonia_diagnosis/staticfiles/;
       }
       
       location /media/ {
           alias /var/www/pneumonia_diagnosis/media/;
       }
       
       location / {
           proxy_pass http://pneumonia_app;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```
   
   Enable site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/pneumonia_diagnosis /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

9. **Configure SSL (Let's Encrypt):**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

#### Option 3: Docker Deployment

1. **Create `Dockerfile`:**
   ```dockerfile
   FROM python:3.11-slim
   
   ENV PYTHONUNBUFFERED=1
   
   WORKDIR /app
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       postgresql-client \
       && rm -rf /var/lib/apt/lists/*
   
   # Install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt gunicorn psycopg2-binary
   
   # Copy project
   COPY . .
   
   # Create necessary directories
   RUN mkdir -p media/uploads ml_models staticfiles
   
   # Collect static files
   RUN python manage.py collectstatic --noinput
   
   # Expose port
   EXPOSE 8000
   
   # Run gunicorn
   CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "pneumonia_diagnosis.wsgi:application"]
   ```

2. **Create `docker-compose.yml`:**
   ```yaml
   version: '3.8'
   
   services:
     db:
       image: postgres:15
       environment:
         POSTGRES_DB: pneumonia_db
         POSTGRES_USER: db_user
         POSTGRES_PASSWORD: secure_password
       volumes:
         - postgres_data:/var/lib/postgresql/data
     
     web:
       build: .
       command: gunicorn --bind 0.0.0.0:8000 --workers 3 pneumonia_diagnosis.wsgi:application
       volumes:
         - ./ml_models:/app/ml_models
         - ./media:/app/media
         - static_volume:/app/staticfiles
       ports:
         - "8000:8000"
       environment:
         - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
         - DJANGO_DEBUG=False
         - DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
         - DB_NAME=pneumonia_db
         - DB_USER=db_user
         - DB_PASSWORD=secure_password
         - DB_HOST=db
         - DB_PORT=5432
       depends_on:
         - db
     
     nginx:
       image: nginx:latest
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf
         - static_volume:/app/staticfiles
         - ./media:/app/media
       ports:
         - "80:80"
         - "443:443"
       depends_on:
         - web
   
   volumes:
     postgres_data:
     static_volume:
   ```

3. **Deploy:**
   ```bash
   docker-compose up -d --build
   docker-compose exec web python manage.py migrate
   ```

### Post-Deployment

#### 1. Test Application

```bash
# Check deployment
curl -I https://yourdomain.com

# Test upload endpoint
curl -X POST https://yourdomain.com/api/images/ \
     -H "Authorization: Token YOUR_TOKEN" \
     -F "image=@test_xray.jpg"
```

#### 2. Setup Monitoring

**Sentry (Error Tracking):**
```bash
pip install sentry-sdk
```

```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
)
```

**Health Check Endpoint:**

Add to `xray_detector/views.py`:
```python
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy', 'version': '1.0'})
```

Add to `xray_detector/urls.py`:
```python
path('health/', views.health_check, name='health'),
```

#### 3. Logging

Configure in `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/error.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

#### 4. Backups

**Database Backup:**
```bash
# Create backup script
#!/bin/bash
pg_dump -U db_user pneumonia_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Add to crontab (daily at 2 AM)
0 2 * * * /path/to/backup_script.sh
```

**Media Files Backup:**
```bash
# Sync to S3 or other storage
aws s3 sync /var/www/pneumonia_diagnosis/media/ s3://your-bucket/backups/media/
```

---

## 🔄 Maintenance & Updates

### Regular Maintenance Tasks

#### Daily
- [ ] Check error logs
- [ ] Monitor server resources
- [ ] Review prediction logs

#### Weekly
- [ ] Database backup verification
- [ ] Security updates check
- [ ] Performance monitoring

#### Monthly
- [ ] Update dependencies
- [ ] Review and archive old data
- [ ] Performance optimization
- [ ] Security audit

### Updating Dependencies

```bash
# Check outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update all packages (carefully)
pip install --upgrade -r requirements.txt

# Test thoroughly after updates
python manage.py test
```

### Database Maintenance

**Backup:**
```bash
python manage.py dumpdata > backup.json
```

**Restore:**
```bash
python manage.py loaddata backup.json
```

**Clean old records:**
```python
# In Django shell
from xray_detector.models import XRayImage
from datetime import timedelta
from django.utils import timezone

# Delete images older than 1 year
old_date = timezone.now() - timedelta(days=365)
XRayImage.objects.filter(uploaded_at__lt=old_date).delete()
```

### Updating the Model

1. **Train new model version**
2. **Test locally**
3. **Backup old model:**
   ```bash
   cp ml_models/mobilenetv2_pneumonia_model.h5 ml_models/mobilenetv2_pneumonia_model_v1_backup.h5
   ```
4. **Upload new model**
5. **Restart application**
6. **Test predictions**
7. **Monitor for issues**

### Troubleshooting Production Issues

**Check Logs:**
```bash
# Application logs
tail -f /var/log/django/error.log

# Nginx logs
tail -f /var/log/nginx/error.log

# Supervisor logs
tail -f /var/log/pneumonia_diagnosis.log
```

**Restart Services:**
```bash
# Restart application
sudo supervisorctl restart pneumonia_diagnosis

# Restart Nginx
sudo systemctl restart nginx

# Restart PostgreSQL
sudo systemctl restart postgresql
```

---

## 📞 Support & Resources

### Documentation

- **Django**: https://docs.djangoproject.com/
- **Django REST Framework**: https://www.django-rest-framework.org/
- **TensorFlow**: https://www.tensorflow.org/guide
- **Pillow**: https://pillow.readthedocs.io/

### Community

- **Django Forums**: https://forum.djangoproject.com/
- **Stack Overflow**: Tag questions with `django`, `tensorflow`
- **GitHub Issues**: Report bugs in project repository

### Project Information

- **Version**: 1.0
- **Last Updated**: February 18, 2026
- **License**: Educational/Research Use
- **Developer**: Attiq

---

## ⚠️ Important Notes

### Medical Disclaimer

This system is intended for:
- ✅ Educational purposes
- ✅ Research and development
- ✅ Diagnostic support tool

NOT intended for:
- ❌ Primary medical diagnosis
- ❌ Direct clinical use without validation
- ❌ Replacement for professional medical opinion

**ALWAYS consult qualified healthcare professionals for medical decisions.**

### Privacy & Data

- Patient data must be handled according to local regulations (HIPAA, GDPR, etc.)
- Implement proper data encryption
- Regular security audits required
- Obtain proper patient consent

### Liability

- Developer assumes no liability for medical decisions  
- System provided "as-is"
- Proper clinical validation required before medical use
- Follow all applicable healthcare regulations

---

## 📝 Changelog

### Version 1.0 (February 2026)
- Initial release
- MobileNetV2 model integration
- User authentication system
- Dashboard and history tracking
- RESTful API
- Responsive web interface
- Comprehensive documentation

---

## 🎓 Credits & Acknowledgments

### Technologies Used
- Django Web Framework
- TensorFlow / Keras
- MobileNetV2 Architecture
- Bootstrap-inspired design principles

### Developer
Created by **Attiq** for pneumonia detection research and education.

---

## 📄 License

This project is for educational and research purposes. Commercial use requires proper validation, certification, and compliance with medical device regulations.

---

**End of Documentation**

For questions, issues, or contributions, please refer to the project repository or contact the development team.

---

*Last updated: February 18, 2026*
