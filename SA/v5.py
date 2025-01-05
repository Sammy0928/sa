# -*- coding: utf-8 -*-
import os
import shutil
import cv2
import torch
import numpy as np
from glob import glob
from random import shuffle
from xml.dom.minidom import parse
from paddleocr import PaddleOCR

# 設定資料夾路徑
base_path = "C:/Users/huang/OneDrive/桌面/SA/plate_train_data"
annotations_path = "C:/Users/huang/OneDrive/桌面/SA/CarLicensePlateDetection/annotations"
images_path = "C:/Users/huang/OneDrive/桌面/SA/CarLicensePlateDetection/images"

# 創建必要的資料夾
os.makedirs(f"{base_path}/images/train", exist_ok=True)
os.makedirs(f"{base_path}/images/val", exist_ok=True)
os.makedirs(f"{base_path}/labels/train", exist_ok=True)
os.makedirs(f"{base_path}/labels/val", exist_ok=True)

# 車牌類別
classes = {"licence": 0}

# 處理 XML 註解檔案並轉為 YOLO 格式
for annotation_file in os.listdir(annotations_path):
    dom = parse(os.path.join(annotations_path, annotation_file))
    root = dom.documentElement
    filename = root.getElementsByTagName("filename")[0].childNodes[0].data.replace(".png", ".txt")
    image_width = int(root.getElementsByTagName("width")[0].childNodes[0].data)
    image_height = int(root.getElementsByTagName("height")[0].childNodes[0].data)

    with open(f"{base_path}/labels/train/{filename}", "w") as r:
        for item in root.getElementsByTagName("object"):
            name = item.getElementsByTagName("name")[0].childNodes[0].data
            xmin = int(item.getElementsByTagName("xmin")[0].childNodes[0].data)
            ymin = int(item.getElementsByTagName("ymin")[0].childNodes[0].data)
            xmax = int(item.getElementsByTagName("xmax")[0].childNodes[0].data)
            ymax = int(item.getElementsByTagName("ymax")[0].childNodes[0].data)

            x_center_norm = ((xmin + xmax) / 2) / image_width
            y_center_norm = ((ymin + ymax) / 2) / image_height
            width_norm = (xmax - xmin) / image_width
            height_norm = (ymax - ymin) / image_height

            r.write(f"{classes[name]} {x_center_norm} {y_center_norm} {width_norm} {height_norm}\n")

# 複製影像到資料夾
for image_file in os.listdir(images_path):
    shutil.copy(os.path.join(images_path, image_file), f"{base_path}/images/train/{image_file}")

# 隨機分配部分影像到驗證資料夾
files = glob(f"{base_path}/images/train/*.png")
shuffle(files)
val_split = 120

txt_train_path = f"{base_path}/labels/train/"
img_train_path = f"{base_path}/images/train/"
txt_val_path = f"{base_path}/labels/val/"
img_val_path = f"{base_path}/images/val/"

for file in files[:val_split]:
    filename = os.path.basename(file)
    shutil.move(f"{txt_train_path}{filename.replace('.png', '.txt')}", f"{txt_val_path}{filename.replace('.png', '.txt')}")
    shutil.move(file, f"{img_val_path}{filename}")

# 建立 YOLO 格式的配置檔案
with open(f"{base_path}/licence.yaml", "w") as yaml_file:
    yaml_file.write(f"train: {base_path}/images/train\n")
    yaml_file.write(f"val: {base_path}/images/val\n")
    yaml_file.write("nc: 1\n")
    yaml_file.write("names: ['licence']\n")

# 克隆 YOLOv5 並安裝必要的套件
if not os.path.exists("./yolov5"):
    os.system("git clone https://github.com/ultralytics/yolov5")
os.system("pip install -r yolov5/requirements.txt")

# 訓練 YOLOv5 模型
os.system(
    f"python yolov5/train.py "
    f"--weights yolov5s.pt "
    f"--cfg yolov5/models/yolov5s.yaml "
    f"--img 416 "
    f"--batch 48 "
    f"--epochs 100 "
    f"--data {base_path}/licence.yaml "
    f"--cache"
)

# 加載 YOLOv5 模型
model_path = "yolov5/runs/train/exp/weights/best.pt"
model = torch.hub.load("ultralytics/yolov5", "custom", path=model_path, force_reload=True)

# 測試 YOLOv5 模型
test_image_path = "C:/Users/huang/OneDrive/桌面/SA/CarLicensePlateDetection/images/test_image.jpg"
image = cv2.imread(test_image_path)

if image is None:
    print(f"圖片加載失敗: {test_image_path}")
else:
    results = model(image)
    detections = results.xyxy[0] if len(results.xyxy) > 0 else None

    if detections is None or len(detections) == 0:
        print("未偵測到任何物體")
    else:
        ocr = PaddleOCR(use_angle_cls=True, lang="en")

        for det in detections:
            x_min, y_min, x_max, y_max, _, _ = map(int, det[:6])
            license_plate = image[y_min:y_max, x_min:x_max]

            if license_plate is None or license_plate.size == 0:
                continue

            cv2.imshow("License Plate", license_plate)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            result = ocr.ocr(license_plate, cls=True)
            if result:
                for line in result[0]:
                    print(f"辨識文字: {line[1]}")

    results.save()
