import os

PROJECT_DIR = "meet-chargily-render"
os.makedirs(PROJECT_DIR, exist_ok=True)
os.chdir(PROJECT_DIR)

# الملفات والمحتوى بعد الإصلاح
files = {
    # ============= ملفات الإعدادات الرئيسية =============
    ".gitignore": """__pycache__/
*.pyc
.env
db.sqlite3
staticfiles/
node_modules/
dist/
.DS_Store
*.log
*.pid
*.seed
*.pid.lock
""",
    
    ".env.example": """SECRET_KEY=your-secret-key-here-make-it-very-long-and-random
DEBUG=False
CHARGILY_API_KEY=your-chargily-api-key
CHARGILY_SECRET_KEY=your-chargily-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
""",
    
    "README.md": """# منصة الدروس الجزائرية - Meet Chargily

## النشر على Render

1. ارفع الكود إلى GitHub
2. سجل دخولك إلى [Render](https://render.com)
3. اضغط "New +" → "Web Service"
4. اختر الـ repository
5. استخدم الإعدادات التالية:
   - **Runtime**: Python
   - **Build Command**: `./render-build.sh`
   - **Start Command**: `./render-start.sh`
6. أضف PostgreSQL Database
7. أضف المتغيرات البيئية من ملف `.env.example`

## المتغيرات البيئية المطلوبة
- `SECRET_KEY`: مفتاح سري قوي
- `DATABASE_URL`: يتم توفيره تلقائياً من Render
- `CHARGILY_API_KEY`: مفتاح API من Chargily
- `CHARGILY_SECRET_KEY`: المفتاح السري من Chargily
""",
    
    # ============= ملفات البناء والتشغيل =============
    "render-build.sh": """#!/bin/bash
# Render build script

echo "🚀 بدء عملية البناء..."

# تثبيت backend
echo "📦 تثبيت مكتبات Python..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# تجميع الملفات الثابتة
echo "📁 تجميع الملفات الثابتة..."
python manage.py collectstatic --noinput --clear

# تنفيذ الترحيلات
echo "🗄️ تنفيذ ترحيلات قاعدة البيانات..."
python manage.py migrate --noinput

# العودة إلى المجلد الرئيسي
cd ..

# بناء frontend
echo "🎨 بناء واجهة المستخدم..."
cd frontend
npm install
npm run build

echo "✅ اكتمل البناء بنجاح!"
""",
    
    "render-start.sh": """#!/bin/bash
# Render start script

echo "🚀 تشغيل التطبيق..."

# تشغيل الترحيلات (تأكيد)
cd backend
python manage.py migrate --noinput

# تشغيل الخادم
gunicorn meet.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --threads 2 --timeout 120
""",
    
    "docker-compose.yml": """version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: meet_db
      POSTGRES_USER: meet_user
      POSTGRES_PASSWORD: meet_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://meet_user:meet_password@db:5432/meet_db
      DEBUG: "True"
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
""",
    
    # ============= ملفات Backend =============
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
dj-database-url==2.1.0
django-heroku==0.3.1
""",
    
    "backend/Dockerfile": """FROM python:3.11-slim

WORKDIR /app

# تثبيت المتطلبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الملفات
COPY . .

# تجميع الملفات الثابتة
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
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
""",
    
    # ============= مجلد meet الرئيسي =============
    "backend/meet/__init__.py": "",
    
    "backend/meet/settings.py": """import os
import dj_database_url
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# الأمان
SECRET_KEY = config('SECRET_KEY', default='django-insecure-key-for-development-only')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = ['*']  # سيتم تحديثه للإنتاج

# التطبيقات المثبتة
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

# الوسائط
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meet.urls'
WSGI_APPLICATION = 'meet.wsgi.application'

# قاعدة البيانات - دعم PostgreSQL و SQLite
DATABASE_URL = config('DATABASE_URL', default=f'sqlite:///{BASE_DIR}/db.sqlite3')
DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# المصادقة
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# اللغة والوقت
LANGUAGE_CODE = 'ar-dz'
TIME_ZONE = 'Africa/Algiers'
USE_I18N = True
USE_TZ = True

# الملفات الثابتة والوسائط
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CORS
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

# Chargily إعدادات
CHARGILY_API_KEY = config('CHARGILY_API_KEY', default='')
CHARGILY_SECRET_KEY = config('CHARGILY_SECRET_KEY', default='')
CHARGILY_MODE = config('CHARGILY_MODE', default='sandbox')  # sandbox or live

# أمان الإنتاج
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
""",
    
    "backend/meet/urls.py": """from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

def health_check(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'الخادم يعمل بشكل طبيعي'
    })

