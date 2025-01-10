import os
import threading
from flask import Flask, render_template, request, jsonify
import webbrowser
import cv2
import numpy as np
import psycopg2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from ultralytics import YOLO
from paddleocr import PaddleOCR
from psycopg2.extras import RealDictCursor
from identify import identify_bp  # 引入 identify.py 的藍圖
from violation import violation_bp  # 引入 violation.py 的藍圖
from invoice import invoice_bp  # 引入 invoice.py 的藍圖
from car_data import car_data_bp  # 引入 car_data.py 的藍圖
from index import index_bp  # 引入 index.py 的藍圖
app = Flask(__name__)

# 註冊 identify.py 的藍圖
app.register_blueprint(identify_bp, url_prefix='/identify')

# 註冊 violation.py 的藍圖
app.register_blueprint(violation_bp, url_prefix='/violation')

app.register_blueprint(invoice_bp, url_prefix='/invoice')

app.register_blueprint(car_data_bp, url_prefix='/car_data')

app.register_blueprint(index_bp, url_prefix='/index')
# 初始化 YOLO 模型和 PaddleOCR
model = YOLO('C:/Users/user/Documents/GitHub/sa/SA/runs/detect/train2/weights/best2.pt')
ocr = PaddleOCR(use_angle_cls=True, lang='en')

DB_CONFIG = {
    "host": "localhost",
    "user": "postgres",
    "password": "1234",  # 替换为你的 PostgreSQL 密码
    "database": "violations_db"
}

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"数据库连接错误: {e}")
        return None

# 自动打开浏览器
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

@app.route('/')
def login():
    """登录页面"""
    return render_template('login.html')

@app.route('/homepage')
def homepage():
    """主页"""
    return render_template('homepage.html')

@app.route('/license')
def upload():
    """上传页面"""
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    """處理上傳的圖片並進行車牌辨識"""
    if 'image' not in request.files:
        return jsonify({'error': '未上傳任何文件'}), 400

    file = request.files['image']
    try:
        # 讀取圖片
        img_array = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # 使用 YOLO 模型檢測
        results = model.predict(img, save=False)
        boxes = results[0].boxes.xyxy

        if boxes is None or len(boxes) == 0:
            # 未檢測到任何車牌
            return jsonify({'plate': None, 'message': '未檢測到車牌'})

        if len(boxes) > 1:
            # 檢測到多個車牌
            return jsonify({'plate': None, 'message': '有多張車牌，轉人工'})

        # 只檢測到一個車牌時進行 OCR 辨識
        x1, y1, x2, y2 = map(int, boxes[0][:4])
        plate_img = img[y1:y2, x1:x2]
        detected_texts = []

        if plate_img.size > 0:
            result = ocr.ocr(plate_img, cls=True)
            for line in result[0]:
                license = line[1][0]
                detected_texts.append(license)

        return jsonify({'plate': detected_texts[0] if detected_texts else None})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_vehicle_data', methods=['POST'])
def get_vehicle_data():
    """通过车牌号查询数据库获取车主和违章信息"""
    data = request.get_json()
    license_plate = data.get('plate')
    if not license_plate:
        return jsonify({'error': 'License plate not provided'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Failed to connect to the database'}), 500

    cursor = None  # 初始化 cursor 为 None
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM vehicle_owner_info WHERE license_plate = %s", (license_plate,))
        person_data = cursor.fetchone()

        cursor.execute("SELECT * FROM violation_records WHERE license_plate = %s", (license_plate,))
        violation_data = cursor.fetchall()

        return jsonify({
            'person_data': person_data,
            'violation_data': violation_data
        })
    except Exception as e:
        print(f"数据库查询错误: {e}")
        return jsonify({'error': 'Failed to retrieve data'}), 500
    finally:
        if cursor:  # 仅在 cursor 存在时关闭
            cursor.close()
        conn.close()


if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        threading.Timer(0.1, open_browser).start()
    app.run(debug=True)


