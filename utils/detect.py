"""
detect.py —— 真实 YOLOv8 检测接口
封装自 zone_check.py 的 HelmetZoneChecker.detect()
"""
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict
import os

# 模型路径（相对项目根目录）
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "best.pt")

# 全局模型实例（懒加载）
_model = None


def _get_model():
    """懒加载 YOLO 模型"""
    global _model
    if _model is None:
        _model = YOLO(MODEL_PATH)
    return _model


def detect(image: np.ndarray, conf_threshold: float = 0.5) -> List[Dict]:
    """
    对图像进行安全帽检测

    Args:
        image: OpenCV 格式的图像 (BGR numpy array)
        conf_threshold: 置信度阈值

    Returns:
        detections 列表，每项格式:
        {
            'class': 'helmet' | 'head',
            'class_id': 0 | 1,
            'bbox': [x1, y1, x2, y2],
            'center': (cx, cy),
            'confidence': 0.95
        }
    """
    model = _get_model()
    results = model(image, verbose=False)
    detections = []
    class_names = {0: 'helmet', 1: 'head'}

    for result in results:
        boxes = result.boxes
        if boxes is None:
            continue

        for box in boxes:
            conf = float(box.conf[0])
            if conf < conf_threshold:
                continue

            cls_id = int(box.cls[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            detections.append({
                'class': class_names.get(cls_id, 'unknown'),
                'class_id': cls_id,
                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                'center': (cx, cy),
                'confidence': conf
            })

    return detections


def get_statistics(detections: List[Dict]) -> Dict:
    """
    从检测结果中提取统计数据

    Returns:
        {
            'total_persons': int,
            'helmet_count': int,
            'no_helmet_count': int,
            'violation_rate': float,
            'avg_confidence': float,
            'timestamp': str
        }
    """
    from datetime import datetime

    total = len(detections)
    helmet_count = sum(1 for d in detections if d['class'] == 'helmet')
    head_count = total - helmet_count
    violation_rate = round(head_count / max(total, 1) * 100, 1)

    avg_conf = 0.0
    if detections:
        avg_conf = round(sum(d['confidence'] for d in detections) / len(detections), 3)

    return {
        'total_persons': total,
        'helmet_count': helmet_count,
        'no_helmet_count': head_count,
        'violation_rate': violation_rate,
        'avg_confidence': avg_conf,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
