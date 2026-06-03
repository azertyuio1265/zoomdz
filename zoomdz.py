import os

PROJECT_DIR = "meet-chargily-render"
os.makedirs(PROJECT_DIR, exist_ok=True)
os.chdir(PROJECT_DIR)

# الملفات والمحتوى
files = {
    # Root files
    "render.yaml": """services:
  - type: web
    name: meet-backend
    runtime: image
    repo: https://github.com/yourusername/meet-chargily-render
    plan: starter
    dockerfilePath: ./backend/Dockerfile
    envVars:
      - key: DATABASE_URL
        value: postgresql://meet_user:password@localhost:5432/meet_db
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: "False"
      - key: CHARGILY_API_KEY
        sync: false
""",
    
    ".gitignore": """__pycache__/
*.pyc
.env
db.sqlite3
staticfiles/
node_modules/
dist/
.DS_Store
""",
    
    ".env.example": """SECRET_KEY=your-secret-key
DEBUG=True
CHARGILY_API_KEY=your-api-key
CHARGILY_SECRET_KEY=your-secret
""",
    
    # Backend files
    "backend/requirements.txt": """Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.1
psycopg2-binary==2.9.9
gunicorn==21.2.0
whitenoise==6.6.0
python-decouple==3.8
requests==2.31.0
djangorestframework-simplejwt==5.3.0
django-redis==5.4.0
""",
    
    "backend/Dockerfile": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn", "meet.wsgi:application", "--bind", "0.0.0.0:8000"]
""",
    
    "backend/manage.py": """#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meet.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
""",
    
    # Meet app
    "backend/meet/__init__.py": "",
    "backend/meet/settings.py": """import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY', default='django-insecure-key')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'bookings',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'meet.urls'
WSGI_APPLICATION = 'meet.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'ar-dz'
TIME_ZONE = 'Africa/Algiers'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True

CHARGILY_API_KEY = config('CHARGILY_API_KEY', default='')
CHARGILY_SECRET_KEY = config('CHARGILY_SECRET_KEY', default='')
""",
    
    "backend/meet/urls.py": """from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('bookings.urls')),
    path('health/', health_check),
]
""",
    
    "backend/meet/wsgi.py": """import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meet.settings')
application = get_wsgi_application()
""",
    
    "backend/meet/asgi.py": """import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meet.settings')
application = get_asgi_application()
""",
    
    # Bookings app
    "backend/bookings/__init__.py": "",
    "backend/bookings/apps.py": """from django.apps import AppConfig

class BookingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookings'
""",
    
    "backend/bookings/admin.py": """from django.contrib import admin
from .models import TeacherProfile, Session, Payment

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'hourly_rate', 'is_verified']

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'teacher', 'student', 'scheduled_time', 'price', 'status']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['session', 'amount', 'status', 'created_at']
""",
    
    "backend/bookings/models.py": """from django.db import models
from django.contrib.auth.models import User
import uuid

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.subject}"

class Session(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('paid', 'تم الدفع'),
        ('completed', 'مكتملة'),
        ('cancelled', 'ملغية'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=100)
    scheduled_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    room_name = models.CharField(max_length=255, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.room_name:
            self.room_name = f"room_{uuid.uuid4().hex[:12]}"
        super().save(*args, **kwargs)

class Payment(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
""",
    
    "backend/bookings/serializers.py": """from rest_framework import serializers
from .models import TeacherProfile, Session

class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = '__all__'

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'
""",
    
    "backend/bookings/urls.py": """from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'teachers', views.TeacherProfileViewSet)
router.register(r'sessions', views.SessionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('initiate-payment/<uuid:session_id>/', views.initiate_payment, name='initiate-payment'),
]
""",
    
    "backend/bookings/views.py": """from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import TeacherProfile, Session
from .serializers import TeacherProfileSerializer, SessionSerializer

class TeacherProfileViewSet(viewsets.ModelViewSet):
    queryset = TeacherProfile.objects.all()
    serializer_class = TeacherProfileSerializer
    permission_classes = [AllowAny]

class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    return Response({
        'payment_url': 'https://sandbox.chargily.dz/pay/test',
        'session_id': str(session.id)
    })
""",
    
    "backend/bookings/utils.py": """import hashlib
import hmac
import json
from django.conf import settings

def verify_chargily_signature(payload, signature):
    secret = settings.CHARGILY_SECRET_KEY
    expected = hmac.new(secret.encode(), json.dumps(payload).encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
""",
    
    # Frontend files
    "frontend/package.json": """{
  "name": "meet-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "react-router-dom": "^6.20.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0"
  }
}
""",
    
    "frontend/Dockerfile": """FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
""",
    
    "frontend/nginx.conf": """server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }
}
""",
    
    "frontend/vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: { port: 3000 }
})
""",
    
    "frontend/index.html": """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة الدروس الجزائرية</title>
</head>
<body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
</body>
</html>
""",
    
    "frontend/src/main.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
