from flask import Flask, render_template, request, jsonify
import webbrowser
import threading
import cv2
import numpy as np
from ultralytics import YOLO
from paddleocr import PaddleOCR

app = Flask(__name__)

# 初始化 YOLO 模型和 PaddleOCR
model = YOLO('C:/Users/user/Documents/GitHub/sa/SA/runs/detect/train2/weights/best2.pt')
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# 自动打开浏览器
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

# 首页路由（登录页面）
@app.route('/')
def login():
    return render_template('login.html')

# 上传页面路由
@app.route('/license')
def upload():
    return render_template('index.html')

# 图片处理的 API
@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': '未上传任何文件'}), 400

    file = request.files['image']
    try:
        # 将文件读取为图片
        img_array = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # 使用 YOLO 模型进行预测
        results = model.predict(img, save=False)
        boxes = results[0].boxes.xyxy

        detected_texts = []  # 存储检测到的车牌文字

        if boxes is None or len(boxes) == 0:
            return jsonify({'plate': None})

        for box in boxes:
            x1, y1, x2, y2 = map(int, box[:4])
            plate_img = img[y1:y2, x1:x2]

            if plate_img.size > 0:
                result = ocr.ocr(plate_img, cls=True)
                for line in result[0]:
                    license = line[1][0]
                    detected_texts.append(license)

        return jsonify({'plate': detected_texts[0] if detected_texts else None})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    threading.Timer(1, open_browser).start()  # 延迟 1 秒打开浏览器
    app.run(debug=True)