def api_root(request):
    return JsonResponse({
        'name': 'Meet Chargily API',
        'version': '1.0.0',
        'endpoints': {
            'teachers': '/api/teachers/',
            'sessions': '/api/sessions/',
            'admin': '/admin/',
            'health': '/health/'
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include('bookings.urls')),
    path('health/', health_check, name='health-check'),
]

# خدمة الملفات الثابتة في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
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
    
    # ============= تطبيق bookings =============
    "backend/bookings/__init__.py": "",
    
    "backend/bookings/apps.py": """from django.apps import AppConfig

class BookingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookings'
    verbose_name = 'الحجوزات'
""",
    
    "backend/bookings/admin.py": """from django.contrib import admin
from .models import TeacherProfile, Session, Payment

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'hourly_rate', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'subject']
    search_fields = ['user__username', 'subject']
    list_editable = ['hourly_rate', 'is_verified']

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'teacher', 'student', 'scheduled_time', 'price', 'status']
    list_filter = ['status', 'scheduled_time']
    search_fields = ['subject', 'teacher__user__username']
    readonly_fields = ['room_name']
    date_hierarchy = 'scheduled_time'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['session', 'amount', 'status', 'created_at']
    list_filter = ['status']
    readonly_fields = ['transaction_id']
""",
    
    "backend/bookings/models.py": """from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    subject = models.CharField(max_length=100, verbose_name='المادة')
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='السعر للساعة')
    bio = models.TextField(blank=True, verbose_name='السيرة الذاتية')
    is_verified = models.BooleanField(default=False, verbose_name='موثق')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'أستاذ'
        verbose_name_plural = 'الأساتذة'
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.subject}"

class Session(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('paid', 'تم الدفع'),
        ('in_progress', 'قيد التنفيذ'),
        ('completed', 'مكتملة'),
        ('cancelled', 'ملغية'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='sessions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='student_sessions')
    subject = models.CharField(max_length=100, verbose_name='المادة')
    scheduled_time = models.DateTimeField(verbose_name='الموعد')
    duration_minutes = models.IntegerField(default=60, verbose_name='المدة (دقائق)')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='السعر')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    room_name = models.CharField(max_length=255, unique=True, blank=True, verbose_name='اسم الغرفة')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'حصة'
        verbose_name_plural = 'الحصص'
        ordering = ['-scheduled_time']
    
    def save(self, *args, **kwargs):
        if not self.room_name:
            self.room_name = f"room_{uuid.uuid4().hex[:12]}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.subject} - {self.scheduled_time}"

class Payment(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='المبلغ')
    transaction_id = models.CharField(max_length=255, unique=True, verbose_name='رقم العملية')
    status = models.CharField(max_length=50, default='pending', verbose_name='الحالة')
    payment_url = models.URLField(blank=True, verbose_name='رابط الدفع')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'دفع'
        verbose_name_plural = 'المدفوعات'
    
    def __str__(self):
        return f"دفع {self.amount} - {self.session.subject}"
""",
    
    "backend/bookings/serializers.py": """from rest_framework import serializers
from django.contrib.auth.models import User
from .models import TeacherProfile, Session, Payment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class TeacherProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = TeacherProfile
        fields = '__all__'

class SessionSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.username', read_only=True)
    student_name = serializers.CharField(source='student.username', read_only=True, allow_null=True)
    
    class Meta:
        model = Session
        fields = '__all__'
        read_only_fields = ['id', 'room_name', 'created_at']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['transaction_id', 'created_at']
""",
    
    "backend/bookings/urls.py": """from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'teachers', views.TeacherProfileViewSet)
router.register(r'sessions', views.SessionViewSet)
router.register(r'payments', views.PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('initiate-payment/<uuid:session_id>/', views.initiate_payment, name='initiate-payment'),
    path('chargily-webhook/', views.chargily_webhook, name='chargily-webhook'),
    path('teachers/<int:pk>/sessions/', views.teacher_sessions, name='teacher-sessions'),
]
""",
    
    "backend/bookings/views.py": """from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import TeacherProfile, Session, Payment
from .serializers import TeacherProfileSerializer, SessionSerializer, PaymentSerializer
import uuid
import json

class TeacherProfileViewSet(viewsets.ModelViewSet):
    queryset = TeacherProfile.objects.all()
    serializer_class = TeacherProfileSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()
    
    @action(detail=True, methods=['get'])
    def available_sessions(self, request, pk=None):
        teacher = self.get_object()
        sessions = Session.objects.filter(teacher=teacher, status='pending')
        serializer = SessionSerializer(sessions, many=True)
        return Response(serializer.data)

class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    
    def get_queryset(self):
        queryset = Session.objects.all()
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save()

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

@api_view(['POST'])
def initiate_payment(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    
    # إنشاء سجل دفع جديد
    payment = Payment.objects.create(
        session=session,
        amount=session.price,
        transaction_id=f"TXN_{uuid.uuid4().hex[:12].upper()}",
        status='pending'
    )
    
    # رابط الدفع التجريبي (سيتم استبداله برابط Chargily الحقيقي)
    payment_url = f"https://sandbox.chargily.dz/pay/test?amount={session.price}&session_id={session.id}"
    payment.payment_url = payment_url
    payment.save()
    
    return Response({
        'payment_url': payment_url,
        'transaction_id': payment.transaction_id,
        'session_id': str(session.id),
        'amount': str(session.price)
    })

@api_view(['POST'])
def chargily_webhook(request):
    """معالج إشعارات Chargily"""
    try:
        data = json.loads(request.body)
        transaction_id = data.get('transaction_id')
        status = data.get('status')
        
        if transaction_id and status == 'paid':
            payment = get_object_or_404(Payment, transaction_id=transaction_id)
            payment.status = 'completed'
            payment.save()
            
            # تحديث حالة الحصة
            session = payment.session
            session.status = 'paid'
            session.save()
            
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        
        return Response({'status': 'ignored'}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def teacher_sessions(request, pk):
    teacher = get_object_or_404(TeacherProfile, pk=pk)
    sessions = Session.objects.filter(teacher=teacher)
    serializer = SessionSerializer(sessions, many=True)
    return Response(serializer.data)
""",
    
    "backend/bookings/utils.py": """import hashlib
import hmac
import json
from django.conf import settings

def verify_chargily_signature(payload, signature):
    """التحقق من توقيع Chargily"""
    secret = settings.CHARGILY_SECRET_KEY
    if not secret:
        return False
    
    expected = hmac.new(
        secret.encode(),
        json.dumps(payload).encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)

def calculate_session_price(hourly_rate, duration_minutes):
    """حساب سعر الحصة بناءً على السعر للساعة والمدة"""
    return (hourly_rate * duration_minutes) / 60
""",
    
    # ============= Frontend =============
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
CMD ["nginx", "-g", "daemon off;"]
""",
    
    "frontend/nginx.conf": """server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /admin/ {
        proxy_pass http://backend:8000;
    }
}
""",
    
    "frontend/vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/admin': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
""",
    
    "frontend/index.html": """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة الدروس الجزائرية | تعلم مع أفضل الأساتذة</title>
    <meta name="description" content="منصة متخصصة في الدروس الخصوصية في الجزائر">
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
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
    
    "frontend/src/index.css": """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Tahoma', 'Segoe UI', Arial, sans-serif;
  direction: rtl;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

