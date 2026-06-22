"""
历史记录页面 —— 违规截图浏览与检测历史（玻璃质感 Bento 风格）
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.fake_data import fake_violation_records

st.set_page_config(
    page_title="历史记录 - 安全帽检测系统",
    page_icon="",
    layout="wide",
)

if "theme" not in st.session_state or st.session_state.theme not in ["dark", "light", "system"]:
    st.session_state.theme = "light"

from utils.styles import inject_common_styles, metric_card, glass_card, section_header, progress_bar
inject_common_styles(theme=st.session_state.theme)

# 标题
st.markdown('<h1 class="main-header">历史记录</h1>', unsafe_allow_html=True)
st.caption("浏览违规截图与检测历史记录")
st.markdown('<hr class="glow-divider" />', unsafe_allow_html=True)

# 筛选器（玻璃卡）
st.markdown(section_header("筛选器", "按时间/区域/严重程度/处理状态过滤"), unsafe_allow_html=True)

c_f1, c_f2, c_f3, c_f4 = st.columns(4)
with c_f1:
    date_range = st.selectbox("时间范围", ["全部", "今日", "近7天", "近30天"], index=0)
with c_f2:
    location_filter = st.selectbox("施工区域",
                                   ["全部", "A区-基坑旁", "B区-脚手架", "C区-材料堆放区",
                                    "D区-塔吊下方", "E区-电梯井口"], index=0)
with c_f3:
    severity_filter = st.selectbox("严重程度", ["全部", "高", "中", "低"], index=0)
with c_f4:
    status_filter = st.selectbox("处理状态", ["全部", "已处理", "待处理", "处理中"], index=0)

# 概览指标
st.markdown(section_header("违规统计", "整体数据概览"), unsafe_allow_html=True)

c_o1, c_o2, c_o3, c_o4 = st.columns(4)
with c_o1:
    st.markdown(metric_card("总违规记录", "156", icon="", delta="本周 +12", variant="warning"), unsafe_allow_html=True)
with c_o2:
    st.markdown(metric_card("已处理", "128", icon="", delta="处理率 82%", variant="success"), unsafe_allow_html=True)
with c_o3:
    st.markdown(metric_card("待处理", "22", icon="", delta="需关注", variant="warning"), unsafe_allow_html=True)
with c_o4:
    st.markdown(metric_card("高危违规", "8", icon="", delta="立即处理", variant="danger"), unsafe_allow_html=True)

# 进度条（综合处理完成度）
pb1 = progress_bar(82.0, "总处理进度", "primary")
pb2 = progress_bar(100 * 28 / (128 + 28), "高危处理进度", "success")
st.markdown(glass_card(
        title="综合处理进度",
        content="",
        variant="primary",
        extra_html=f'<div style="margin-top:0.8rem;">{pb1}</div><div style="margin-top:0.8rem;">{pb2}</div>',
    ), unsafe_allow_html=True)

st.markdown('<hr class="glow-divider" />', unsafe_allow_html=True)

# 记录表格（玻璃卡）
st.markdown(section_header("违规记录列表", "按严重程度排序"), unsafe_allow_html=True)

records = fake_violation_records(count=20)

import pandas as pd
df = pd.DataFrame(records)
if location_filter != "全部":
    df = df[df["location"] == location_filter]
if severity_filter != "全部":
    df = df[df["severity"] == severity_filter]
if status_filter != "全部":
    df = df[df["status"] == status_filter]

# 对严重程度与状态上色
def _severity_badge(s):
    mapping = {"高": ("danger", "#ef4444"), "中": ("warning", "#f59e0b"), "低": ("success", "#10b981")}
    _, color = mapping.get(s, ("primary", "#3b82f6"))
    return f'<span class="severity-badge" style="background:{color};">{s}</span>'

def _status_badge(s):
    mapping = {"已处理": "#10b981", "待处理": "#ef4444", "处理中": "#f59e0b"}
    color = mapping.get(s, "#3b82f6")
    return f'<span class="severity-badge" style="background:{color};">{s}</span>'

# 构建单行 HTML 表格
styled_rows = ""
for _, row in df.iterrows():
    styled_rows += f'<tr style="border-bottom:1px solid rgba(255,255,255,0.06);"><td style="padding:0.5rem 0.8rem;color:var(--text-primary);font-weight:600;">{row["id"]}</td><td style="padding:0.5rem 0.8rem;color:var(--text-secondary);">{row["timestamp"]}</td><td style="padding:0.5rem 0.8rem;color:var(--text-primary);">{row["location"]}</td><td style="padding:0.5rem 0.8rem;color:var(--text-secondary);">{row["violation_type"]}</td><td style="padding:0.5rem 0.8rem;">{_severity_badge(row["severity"])}</td><td style="padding:0.5rem 0.8rem;">{_status_badge(row["status"])}</td></tr>'

table_html = f'<div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:18px;padding:0.8rem 1rem;backdrop-filter:blur(14px);overflow-x:auto;"><table style="width:100%;border-collapse:collapse;"><thead><tr style="text-align:left;color:var(--text-secondary);font-size:0.78rem;letter-spacing:0.06em;text-transform:uppercase;"><th style="padding:0.6rem 0.8rem;">编号</th><th style="padding:0.6rem 0.8rem;">时间</th><th style="padding:0.6rem 0.8rem;">位置</th><th style="padding:0.6rem 0.8rem;">违规类型</th><th style="padding:0.6rem 0.8rem;">严重程度</th><th style="padding:0.6rem 0.8rem;">状态</th></tr></thead><tbody>{styled_rows}</tbody></table></div>'
st.markdown(table_html, unsafe_allow_html=True)

# 违规截图预览（Bento 风格）
st.markdown(section_header("违规截图预览", "最近的违规行为预览"), unsafe_allow_html=True)

c_p1, c_p2, c_p3, c_p4 = st.columns(4)
previews = [
    ("VIO-1001", "A区-基坑旁", "高危", "2026-06-06 14:32:15"),
    ("VIO-1003", "B区-脚手架", "中危", "2026-06-06 11:20:08"),
    ("VIO-1005", "D区-塔吊下方", "高危", "2026-06-05 16:45:33"),
    ("VIO-1008", "C区-材料堆放区", "低危", "2026-06-05 09:12:47"),
]

for c, (pid, loc, sev, ts) in zip([c_p1, c_p2, c_p3, c_p4], previews):
    variant = "danger" if "高危" in sev else "warning" if "中危" in sev else "success"
    with c:
        preview_extra = f'<div style="line-height:1.9;font-size:0.85rem;"><div style="color:var(--text-secondary);">{loc}</div><div style="color:var(--text-primary);font-weight:600;">{sev}</div><div style="color:var(--text-secondary);font-size:0.75rem;margin-top:0.3rem;">{ts}</div></div><div style="margin-top:1rem;background:rgba(0,0,0,0.35);border-radius:12px;padding:2rem 1rem;text-align:center;color:var(--text-secondary);font-size:0.8rem;border:1px dashed rgba(255,255,255,0.15);">图片预览占位</div>'
        st.markdown(glass_card(
            title=pid,
            content="",
            variant=variant,
            extra_html=preview_extra,
        ), unsafe_allow_html=True)

# 操作按钮
st.markdown('<hr class="glow-divider" />', unsafe_allow_html=True)
c_b1, c_b2, c_b3 = st.columns(3)
with c_b1:
    if st.button("导出全部记录", type="primary"):
        csv_path = Path("outputs/violations/violation_records.csv")
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        st.success(f"已导出到：{csv_path}")
with c_b2:
    if st.button("导出筛选结果"):
        st.info("已导出筛选后的记录")
with c_b3:
    if st.button("清除历史记录"):
        st.warning("确认要清除所有历史记录吗？")
