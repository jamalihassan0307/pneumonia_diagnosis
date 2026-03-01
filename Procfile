web: python manage.py migrate && gunicorn pneumonia_diagnosis.wsgi --bind 0.0.0.0:$PORT --timeout 120 --workers 2
