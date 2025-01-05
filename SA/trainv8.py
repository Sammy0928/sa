import os
import shutil
import time
from ultralytics import YOLO

if __name__ == '__main__':
    # 設定基礎輸出目錄
    save_dir = "./runs/detect/train2"
    
    # 確保基礎目錄存在
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"創建目錄：{save_dir}")

    # 確保目標目錄存在
    weights_dir = os.path.join(save_dir, "weights")
    os.makedirs(weights_dir, exist_ok=True)
    print(f"已創建權重目錄：{weights_dir}")

    # 檢查配置文件
    if not os.path.exists('./data.yaml'):
        raise FileNotFoundError("配置文件 './data.yaml' 不存在，請檢查路徑！")

    # 檢查模型文件
    if not os.path.exists('yolov8n.pt'):
        raise FileNotFoundError("模型文件 'yolov8n.pt' 不存在，請檢查路徑或下載！")

    # 加載模型
    model = YOLO('yolov8n.pt')  # 使用 YOLOv8 nano 模型
    print("開始訓練 .........")
    t1 = time.time()

    # 開始訓練
    model.train(
        data='./data.yaml',
        epochs=200,
        imgsz=640,
        batch=8,
        save_dir=save_dir  # 訓練結果保存目錄
    )
    # 匯出模型
    path = model.export()
    print(f"model.export() 返回的路徑: {path}")
    if path and os.path.exists(path):
        export_path = os.path.join(save_dir, os.path.basename(path))
        shutil.move(path, export_path)  # 將匯出的模型移動到訓練輸出目錄
        print(f"模型匯出成功，路徑 : {export_path}")
    else:
        print("模型匯出失敗或輸出路徑無效！")
