from flask import Blueprint, request, render_template, jsonify
import os
import psycopg2

# 創建藍圖
violation_bp = Blueprint('violation', __name__, template_folder='templates')

# 配置 PostgreSQL 連接
db = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="1234",  # 替換為你的 PostgreSQL 密碼
    database="violations_db"
)

# 違規記錄表單頁面
@violation_bp.route('/')
def index():
    return render_template('violation.html')

# 處理表單提交
@violation_bp.route('/save_record', methods=['POST'])
def save_record():
    try:
        # 提取表單數據
        vehicle_number = request.form.get('vehicle_number')
        owner_name = request.form.get('owner_name')
        date = request.form.get('date')
        location = request.form.get('location')
        description = request.form.get('description')
        fine_amount = request.form.get('fine_amount')

        # 處理文件上傳
        photo = request.files.get('photo')
        photo_path = None
        if photo and photo.filename != '':
            upload_folder = 'static/uploads'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            photo_path = os.path.join(upload_folder, photo.filename)
            photo.save(photo_path)

        # 驗證必填字段
        if not vehicle_number or not owner_name or not date or not fine_amount:
            return jsonify({'success': False, 'error': '缺少必填字段'}), 400

        # 插入數據到資料庫
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO violation_records (license_plate, owner_name, date, location, description, fine_amount, photo_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (vehicle_number, owner_name, date, location, description, fine_amount, photo_path))
        db.commit()
        cursor.close()

        return jsonify({'success': True, 'message': '資料成功插入！'})

    except Exception as e:
        print(f"Error saving record: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500 