#root {
  min-height: 100vh;
}

/* تخصيص شريط التمرير */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* تحسينات للعربية */
[dir="rtl"] {
  text-align: right;
}

button {
  cursor: pointer;
  transition: all 0.3s ease;
}

button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}
""",
    
    "frontend/src/App.jsx": """import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import PaymentPage from './pages/PaymentPage'
import Room from './pages/Room'
import TeacherProfile from './pages/TeacherProfile'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/payment/:sessionId" element={<PaymentPage />} />
        <Route path="/room/:roomName" element={<Room />} />
        <Route path="/teacher/:id" element={<TeacherProfile />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
""",
    
    "frontend/src/pages/Dashboard.jsx": """import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Link } from 'react-router-dom'

function Dashboard() {
  const [teachers, setTeachers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchTeachers()
  }, [])

  const fetchTeachers = async () => {
    try {
      const response = await axios.get('/api/teachers/')
      setTeachers(response.data)
      setLoading(false)
    } catch (err) {
      setError('حدث خطأ في تحميل البيانات')
      setLoading(false)
      console.error(err)
    }
  }

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <div style={styles.spinner}></div>
        <p>جاري التحميل...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div style={styles.errorContainer}>
        <h2>⚠️ {error}</h2>
        <button onClick={fetchTeachers} style={styles.retryButton}>محاولة مرة أخرى</button>
      </div>
    )
  }

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1>📚 منصة الدروس الجزائرية</h1>
        <p>تعلم مع أفضل الأساتذة في الجزائر</p>
      </header>

      <div style={styles.grid}>
        {teachers.map(teacher => (
          <Link to={`/teacher/${teacher.id}`} key={teacher.id} style={{ textDecoration: 'none' }}>
            <div style={styles.card}>
              <div style={styles.cardHeader}>
                <div style={styles.avatar}>
                  {teacher.user?.username?.[0]?.toUpperCase() || 'أ'}
                </div>
                <h3>{teacher.user?.username || 'أستاذ'}</h3>
              </div>
              <div style={styles.cardBody}>
                <p><strong>📖 المادة:</strong> {teacher.subject}</p>
                <p><strong>💰 السعر:</strong> {teacher.hourly_rate} دج/ساعة</p>
                {teacher.bio && <p><strong>📝 نبذة:</strong> {teacher.bio.substring(0, 100)}...</p>}
                {teacher.is_verified && <span style={styles.verifiedBadge}>✓ موثق</span>}
              </div>
              <button style={styles.bookButton}>احجز حصة الآن</button>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}

const styles = {
  container: {
    padding: '20px',
    maxWidth: '1200px',
    margin: '0 auto'
  },
  header: {
    textAlign: 'center',
    color: 'white',
    marginBottom: '40px',
    padding: '20px'
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: '25px'
  },
  card: {
    background: 'white',
    borderRadius: '12px',
    padding: '20px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
    transition: 'transform 0.3s ease, box-shadow 0.3s ease',
    cursor: 'pointer'
  },
  cardHeader: {
    textAlign: 'center',
    marginBottom: '15px'
  },
  avatar: {
    width: '80px',
    height: '80px',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '0 auto 10px',
    color: 'white',
    fontSize: '32px',
    fontWeight: 'bold'
  },
  cardBody: {
    marginBottom: '15px'
  },
  verifiedBadge: {
    display: 'inline-block',
    background: '#28a745',
    color: 'white',
    padding: '3px 8px',
    borderRadius: '5px',
    fontSize: '12px',
    marginTop: '10px'
  },
  bookButton: {
    width: '100%',
    padding: '10px',
    background: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '16px',
    cursor: 'pointer',
    transition: 'background 0.3s ease'
  },
  loadingContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    color: 'white'
  },
  spinner: {
    width: '50px',
    height: '50px',
    border: '5px solid rgba(255,255,255,0.3)',
    borderRadius: '50%',
    borderTopColor: 'white',
    animation: 'spin 1s ease-in-out infinite'
  },
  errorContainer: {
    textAlign: 'center',
    padding: '50px',
    color: 'white'
  },
  retryButton: {
    padding: '10px 20px',
    background: '#28a745',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    marginTop: '20px'
  }
}

export default Dashboard
""",
    
    "frontend/src/pages/PaymentPage.jsx": """import React, { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'

function PaymentPage() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [paymentInfo, setPaymentInfo] = useState(null)

  const handlePayment = async () => {
    setLoading(true)
    try {
      const response = await axios.post(`/api/initiate-payment/${sessionId}/`)
      setPaymentInfo(response.data)
      // فتح رابط الدفع في نافذة جديدة
      window.open(response.data.payment_url, '_blank')
    } catch (err) {
      alert('حدث خطأ في عملية الدفع. يرجى المحاولة مرة أخرى.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1>💰 الدفع عبر شارجيلي</h1>
        <p>سيتم توجيهك إلى بوابة الدفع الآمنة</p>
        
        {paymentInfo && (
          <div style={styles.info}>
            <p><strong>رقم العملية:</strong> {paymentInfo.transaction_id}</p>
            <p><strong>المبلغ:</strong> {paymentInfo.amount} دج</p>
          </div>
        )}
        
        <button 
          onClick={handlePayment} 
          disabled={loading}
          style={styles.payButton}
        >
          {loading ? 'جاري التحويل...' : 'ادفع الآن'}
        </button>
        
        <button 
          onClick={() => navigate('/')}
          style={styles.backButton}
        >
          العودة للرئيسية
        </button>
      </div>
    </div>
  )
}

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    padding: '20px'
  },
  card: {
    background: 'white',
    borderRadius: '12px',
    padding: '40px',
    textAlign: 'center',
    maxWidth: '500px',
    width: '100%',
    boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
  },
  payButton: {
    background: '#28a745',
    color: 'white',
    padding: '15px 30px',
    border: 'none',
    borderRadius: '8px',
    fontSize: '18px',
    cursor: 'pointer',
    margin: '20px 10px'
  },
  backButton: {
    background: '#6c757d',
    color: 'white',
    padding: '15px 30px',
    border: 'none',
    borderRadius: '8px',
    fontSize: '18px',
    cursor: 'pointer',
    margin: '20px 10px'
  },
  info: {
    background: '#f8f9fa',
    padding: '15px',
    borderRadius: '8px',
    margin: '20px 0'
  }
}

export default PaymentPage
""",
    
    "frontend/src/pages/Room.jsx": """import React, { useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'

function Room() {
  const { roomName } = useParams()
  const navigate = useNavigate()
  const videoRef = useRef(null)

  useEffect(() => {
    // هنا سيتم إضافة WebRTC أو Jitsi Meet
    console.log(`دخول إلى الغرفة: ${roomName}`)
  }, [roomName])

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1>🎥 غرفة الفيديو: {roomName}</h1>
        <button onClick={() => navigate('/')} style={styles.exitButton}>
          خروج
        </button>
      </div>
      
      <div style={styles.videoContainer}>
        <div style={styles.localVideo}>
          <video ref={videoRef} autoPlay muted style={styles.video} />
          <p>أنت</p>
        </div>
        <div style={styles.remoteVideo}>
          <p>سيتم إضافة فيديو الأستاذ هنا</p>
        </div>
      </div>
      
      <div style={styles.controls}>
        <button style={styles.controlButton}>🎤 كتم الصوت</button>
        <button style={styles.controlButton}>📹 إيقاف الكاميرا</button>
        <button style={styles.controlButton}>📝 مشاركة الشاشة</button>
      </div>
      
      <div style={styles.info}>
        <p>⚠️ ميزة الفيديو المباشر قيد التطوير وسيتم إضافتها قريباً</p>
        <p>يمكنك حالياً استخدام الرابط للتواصل مع الأستاذ عبر منصة أخرى</p>
      </div>
    </div>
  )
}

const styles = {
  container: {
    padding: '20px',
    background: '#1a1a2e',
    minHeight: '100vh',
    color: 'white'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '30px'
  },
  exitButton: {
    padding: '10px 20px',
    background: '#dc3545',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer'
  },
  videoContainer: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '20px',
    marginBottom: '20px'
  },
  localVideo: {
    background: '#16213e',
    borderRadius: '10px',
    padding: '10px',
    textAlign: 'center'
  },
  remoteVideo: {
    background: '#16213e',
    borderRadius: '10px',
    padding: '10px',
    textAlign: 'center',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '400px'
  },
  video: {
    width: '100%',
    borderRadius: '8px',
    background: '#0f3460'
  },
  controls: {
    display: 'flex',
    justifyContent: 'center',
    gap: '20px',
    marginBottom: '30px'
  },
  controlButton: {
    padding: '10px 20px',
    background: '#e94560',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer'
  },
  info: {
    textAlign: 'center',
    padding: '20px',
    background: '#16213e',
    borderRadius: '10px',
    marginTop: '20px'
  }
}

