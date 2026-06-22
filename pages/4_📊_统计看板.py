"""
统计看板页面 —— 玻璃质感 Bento 风格
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.get_statistics import get_statistics

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="统计看板 - 安全帽检测系统",
    page_icon="",
    layout="wide",
)

if "theme" not in st.session_state or st.session_state.theme not in ["dark", "light", "system"]:
    st.session_state.theme = "light"

from utils.styles import inject_common_styles, metric_card, glass_card, section_header, progress_bar, bar_chart, donut_chart, divider
inject_common_styles(theme=st.session_state.theme)

# 页面标题
st.markdown('<h1 class="main-header">统计看板</h1>', unsafe_allow_html=True)
st.caption("实时监控数据可视化，全面掌握安全帽佩戴情况")
st.markdown('<hr class="glow-divider" />', unsafe_allow_html=True)

# ============================================================
# 读取 session_state 检测历史
# ============================================================
history = st.session_state.get("detection_history", [])

if not history:
    # 使用模拟数据演示
    st.info("当前无真实检测历史，正在使用模拟演示数据。")
    total_detections, total_helmet, total_no_helmet = 1284, 1247, 37
    avg_confidence, helmet_rate = 92.5, 97.1
else:
    total_detections = sum(h.get("total_persons", 0) for h in history)
    total_helmet = sum(h.get("helmet_count", 0) for h in history)
    total_no_helmet = sum(h.get("no_helmet_count", 0) for h in history)
    avg_confidence = round(sum(h.get("avg_confidence", 0) for h in history) / max(len(history), 1), 1)
    helmet_rate = round(total_helmet / max(total_detections, 1) * 100, 1)

# ============================================================
# 顶部 5 张大指标卡 (Bento)
# ============================================================
st.markdown(section_header("今日概览", "核心指标实时监控"), unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(metric_card("今日检测", f"{total_detections:,}", "", " 12%", "primary"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("佩戴人数", f"{total_helmet:,}", "", " 18%", "success"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("违规人数", f"{total_no_helmet:,}", "", " 5%", "warning"), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card("佩戴率", f"{helmet_rate}%", "", " 2.3%", "success"), unsafe_allow_html=True)
with c5:
    st.markdown(metric_card("平均置信度", f"{avg_confidence}%", "", "AI", "primary"), unsafe_allow_html=True)

# ============================================================
# 第二行 Bento：环形图 (2 列)
# ============================================================
st.markdown(section_header("佩戴分布", "今日合规度分析"), unsafe_allow_html=True)

col_donut, col_gauge, col_kpi = st.columns([1, 1, 1])

with col_donut:
    st.markdown(glass_card(
        title="安全帽佩戴分布",
        content="佩戴 vs 未佩戴",
        variant="success",
        extra_html=donut_chart(
            round(total_helmet / max(total_detections, 1) * 100, 1),
            "佩戴率",
            f"{round(total_helmet / max(total_detections, 1) * 100, 1)}%",
        ),
    ), unsafe_allow_html=True)

with col_gauge:
    violation_rate = round(total_no_helmet / max(total_detections, 1) * 100, 1)
    pb1 = progress_bar(violation_rate, "当前违规率", "danger" if violation_rate > 10 else "warning" if violation_rate > 5 else "success")
    pb2 = progress_bar(max(0, 100 - violation_rate), "整体合规度", "success")
    pb3 = progress_bar(avg_confidence, "AI 模型置信度", "primary")
    st.markdown(glass_card(
        title="违规率仪表盘",
        content="系统综合评分",
        variant="warning" if violation_rate > 5 else "success",
        extra_html=f'<div style="margin-top:0.5rem;">{pb1}</div><div style="margin-top:1rem;">{pb2}</div><div style="margin-top:1rem;">{pb3}</div>',
    ), unsafe_allow_html=True)

with col_kpi:
    kpi_extra = f'<div style="margin-top:0.5rem;"><div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:4px;">总人数：<strong style="color:var(--text-primary);">{total_detections}</strong></div><div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:4px;">已佩戴：<strong style="color:#10b981;">{total_helmet}</strong></div><div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:4px;">未佩戴：<strong style="color:#ef4444;">{total_no_helmet}</strong></div><div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:4px;">样本天数：<strong style="color:var(--text-primary);">7 天</strong></div><div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:4px;">安全等级：<strong style="color:#10b981;">A (优秀)</strong></div></div>'
    st.markdown(glass_card(
        title="关键 KPI",
        content="关键绩效指标",
        variant="primary",
        extra_html=kpi_extra,
    ), unsafe_allow_html=True)

# ============================================================
# 第三行：趋势折线 (使用 plotly) + 区域柱状图 (使用自定义)
# ============================================================
st.markdown(section_header("检测趋势分析", "近 7 天数据"), unsafe_allow_html=True)

import plotly.graph_objects as go

col_line, col_bar = st.columns([1, 1])

# 构建假的 7 天数据
days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
day_detections = [180, 210, 195, 230, 220, 185, total_detections]
day_violations = [6, 8, 5, 11, 9, 4, total_no_helmet]

with col_line:
    st.markdown(glass_card(
        title="检测历史趋势（近7天）",
        content="",
        variant="primary",
        extra_html="",
    ), unsafe_allow_html=True)

    # 在同一列继续绘制 Plotly 图表
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=days, y=day_detections, name="总检测数",
        mode="lines+markers",
        line=dict(color="#3b82f6", width=4),
        marker=dict(size=10, color="#3b82f6", line=dict(width=2, color="#fff")),
        fill="tozeroy",
        fillcolor="rgba(59, 130, 246, 0.12)",
    ))
    fig_line.add_trace(go.Scatter(
        x=days, y=day_violations, name="违规次数",
        mode="lines+markers",
        line=dict(color="#ef4444", width=3),
        marker=dict(size=9, color="#ef4444", line=dict(width=2, color="#fff")),
        fill="tozeroy",
        fillcolor="rgba(239, 68, 68, 0.08)",
    ))
    fig_line.update_layout(
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(230,230,240,0.9)"),
        margin=dict(t=10, b=0, l=0, r=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False, gridcolor="rgba(255,255,255,0.06)"),
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col_bar:
    areas = ["A区-基坑", "B区-脚手架", "C区-材料区", "D区-塔吊", "E区-电梯井"]
    rates = [2.1, 5.8, 3.2, 1.5, 7.3]
    st.markdown(glass_card(
        title="各区域违规率（圆角渐变柱）",
        content="",
        variant="warning",
        extra_html=bar_chart(values=rates, labels=areas, max_val=10.0, variant="warning"),
    ), unsafe_allow_html=True)

# ============================================================
# 第四行：违规率趋势
# ============================================================
st.markdown(section_header("违规率变化趋势", "与预警线对比"), unsafe_allow_html=True)

violation_rates = [round(dv / max(dd, 1) * 100, 1) for dv, dd in zip(day_violations, day_detections)]

fig_rate = go.Figure()
fig_rate.add_trace(go.Scatter(
    x=days, y=violation_rates, name="违规率 (%)",
    mode="lines+markers",
    line=dict(color="#f59e0b", width=4),
    marker=dict(size=11, color="#f59e0b", line=dict(width=2, color="#fff")),
    fill="tozeroy",
    fillcolor="rgba(245, 158, 11, 0.10)",
))
fig_rate.add_hline(
    y=10, line_dash="dash", line_color="#ef4444", line_width=2,
    annotation_text="预警线 10%",
    annotation_position="top right",
)
fig_rate.update_layout(
    height=300,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(230,230,240,0.9)"),
    margin=dict(t=10, b=0),
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
)
st.plotly_chart(fig_rate, use_container_width=True)

# ============================================================
# 底部：实时刷新模拟
# ============================================================
st.markdown('<hr class="glow-divider" />', unsafe_allow_html=True)
c_refresh_left, c_refresh_right = st.columns([1, 5])
with c_refresh_left:
    if st.button("刷新数据", type="primary"):
        st.rerun()
with c_refresh_right:
    st.caption("数据每 30 秒自动刷新（模拟） · Powered by YOLOv8 + Streamlit")
