"""
模型训练模块 — 组长 A 负责
包含数据准备、YOLOv8 训练、消融实验对比
"""

import torch
from pathlib import Path
from ultralytics import YOLO


PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
MODEL_DIR = PROJECT_DIR / "models"


def check_gpu():
    """检查 GPU 可用性"""
    if torch.cuda.is_available():
        device = torch.cuda.get_device_name(0)
        print(f"[GPU] {device} 可用")
        return "cuda"
    else:
        print("[CPU] 未检测到 GPU，将使用 CPU 训练（速度较慢）")
        return "cpu"


def download_dataset():
    """
    下载安全帽数据集指南

    推荐数据集来源：
    1. Roboflow - Safety Helmet Detection
       https://universe.roboflow.com/ 搜索 "Hard Hat Workers"
       使用 roboflow API 下载

    2. Kaggle - Hard Hat Detection
       https://www.kaggle.com/datasets/ 搜索 "hard hat detection"

    下载后放入 data/ 目录，结构：
    data/
      train/
        images/
        labels/
      valid/
        images/
        labels/
    """
    print("""
    ===== 数据集下载指南 =====

    方式1 (推荐): Roboflow
    pip install roboflow
    python -c "from roboflow import Roboflow; rf = Roboflow(api_key='YOUR_KEY'); rf.workspace('...').project('...').version(1).download('yolov8')"

    方式2: 手动下载
    https://universe.roboflow.com/ → 搜索 "Hard Hat Workers" → 下载 YOLOv8 格式

    下载后将数据放入: data/
    """)


def create_data_yaml():
    """创建 YOLOv8 数据集配置文件"""
    yaml_content = f"""
path: {str(DATA_DIR.absolute())}
train: train/images
val: valid/images

nc: 3
names:
  0: helmet
  1: head
  2: person
"""
    yaml_path = DATA_DIR / "data.yaml"
    yaml_path.write_text(yaml_content, encoding="utf-8")
    print(f"[OK] 数据集配置已创建: {yaml_path}")
    return yaml_path


def train_yolo(model_size="s", epochs=100, imgsz=640, batch=16):
    """
    训练 YOLOv8 模型

    Args:
        model_size: n/s/m/l/x
        epochs: 训练轮数
        imgsz: 输入图像尺寸
        batch: 批次大小
    """
    device = check_gpu()
    yaml_path = DATA_DIR / "data.yaml"

    if not yaml_path.exists():
        create_data_yaml()

    model_name = f"yolov8{model_size}.pt"
    model = YOLO(model_name)

    print(f"\n===== 开始训练 YOLOv8{model_size} =====")
    results = model.train(
        data=str(yaml_path),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=device,
        name=f"helmet_yolov8{model_size}",
        exist_ok=True,
        patience=20,
        save=True,
        plots=True,
    )

    print(f"\n[OK] 训练完成！最佳模型: {results.save_dir}/weights/best.pt")

    return results


def run_ablation_study():
    """
    消融实验：对比 YOLOv8n/s/m 三个规格

    输出对比表格：

    | 模型      | mAP@0.5 | Precision | Recall | 推理速度(ms) | 模型大小 |
    |-----------|---------|-----------|--------|-------------|---------|
    | YOLOv8n   |   xx%   |    xx%    |  xx%   |    xms      |   xMB   |
    | YOLOv8s   |   xx%   |    xx%    |  xx%   |    xms      |   xMB   |
    | YOLOv8m   |   xx%   |    xx%    |  xx%   |    xms      |   xMB   |
    """
    print("\n===== 消融实验：YOLOv8 规格对比 =====")

    results_table = []
    for size in ["n", "s", "m"]:
        print(f"\n--- 训练 YOLOv8{size} ---")
        result = train_yolo(model_size=size, epochs=100)
        results_table.append({
            "model": f"YOLOv8{size}",
            "map50": round(float(result.box.map50), 4),
            "precision": round(float(result.box.mp), 4),
            "recall": round(float(result.box.mr), 4),
        })

    print("\n===== 消融实验结果汇总 =====")
    print(f"{'模型':<12}{'mAP@0.5':<12}{'Precision':<12}{'Recall':<12}")
    print("-" * 48)
    for r in results_table:
        print(f"{r['model']:<12}{r['map50']:<12}{r['precision']:<12}{r['recall']:<12}")

    return results_table


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "ablation":
        run_ablation_study()
    elif len(sys.argv) > 1:
        train_yolo(model_size=sys.argv[1])
    else:
        print("用法:")
        print("  python train.py s         # 训练 YOLOv8s")
        print("  python train.py n         # 训练 YOLOv8n")
        print("  python train.py m         # 训练 YOLOv8m")
        print("  python train.py ablation  # 运行消融实验")
        download_dataset()
