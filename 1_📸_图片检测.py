"""
图片检测页面 —— 上传图片，展示真实检测结果
"""
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="图片检测 - 安全帽检测系统",
    page_icon="",
    layout="wide",
)

if "theme" not in st.session_state or st.session_state.theme not in ["dark", "light", "system"]:
    st.session_state.theme = "light"

from utils.styles import inject_common_styles, metric_card, glass_card, section_header, progress_bar
inject_common_styles(theme=st.session_state.theme)

# 主题切换器（放在侧边栏）
with st.sidebar:
    st.markdown("### 主题设置")
    new_theme = st.selectbox(
        "选择主题",
        options=["dark", "light", "system"],
        format_func=lambda x: {
            "dark": "深色主题",
            "light": "浅色主题",
            "system": "跟随系统",
        }.get(x, x),
        label_visibility="collapsed",
        index=["dark", "light", "system"].index(st.session_state.theme),
        key="page_theme_selector_1",
    )
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    st.markdown("---")

# 懒加载真实检测器
@st.cache_resource
def load_detector():
    from utils.detect import detect
    from utils.get_statistics import get_statistics
    return detect, get_statistics

# 标题
st.markdown('<h1 class="main-header">图片检测</h1>', unsafe_allow_html=True)
st.caption("上传施工现场图片，AI 自动识别安全帽佩戴情况")
st.markdown('<hr class="glow-divider" />', unsafe_allow_html=True)

# ============================================================
# 上传区域 + 说明（Bento 风格 —— 左大右小）
# ============================================================
col_upload, col_info = st.columns([2, 1])

with col_upload:
    st.markdown(glass_card(
        title="上传图片",
        content="支持 JPG / PNG / BMP / WEBP 格式",
        variant="primary",
        extra_html="",
    ), unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "选择图片文件开始检测",
        type=["jpg", "jpeg", "png", "bmp", "webp"],
        help="支持 JPG / PNG / BMP / WebP 格式",
        label_visibility="collapsed",
    )

with col_info:
    info_extra = '<div style="line-height:1.8;"><div>1 点击上传区域选择图片</div><div>2 系统自动进行安全帽检测</div><div>3 查看检测结果和统计信息</div><div style="margin-top:1rem;opacity:0.7;font-size:0.8rem;">支持格式：JPG · PNG · BMP · WebP<br>最大尺寸：20 MB</div></div>'
    st.markdown(glass_card(
        title="使用说明",
        content="",
        variant="success",
        extra_html=info_extra,
    ), unsafe_allow_html=True)

# ============================================================
# 检测逻辑（真实模型）
# ============================================================
if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if image is not None:
        with st.spinner("YOLOv8 正在检测中..."):
            detect_fn, get_stats_fn = load_detector()
            detections = detect_fn(image)
            stats = get_stats_fn(detections)

        # 在图片上画检测框
        annotated = image.copy()
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            conf = det["confidence"]
            if det["class"] == "helmet":
                color = (16, 185, 129)  # 绿色
                label = f"Helmet {conf:.0%}"
            else:
                color = (239, 68, 68)  # 红色
                label = f"NO Helmet {conf:.0%}"

            # 画发光检测框（两层：外层半透明 + 内层实色）
            overlay = annotated.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 6)
            cv2.addWeighted(overlay, 0.35, annotated, 0.65, 0, annotated)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            # 标签背景
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(annotated, (x1, y1 - th - 12), (x1 + tw + 8, y1), color, -1)
            cv2.putText(annotated, label, (x1 + 4, y1 - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # 展示结果
        st.markdown(section_header("检测结果", "AI 识别输出"), unsafe_allow_html=True)

        col_result, col_stats = st.columns([2, 1])

        with col_result:
            st.markdown(glass_card(
                title="识别画面",
                content="",
                variant="primary",
                extra_html="",
            ), unsafe_allow_html=True)
            annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            st.image(annotated_rgb, use_container_width=True)

        with col_stats:
            st.markdown(glass_card(
                title="检测统计",
                content="",
                variant="success",
                extra_html="",
            ), unsafe_allow_html=True)

            # 三张发光指标卡
            c_s1, c_s2 = st.columns(2)
            with c_s1:
                st.markdown(metric_card("检测人数", stats["total_persons"], icon="", variant="primary"), unsafe_allow_html=True)
            with c_s2:
                st.markdown(metric_card("佩戴", stats["helmet_count"], icon="", variant="success"), unsafe_allow_html=True)

            c_s3, c_s4 = st.columns(2)
            with c_s3:
                st.markdown(metric_card("未佩戴", stats["no_helmet_count"], icon="", variant="warning"), unsafe_allow_html=True)
            with c_s4:
                st.markdown(metric_card("置信度", f"{stats['avg_confidence']:.1%}", icon="", variant="primary"), unsafe_allow_html=True)

            # 违规率进度条（发光）
            violation_rate = stats["violation_rate"]
            variant = "success" if violation_rate < 10 else "warning" if violation_rate < 20 else "danger"
            st.markdown(glass_card(
                title="违规率",
                content=f"{violation_rate}%",
                variant=variant,
                extra_html=f'<div style="margin-top:0.8rem;">{progress_bar(violation_rate, "当前违规率", variant)}</div>',
            ), unsafe_allow_html=True)

        # 详细检测列表
        if detections:
            with st.expander("检测详情（展开查看每个目标）", expanded=False):
                for i, det in enumerate(detections):
                    c1, c2, c3 = st.columns([1, 2, 1])
                    with c1:
                        st.markdown(f"**目标 #{i + 1}**")
                    with c2:
                        st.text(f"位置: ({det['bbox'][0]}, {det['bbox'][1]}) → ({det['bbox'][2]}, {det['bbox'][3]})")
                    with c3:
                        st.markdown(f"置信度: **{det['confidence']:.1%}**")
                    st.markdown('<hr class="glow-divider" />', unsafe_allow_html=True)

        # 保存到 session_state
        if "detection_history" not in st.session_state:
            st.session_state.detection_history = []
        st.session_state.detection_history.append(stats)
        st.success("检测已完成，结果已同步至「统计看板」。")

    else:
        st.error("无法解析图片文件，请检查格式是否正确。")
else:
    # 没有上传图片时显示示例 Bento
    st.markdown(section_header("上传图片开始检测", "无图片时显示示例效果"), unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        pb1 = progress_bar(95, "佩戴率", "success")
        st.markdown(glass_card(
            title="示例 A 区",
            content="基坑施工区域",
            variant="success",
            extra_html=f'<div style="margin-top:1rem;">{pb1}</div>',
        ), unsafe_allow_html=True)
    with col2:
        pb2 = progress_bar(78, "佩戴率", "warning")
        st.markdown(glass_card(
            title="示例 B 区",
            content="脚手架作业区",
            variant="warning",
            extra_html=f'<div style="margin-top:1rem;">{pb2}</div>',
        ), unsafe_allow_html=True)
    with col3:
        pb3 = progress_bar(62, "佩戴率", "danger")
        st.markdown(glass_card(
            title="示例 C 区",
            content="材料堆放区域",
            variant="warning",
            extra_html=f'<div style="margin-top:1rem;">{pb3}</div>',
        ), unsafe_allow_html=True)
