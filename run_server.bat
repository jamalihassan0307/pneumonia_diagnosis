@echo off
REM Django Development Server Startup Script
REM This script ensures the correct Python virtual environment is used

echo ================================================================
echo Starting Pneumonia Diagnosis Django Server
echo ================================================================

REM Set the virtual environment Python path
set VENV_PYTHON=venv_py311\Scripts\python.exe

REM Check if venv exists
if not exist "%VENV_PYTHON%" (
    echo ERROR: Virtual environment not found at %VENV_PYTHON%
    echo Please run: python -m venv venv_py311
    pause
    exit /b 1
)

REM Verify Django is installed
%VENV_PYTHON% -c "import django" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Django is not installed in the virtual environment
    echo Installing requirements...
    %VENV_PYTHON% -m pip install -r requirements.txt
)

REM Run migrations if needed
%VENV_PYTHON% manage.py migrate --noinput

REM Start the development server
echo.
echo ✓ Virtual environment verified
echo ✓ Database migrations applied
echo.
echo Starting server on http://127.0.0.1:8000/
echo Press CTRL+C to stop
echo.

%VENV_PYTHON% manage.py runserver

pause
