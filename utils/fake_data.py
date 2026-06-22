"""
假数据模块 —— 第一周搭骨架用
第二周接入真实模型后替换为真实接口
"""
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

# ============================================================
# 模拟检测结果
# ============================================================

def fake_detect(image: np.ndarray) -> List[Dict]:
    """
    模拟 detect(image) 的返回格式
    返回: [{"bbox": [x1,y1,x2,y2], "class": "helmet"/"head", "conf": 0.xx}, ...]
    """
    h, w = image.shape[:2]
    detections = []
    num_objects = random.randint(3, 8)

    for i in range(num_objects):
        # 随机生成 bbox
        bw = random.randint(int(w * 0.05), int(w * 0.15))
        bh = random.randint(int(h * 0.08), int(h * 0.20))
        x1 = random.randint(0, max(1, w - bw))
        y1 = random.randint(0, max(1, h - bh))
        x2 = x1 + bw
        y2 = y1 + bh

        # 随机类别：70% 概率戴安全帽，30% 概率没戴
        if random.random() < 0.7:
            cls = "helmet"
            conf = random.uniform(0.85, 0.99)
        else:
            cls = "head"
            conf = random.uniform(0.75, 0.95)

        detections.append({
            "bbox": [x1, y1, x2, y2],
            "class": cls,
            "conf": round(conf, 3),
            "label": "佩戴安全帽" if cls == "helmet" else "⚠️ 未佩戴安全帽",
        })

    return detections


def fake_get_statistics(detections: List[Dict]) -> Dict:
    """
    模拟 get_statistics(detections) 的返回格式
    """
    total = len(detections)
    helmet_count = sum(1 for d in detections if d["class"] == "helmet")
    head_count = total - helmet_count
    violation_rate = round(head_count / max(total, 1) * 100, 1)

    return {
        "total_persons": total,
        "helmet_count": helmet_count,
        "no_helmet_count": head_count,
        "violation_rate": violation_rate,
        "avg_confidence": round(np.mean([d["conf"] for d in detections]), 3),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


# ============================================================
# 模拟历史统计数据（用于看板折线图）
# ============================================================

def fake_history_data(days: int = 7) -> List[Dict]:
    """
    生成过去 N 天的模拟检测历史
    """
    history = []
    for i in range(days):
        date = datetime.now() - timedelta(days=days - 1 - i)
        total = random.randint(80, 200)
        violations = random.randint(2, int(total * 0.15))
        history.append({
            "date": date.strftime("%m-%d"),
            "total_detections": total,
            "violations": violations,
            "violation_rate": round(violations / total * 100, 1),
            "helmet_count": total - violations,
        })
    return history


# ============================================================
# 模拟危险区域违规检测
# ============================================================

def fake_check_zone_violations(detections: List[Dict], zone: List[Tuple]) -> List[Dict]:
    """
    模拟 check_zone_violations() 的返回
    zone: 多边形顶点列表 [(x1,y1), (x2,y2), ...]
    返回: 区域内的违规检测列表
    """
    violations = [d for d in detections if d["class"] == "head"]
    # 随机标记一些为区域内违规
    for v in violations:
        v["in_zone"] = random.random() < 0.6
    return violations


# ============================================================
# 模拟 LLM 报告
# ============================================================

def fake_generate_report(stats: Dict) -> str:
    """
    模拟 generate_report(stats) 的返回
    """
    return f"""# 🤖 AI 安全分析报告

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 📊 检测概况

| 指标 | 数值 |
|------|------|
| 检测总人数 | {stats.get('total_persons', 0)} 人 |
| 佩戴安全帽 | {stats.get('helmet_count', 0)} 人 |
| 未佩戴安全帽 | {stats.get('no_helmet_count', 0)} 人 |
| 违规率 | {stats.get('violation_rate', 0)}% |
| 平均置信度 | {stats.get('avg_confidence', 0)} |

---

## 🔍 分析与建议

### 1. 整体安全状况
本次检测共识别 **{stats.get('total_persons', 0)}** 名施工人员，其中 **{stats.get('helmet_count', 0)}** 人正确佩戴安全帽，佩戴率为 **{100 - stats.get('violation_rate', 0):.1f}%**。

### 2. 风险评估
- **风险等级**: {'🟢 低风险' if stats.get('violation_rate', 0) < 10 else '🟡 中等风险' if stats.get('violation_rate', 0) < 20 else '🔴 高风险'}
- **主要问题**: 部分施工人员在作业区域未正确佩戴安全帽

### 3. 改进建议
1. **加强安全教育**: 建议对未佩戴安全帽的人员进行安全培训
2. **完善管理制度**: 在施工入口设置安全检查点
3. **增加巡查频次**: 在高风险时段增加现场安全巡查
4. **技术预警**: 建议在重点区域部署实时检测预警系统

---

*本报告由 AI 安全分析系统自动生成，仅供参考。*
"""


# ============================================================
# 模拟历史违规记录
# ============================================================

def fake_violation_records(count: int = 12) -> List[Dict]:
    """
    生成模拟违规记录
    """
    records = []
    locations = ["A区-基坑旁", "B区-脚手架", "C区-材料堆放区", "D区-塔吊下方",
                 "E区-电梯井口", "F区-配电房", "G区-焊接区", "H区-混凝土浇筑区"]
    for i in range(count):
        dt = datetime.now() - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        records.append({
            "id": f"VIO-{1000 + i}",
            "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "location": random.choice(locations),
            "violation_type": random.choice(["未佩戴安全帽", "安全帽未系紧", "使用非标准安全帽"]),
            "severity": random.choice(["低", "中", "高"]),
            "status": random.choice(["已处理", "待处理", "处理中"]),
        })
    records.sort(key=lambda x: x["timestamp"], reverse=True)
    return records
