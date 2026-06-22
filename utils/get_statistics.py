"""
get_statistics.py —— 统计数据接口
从检测结果中提取统计信息，供看板使用
"""
from typing import List, Dict
from datetime import datetime


def get_statistics(detections: List[Dict]) -> Dict:
    """
    从检测结果中提取统计数据

    Args:
        detections: detect() 返回的检测列表

    Returns:
        {
            'total_persons': int,      # 总人数
            'helmet_count': int,       # 佩戴安全帽人数
            'no_helmet_count': int,    # 未佩戴人数
            'violation_rate': float,   # 违规率 (%)
            'avg_confidence': float,   # 平均置信度
            'timestamp': str           # 检测时间
        }
    """
    total = len(detections)
    helmet_count = sum(1 for d in detections if d.get('class') == 'helmet')
    head_count = total - helmet_count
    violation_rate = round(head_count / max(total, 1) * 100, 1)

    avg_conf = 0.0
    if detections:
        avg_conf = round(sum(d.get('confidence', 0) for d in detections) / len(detections), 3)

    return {
        'total_persons': total,
        'helmet_count': helmet_count,
        'no_helmet_count': head_count,
        'violation_rate': violation_rate,
        'avg_confidence': avg_conf,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
