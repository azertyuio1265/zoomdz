#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
منصة الدروس الخصوصية الجزائرية - ملف واحد فقط
انسخ هذا الملف وارفعه مباشرة إلى Render
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import uuid
import os

app = Flask(__name__)
CORS(app)

# ============================================
# بيانات وهمية (مؤقتة)
# ============================================
teachers = [
    {"id": "1", "name": "أحمد بن علي", "subject": "الرياضيات", "price": 1500, "bio": "أستاذ رياضيات خبرة 10 سنوات", "rating": 4.8},
    {"id": "2", "name": "فاطمة الزهراء", "subject": "الفيزياء", "price": 1200, "bio": "دكتورة في الفيزياء", "rating": 4.9},
    {"id": "3", "name": "محمد الأمين", "subject": "اللغة العربية", "price": 1000, "bio": "أستاذ اللغة العربية", "rating": 4.7},
    {"id": "4", "name": "سارة بن عمر", "subject": "الإنجليزية", "price": 1300, "bio": "متخصصة في اللغة الإنجليزية", "rating": 4.8},
    {"id": "5", "name": "كريم جاب الله", "subject": "العلوم", "price": 1100, "bio": "أستاذ علوم الطبيعة", "rating": 4.6},
]

sessions = {}

# ============================================
# API Routes
# ============================================

@app.route('/api/teachers', methods=['GET'])
def get_teachers():
    return jsonify(teachers)

@app.route('/api/sessions', methods=['POST'])
def create_session():
    data = request.json
    session_id = str(uuid.uuid4())[:8]
    sessions[session_id] = {
        "id": session_id,
        "teacher_id": data.get('teacher_id'),
        "subject": data.get('subject'),
        "price": data.get('price'),
        "status": "pending",
        "created_at": str(uuid.uuid4())
    }
    return jsonify({"session_id": session_id})

@app.route('/api/initiate-payment/<session_id>', methods=['POST'])
def initiate_payment(session_id):
    session = sessions.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    # رابط تجريبي لشارجيلي (يمكن استبداله برابط حقيقي لاحقاً)
    payment_url = f"https://buy.stripe.com/test_{session_id}"
    
    return jsonify({
        "payment_url": payment_url,
        "session_id": session_id,
        "amount": session.get('price', 1000)
    })

# ============================================
# الواجهة الأمامية (HTML/CSS/JS مدمج)
# ============================================

