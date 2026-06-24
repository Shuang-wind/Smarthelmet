import requests
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("reports")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen:4b"


def build_report_prompt(stats: dict) -> str:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    compliance_rate = (1 - stats['violation_rate']) * 100

    return f"""你是一个工地安全分析专家。请根据以下检测数据，生成一份中文安全报告。

## 检测数据
- 检测时间：{current_time}
- 总人数：{stats['total_workers']} 人
- 佩戴安全帽：{stats['helmet_count']} 人
- 未佩戴安全帽：{stats['head_count']} 人
- 合规率：{compliance_rate:.1f}%
- 违规率：{stats['violation_rate'] * 100:.1f}%

## 报告要求
请严格按照以下四段式结构输出，语言简洁专业：

1. 概况（1 句话总结整体安全状况，必须包含合规率和违规率数据）
2. 违规详情（列出哪些区域/人员违规，使用具体数字和百分比说明）
3. 风险评估（给出风险等级：高/中/低，并简要说明理由）
4. 改进建议（提供 2-3 条具体、可执行的安全改进建议）

## 输出约束
- 输出格式：markdown
- 语言：请使用简体中文输出，不要出现乱码或过多英文术语
- 字数：报告正文不超过 200 字，重点突出数据支撑，不要冗余"""


def generate_report(stats: dict, zone_violations: list = None, mode: str = "auto", api_key: str = "") -> str:
    if not isinstance(stats, dict):
        raise ValueError(f"stats 必须是 dict，但实际是 {type(stats)}")

    prompt = build_report_prompt(stats)

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7}
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "生成失败")
        else:
            return f"[错误] Ollama 连接失败: {response.status_code}"

    except requests.exceptions.ConnectionError:
        return "[错误] 无法连接到 Ollama，请确保 Ollama 正在运行"
    except Exception as e:
        return f"[错误] {str(e)}"


def save_report(report_text: str, stats: dict) -> str:
    if not isinstance(report_text, str):
        raise ValueError(f"report_text 必须是 str，但实际是 {type(report_text)}")

    if not isinstance(stats, dict):
        raise ValueError(f"stats 必须是 dict，但实际是 {type(stats)}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}.md"
    filepath = OUTPUT_DIR / filename

    content = f"""# 安全帽检测报告

## 报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 检测统计

| 项目 | 数值 |
|------|------|
| 总人数 | {stats['total_workers']} |
| 佩戴安全帽 | {stats['helmet_count']} |
| 未佩戴安全帽 | {stats['head_count']} |
| 违规率 | {stats['violation_rate']:.1%} |

## AI 分析报告

{report_text}
"""

    filepath.write_text(content, encoding="utf-8")
    return str(filepath)