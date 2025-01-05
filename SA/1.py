import os
import platform
import pylab as plt
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageFont, ImageDraw
from ultralytics import YOLO

# 设置 Tesseract 可执行文件路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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

model = YOLO('./runs/detect/train2/weights/best.pt')
path = "./valid/images"
plt.figure(figsize=(12, 9))

for i, file in enumerate(os.listdir(path)[0:6]):
    full = os.path.join(path, file)
    print(full)
    img = cv2.imdecode(np.fromfile(full, dtype=np.uint8), cv2.IMREAD_COLOR)
    img = img[:, :, ::-1].copy()

    results = model.predict(img, save=False)
    boxes = results[0].boxes.xyxy
    for box in boxes:
        x1 = int(box[0])
        y1 = int(box[1])
        x2 = int(box[2])
        y2 = int(box[3])
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        tmp = cv2.cvtColor(img[y1:y2, x1:x2].copy(), cv2.COLOR_RGB2GRAY)
        license = pytesseract.image_to_string(tmp, lang='eng', config='--psm 11')
        img = text(img, license, (x1, y1 - 20), (0, 255, 0), 25)
        print(f"偵測到的車牌文字：{license}")
    plt.subplot(2, 3, i + 1)
    plt.axis("off")
    plt.imshow(img)
plt.savefig("yolov8_car.jpg")
plt.show()
