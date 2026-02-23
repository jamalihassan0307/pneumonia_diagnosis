@echo off
REM Activate Python 3.11 virtual environment
call venv_py311\Scripts\activate.bat
REM Run django server
python manage.py runserver

REM Keep the window open
cmd /k
