# Pneumonia Diagnosis System - Project Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Installation & Setup](#installation--setup)
5. [Project Structure](#project-structure)
6. [Features & Workflow](#features--workflow)
7. [API Documentation](#api-documentation)
8. [Database Schema](#database-schema)
9. [Deployment](#deployment)
10. [Maintenance](#maintenance)

---

## 🏥 Project Overview

**Pneumonia Diagnosis System** is an AI-powered Django web application designed to assist medical professionals in preliminary screening of pneumonia from chest X-ray images using a trained MobileNetV2 CNN model.

### Key Objectives:
- ✅ Provide rapid, automated preliminary assessment of chest X-rays
- ✅ Support clinical decision-making without replacing professional diagnosis
- ✅ Ensure data security and medical compliance
- ✅ Deliver intuitive interface for medical professionals
- ✅ Track prediction history and audit trails

### Important Disclaimer:
⚠️ **This system is a preliminary screening tool only.** Results must be reviewed by qualified radiologists and should not be used as the sole basis for medical decisions.

---

## 🏗️ System Architecture

### Architectural Pattern: Model-View-Template (MVT)

```
┌─────────────────────────────────────────────────────┐
│           Presentation Layer (Templates)            │
│  - Authentication Pages (Login, Register)           │
│  - Dashboard & Statistics                           │
│  - Upload Interface                                 │
│  - Results Display                                  │
│  - History Management                               │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│        Business Logic Layer (Django Views)          │
│  - Authentication & Session Management              │
│  - Image Upload & Validation                        │
│  - Diagnosis Workflow                               │
│  - Result Management                                │
│  - User History Tracking                            │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼───────────┬──────────────────────┐
│   AI Processing Layer       │  Data Layer          │
│  - Image Preprocessing      │  - SQLite Database   │
│  - Model Inference          │  - Media Storage     │
│  - Result Generation        │  - Logging           │
└────────────────┬────────────┴──────────────────────┘
                 │
        ┌────────▼─────────┐
        │  MobileNetV2 CNN  │
        │   Model (h5)      │
        └───────────────────┘
```

### System Components:

#### 1. **Authentication & User Management Module**
- User registration with validation
- Secure password hashing (PBKDF2-SHA256)
- Session management (24-hour timeout)
- Auto-logout on browser close

#### 2. **Image Management Module**
- File upload with validation
- Format support: JPEG, PNG
- Size limit: 10 MB
- Metadata tracking (dimensions, format, size)

#### 3. **AI Processing Module**
- Image preprocessing (resizing to 224×224)
- Normalization using ImageNet statistics
- MobileNetV2 model inference
- Confidence scoring and classification

#### 4. **Result Display Module**
- Real-time result visualization
- Confidence level indicators
- Processing time metrics
- Model version tracking

#### 5. **History & Audit Module**
- Prediction history with filtering
- User activity logging
- IP address tracking
- Result archival

---

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 4.2.7
- **Python Version**: 3.8+
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: Django ORM

### ML/AI
- **Deep Learning**: TensorFlow 2.13.0
- **Model**: MobileNetV2 (pre-trained, fine-tuned for pneumonia)
- **Image Processing**: Pillow, NumPy
- **Model Format**: Keras H5

### Frontend
- **Template Engine**: Django Templates
- **Styling**: Custom CSS (responsive design)
- **JavaScript**: Vanilla JS for interactivity
- **Design Pattern**: Responsive grid layout

### Deployment
- **Web Server**: Gunicorn
- **Cloud Platforms**: Railway, Heroku, Netlify
- **WSGI Server**: Built-in Django development server

### Security
- **HTTPS/SSL**: Required for production
- **Password Hashing**: PBKDF2-SHA256
- **CSRF Protection**: Django middleware
- **XSS Prevention**: Django template escaping
- **SQL Injection**: Django ORM parameterized queries

---

## 💻 Installation & Setup

### 1. Clone/Extract Project

```bash
cd pneumonia_diagnosis
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/Scripts/activate  # Windows
source venv/bin/activate       # Linux/Mac
```

### 3. Install Dependencies

```bash
pip install django==4.2.7
pip install tensorflow==2.13.0
pip install pillow==10.0.0
pip install numpy==1.24.3
pip install pandas==2.0.3
```

### 4. Database Setup

```bash
python manage.py migrate
python manage.py makemigrations model_service
python manage.py migrate model_service
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
# Follow prompts to create admin user
```

### 6. Verify Model File

Ensure `model_service/mobilenetv2.h5` exists in the model_service app directory.

### 7. Run Development Server

```bash
python manage.py runserver
```

Access at: `http://localhost:8000`

### 8. Create Test User

- Go to `http://localhost:8000/register/`
- Register with test credentials
- Or use Django admin: `http://localhost:8000/admin/`

---

## 📁 Project Structure

```
pneumonia_diagnosis/
├── manage.py                                 # Django management script
├── db.sqlite3                               # Development database
├── media/                                   # User uploads
│   └── xray_images/                        # Chest X-ray images
├── model_service/                          # Main application
│   ├── migrations/                         # Database migrations
│   ├── templates/model_service/
│   │   ├── base.html                      # Base template
│   │   ├── login.html                     # Login page
│   │   ├── register.html                  # Registration page
│   │   ├── dashboard.html                 # Main dashboard
│   │   ├── upload.html                    # Upload interface
│   │   ├── result.html                    # Results display
│   │   ├── history.html                   # Prediction history
│   │   └── error.html                     # Error page
│   ├── models.py                          # Database models
│   │   ├── ModelVersion                   # ML model versions
│   │   ├── XRayImage                      # Uploaded images
│   │   ├── PredictionResult               # Prediction results
│   │   ├── UserHistory                    # Activity audit log
│   │   ├── SystemConfig                   # Configuration settings
│   │   └── ProcessingLog                  # Processing logs
│   ├── views.py                           # View logic
│   ├── urls.py                            # URL routing
│   ├── services.py                        # AI services
│   │   ├── ImagePreprocessor              # Image preprocessing
│   │   ├── PneumoniaDetectionService      # Model inference
│   │   └── DiagnosisService               # Complete workflow
│   ├── admin.py                           # Admin configuration
│   └── mobilenetv2.h5                     # Trained CNN model
├── users/                                  # User management app
├── pneumonia_config/                      # Project settings
│   ├── settings.py                        # Django settings
│   ├── urls.py                            # Main URL config
│   ├── wsgi.py                            # WSGI configuration
│   └── asgi.py                            # ASGI configuration
└── logs/                                   # Application logs
```

---

## 🎯 Features & Workflow

### 1. User Authentication Flow

```
┌─────────────────────────────────────────┐
│  User Visits Application                 │
└────────────────┬────────────────────────┘
                 │
         ┌───────▼───────┐
         │ Authenticated?│
         └───┬───────┬───┘
             │       │
          YES│       │NO
             │       └──────────────────────────┐
             │                                  │
    ┌────────▼──────┐              ┌───────────▼─────────┐
    │   Dashboard   │              │ Login/Register Page │
    └───────────────┘              └───────────┬─────────┘
                                               │
                                    ┌──────────▼──────────┐
                                    │ Validate Credentials│
                                    └──────┬───────┬──────┘
                                           │       │
                                    Valid  │       │Invalid
                                           │       │
                                    ┌──────▼──┐    │
                                    │Dashboard│    │
                                    └──────────┘    │
                                                    │
                                         ┌──────────▼──────┐
                                         │ Show Error Msg  │
                                         └─────────────────┘
```

### 2. Diagnosis Workflow

```python
"""
DIAGNOSIS WORKFLOW - Complete Flow
"""

User Upload
    ↓
File Validation
├─ Check JPEG/PNG format
├─ Verify size < 10MB
└─ Confirm file integrity
    ↓
Image Preprocessing
├─ Load image file
├─ Convert to RGB if needed
├─ Resize to 224×224
├─ Normalize to [0,1]
├─ Apply ImageNet normalization
└─ Add batch dimension
    ↓
Model Inference
├─ Load MobileNetV2 model
├─ Perform forward pass
├─ Get predictions for both classes
└─ Calculate confidence scores
    ↓
Result Generation
├─ Determine prediction label (Normal/Pneumonia)
├─ Calculate confidence percentage
├─ Assign confidence level (High/Moderate/Low)
├─ Calculate processing time
└─ Format for display
    ↓
Database Storage
├─ Create PredictionResult record
├─ Store raw predictions (JSON)
├─ Log processing time
└─ Record timestamps
    ↓
Display Results
├─ Show prediction with confidence
├─ Display probability distribution
├─ Provide action buttons
└─ Show medical disclaimer
```

### 3. Image Preprocessing Pipeline

```python
# INPUT: Raw chest X-ray image (JPEG/PNG)

# STEP 1: Load Image
from PIL import Image
img = Image.open(image_path)  # Load with PIL

# STEP 2: Convert to RGB
if img.mode != 'RGB':
    img = img.convert('RGB')  # Handle grayscale

# STEP 3: Resize
from PIL.Image import Resampling
img = img.resize((224, 224), Resampling.LANCZOS)

# STEP 4: Convert to Array
import numpy as np
img_array = np.array(img, dtype=np.float32)

# STEP 5: Normalize to [0, 1]
img_normalized = img_array / 255.0

# STEP 6: Apply ImageNet Normalization
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]
img_normalized = (img_normalized - MEAN) / STD

# STEP 7: Add Batch Dimension
img_batch = np.expand_dims(img_normalized, axis=0)
# Shape: (1, 224, 224, 3)

# OUTPUT: Ready for model inference
```

### 4. Model Inference Algorithm

```python
"""
CNN INFERENCE - MobileNetV2 Model

INPUT: Preprocessed image tensor (1, 224, 224, 3)
MODEL: MobileNetV2 trained on Kaggle chest X-ray dataset

PROCESS:
1. Load pre-trained model from mobilenetv2.h5
2. Forward pass through CNN layers
3. Output: [probability_normal, probability_pneumonia]
"""

# Example Output:
predictions = [[0.15, 0.85]]
# Normal: 15%
# Pneumonia: 85%

# Determine Labels:
confidence_normal = predictions[0][0]      # 0.15
confidence_pneumonia = predictions[0][1]   # 0.85

if confidence_pneumonia > confidence_normal:
    label = "PNEUMONIA"
    confidence = confidence_pneumonia       # 0.85 (85%)
else:
    label = "NORMAL"
    confidence = confidence_normal          # 0.15 (15%)

# Confidence Level Assignment:
confidence_pct = confidence * 100           # 85%
if confidence_pct >= 95:
    level = "HIGH"                          # > 95%
elif confidence_pct >= 80:
    level = "MODERATE"                      # 80-95%
else:
    level = "LOW"                           # < 80%
```

### 5. URL Routing

```
/                          → Dashboard (if authenticated)
/login/                    → User login page
/logout/                   → User logout
/register/                 → User registration
/dashboard/               → Main dashboard
/upload/                  → X-ray upload interface
/analyze/<image_id>/      → Perform analysis
/result/<result_id>/      → Display results
/history/                 → View prediction history
/delete/<result_id>/      → Delete prediction
/api/diagnose/            → API endpoint for diagnosis
```

---

## 🔌 API Documentation

### REST API Endpoints

#### 1. User Authentication

```
POST /register/
├─ body: {username, email, password, password_confirm}
└─ response: Redirect to dashboard or re-render with errors

POST /login/
├─ body: {username, password}
└─ response: Session created, redirect to dashboard

POST /logout/
└─ response: Session destroyed, redirect to login
```

#### 2. Diagnosis API

```
POST /api/diagnose/
├─ headers: Content-Type: multipart/form-data
├─ body: {image (file)} // Max 10MB JPEG/PNG
└─ response:
   {
     "status": "success",
     "result_id": 123,
     "prediction": "PNEUMONIA",
     "confidence": 0.85,
     "confidence_percentage": 85.0,
     "confidence_level": "HIGH"
   }
```

#### 3. Results Endpoints

```
GET /result/<result_id>/
└─ response: Renders result.html with prediction details

GET /history/
├─ query params: {label, search, page}
└─ response: Renders history.html with filtered predictions

POST /delete/<result_id>/
└─ response: Deletes result, redirects to history
```

---

## 📊 Database Schema

### Users Table (Django built-in)
```
auth_user
├── id (PK)
├── username (UNIQUE)
├── email
├── password_hash (PBKDF2-SHA256)
├── is_active
└── date_joined
```

### X-Ray Images Table
```
xray_image
├── id (PK)
├── user_id (FK → auth_user)
├── original_filename
├── stored_filename
├── file_path
├── file_size (bytes)
├── upload_time
├── image_width (pixels)
├── image_height (pixels)
├── format (JPEG/PNG)
├── is_preprocessed
└── preprocessing_notes
```

### Prediction Results Table
```
prediction_result
├── id (PK)
├── image_id (FK → xray_image)
├── prediction_label (NORMAL/PNEUMONIA)
├── confidence_score (0.0000-1.0000)
├── confidence_level (HIGH/MODERATE/LOW)
├── processing_time (seconds)
├── created_at
├── model_version_id (FK)
├── raw_predictions (JSON)
├── is_archived
└── notes
```

### User History Table
```
user_history
├── id (PK)
├── user_id (FK → auth_user)
├── action_type (UPLOAD/ANALYZE/VIEW_RESULT/DELETE/LOGIN/LOGOUT)
├── image_id (FK → xray_image, nullable)
├── prediction_result_id (FK, nullable)
├── timestamp
└── ip_address
```

### Model Version Table
```
model_version
├── id (PK)
├── model_name
├── model_path
├── version
├── accuracy
├── precision
├── recall
├── f1_score
├── input_size (224x224)
├── is_active
├── created_at
├── updated_at
└── description
```

---

## 🚀 Deployment

### Prerequisites
- Python 3.8+
- Git
- Railway/Heroku/Netlify account

### Step-by-Step Deployment (Railway)

#### 1. Prepare Project
```bash
# Create requirements.txt
pip freeze > requirements.txt

# Create Procfile
echo "web: gunicorn pneumonia_config.wsgi" > Procfile

# Create runtime.txt
echo "python-3.9.16" > runtime.txt
```

#### 2. Configure Settings for Production

```python
# In settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Enable security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

#### 3. Deploy to Railway

```bash
# Login to Railway
npm i -g @railway/cli
railway login

# Create new project
railway init

# Deploy
railway up
```

#### 4. Production Database Setup

```bash
# Connect to production database
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser
```

#### 5. Environment Variables

Set in Railway dashboard:
```
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgres://...
EMAIL_HOST_PASSWORD=your-email-password
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

---

## 🔧 Maintenance

### Regular Maintenance Tasks

#### Daily
- Monitor logs for errors
- Check system uptime
- Verify database backups

#### Weekly
- Clean temporary files
- Rotate log files
- Review user activity logs

#### Monthly
- Update dependencies
- Run security patches
- Check model performance

#### Quarterly
- Evaluate retraining needs
- Performance optimization
- Security audit

### Troubleshooting

#### Issue: Model not loading
```
Solution:
1. Verify mobilenetv2.h5 exists in model_service/
2. Check file permissions
3. Ensure TensorFlow version matches
```

#### Issue: Image upload fails
```
Solution:
1. Verify file size < 10MB
2. Check format is JPEG/PNG
3. Ensure media directory exists
4. Check storage permissions
```

#### Issue: Database migrations error
```
Solution:
python manage.py makemigrations
python manage.py migrate --plan  # Review first
python manage.py migrate
```

---

## 📝 Key Files Reference

| File | Purpose |
|------|---------|
| `models.py` | Database models and schema |
| `views.py` | Request handlers and logic |
| `services.py` | AI/ML services and preprocessing |
| `urls.py` | URL routing configuration |
| `admin.py` | Django admin interface |
| `settings.py` | Django project settings |
| `mobilenetv2.h5` | Trained CNN model |
| `base.html` | Master template |
| `dashboard.html` | Main user interface |
| `result.html` | Results display |

---

## ⚖️ Legal & Compliance

### Medical Disclaimer
This system is a preliminary screening tool for educational and research purposes. It is NOT intended for clinical use without proper medical oversight.

### Data Privacy
- HIPAA compliance for protected health information
- GDPR compliance for EU users
- Secure transmission via HTTPS
- Temporary file retention (24 hours maximum)

### Liability
Users assume full responsibility for all diagnostic and clinical decisions. Developers provide NO warranty for accuracy or reliability.

---

## 📞 Support & Resources

### Documentation
- [Django Documentation](https://docs.djangoproject.com/)
- [TensorFlow/Keras Documentation](https://www.tensorflow.org/api_docs)
- [SRS Document](./SRS.md)
- [SDD Document](./SDD.md)

### Useful Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver

# Create static files
python manage.py collectstatic

# Run tests
python manage.py test

# Access Django shell
python manage.py shell
```

---

## 🎓 Academic References

1. Kaggle Chest X-Ray Images (Pneumonia) Dataset
2. MobileNetV2: Inverted Residuals and Linear Bottlenecks
3. IEEE Standards for Software Design
4. HIPAA Privacy and Security Rules
5. OWASP Web Security Testing Guide

---

## 📄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-02-17 | Initial release with MobileNetV2 model |
| | | User authentication implemented |
| | | Image upload and preprocessing |
| | | Result display and history tracking |

---

**Last Updated**: February 17, 2025  
**Author**: Attiq ur Rehman  
**Supervisor**: Mr. Muhammad Akmal  
**Institution**: The Islamia University of Bahawalpur, Department of Computer Science

---

## Quick Start Commands

```bash
# Complete setup
cd pneumonia_diagnosis
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Access
# Frontend: http://localhost:8000
# Admin: http://localhost:8000/admin
```

---

⚠️  **Important Disclaimer**: This system is for research and educational purposes only. It should not be used for clinical decision-making without proper medical oversight and professional review.