export default Room
""",
    
    "frontend/src/pages/TeacherProfile.jsx": """import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'

function TeacherProfile() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [teacher, setTeacher] = useState(null)
  const [loading, setLoading] = useState(true)
  const [bookingData, setBookingData] = useState({
    subject: '',
    scheduled_time: '',
    duration_minutes: 60
  })

  useEffect(() => {
    fetchTeacher()
  }, [id])

  const fetchTeacher = async () => {
    try {
      const response = await axios.get(`/api/teachers/${id}/`)
      setTeacher(response.data)
      setBookingData(prev => ({ ...prev, subject: response.data.subject }))
      setLoading(false)
    } catch (err) {
      console.error(err)
      setLoading(false)
    }
  }

  const handleBooking = async (e) => {
    e.preventDefault()
    try {
      const sessionData = {
        ...bookingData,
        teacher: parseInt(id),
        price: (teacher.hourly_rate * bookingData.duration_minutes) / 60
      }
      const response = await axios.post('/api/sessions/', sessionData)
      navigate(`/payment/${response.data.id}`)
    } catch (err) {
      alert('حدث خطأ في حجز الحصة')
      console.error(err)
    }
  }

  if (loading) return <div style={styles.loading}>جاري التحميل...</div>
  if (!teacher) return <div style={styles.error}>لم يتم العثور على الأستاذ</div>

  return (
    <div style={styles.container}>
      <div style={styles.profileCard}>
        <div style={styles.avatar}>
          {teacher.user?.username?.[0]?.toUpperCase() || 'أ'}
        </div>
        <h1>{teacher.user?.username || 'أستاذ'}</h1>
        {teacher.is_verified && <span style={styles.verified}>✓ موثق</span>}
        
        <div style={styles.info}>
          <p><strong>📖 المادة:</strong> {teacher.subject}</p>
          <p><strong>💰 السعر:</strong> {teacher.hourly_rate} دج/ساعة</p>
          <p><strong>📝 نبذة:</strong> {teacher.bio || 'لا توجد نبذة'}</p>
        </div>
        
        <form onSubmit={handleBooking} style={styles.form}>
          <h2>احجز حصة الآن</h2>
          
          <div style={styles.formGroup}>
            <label>المادة:</label>
            <input
              type="text"
              value={bookingData.subject}
              onChange={(e) => setBookingData({...bookingData, subject: e.target.value})}
              required
              style={styles.input}
            />
          </div>
          
          <div style={styles.formGroup}>
            <label>الموعد:</label>
            <input
              type="datetime-local"
              value={bookingData.scheduled_time}
              onChange={(e) => setBookingData({...bookingData, scheduled_time: e.target.value})}
              required
              style={styles.input}
            />
          </div>
          
          <div style={styles.formGroup}>
            <label>المدة (دقائق):</label>
            <select
              value={bookingData.duration_minutes}
              onChange={(e) => setBookingData({...bookingData, duration_minutes: parseInt(e.target.value)})}
              style={styles.input}
            >
              <option value="30">30 دقيقة</option>
              <option value="60">60 دقيقة</option>
              <option value="90">90 دقيقة</option>
              <option value="120">120 دقيقة</option>
            </select>
          </div>
          
          <div style={styles.pricePreview}>
            السعر المتوقع: {(teacher.hourly_rate * bookingData.duration_minutes / 60).toFixed(2)} دج
          </div>
          
          <button type="submit" style={styles.bookButton}>
            تأكيد الحجز والدفع
          </button>
        </form>
        
        <button onClick={() => navigate('/')} style={styles.backButton}>
          العودة للرئيسية
        </button>
      </div>
    </div>
  )
}

