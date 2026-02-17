# 🏥 Pneumonia Diagnosis System

AI-powered Django web application for preliminary pneumonia screening using chest X-ray images with MobileNetV2 CNN model.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Admin User
```bash
python manage.py createsuperuser
```

### 4. Run Development Server
```bash
python manage.py runserver
```

Access the application at: **http://localhost:8000**

---

## 📦 Project Structure

```
pneumonia_diagnosis/
├── manage.py                  # Django management
├── db.sqlite3                # Database (development)
├── requirements.txt          # Python dependencies
├── PROJECT.md               # Detailed documentation
├── model_service/           # Main application
│   ├── models.py           # Database models
│   ├── views.py            # View logic
│   ├── services.py         # AI/ML services
│   ├── urls.py             # URL routing
│   ├── admin.py            # Admin config
│   ├── mobilenetv2.h5      # Trained model
│   └── templates/          # HTML templates
├── pneumonia_config/        # Project settings
│   ├── settings.py         # Django config
│   ├── urls.py             # Main URLs
│   └── wsgi.py             # WSGI config
└── media/                   # User uploads
    └── xray_images/        # X-ray storage
```

---

## ✨ Features

✅ **User Authentication** - Secure login/registration for medical professionals  
✅ **X-ray Upload** - Support for JPEG/PNG up to 10MB  
✅ **AI Diagnosis** - MobileNetV2 model inference  
✅ **Results Display** - Clear visualization with confidence scores  
✅ **History Management** - Track all predictions  
✅ **Audit Logging** - Complete activity tracking  
✅ **Responsive UI** - Works on desktop and tablets  

---

## 🔐 Admin Access

```
URL: http://localhost:8000/admin
Username: [created with createsuperuser]
Password: [your password]
```

---

## 🎯 Main URLs

| URL | Purpose |
|-----|---------|
| `/` | Dashboard |
| `/login/` | User login |
| `/register/` | User registration |
| `/upload/` | Upload X-ray |
| `/history/` | View predictions |
| `/admin/` | Administration |

---

## ⚠️ Important Disclaimer

**This system is a preliminary screening tool only.** 
- NOT a replacement for professional medical diagnosis
- Results must be reviewed by qualified radiologists
- Do not use as sole basis for medical decisions

---

## 📚 Documentation

See [PROJECT.md](./PROJECT.md) for comprehensive documentation including:
- System architecture
- Detailed workflow
- Database schema
- Deployment guide
- Maintenance procedures
- API documentation

---

## 🐛 Common Issues

### Model not loading
```bash
# Verify model file exists
ls model_service/mobilenetv2.h5

# Reinstall TensorFlow if needed
pip install tensorflow==2.13.0 --force-reinstall
```

### Database errors
```bash
# Reset database (development only)
rm db.sqlite3
python manage.py migrate
```

### Upload fails
- Check file size < 10MB
- Verify format is JPEG/PNG
- Ensure media/ directory has write permissions

---

## 🔧 Configuration

Edit `pneumonia_config/settings.py` to:
- Change database backend
- Modify session timeout
- Adjust file upload limits
- Configure logging

---

## 📞 Support

For issues or questions:
1. Check PROJECT.md documentation
2. Review SRS/SDD documents
3. Check Django admin logs
4. Enable DEBUG mode for development

---

## 📄 License & Compliance

- Educational and research purposes
- HIPAA considerations for medical data
- GDPR compliance for EU users
- No warranty express or implied

---

## 👨‍💻 Development Team

- **Developer**: Attiq ur Rehman (F22BDOCS1M01124)
- **Supervisor**: Mr. Muhammad Akmal
- **Institution**: The Islamia University of Bahawalpur
- **Department**: Computer Science

---

**Version**: 1.0  
**Last Updated**: February 17, 2025

---

## 🎓 Technologies Used

- Django 4.2.7
- TensorFlow 2.13.0
- MobileNetV2 CNN
- SQLite/PostgreSQL
- Pillow, NumPy, Pandas
- HTML5, CSS3, Vanilla JavaScript

---

**Ready to use!** 🚀
