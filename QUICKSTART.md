# Quick Start Guide

## For First-Time Setup

1. **Open PowerShell and navigate to project:**
   ```powershell
   cd "e:\uni projects\ML\pneumonia diagnosis(updated)\attiq_pneumonia_project\Pneumonia_digonosis"
   ```

2. **Create and activate virtual environment:**
   ```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Add your trained model:**
   - Place your model file at: `ml_models\mobilenetv2_pneumonia_model.h5`

5. **Run migrations:**
   ```powershell
   python manage.py migrate
   ```

6. **Start server:**
   ```powershell
   python manage.py runserver
   ```

7. **Open browser:**
   - Go to: http://127.0.0.1:8000/

## For Daily Use

```powershell
# Navigate to project
cd "e:\uni projects\ML\pneumonia diagnosis(updated)\attiq_pneumonia_project\Pneumonia_digonosis"

# Activate virtual environment
venv\Scripts\Activate.ps1

# Start server
python manage.py runserver
```

## To Stop Server

- Press `Ctrl + C` in the terminal

## Common Commands

```powershell
# Check if model exists
Test-Path "ml_models\mobilenetv2_pneumonia_model.h5"

# Create superuser (admin access)
python manage.py createsuperuser

# Run on different port
python manage.py runserver 8080

# Deactivate virtual environment
deactivate
```

## Need Help?

- See [README.md](README.md) for full documentation
- See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for detailed setup
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

## Project Structure

```
Pneumonia_digonosis/
├── manage.py                    # Django management
├── requirements.txt             # Dependencies
├── pneumonia_diagnosis/         # Main project settings
├── xray_detector/              # Application code
├── templates/                  # HTML templates
├── ml_models/                  # Place your model here!
│   └── mobilenetv2_pneumonia_model.h5
└── media/uploads/              # Temporary uploads (auto-deleted)
```

## ✅ Checklist

Before first run:
- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Model file at `ml_models\mobilenetv2_pneumonia_model.h5`
- [ ] Migrations run (`python manage.py migrate`)
- [ ] Server starts without errors

You're ready to diagnose pneumonia! 🎉
