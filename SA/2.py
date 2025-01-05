import os
import shutil
import time
from ultralytics import YOLO

if __name__ == '__main__':
    # 設定訓練輸出路徑
    save_dir = "./runs/detect/train2/wights"
    if os.path.exists(save_dir):
        shutil.rmtree(save_dir)
        print(f"已清理舊的目錄：{save_dir}")
    else:
        print(f"目標目錄不存在，將創建新目錄：{save_dir}")

    # 確保目標目錄存在
    weights_dir = os.path.join(save_dir, "weights")
    os.makedirs(weights_dir, exist_ok=True)
    print(f"已創建權重目錄：{weights_dir}")

    # 檢查配置文件
    if not os.path.exists('C:/Users/user/Documents/GitHub/sa/SA/data.yaml'):
        raise FileNotFoundError("配置文件 './data.yaml' 不存在，請檢查路徑！")

    # 檢查模型文件
    if not os.path.exists('C:/Users/user/Documents/GitHub/sa/SA/yolov8n.pt'):
        raise FileNotFoundError("模型文件 'yolov8n.pt' 不存在，請檢查路徑或下載！")

    # 加載模型
    model = YOLO('yolov8n.pt')  # 使用 YOLOv8 nano 模型
    print("開始訓練 .........")
    t1 = time.time()

    # 開始訓練
    model.train(
    data='C:/Users/user/Documents/GitHub/sa/SA/data.yaml',
    epochs=1,
    imgsz=448,
    batch=120,
    save_dir=save_dir
)


    # 訓練結束，計算耗時
    t2 = time.time()
    elapsed_time = t2 - t1
    minutes, seconds = divmod(elapsed_time, 60)
    print(f"訓練花費時間 : {int(minutes)}分 {seconds:.2f}秒")

    # 匯出模型
    path = model.export()
    if path and os.path.exists(path):
        print(f"模型匯出成功，路徑 : {path}")
    else:
        print("模型匯出失敗或輸出路徑無效！")