const styles = {
  container: {
    padding: '20px',
    maxWidth: '800px',
    margin: '0 auto'
  },
  profileCard: {
    background: 'white',
    borderRadius: '12px',
    padding: '30px',
    textAlign: 'center',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
  },
  avatar: {
    width: '100px',
    height: '100px',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '0 auto 20px',
    color: 'white',
    fontSize: '40px',
    fontWeight: 'bold'
  },
  verified: {
    display: 'inline-block',
    background: '#28a745',
    color: 'white',
    padding: '3px 10px',
    borderRadius: '5px',
    fontSize: '14px',
    marginLeft: '10px'
  },
  info: {
    textAlign: 'right',
    margin: '20px 0',
    padding: '15px',
    background: '#f8f9fa',
    borderRadius: '8px'
  },
  form: {
    marginTop: '30px',
    textAlign: 'right'
  },
  formGroup: {
    marginBottom: '15px'
  },
  input: {
    width: '100%',
    padding: '10px',
    border: '1px solid #ddd',
    borderRadius: '5px',
    fontSize: '16px'
  },
  pricePreview: {
    padding: '10px',
    background: '#e7f3ff',
    borderRadius: '5px',
    margin: '15px 0',
    textAlign: 'center',
    fontSize: '18px',
    color: '#0066cc'
  },
  bookButton: {
    width: '100%',
    padding: '12px',
    background: '#28a745',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    fontSize: '18px',
    cursor: 'pointer',
    marginTop: '10px'
  },
  backButton: {
    width: '100%',
    padding: '10px',
    background: '#6c757d',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    marginTop: '10px'
  },
  loading: {
    textAlign: 'center',
    padding: '50px',
    fontSize: '18px'
  },
  error: {
    textAlign: 'center',
    padding: '50px',
    fontSize: '18px',
    color: 'red'
  }
}

