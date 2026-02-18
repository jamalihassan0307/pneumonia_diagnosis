# Deployment Notes

## ⚠️ Important: This is a Development Setup

The current configuration is for **development and testing only**. Do NOT deploy to production without making security changes.

## 🔒 Security Changes for Production

### 1. Settings.py Modifications

```python
# Change DEBUG to False
DEBUG = False

# Set allowed hosts
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Generate new secret key (CRITICAL!)
# Use: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY = 'your-new-randomly-generated-secret-key'

# Use environment variables for sensitive data
import os
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

# Use proper database (PostgreSQL recommended)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': '5432',
    }
}

# HTTPS settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### 2. Static Files for Production

```python
# In settings.py
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Collect static files
python manage.py collectstatic
```

### 3. Use Production Web Server

**Don't use `runserver` in production!**

Use Gunicorn or uWSGI:

```powershell
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn pneumonia_diagnosis.wsgi:application --bind 0.0.0.0:8000
```

### 4. Use Reverse Proxy (Nginx)

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }
}
```

## 🌐 Deployment Options

### Option 1: Cloud Platform (Easiest)

**Heroku:**
1. Add `Procfile`:
   ```
   web: gunicorn pneumonia_diagnosis.wsgi
   ```
2. Add `runtime.txt`:
   ```
   python-3.11.0
   ```
3. Deploy:
   ```
   heroku create your-app-name
   git push heroku main
   ```

**AWS Elastic Beanstalk:**
- Use EB CLI
- Configure Django settings for AWS
- Upload environment variables

**Google Cloud Platform:**
- Use App Engine
- Configure app.yaml
- Deploy with gcloud

### Option 2: VPS (More Control)

**DigitalOcean, Linode, AWS EC2:**

1. **Setup Server:**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install dependencies
   sudo apt install python3-pip python3-venv nginx -y
   ```

2. **Clone/Upload Project**

3. **Setup Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

4. **Configure Nginx** (see above)

5. **Setup Systemd Service:**
   ```ini
   [Unit]
   Description=Pneumonia Detection Gunicorn
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/project
   Environment="PATH=/path/to/venv/bin"
   ExecStart=/path/to/venv/bin/gunicorn --workers 3 --bind unix:/path/to/project/gunicorn.sock pneumonia_diagnosis.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

6. **Enable and Start:**
   ```bash
   sudo systemctl enable pneumonia-detection
   sudo systemctl start pneumonia-detection
   ```

### Option 3: Docker (Recommended for Production)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

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

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./ml_models:/app/ml_models
      - ./media:/app/media
    environment:
      - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
      - DJANGO_DEBUG=False
    restart: unless-stopped
```

Deploy:
```bash
docker-compose up -d
```

## 📊 Performance Optimization

### 1. Model Loading

- Use model caching (already implemented)
- Consider model optimization (quantization, pruning)
- Use TensorFlow Lite for faster inference

### 2. Caching

Add Redis for caching:

```python
# In settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 3. Database

- Use PostgreSQL instead of SQLite
- Add database indexes if storing results
- Use connection pooling

### 4. CDN

- Use CDN for static files
- Examples: Cloudflare, AWS CloudFront

## 🔐 Security Checklist

- [ ] DEBUG = False
- [ ] New SECRET_KEY generated
- [ ] ALLOWED_HOSTS configured
- [ ] HTTPS enabled
- [ ] Secure cookies enabled
- [ ] Environment variables for secrets
- [ ] Regular security updates
- [ ] Rate limiting implemented
- [ ] File upload validation (already implemented)
- [ ] CSRF protection enabled (already implemented)
- [ ] Input sanitization
- [ ] SQL injection protection (Django ORM handles this)
- [ ] XSS protection enabled

## 📈 Monitoring

### Add Health Check Endpoint

In `xray_detector/views.py`:

```python
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy'})
```

In `xray_detector/urls.py`:

```python
urlpatterns = [
    path('', views.index, name='index'),
    path('health/', views.health_check, name='health'),
]
```

### Logging

Configure proper logging in settings.py:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/error.log',
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

### Monitor with:
- Sentry (error tracking)
- New Relic (performance)
- Datadog (infrastructure)
- Prometheus + Grafana

## 🚀 Deployment Checklist

- [ ] All security changes applied
- [ ] Environment variables configured
- [ ] Database setup (if not SQLite)
- [ ] Static files collected
- [ ] Model file uploaded to server
- [ ] Gunicorn/uWSGI configured
- [ ] Nginx/Apache configured
- [ ] HTTPS certificate installed (Let's Encrypt)
- [ ] Firewall configured
- [ ] Domain name configured
- [ ] Testing on staging environment
- [ ] Backups configured
- [ ] Monitoring setup
- [ ] Error tracking enabled
- [ ] Documentation updated

## 📝 Environment Variables

Create `.env` file (don't commit to git):

```ini
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=pneumonia_db
DB_USER=db_user
DB_PASSWORD=secure_password
DB_HOST=localhost
```

Load in settings.py:

```python
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',')
```

## 🔄 Updates and Maintenance

### Regular Tasks:

1. **Update dependencies:**
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

2. **Security patches:**
   ```bash
   pip install --upgrade django
   ```

3. **Database backups:**
   ```bash
   python manage.py dumpdata > backup.json
   ```

4. **Check logs:**
   ```bash
   tail -f /var/log/django/error.log
   ```

## ⚠️ Current Limitations

1. **No user authentication** - Anyone can access
2. **No rate limiting** - Can be abused
3. **No result history** - No database storage
4. **Single server** - No load balancing
5. **No API** - Only web interface

Consider adding these features for production use.

## 📞 Support

For production deployment assistance, consider:
- Hiring DevOps consultant
- Using managed services (AWS, GCP, Azure)
- Consulting Django deployment documentation

---

**Remember:** Development server (`python manage.py runserver`) is NOT for production use!
