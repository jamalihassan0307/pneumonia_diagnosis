# 🏥 Pneumonia Detection System - Complete Documentation

**AI-Powered Chest X-Ray Analysis System**  
**Version:** 1.0 | **Last Updated:** February 23, 2026  
**Developer:** Attiq | **Technology:** Django + MobileNetV2

---

## 📑 Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Pages & Features](#pages--features)
4. [Design System](#design-system)
5. [Installation Guide](#installation-guide)
6. [Usage Guide](#usage-guide)
7. [API Reference](#api-reference)
8. [Deployment](#deployment)

---

## 📋 Project Overview

### About the System

The Pneumonia Detection System is a web-based medical diagnostic tool that uses deep learning to analyze chest X-ray images. Built with Django framework and powered by MobileNetV2 neural network, it provides rapid pneumonia detection with confidence scores.

### Key Features

✅ **Drag & Drop Upload** - Intuitive file upload interface  
✅ **Real-time Analysis** - AI predictions in 2-5 seconds  
✅ **User Dashboard** - Personal statistics and history  
✅ **Session Authentication** - Secure login system  
✅ **Responsive Design** - Works on all devices  
✅ **History Tracking** - View past diagnoses  
✅ **Result Management** - Delete and organize results  
✅ **Confidence Display** - Visual percentage bars

### Architecture

```
┌──────────────────────────────────────────┐
│         Frontend (HTML/CSS/JS)           │
│  Dashboard | Results | History | Profile │
└────────────────┬─────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│        Django Backend + REST API         │
│  Authentication | File Upload | Session  │
└────────────────┬─────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│    MobileNetV2 Model (TensorFlow)        │
│  Input: 224x224 RGB | Output: 0-1 Score │
└──────────────────────────────────────────┘
```

---

## 🛠 Technology Stack

### Backend Technologies

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.8-3.11 | Core language |
| **Django** | 4.2.7 | Web framework |
| **Django REST Framework** | 3.14.0 | API development |
| **TensorFlow** | 2.15+ | Deep learning |
| **Pillow** | 10.1.0 | Image processing |
| **NumPy** | 1.24+ | Numerical operations |

### Frontend Technologies

| Technology | Purpose |
|-----------|---------|
| **HTML5** | Page structure |
| **CSS3** | Styling and animations |
| **JavaScript** | Client-side interactivity |
| **AJAX/Fetch** | Asynchronous requests |

### Database & Storage

- **SQLite** (Development)
- **PostgreSQL** (Production recommended)
- **File System** (Media storage)

### Machine Learning Model

- **Architecture:** MobileNetV2
- **Task:** Binary Classification (NORMAL vs PNEUMONIA)
- **Input:** 224x224x3 RGB images
- **Output:** Single probability score (0-1)
- **File:** mobilenetv2_pneumonia_model.h5

---

## 📱 Pages & Features

### 1. Landing Page (/)

**Purpose:** Welcome screen and system introduction

**Features:**
- System overview and description
- Login/Register buttons
- Feature highlights
- Clean gradient design

**Files:**
- Template: `templates/xray_detector/index.html`
- Route: `/`

---

### 2. Login Page (/login/)

**Purpose:** User authentication

**Features:**
- Username/password form
- Session-based authentication
- Error message display
- Redirect to dashboard after login

**Form Fields:**
- Username (required)
- Password (required)

**Files:**
- Template: `templates/xray_detector/login.html`
- View: `xray_detector/views.py:login_view()`
- Route: `/login/`

---

### 3. Register Page (/register/)

**Purpose:** New user account creation

**Features:**
- Registration form
- Password confirmation
- Client-side validation
- Auto-redirect after signup

**Form Fields:**
- Username (unique, required)
- Email (optional)
- Password (min 8 characters)
- Confirm Password

**Files:**
- Template: `templates/xray_detector/register.html`
- View: `xray_detector/views.py:register_view()`
- Route: `/register/`

---

### 4. Dashboard (/dashboard/)

**Purpose:** Main user interface after login

**Features:**

#### Statistics Cards
- **Total Uploads:** Count of all uploaded images
- **Total Analyzed:** Successfully processed images
- **Normal Results:** Count of normal diagnoses
- **Pneumonia Results:** Count of pneumonia detections

#### Upload Section
- Drag & drop file upload
- Click to browse file selector
- Image preview before analysis
- Real-time analysis with loading spinner
- Result display with confidence bar
- Success/error notifications

#### Recent Analyses Table
- Last 10 diagnoses displayed
- Columns: Filename | Result | Confidence | Date
- Auto-updates after new upload (no page reload)
- Color-coded badges (green=normal, red=pneumonia)

**User Experience:**
1. User drags/selects X-ray image
2. Preview appears instantly
3. Click "Analyze X-Ray"
4. Loading spinner (2-5 seconds)
5. Result badge displays (NORMAL/PNEUMONIA)
6. Confidence bar animates to percentage
7. Stats update automatically
8. New row appears in history table
9. User can analyze another without reload

**Files:**
- Template: `templates/xray_detector/dashboard.html`
- Styles: `static/css/dashboard.css`
- View: `xray_detector/views.py:dashboard_view()`
- API: `/api/images/upload/`
- Route: `/dashboard/`

**Data Flow:**
```
Context Data (Server-side):
- total_uploads: int
- total_analyzed: int
- normal_count: int
- pneumonia_count: int
- history: list of recent results

JavaScript (Client-side):
- Updates stats dynamically after upload
- Adds new row to table without reload
- Manages file upload and preview
```

---

### 5. Results Page (/results/)

**Purpose:** View all analysis results in grid/list format

**Features:**

#### Display Options
- Grid view (default) or list view
- Result cards with image thumbnails
- Prediction badges (NORMAL/PNEUMONIA)
- Confidence percentage display
- Date/time of analysis

#### Interaction
- Click card to view full details
- Hover effects for better UX
- Responsive grid layout
- Auto-pagination for large datasets

**Data Displayed:**
- X-ray image thumbnail
- Prediction result
- Confidence score
- Upload date
- Quick actions

**Files:**
- Template: `templates/xray_detector/results.html`
- Styles: `static/css/results.css`
- View: `xray_detector/views.py:results_view()`
- Route: `/results/`

**Data Flow:**
```
Context Data:
- results: JSON array from PredictionResult model
- Serialized fields: id, image_url, prediction, confidence, date
```

---

### 6. Result Detail Page (/result-detail/?id=X)

**Purpose:** View single result with full details and management options

**Features:**

#### Image Display
- Full-size X-ray image
- Preview with zoom capability
- Image metadata (filename, size, format)

#### Prediction Details
- Large result badge (NORMAL/PNEUMONIA)
- Confidence percentage with visual bar
- Raw model score
- Prediction timestamp

#### Actions
- Delete result (with CSRF protection)
- Download image
- Back to results list

**Files:**
- Template: `templates/xray_detector/result_detail.html`
- Styles: `static/css/result_detail.css`
- View: `xray_detector/views.py:result_detail_view()`
- Route: `/result-detail/`

**Authentication:**
- Session-based authentication
- CSRF token for delete operations
- User can only view own results

---

### 7. History Page (/history/)

**Purpose:** Timeline view of all user activities

**Features:**

#### Timeline Display
- Chronological activity log
- Visual timeline with icons
- Grouped by date
- Activity type indicators

#### Information Shown
- Upload events
- Analysis completion
- Result summaries
- Timestamps

#### Filters
- Date range selector
- Result type filter (All/Normal/Pneumonia)
- Search by filename

**Files:**
- Template: `templates/xray_detector/history.html`
- Styles: `static/css/history.css`
- View: `xray_detector/views.py:history_view()`
- Route: `/history/`

**Data Flow:**
```
Context Data:
- history: JSON array from UserHistory model
- Includes: action type, timestamp, result, metadata
```

---

### 8. Profile Page (/profile/)

**Purpose:** User account information and statistics

**Features:**

#### User Information
- Username display
- Email address
- Join date
- Account status

#### Statistics Dashboard
- Total scans performed
- Normal results count
- Pneumonia results count
- Success rate percentage
- Most active dates

#### Account Settings
- Update name
- Change email
- Password change link
- Account preferences

**Files:**
- Template: `templates/xray_detector/profile.html`
- Styles: `static/css/profile.css`
- View: `xray_detector/views.py:profile_view()`
- Route: `/profile/`

**Data Flow:**
```
Context Data:
- user: Django User object
- stats: Dictionary with counts and percentages
```

---

### 9. Model Info Page (/model-info/)

**Purpose:** Information about the AI model

**Features:**

#### Model Details
- Architecture overview (MobileNetV2)
- Input/output specifications
- Performance metrics
- Training information

#### Technical Specifications
- Input size: 224x224 RGB
- Model parameters count
- File size and format
- Version information

#### Usage Guidelines
- How to interpret results
- Confidence threshold explanation
- Best practices for X-ray quality
- Limitations and disclaimers

**Files:**
- Template: `templates/xray_detector/model_info.html`
- Styles: `static/css/model_info.css`
- API: `/api/model-versions/`
- Route: `/model-info/`

---

## 🎨 Design System

### Color Palette

#### Primary Colors

| Color Name | Hex Code | RGB | Usage |
|-----------|----------|-----|-------|
| **Primary Purple** | `#667eea` | rgb(102, 126, 234) | Buttons, links, primary actions |
| **Secondary Purple** | `#764ba2` | rgb(118, 75, 162) | Gradients, hover states |
| **Background** | `#f5f7fa` | rgb(245, 247, 250) | Page background |
| **Card White** | `#ffffff` | rgb(255, 255, 255) | Content cards |
| **Text Dark** | `#333333` | rgb(51, 51, 51) | Primary text |
| **Text Muted** | `#999999` | rgb(153, 153, 153) | Secondary text |

#### Gradient Combinations

```css
/* Primary Gradient (Purple) */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Success Gradient (Green - Normal Result) */
background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);

/* Danger Gradient (Red - Pneumonia) */
background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);

/* Blue Gradient (Info) */
background: linear-gradient(135deg, #4e73df 0%, #224abe 100%);
```

#### Semantic Colors

| Purpose | Background | Text | Border | Usage |
|---------|-----------|------|--------|-------|
| **Success** | `#c8e6c9` | `#2e7d32` | `#2e7d32` | Normal results, success messages |
| **Danger** | `#ffcdd2` | `#c62828` | `#c62828` | Pneumonia results, errors |
| **Warning** | `#fff9c4` | `#f57f17` | `#f57f17` | Warnings, attention needed |
| **Info** | `#bbdefb` | `#1565c0` | `#1565c0` | Information, hints |

---

### Typography

#### Font Family
```css
font-family: 'Segoe UI', Arial, Helvetica, sans-serif;
```

#### Font Sizes & Weights

| Element | Size | Weight | Usage |
|---------|------|--------|-------|
| **H1** | 36px | Bold (700) | Page titles |
| **H2** | 22px | Bold (700) | Section headings |
| **H3** | 18px | Bold (700) | Subsections |
| **Body** | 14px | Regular (400) | Default text |
| **Small** | 12px | Regular (400) | Labels, metadata |
| **Button** | 14px | Semi-bold (600) | All buttons |

#### Text Styles
```css
/* Headings */
h1 { font-size: 36px; font-weight: 700; color: #333; margin-bottom: 20px; }
h2 { font-size: 22px; font-weight: 700; color: #333; margin-bottom: 15px; }
h3 { font-size: 18px; font-weight: 700; color: #333; margin-bottom: 10px; }

/* Body text */
body { font-size: 14px; line-height: 1.6; color: #333; }

/* Muted text */
.text-muted { color: #999; font-size: 12px; }
```

---

### Component Styles

#### 1. Navigation Bar

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

**Colors:**
- Background: Purple gradient (#667eea → #764ba2)
- Text: White (#ffffff)
- Hover: Translucent white overlay
- Active: Stronger white overlay

---

#### 2. Buttons

**Primary Button:**
```css
.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 25px;
    border-radius: 8px;
    font-weight: 600;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.6);
}
```

**Secondary Button:**
```css
.btn-secondary {
    background: #f0f0f0;
    color: #333;
    padding: 12px 25px;
    border-radius: 8px;
    font-weight: 600;
}

.btn-secondary:hover {
    background: #e0e0e0;
}
```

**Success/Danger Buttons:**
```css
.btn-success {
    background: #10b981;
    color: white;
}

.btn-danger {
    background: #ffcdd2;
    color: #c62828;
}
```

**Button Colors:**
- Primary: Purple gradient (#667eea → #764ba2)
- Secondary: Light gray (#f0f0f0)
- Success: Green (#10b981)
- Danger: Red background (#ffcdd2) with red text (#c62828)

---

#### 3. Cards

```css
.card {
    background: white;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
    transition: all 0.3s ease;
}

.card:hover {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}
```

**Card Colors:**
- Background: White (#ffffff)
- Shadow: Light gray (rgba(0, 0, 0, 0.1))
- Hover shadow: Darker gray (rgba(0, 0, 0, 0.15))
- Border radius: 12px

---

#### 4. Upload Area

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

**Upload Area Colors:**
- Border: Dashed purple (#667eea)
- Background: Very light purple (#f8f9ff)
- Hover background: Lighter purple (#f0f2ff)
- Dragover background: Light blue-purple (#e8ebff)

---

#### 5. Result Display

**Normal Result:**
```css
.result-area.normal {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    color: white;
    padding: 30px;
    border-radius: 15px;
    text-align: center;
}

.result-badge {
    font-size: 36px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
}
```

**Pneumonia Result:**
```css
.result-area.pneumonia {
    background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    color: white;
    padding: 30px;
    border-radius: 15px;
    text-align: center;
}
```

**Result Colors:**
- Normal: Green gradient (#11998e → #38ef7d)
- Pneumonia: Red gradient (#eb3349 → #f45c43)
- Text: White (#ffffff)
- Badge text: Extra large (36px), uppercase

---

#### 6. Confidence Bar

```css
.confidence-bar-container {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 25px;
    height: 30px;
    overflow: hidden;
    margin: 20px 0;
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
    color: #333;
}
```

**Confidence Bar Colors:**
- Container: Translucent white (rgba(255, 255, 255, 0.3))
- Bar: Solid white (#ffffff)
- Text: Dark gray (#333)
- Animation: 1 second smooth width transition

---

#### 7. Badges

```css
/* Normal Badge (Green) */
.badge.normal {
    background: #c8e6c9;
    color: #2e7d32;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

/* Pneumonia Badge (Red) */
.badge.pneumonia {
    background: #ffcdd2;
    color: #c62828;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}
```

**Badge Colors:**
- Normal: Light green background (#c8e6c9), dark green text (#2e7d32)
- Pneumonia: Light red background (#ffcdd2), dark red text (#c62828)
- Border radius: 20px (pill shape)

---

#### 8. Statistics Cards

```css
.stat-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.stat-number {
    font-size: 48px;
    font-weight: 700;
    color: #667eea;
}

.stat-label {
    font-size: 14px;
    color: #999;
    margin-top: 10px;
}
```

**Stat Card Colors:**
- Background: White (#ffffff)
- Number: Purple (#667eea)
- Label: Gray (#999)
- Hover: Lifts up with enhanced shadow

---

#### 9. Tables

```css
table {
    width: 100%;
    border-collapse: collapse;
}

table th {
    background: #f5f7fa;
    color: #333;
    padding: 15px;
    text-align: left;
    font-weight: 600;
    border-bottom: 2px solid #ddd;
}

table td {
    padding: 15px;
    border-bottom: 1px solid #eee;
    color: #333;
}

table tr:hover {
    background: #f9fafb;
}
```

**Table Colors:**
- Header background: Light gray (#f5f7fa)
- Header text: Dark gray (#333)
- Header border: Gray (#ddd)
- Row border: Light gray (#eee)
- Hover: Very light gray (#f9fafb)

---

#### 10. Loading Spinner

```css
.spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #667eea;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.loading {
    display: none;
    text-align: center;
    padding: 40px;
}

.loading.active {
    display: block;
}
```

**Spinner Colors:**
- Border: Light gray (#f3f3f3)
- Top border: Purple (#667eea)
- Animation: 1 second continuous rotation

---

### Animations & Transitions

#### Fade In Animation
```css
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

.fade-in {
    animation: fadeIn 0.5s ease;
}
```

#### Button Hover Effect
```css
.btn:hover {
    transform: translateY(-2px);
    transition: all 0.3s ease;
}
```

#### Card Hover Effect
```css
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
}
```

---

### Responsive Breakpoints

```css
/* Tablet (768px and below) */
@media (max-width: 768px) {
    .navbar {
        height: auto;
        padding: 10px;
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

---

### Design Customization Guide

#### Change Primary Color

To change from purple to blue:

```css
/* Find and replace: */
#667eea → #4e73df (primary blue)
#764ba2 → #224abe (darker blue)

/* Update gradients: */
background: linear-gradient(135deg, #4e73df 0%, #224abe 100%);
```

#### Change Result Colors

```css
/* Normal result (Green → Blue) */
.result-area.normal {
    background: linear-gradient(135deg, #4e73df 0%, #2c5aa0 100%);
}

/* Pneumonia result (Red → Orange) */
.result-area.pneumonia {
    background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
}
```

#### Change Font

```css
/* Use Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

body {
    font-family: 'Poppins', sans-serif;
}
```

---

## 📦 Installation Guide

### Prerequisites

- **Python:** 3.8 to 3.11 (TensorFlow 2.15 compatibility)
- **pip:** Package manager
- **8GB RAM:** Recommended for ML model
- **Model File:** `mobilenetv2_pneumonia_model.h5`

### Step 1: Navigate to Project

```powershell
cd "e:\uni projects\ML\pneumonia diagnosis(updated)\attiq_pneumonia_project\Pneumonia_digonosis"
```

### Step 2: Activate Virtual Environment

**Windows:**
```powershell
# Option 1: Batch file
.\activate_env.bat

# Option 2: PowerShell
venv_py311\Scripts\Activate.ps1

# Option 3: Command Prompt
venv_py311\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Step 3: Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### Step 4: Add Model File

**CRITICAL:** Place your trained model file:

```
ml_models/mobilenetv2_pneumonia_model.h5
```

**Verify:**
```powershell
Test-Path "ml_models\mobilenetv2_pneumonia_model.h5"
```

### Step 5: Run Migrations

```powershell
python manage.py migrate
```

### Step 6: Create Admin User (Optional)

```powershell
python manage.py createsuperuser
```

### Step 7: Start Server

```powershell
python manage.py runserver
```

### Step 8: Access Application

Open browser: **http://127.0.0.1:8000/**

---

## 📖 Usage Guide

### For End Users

#### 1. Create Account
- Navigate to `/register/`
- Fill in username, email, password
- Click "Register"
- Auto-redirect to login

#### 2. Login
- Go to `/login/`
- Enter credentials
- Access dashboard

#### 3. Upload X-Ray
- From dashboard
- Drag & drop or click "Choose File"
- Supported: PNG, JPG, JPEG (max 16MB)
- Preview appears automatically

#### 4. Analyze Image
- Click "Analyze X-Ray" button
- Wait 2-5 seconds (loading spinner)
- View results:
  - **NORMAL** (green) - No pneumonia
  - **PNEUMONIA** (red) - Pneumonia detected
  - Confidence percentage shown

#### 5. View History
- Click "History" in navigation
- View past diagnoses
- Timeline format
- Filter by date/result

#### 6. Manage Profile
- Click "Profile" in navigation
- View statistics
- Update account info
- Change password

---

## 🔌 API Reference

### Authentication

#### Login
```http
POST /api/login/
Content-Type: application/json

{
    "username": "user",
    "password": "pass"
}
```

**Response:**
```json
{
    "token": "abc123...",
    "user": {
        "id": 1,
        "username": "user"
    }
}
```

---

### Image Upload & Analysis

#### Upload Image
```http
POST /api/images/upload/
Content-Type: multipart/form-data
X-CSRFToken: <csrf_token>

Form Data:
- image: <file>
```

**Response:**
```json
{
    "status": "success",
    "prediction": "NORMAL",
    "confidence": 92.5,
    "image_id": 123,
    "message": "Analysis complete"
}
```

---

### Results

#### Get All Results
```http
GET /api/results/
Authorization: Token <token>
```

**Response:**
```json
{
    "count": 50,
    "results": [
        {
            "id": 1,
            "prediction": "NORMAL",
            "confidence": 95.2,
            "created_at": "2026-02-23T10:30:00Z"
        }
    ]
}
```

#### Delete Result
```http
DELETE /api/results/{id}/
Authorization: Token <token>
X-CSRFToken: <csrf_token>
```

---

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG = False` in settings.py
- [ ] Generate new `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use PostgreSQL database
- [ ] Set up environment variables (.env)
- [ ] Collect static files
- [ ] Configure HTTPS/SSL
- [ ] Set up Gunicorn/uWSGI
- [ ] Configure Nginx
- [ ] Enable logging
- [ ] Set up backups

### Environment Variables

Create `.env` file:

```ini
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_NAME=pneumonia_db
DB_USER=db_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432
```

### Gunicorn Command

```bash
gunicorn --bind 0.0.0.0:8000 --workers 3 pneumonia_diagnosis.wsgi:application
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    client_max_body_size 20M;
    
    location /static/ {
        alias /path/to/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📊 Database Models

### XRayImage
- `id`: Primary key
- `user`: Foreign key to User
- `image`: File field
- `uploaded_at`: DateTime
- `file_size`: Integer

### PredictionResult
- `id`: Primary key
- `xray_image`: Foreign key to XRayImage
- `predicted_class`: Char field (NORMAL/PNEUMONIA)
- `confidence`: Float (0-100)
- `raw_score`: Float (0-1)
- `created_at`: DateTime

### UserHistory
- `id`: Primary key
- `user`: Foreign key to User
- `action`: Char field
- `result`: Foreign key to PredictionResult
- `timestamp`: DateTime

---

## ⚠️ Important Notes

### Medical Disclaimer

This system is for:
- ✅ Educational purposes
- ✅ Research and development
- ✅ Diagnostic support tool

**NOT for:**
- ❌ Primary medical diagnosis
- ❌ Direct clinical use without validation
- ❌ Replacement for professional opinion

**Always consult qualified healthcare professionals.**

### Security Notes

- Use HTTPS in production
- Enable CSRF protection
- Sanitize file uploads
- Rate limit API endpoints
- Regular security audits
- Comply with HIPAA/GDPR

---

## 📞 Support & Credits

### Developer
**Attiq** - Primary developer and maintainer

### Technology Credits
- Django Web Framework
- TensorFlow / Keras
- MobileNetV2 Architecture
- Python Community

### Version History
- **v1.0** (Feb 2026) - Initial release with full features

---

## 📄 License

Educational and research use only. Commercial deployment requires proper medical certification and compliance with healthcare regulations.

---

**Last Updated:** February 23, 2026  
**Version:** 1.0  
**Status:** Production Ready

---

*End of Complete Project Documentation*