HTML_CODE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة الدروس الخصوصية الجزائرية</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Tahoma', 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        /* الهيدر */
        .header {
            text-align: center;
            color: white;
            padding: 40px 20px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .header .badge {
            background: rgba(255,255,255,0.2);
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            margin-top: 15px;
            font-size: 14px;
        }
        
        /* شبكة الأساتذة */
        .teachers-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 25px;
            padding: 20px;
        }
        
        /* بطاقة الأستاذ */
        .teacher-card {
            background: white;
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s, box-shadow 0.3s;
            cursor: pointer;
        }
        
        .teacher-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }
        
        .teacher-name {
            font-size: 1.4rem;
            color: #333;
            margin-bottom: 5px;
        }
        
        .teacher-subject {
            color: #667eea;
            font-weight: bold;
            margin: 10px 0;
            font-size: 1.1rem;
        }
        
        .teacher-price {
            font-size: 1.8rem;
            color: #28a745;
            font-weight: bold;
            margin: 15px 0;
        }
        
        .teacher-price small {
            font-size: 0.8rem;
            color: #666;
        }
        
        .teacher-bio {
            color: #666;
            margin: 15px 0;
            line-height: 1.5;
        }
        
        .teacher-rating {
            color: #ffc107;
            margin-bottom: 15px;
        }
        
        .btn-book {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 10px;
            cursor: pointer;
            width: 100%;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .btn-book:hover {
            transform: scale(1.02);
            opacity: 0.9;
        }
        
        /* نافذة الدفع المنبثقة */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.6);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        
        .modal-content {
            background: white;
            border-radius: 25px;
            max-width: 450px;
            width: 90%;
            text-align: center;
            animation: fadeIn 0.3s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.9); }
            to { opacity: 1; transform: scale(1); }
        }
        
        .modal-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 25px 25px 0 0;
        }
        
        .modal-header h2 {
            margin: 0;
        }
        
        .modal-body {
            padding: 25px;
        }
        
        .modal-details {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 15px;
            margin: 15px 0;
            text-align: right;
        }
        
        .modal-details p {
            margin: 8px 0;
        }
        
        .payment-methods {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        
        .payment-method {
            background: #f0f0f0;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 12px;
        }
        
        .btn-pay {
            background: #28a745;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 12px;
            cursor: pointer;
            font-size: 18px;
            font-weight: bold;
            width: 100%;
            margin-top: 10px;
            transition: all 0.3s;
        }
        
        .btn-pay:hover {
            background: #218838;
            transform: scale(1.02);
        }
        
        .btn-close {
            background: #ccc;
            color: #333;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            margin-top: 10px;
            width: 100%;
        }
        
        /* مؤشر التحميل */
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .payment-loading {
            display: none;
        }
        
        .note {
            font-size: 11px;
            color: #888;
            margin-top: 15px;
        }
        
        /* الفوتر */
        .footer {
            text-align: center;
            color: white;
            padding: 30px;
            opacity: 0.8;
        }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 1.8rem; }
            .teachers-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 منصة الدروس الخصوصية الجزائرية</h1>
            <p>تعلم مع أفضل الأساتذة - دفع آمن عبر شارجيلي</p>
            <div class="badge">🎓 أكثر من 500 طالب وطالبة</div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>جاري تحميل الأساتذة...</p>
        </div>
        
        <div class="teachers-grid" id="teachersGrid"></div>
        
        <div class="footer">
            <p>© 2024 منصة الدروس الجزائرية | جميع الحقوق محفوظة</p>
        </div>
    </div>
    
    <!-- نافذة الدفع -->
    <div class="modal" id="paymentModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>💳 تأكيد الحجز</h2>
            </div>
            <div class="modal-body">
                <div id="modalDetails"></div>
                <div class="payment-methods">
                    <span class="payment-method">🏦 EDAHABIA</span>
                    <span class="payment-method">💳 CIB</span>
                    <span class="payment-method">📮 CCP</span>
                    <span class="payment-method">📱 Baridimob</span>
                </div>
                <div id="paymentLoading" class="payment-loading">
                    <div class="spinner"></div>
                    <p>جاري التوجيه إلى بوابة الدفع...</p>
                </div>
                <button class="btn-pay" id="payBtn">الدفع الآن</button>
                <button class="btn-close" onclick="closeModal()">إلغاء</button>
                <p class="note">🔒 الدفع مشفر وآمن 100%</p>
            </div>
        </div>
    </div>
    
    <!-- رسالة نجاح -->
    <div class="modal" id="successModal">
        <div class="modal-content">
            <div class="modal-header" style="background: #28a745;">
                <h2>✅ تم الحجز بنجاح!</h2>
            </div>
            <div class="modal-body">
                <p style="font-size: 18px; margin: 20px 0;">سيتم إرسال رابط الحصة إلى بريدك الإلكتروني</p>
                <p style="color: #666;">يمكنك متابعة الحصة من خلال لوحة التحكم</p>
                <button class="btn-close" onclick="closeSuccessModal()" style="background: #28a745; color: white;">حسناً</button>
            </div>
        </div>
    </div>

    <script>
        let currentSessionId = null;
        let currentTeacher = null;
        
        // جلب الأساتذة من API
        async function loadTeachers() {
            document.getElementById('loading').style.display = 'block';
            try {
                const response = await fetch('/api/teachers');
                const teachers = await response.json();
                displayTeachers(teachers);
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('teachersGrid').innerHTML = '<p style="color:white; text-align:center;">⚠️ حدث خطأ في تحميل البيانات</p>';
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        // عرض الأساتذة
        function displayTeachers(teachers) {
            const grid = document.getElementById('teachersGrid');
            grid.innerHTML = teachers.map(teacher => `
                <div class="teacher-card">
                    <div class="teacher-name">👨‍🏫 ${teacher.name}</div>
                    <div class="teacher-subject">📖 ${teacher.subject}</div>
                    <div class="teacher-rating">${'⭐'.repeat(Math.floor(teacher.rating))} ${teacher.rating}</div>
                    <div class="teacher-price">${teacher.price} <small>دج/ساعة</small></div>
                    <div class="teacher-bio">${teacher.bio}</div>
                    <button class="btn-book" onclick="bookSession('${teacher.id}', '${teacher.name}', '${teacher.subject}', ${teacher.price})">
                        🎯 احجز حصة الآن
                    </button>
                </div>
            `).join('');
        }
        
        // حجز حصة
        async function bookSession(teacherId, teacherName, subject, price) {
            currentTeacher = { teacherId, teacherName, subject, price };
            
            try {
                const response = await fetch('/api/sessions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        teacher_id: teacherId,
                        subject: subject,
                        price: price
                    })
                });
                const data = await response.json();
                currentSessionId = data.session_id;
                
                // عرض تفاصيل الحجز
                document.getElementById('modalDetails').innerHTML = `
                    <div class="modal-details">
                        <p><strong>👨‍🏫 الأستاذ:</strong> ${teacherName}</p>
                        <p><strong>📖 المادة:</strong> ${subject}</p>
                        <p><strong>💰 السعر:</strong> ${price} دج</p>
                        <p><strong>⏰ المدة:</strong> 60 دقيقة</p>
                        <p><strong>📅 التاريخ:</strong> ${new Date().toLocaleDateString('ar-DZ')}</p>
                    </div>
                `;
                document.getElementById('paymentModal').style.display = 'flex';
            } catch (error) {
                alert('حدث خطأ في إنشاء الحجز، حاول مرة أخرى');
            }
        }
        
        // معالجة الدفع
        document.getElementById('payBtn').onclick = async () => {
            const payBtn = document.getElementById('payBtn');
            const paymentLoading = document.getElementById('paymentLoading');
            
            payBtn.style.display = 'none';
            paymentLoading.style.display = 'block';
            
            try {
                const response = await fetch(`/api/initiate-payment/${currentSessionId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                const data = await response.json();
                
                if (data.payment_url) {
                    // فتح رابط الدفع
                    window.open(data.payment_url, '_blank');
                    
                    // إغلاق نافذة الدفع وفتح نافذة النجاح
                    setTimeout(() => {
                        document.getElementById('paymentModal').style.display = 'none';
                        document.getElementById('successModal').style.display = 'flex';
                        paymentLoading.style.display = 'none';
                        payBtn.style.display = 'block';
                    }, 2000);
                }
            } catch (error) {
                alert('حدث خطأ في عملية الدفع');
                paymentLoading.style.display = 'none';
                payBtn.style.display = 'block';
            }
        };
        
        function closeModal() {
            document.getElementById('paymentModal').style.display = 'none';
            document.getElementById('paymentLoading').style.display = 'none';
            document.getElementById('payBtn').style.display = 'block';
            currentSessionId = null;
        }
        
        function closeSuccessModal() {
            document.getElementById('successModal').style.display = 'none';
            location.reload();
        }
        
        // تشغيل التطبيق
        loadTeachers();
    </script>
</body>
</html>
'''

@app.route('/')
def serve_index():
    return HTML_CODE

# ============================================
# تشغيل السيرفر
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)