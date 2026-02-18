# Pneumonia Detection System

AI-Powered Chest X-Ray Analysis using Django and MobileNetV2

## 📋 Project Overview

This is a web-based pneumonia detection system that uses a MobileNetV2 deep learning model to analyze chest X-ray images and predict whether the patient has pneumonia or is normal.

### Features

- ✅ Modern, responsive web interface
- ✅ Drag & drop file upload
- ✅ Real-time image preview
- ✅ AJAX-based analysis (no page reload)
- ✅ Confidence percentage display
- ✅ File validation (type, size, integrity)
- ✅ Automatic file cleanup after processing
- ✅ Medical-themed UI design
- ✅ Mobile-friendly responsive design

## 📁 Project Structure

```
Pneumonia_digonosis/
│
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── README.md                         # This file
├── SETUP_INSTRUCTIONS.md             # Detailed setup guide
├── TROUBLESHOOTING.md                # Common issues and solutions
│
├── pneumonia_diagnosis/              # Main project folder
│   ├── __init__.py
│   ├── settings.py                   # Django settings with ML_MODELS_PATH
│   ├── urls.py                       # Main URL configuration
│   ├── asgi.py
│   └── wsgi.py
│
├── xray_detector/                    # Main application
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py                     # No database models needed
│   ├── views.py                      # Upload and prediction views
│   ├── urls.py                       # App URL configuration
│   ├── services.py                   # ML prediction service
│   └── admin.py
│
├── templates/                        # HTML templates
│   └── xray_detector/
│       └── index.html                # Main interface
│
├── media/                            # Temporary file storage
│   └── uploads/                      # Uploaded images (auto-deleted)
│
├── ml_models/                        # ML model directory
│   └── mobilenetv2_pneumonia_model.h5  # Your trained model (ADD THIS)
│
└── db.sqlite3                        # SQLite database (auto-created)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Trained MobileNetV2 model file (.h5 format)

### Installation Steps

1. **Navigate to project directory:**
   ```bash
   cd "e:\uni projects\ML\pneumonia diagnosis(updated)\attiq_pneumonia_project\Pneumonia_digonosis"
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Place your trained model:**
   - Create `ml_models` directory if it doesn't exist
   - Copy your trained MobileNetV2 model to: `ml_models/mobilenetv2_pneumonia_model.h5`

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional, for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server:**
   ```bash
   python manage.py runserver
   ```

8. **Open your browser:**
   Navigate to: `http://127.0.0.1:8000/`

## 🎯 Usage

1. **Upload X-Ray:**
   - Drag and drop an X-ray image, or click "Choose File"
   - Supported formats: PNG, JPG, JPEG
   - Maximum file size: 16MB

2. **View Preview:**
   - Image preview will be displayed
   - Click "Analyze X-Ray" to start analysis

3. **View Results:**
   - Results show NORMAL (green) or PNEUMONIA (red)
   - Confidence percentage is displayed
   - Click "Analyze Another X-Ray" to test more images

## 🔧 Configuration

### Settings (settings.py)

Key configuration options:

```python
# Debug mode (set to False in production)
DEBUG = True

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ML Model path
ML_MODELS_PATH = BASE_DIR / 'ml_models'

# File upload limits
FILE_UPLOAD_MAX_MEMORY_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg']
```

## 📊 Model Information

The application expects a MobileNetV2 model trained for binary classification:

- **Input:** 224x224x1 (grayscale images)
- **Output:** Single value between 0 and 1
  - < 0.5 = NORMAL
  - ≥ 0.5 = PNEUMONIA
- **Format:** Keras model (.h5 file)
- **Location:** `ml_models/mobilenetv2_pneumonia_model.h5`

## 🔒 Security Features

- CSRF protection enabled
- File type validation
- File size validation
- Image integrity verification
- Temporary files auto-deleted after processing
- No persistent storage of sensitive data

## 📱 Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🎨 Customization

### Change Color Scheme

Edit the CSS in `templates/xray_detector/index.html`:

```css
/* Primary gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Normal result color */
.result-area.normal {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

/* Pneumonia result color */
.result-area.pneumonia {
    background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
}
```

### Adjust Prediction Threshold

Edit `xray_detector/services.py`:

```python
# Change threshold (default: 0.5)
if raw_score >= 0.5:  # Adjust this value
    predicted_class = 'PNEUMONIA'
```

## 📝 API Response Format

The application returns JSON responses:

**Success:**
```json
{
    "success": true,
    "predicted_class": "PNEUMONIA",
    "confidence": 92.5,
    "raw_score": 0.925
}
```

**Error:**
```json
{
    "success": false,
    "error": "Error message here"
}
```

## 🐛 Common Issues

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.

## 📄 License

This project is for educational purposes.

## 👨‍💻 Developer

Created by Attiq for pneumonia detection research.

## 📞 Support

For issues or questions, please check the troubleshooting guide or create an issue in the project repository.