""",
    
    "frontend/src/index.css": """* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Tahoma', Arial, sans-serif; direction: rtl; background: #f5f7fb; }
""",
    
    "frontend/src/App.jsx": """import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import PaymentPage from './pages/PaymentPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/payment/:sessionId" element={<PaymentPage />} />
      </Routes>
    </BrowserRouter>
  )
}
export default App
""",
    
    "frontend/src/pages/Dashboard.jsx": """import React, { useState, useEffect } from 'react'
import axios from 'axios'

function Dashboard() {
  const [teachers, setTeachers] = useState([])

  useEffect(() => {
    axios.get('/api/teachers/').then(res => setTeachers(res.data))
  }, [])

  return (
    <div style={{padding: 20}}>
      <h1>منصة الدروس الجزائرية</h1>
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 20}}>
        {teachers.map(t => (
          <div key={t.id} style={{border: '1px solid #ddd', padding: 15, borderRadius: 10}}>
            <h3>{t.user?.username}</h3>
            <p>{t.subject} - {t.hourly_rate} دج/ساعة</p>
          </div>
        ))}
      </div>
    </div>
  )
}
export default Dashboard
""",
    
    "frontend/src/pages/PaymentPage.jsx": """import React, { useState } from 'react'
import { useParams } from 'react-router-dom'
import axios from 'axios'

function PaymentPage() {
  const { sessionId } = useParams()
  const [loading, setLoading] = useState(false)

  const handlePayment = async () => {
    setLoading(true)
    try {
      const res = await axios.post(`/api/initiate-payment/${sessionId}/`)
      window.location.href = res.data.payment_url
    } catch (err) {
      alert('حدث خطأ في الدفع')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{textAlign: 'center', padding: 50}}>
      <h1>الدفع عبر شارجيلي</h1>
      <button onClick={handlePayment} disabled={loading} style={{background: '#28a745', color: 'white', padding: '15px 30px', border: 'none', borderRadius: 8}}>
        {loading ? 'جاري التحويل...' : 'ادفع الآن'}
      </button>
    </div>
  )
}
export default PaymentPage
""",
    
    "frontend/src/pages/Room.jsx": """import React from 'react'
import { useParams } from 'react-router-dom'

function Room() {
  const { roomName } = useParams()
  return (
    <div style={{textAlign: 'center', padding: 50}}>
      <h1>غرفة الفيديو: {roomName}</h1>
      <p>سيتم إضافة ميزة الفيديو المباشر قريباً</p>
    </div>
  )
}
export default Room
""",
    
    "frontend/src/components/PaymentButton.jsx": """import React, { useState } from 'react'
import axios from 'axios'

function PaymentButton({ sessionId, amount }) {
  const [loading, setLoading] = useState(false)

  const handlePayment = async () => {
    setLoading(true)
    try {
      const res = await axios.post(`/api/initiate-payment/${sessionId}/`)
      window.location.href = res.data.payment_url
    } catch (err) {
      alert('فشل الدفع')
    } finally {
      setLoading(false)
    }
  }

  return (
    <button onClick={handlePayment} disabled={loading}>
      {loading ? 'جاري...' : `دفع ${amount} دج`}
    </button>
  )
}
export default PaymentButton
"""
}

# إنشاء جميع الملفات
for filepath, content in files.items():
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ تم إنشاء: {filepath}")

print(f"\n🎉 تم إنشاء المشروع بالكامل في مجلد: {os.getcwd()}")
print("📦 الآن يمكنك ضغط المجلد ورفعه إلى Render")
