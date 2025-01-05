import os
import platform
import cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw
from ultralytics import YOLO
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog
from paddleocr import PaddleOCR

# 初始化 PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')  # 支持多语言（根据需要更改 lang 参数）

# 在图片上绘制文字的函数
def text(img, text, xy=(0, 0), color=(0, 0, 0), size=20):
    pil = Image.fromarray(img)
    s = platform.system()
    if s == "Linux":
        font = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', size)
    elif s == "Darwin":
        font = ImageFont.truetype('....', size)
    else:
        font = ImageFont.truetype('simsun.ttc', size)
    ImageDraw.Draw(pil).text(xy, text, font=font, fill=color)
    return np.asarray(pil)

# 加载 YOLO 模型
model = YOLO('C:/Users/user/Documents/GitHub/sa/SA/runs/detect/train2/weights/best2.pt')

# 弹出文件选择对话框
Tk().withdraw()  # 隐藏主窗口
file_path = filedialog.askopenfilename(title="選擇一張照片", filetypes=[("圖片文件", "*.jpg;*.png;*.jpeg")])

if file_path:
    print(f"处理文件: {file_path}")

    # 读取图片并设置为可写
    img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    img = img[:, :, ::-1].copy()  # 转换为 RGB 格式

    # 使用 YOLO 模型进行预测
    results = model.predict(img, save=False)
    boxes = results[0].boxes.xyxy

    detected_texts = []  # 存储检测到的车牌文字

    # 绘制检测框和车牌文字
    for box in boxes:
        x1, y1, x2, y2 = map(int, box[:4])
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # 提取车牌区域并进行 OCR 识别
        plate_img = img[y1:y2, x1:x2]
        if plate_img.size > 0:
            result = ocr.ocr(plate_img, cls=True)  # 使用 PaddleOCR 进行识别
            for line in result[0]:  # 提取识别结果
                license = line[1][0]
                detected_texts.append(license)
                # 在图片上显示车牌文字
                img = text(img, license, (x1, y1 - 20), (0, 255, 0), 25)

    # 显示结果
    plt.figure(figsize=(8, 6))
    plt.imshow(img)
    plt.axis("off")
    plt.title("車牌：")
    plt.show()

    # 输出检测到的车牌文字
    print("車牌：")
    for idx, text in enumerate(detected_texts, 1):
        print(f"{idx}: {text}")
else:
    print("請選擇文件。")
