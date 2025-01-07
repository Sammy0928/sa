from flask import Flask, render_template, request, jsonify
import psycopg2
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 設定圖片上傳目錄
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 確保上傳目錄存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 檢查檔案副檔名是否有效
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 配置 PostgreSQL 連接
db = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="1234",  # 這裡填入你的 PostgreSQL 密碼
    database="violations_db"
)

@app.route('/')
def index():
    return render_template('identify.html')

@app.route('/violation', methods=['GET', 'POST'])
def violation():
    if request.method == 'POST':
        # 處理表單資料
        license_plate = request.form.get('license_plate')
        car_type = request.form.get('car')
        violation_reason = request.form.get('violation_reason')
        violation_result = request.form.get('violation')
        reason = request.form.get('reason')

        # 處理圖片上傳
        if 'image' not in request.files:
            return jsonify(success=False, message="No file part")
        
        file = request.files['image']
        if file.filename == '':
            return jsonify(success=False, message="No selected file")
        
        if file and allowed_file(file.filename):
            # 安全儲存檔案
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # 將資料存入資料庫
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO violation_people (license_plate, car_type, violation_reason, violation_result, reason, image_path)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (license_plate, car_type, violation_reason, violation_result, reason, filepath))
            db.commit()
            cursor.close()

            return jsonify(success=True, message="Record saved successfully")
        else:
            return jsonify(success=False, message="Invalid file type")

    return render_template('violation.html')

if __name__ == '__main__':
    app.run(debug=True)
