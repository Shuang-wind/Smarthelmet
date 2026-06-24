"""
zone_check.py - 危险区域安全帽检测模块
YOLOv8s 检测 + 多边形区域判断 + 违章统计

使用方法:
    from utils.zone_check import HelmetZoneChecker
    
    checker = HelmetZoneChecker(
        model_path='best.pt',
        zone_polygon=[(100, 200), (400, 200), (400, 500), (100, 500)]
    )
    results = checker.check(image_path)
    print(f"违章人数: {results['violation_count']}")
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Dict, Optional


class HelmetZoneChecker:
    """
    安全帽检测 + 危险区域判断
    
    Attributes:
        model: YOLOv8 模型实例
        zone_polygon: 危险区域多边形顶点列表 [(x1,y1), (x2,y2), ...]
        conf_threshold: 检测置信度阈值
    """
    
    def __init__(
        self,
        model_path: str = 'best.pt',
        zone_polygon: Optional[List[Tuple[int, int]]] = None,
        conf_threshold: float = 0.5
    ):
        """
        初始化检测器
        
        Args:
            model_path: YOLO 模型权重路径
            zone_polygon: 危险区域多边形顶点，例如 [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
            conf_threshold: 检测置信度阈值，低于此值的检测结果会被忽略
        """
        self.model = YOLO(model_path)
        self.zone_polygon = zone_polygon or []
        self.conf_threshold = conf_threshold
        self.class_names = {0: 'helmet', 1: 'head'}
    
    def set_zone(self, polygon: List[Tuple[int, int]]):
        """设置/更新危险区域"""
        self.zone_polygon = polygon
    
    # ============================================================
    # 核心算法：射线法判断点是否在多边形内
    # ============================================================
    @staticmethod
    def point_in_polygon(x: float, y: float, polygon: List[Tuple[int, int]]) -> bool:
        """
        射线法判断点 (x, y) 是否在多边形内
        
        原理：从点向右发射水平射线，统计与多边形边的交点数量。
        奇数个交点 → 点在多边形内；偶数个 → 点在多边形外。
        
        Args:
            x, y: 待判断点的坐标
            polygon: 多边形顶点列表
            
        Returns:
            True 如果点在多边形内
        """
        n = len(polygon)
        if n < 3:
            return False
        
        inside = False
        j = n - 1
        
        for i in range(n):
            xi, yi = polygon[i]
            xj, yj = polygon[j]
            
            # 检查射线是否与边相交
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            
            j = i
        
        return inside
    
    # ============================================================
    # 检测接口
    # ============================================================
    def detect(self, image: np.ndarray) -> List[Dict]:
        """
        对图像进行安全帽检测
        
        Args:
            image: OpenCV 格式的图像 (BGR numpy array)
            
        Returns:
            detections 列表，每项格式:
            {
                'class': 'helmet' | 'head',
                'class_id': 0 | 1,
                'bbox': [x1, y1, x2, y2],   # 像素坐标
                'center': (cx, cy),           # 边界框中心点
                'confidence': 0.95
            }
        """
        results = self.model(image, verbose=False)
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            
            for box in boxes:
                conf = float(box.conf[0])
                if conf < self.conf_threshold:
                    continue
                
                cls_id = int(box.cls[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                
                detections.append({
                    'class': self.class_names.get(cls_id, 'unknown'),
                    'class_id': cls_id,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'center': (cx, cy),
                    'confidence': conf
                })
        
        return detections
    
    # ============================================================
    # 违章检查接口（B 和 C 的主要调用入口）
    # ============================================================
    def check(self, image: np.ndarray) -> Dict:
        """
        完整检测流程：检测 + 区域判断 + 统计
        
        Args:
            image: OpenCV 格式的图像
            
        Returns:
            {
                'detections': [...],          # 所有检测结果
                'zone_violations': [...],     # 危险区域内未戴安全帽的人
                'violation_count': int,       # 违章人数
                'helmet_in_zone': int,        # 区域内戴安全帽人数
                'head_in_zone': int,          # 区域内未戴安全帽人数（=违章）
                'total_helmet': int,          # 全图安全帽数
                'total_head': int,            # 全图人头数
                'zone_polygon': [...]         # 使用的危险区域
            }
        """
        detections = self.detect(image)
        
        # 统计
        total_helmet = sum(1 for d in detections if d['class'] == 'helmet')
        total_head = sum(1 for d in detections if d['class'] == 'head')
        
        helmet_in_zone = 0
        head_in_zone = 0
        zone_violations = []
        
        if self.zone_polygon and len(self.zone_polygon) >= 3:
            for d in detections:
                cx, cy = d['center']
                if self.point_in_polygon(cx, cy, self.zone_polygon):
                    if d['class'] == 'helmet':
                        helmet_in_zone += 1
                    elif d['class'] == 'head':
                        head_in_zone += 1
                        zone_violations.append(d)
        
        return {
            'detections': detections,
            'zone_violations': zone_violations,
            'violation_count': head_in_zone,
            'helmet_in_zone': helmet_in_zone,
            'head_in_zone': head_in_zone,
            'total_helmet': total_helmet,
            'total_head': total_head,
            'zone_polygon': self.zone_polygon
        }
    
    # ============================================================
    # 可视化接口
    # ============================================================
    def draw_results(self, image: np.ndarray, results: Dict) -> np.ndarray:
        """
        在图像上绘制检测结果和危险区域
        
        Args:
            image: 原始图像
            results: check() 方法的返回值
            
        Returns:
            绘制后的图像
        """
        img = image.copy()
        
        # 绘制危险区域（红色半透明）
        if self.zone_polygon and len(self.zone_polygon) >= 3:
            overlay = img.copy()
            pts = np.array(self.zone_polygon, np.int32).reshape((-1, 1, 2))
            cv2.polylines(overlay, [pts], True, (0, 0, 255), 2)
            cv2.fillPoly(overlay, [pts], (0, 0, 255))
            img = cv2.addWeighted(overlay, 0.15, img, 0.85, 0)
        
        # 绘制所有检测框
        for d in results['detections']:
            x1, y1, x2, y2 = d['bbox']
            is_violation = d in results['zone_violations']
            
            if d['class'] == 'helmet':
                color = (0, 255, 0)      # 绿色 = 安全
                label = f"Helmet {d['confidence']:.2f}"
            else:
                color = (0, 0, 255) if is_violation else (0, 165, 255)
                label = f"NO Helmet {d['confidence']:.2f}" if is_violation else f"Head {d['confidence']:.2f}"
            
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # 绘制统计信息
        info_lines = [
            f"Helmet: {results['total_helmet']}  Head: {results['total_head']}",
            f"Zone Violations: {results['violation_count']}"
        ]
        y_offset = 30
        for line in info_lines:
            cv2.putText(img, line, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            y_offset += 30
        
        return img


# ============================================================
# 便捷函数（B 可以直接调用）
# ============================================================
def check_image(
    image_path: str,
    model_path: str = 'best.pt',
    zone_polygon: Optional[List[Tuple[int, int]]] = None
) -> Dict:
    """
    单张图片检测的便捷函数
    
    使用示例:
        result = check_image(
            'test.jpg',
            model_path='best.pt',
            zone_polygon=[(100, 100), (500, 100), (500, 400), (100, 400)]
        )
        print(f"违章人数: {result['violation_count']}")
    """
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"无法读取图片: {image_path}")
    
    checker = HelmetZoneChecker(model_path, zone_polygon)
    return checker.check(image)


# ============================================================
# 自测代码
# ============================================================
if __name__ == '__main__':
    # 示例：定义一个矩形危险区域
    zone = [(200, 150), (600, 150), (600, 450), (200, 450)]
    
    checker = HelmetZoneChecker(
        model_path='best.pt',
        zone_polygon=zone,
        conf_threshold=0.5
    )
    
    # 检测图片
    import sys
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    else:
        img_path = 'test.jpg'  # 替换为实际图片路径
    
    image = cv2.imread(img_path)
    if image is None:
        print(f"请提供有效的图片路径: python zone_check.py <image_path>")
        sys.exit(1)
    
    results = checker.check(image)
    print(f"\n检测结果:")
    print(f"  总安全帽数: {results['total_helmet']}")
    print(f"  总人头数:   {results['total_head']}")
    print(f"  区域内安全帽: {results['helmet_in_zone']}")
    print(f"  违章人数:    {results['violation_count']}")
    
    # 可视化
    result_img = checker.draw_results(image, results)
    cv2.imwrite('result.jpg', result_img)
    print("\n结果已保存到 result.jpg")
