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
def text(img, text, xy=(0, 0), color=(0, 255, 0), size=20):
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
Tk().withdraw()
file_path = filedialog.askopenfilename(title="選擇一張照片", filetypes=[("圖片文件", "*.jpg;*.png;*.jpeg")])

if file_path:
    print(f"处理文件: {file_path}")

    try:
        # 读取图片
        img = cv2.imread(file_path, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("图片加载失败！请检查路径是否正确或文件是否损坏。")

        # 转换为 RGB 格式并解除只读状态
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.copy()
        img.setflags(write=1)

        # 使用 YOLO 模型进行预测
        results = model.predict(img, save=False)
        boxes = results[0].boxes.xyxy

        # 检查是否检测到车牌
        if boxes is None or len(boxes) == 0:
            print("未检测到任何车牌")
            plt.figure(figsize=(8, 6))
            plt.imshow(img)
            plt.axis("off")
            plt.title("未检测到任何车牌")
            plt.show()
        else:
            detected_texts = []  # 存储检测到的车牌文字

            for box in boxes:
                x1, y1, x2, y2 = map(int, box[:4])
                try:
                    # 绘制检测框
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    # 提取车牌区域并进行 OCR 识别
                    plate_img = img[y1:y2, x1:x2]
                    if plate_img.size > 0:
                        result = ocr.ocr(plate_img, cls=True)
                        for line in result[0]:
                            license = line[1][0]
                            detected_texts.append(license)
                            img = text(img, license, (x1, y1 - 20), (0, 255, 0), 25)
                except Exception as e:
                    print(f"无法绘制检测框或识别车牌: {e}")
                    plt.figure(figsize=(8, 6))
                    plt.imshow(img)
                    plt.axis("off")
                    plt.title("無法辨識")
                    plt.show()
                    break

            if len(detected_texts) == 0:
                print("無法辨識")
                plt.figure(figsize=(8, 6))
                plt.imshow(img)
                plt.axis("off")
                plt.title("無法辨識")
                plt.show()
            elif len(detected_texts) > 1:
                print(f"照片中有 {len(detected_texts)} 張車牌")
                plt.figure(figsize=(8, 6))
                plt.imshow(img)
                plt.axis("off")
                plt.title(f"照片中有 {len(detected_texts)} 張車牌")
                plt.show()
            else:
                plt.figure(figsize=(8, 6))
                plt.imshow(img)
                plt.axis("off")
                plt.title(f"車牌：{detected_texts[0]}")
                plt.show()

                print("車牌：")
                for idx, text in enumerate(detected_texts, 1):
                    print(f"{idx}: {text}")
    except Exception as e:
        print(f"处理图像时出错: {e}")
        plt.figure(figsize=(8, 6))
        plt.axis("off")
        plt.title("無法辨識")
        plt.show()
else:
    print("請選擇文件。")