export default TeacherProfile
""",
    
    "frontend/src/components/PaymentButton.jsx": """import React, { useState } from 'react'
import axios from 'axios'

function PaymentButton({ sessionId, amount, onSuccess }) {
  const [loading, setLoading] = useState(false)

  const handlePayment = async () => {
    setLoading(true)
    try {
      const response = await axios.post(`/api/initiate-payment/${sessionId}/`)
      window.open(response.data.payment_url, '_blank')
      if (onSuccess) onSuccess()
    } catch (err) {
      alert('فشل في عملية الدفع. يرجى المحاولة مرة أخرى.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <button 
      onClick={handlePayment} 
      disabled={loading}
      style={{
        background: '#28a745',
        color: 'white',
        padding: '10px 20px',
        border: 'none',
        borderRadius: '5px',
        cursor: loading ? 'not-allowed' : 'pointer',
        opacity: loading ? 0.7 : 1
      }}
    >
      {loading ? 'جاري...' : `دفع ${amount} دج`}
    </button>
  )
}

export default PaymentButton
"""
}

# إنشاء جميع الملفات
print("🚀 جاري إنشاء مشروع Meet Chargily...")
print("=" * 50)

for filepath, content in files.items():
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ تم إنشاء: {filepath}")

# جعل ملفات shell قابلة للتنفيذ
os.chmod("render-build.sh", 0o755)
os.chmod("render-start.sh", 0o755)

print("\n" + "=" * 50)
print("🎉 تم إنشاء المشروع بالكامل بنجاح!")
print(f"📁 موقع المشروع: {os.getcwd()}")
print("\n" + "=" * 50)
print("📋 خطوات النشر على Render:")
print("=" * 50)
print("""
1. رفع المشروع إلى GitHub:
   -------------------------
   cd meet-chargily-render
   git init
   git add .
   git commit -m "Initial commit with Render support"
   git branch -M main
   git remote add origin https://github.com/اسم-المستخدم/meet-chargily-render.git
   git push -u origin main

2. إنشاء حساب على Render.com:
   -------------------------
   - سجل دخولك باستخدام GitHub

3. إضافة قاعدة البيانات:
   --------------------
   - اضغط "New +" → "PostgreSQL"
   - Name: meet-db
   - Database: meet_db
   - User: meet_user
   - اضغط "Create Database"
   - انسخ DATABASE_URL (سيظهر بعد الإنشاء)

4. نشر التطبيق:
   ------------
   - اضغط "New +" → "Web Service"
   - اختر repository "meet-chargily-render"
   - Name: meet-backend
   - Runtime: Python
   - Build Command: ./render-build.sh
   - Start Command: ./render-start.sh
  
5. إضافة المتغيرات البيئية:
   ------------------------
   - اذهب إلى Dashboard التطبيق
   - اضغط "Environment"
   - أضف:
     * DATABASE_URL = (انسخ من قاعدة البيانات)
     * SECRET_KEY = (أنشئ مفتاحاً عشوائياً)
     * DEBUG = False
     * CHARGILY_API_KEY = (مفتاح Chargily)
     * CHARGILY_SECRET_KEY = (المفتاح السري)

6. انتظر اكتمال البناء:
   --------------------
   - سيتم تثبيت المتطلبات تلقائياً
   - سيتم بناء واجهة المستخدم
   - ستظهر رسالة "Live" عند النجاح

7. اختبار التطبيق:
   ---------------
   - افتح الرابط: https://meet-backend.onrender.com
   - جرب إنشاء أستاذ عبر /admin
   - اختبر حجز الحصص والدفع

🔧 ملاحظات مهمة:
- تأكد من أن المتغيرات البيئية صحيحة
- انتظر 2-3 دقائق للبناء الأول
- استخدم الساندبوكس لاختبار Chargily أولاً
- يمكنك مراقبة السجلات في Logs tab

📞 الدعم:
- مشكلة في البناء؟ راجع Logs
- مشكلة في قاعدة البيانات؟ تأكد من DATABASE_URL
- مشكلة في Chargily؟ تحقق من API keys

مبروك! 🎉 مشروعك جاهز للنشر على Render
""")

# إنشاء ملف إرشادي إضافي
with open("HOW_TO_DEPLOY.md", "w", encoding='utf-8') as f:
    f.write("""# دليل نشر مشروع Meet Chargily على Render

## المتطلبات المسبقة
1. حساب على [GitHub](https://github.com)
2. حساب على [Render](https://render.com)
3. حساب على [Chargily](https://chargily.dz) (للدفع)

## خطوات سريعة

### 1. رفع الكود إلى GitHub
```bash
git init
git add .
git commit -m "Deploy to Render"
git remote add origin https://github.com/USERNAME/REPO-NAME.git
git push -u origin main
