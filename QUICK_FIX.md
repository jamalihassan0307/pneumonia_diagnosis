# Quick Fix Guide for Setup Issues

## ✅ Your Situation

You have:
- Python 3.14 installed globally (not compatible with TensorFlow 2.15)
- Python 3.11 virtual environment at: `venv_py311` (PERFECT! Use this!)
- PowerShell execution policy blocking script activation

## 🚀 Quick Solution

### Option 1: Use Batch File (EASIEST)

I've created `activate_env.bat` for you. Just run:

```powershell
.\activate_env.bat
```

Then install packages:
```powershell
pip install -r requirements.txt
```

### Option 2: Activate Manually with CMD

```cmd
venv_py311\Scripts\activate.bat
pip install -r requirements.txt
```

### Option 3: PowerShell Bypass (One-Time)

```powershell
# Bypass execution policy for this session only
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Then activate
venv_py311\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

### Option 4: PowerShell Fix (Permanent)

Run PowerShell as Administrator and execute:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then in regular PowerShell:
```powershell
venv_py311\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 📦 Install Dependencies

Once your environment is activated (you'll see `(venv_py311)` in your prompt):

```powershell
pip install -r requirements.txt
```

This will install:
- Django 4.2.7
- TensorFlow (compatible version for Python 3.11)
- Pillow
- NumPy

## ▶️ Run the Application

After successful installation:

```powershell
# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

Open browser: http://127.0.0.1:8000/

## 🔍 Verify Everything Works

```powershell
# Check you're using the right Python
python --version
# Should show: Python 3.11.x

# Check packages are installed
pip list

# Check virtual environment is active
# Should see (venv_py311) in your prompt
```

## ⚠️ Important Notes

1. **Always use `venv_py311`** not the `venv` folder
2. **Python 3.14** is too new for TensorFlow 2.15
3. **Python 3.11** (your venv_py311) is PERFECT!

## 🐛 Still Having Issues?

If pip install fails:
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt
```

If specific package fails:
```powershell
# Install one by one
pip install Django==4.2.7
pip install tensorflow
pip install Pillow
pip install numpy
```

## ✅ Success Checklist

- [ ] Virtual environment activated (see `(venv_py311)` in prompt)
- [ ] All packages installed without errors
- [ ] `python manage.py migrate` runs successfully
- [ ] `python manage.py runserver` starts without errors
- [ ] Can access http://127.0.0.1:8000/

---

**TL;DR:** Use `activate_env.bat` or `venv_py311\Scripts\activate.bat` instead of trying to activate the PowerShell script.
