"""
视频检测页面 —— 玻璃质感 Bento 风格
"""
import streamlit as st
import cv2
import numpy as np
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

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
        key="page_theme_selector_2",
    )
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    st.markdown("---")

# 标题
st.markdown('<h1 class="main-header">视频检测</h1>', unsafe_allow_html=True)
st.caption("上传施工监控视频，逐帧分析安全帽佩戴情况")
st.markdown('<hr class="glow-divider" />', unsafe_allow_html=True)

# 懒加载
@st.cache_resource
def load_detector():
    from utils.detect import detect
    from utils.get_statistics import get_statistics
    return detect, get_statistics

# 配置区
col_upload, col_ctrl = st.columns([2, 1])

with col_upload:
    st.markdown(glass_card(
        title="上传视频",
        content="支持 MP4 / AVI / MOV / MKV 格式",
        variant="primary",
        extra_html="",
    ), unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "选择视频文件开始检测",
        type=["mp4", "avi", "mov", "mkv"],
        help="支持 MP4 / AVI / MOV / MKV 格式",
        label_visibility="collapsed",
    )

with col_ctrl:
    st.markdown(glass_card(
        title="⚙️ 检测参数",
        content="",
        variant="success",
        extra_html="",
    ), unsafe_allow_html=True)
    skip_frames = st.slider("帧采样间隔", 1, 10, 3)
    conf_threshold = st.slider("置信度阈值", 0.1, 1.0, 0.5)

# ============================================================
# 检测逻辑
# ============================================================
if uploaded_file is not None:
    temp_path = f"temp_video.{uploaded_file.name.split('.')[-1]}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())

    cap = cv2.VideoCapture(temp_path)
    if not cap.isOpened():
        st.error("无法打开视频文件，请检查格式。")
    else:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / max(fps, 1)

        st.markdown(section_header("视频信息", "基础参数概览"), unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(metric_card("总帧数", f"{total_frames:,}", "", "帧", "primary"), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_card("帧率", f"{fps:.1f}", "", "FPS", "success"), unsafe_allow_html=True)
        with c3:
            st.markdown(metric_card("时长", f"{duration:.1f}s", "", "持续", "warning"), unsafe_allow_html=True)

        if st.button("开始检测", type="primary"):
            placeholder = st.empty()
            stats_placeholder = st.empty()
            progress_bar_widget = st.progress(0)

            detect_fn, get_stats_fn = load_detector()
            frame_count = 0
            all_stats = []

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                frame_count += 1
                if frame_count % skip_frames != 0:
                    continue

                detections = detect_fn(frame, conf_threshold=conf_threshold)
                stats = get_stats_fn(detections)
                all_stats.append(stats)

                # 画检测框（发光双层边框）
                annotated = frame.copy()
                for det in detections:
                    x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
                    color = (16, 185, 129) if det["class"] == "helmet" else (239, 68, 68)
                    overlay = annotated.copy()
                    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 6)
                    cv2.addWeighted(overlay, 0.35, annotated, 0.65, 0, annotated)
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                    label = f"Helmet {det['confidence']:.0%}" if det["class"] == "helmet" else f"NO Helmet {det['confidence']:.0%}"
                    cv2.putText(annotated, label, (x1, y1 - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                placeholder.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), use_container_width=True)

                # 更新进度条
                progress = min(frame_count / total_frames, 1.0)
                progress_bar_widget.progress(progress)

                with stats_placeholder.container():
                    s1, s2, s3, s4 = st.columns(4)
                    with s1:
                        st.markdown(metric_card("已处理", frame_count, "", "帧", "primary"), unsafe_allow_html=True)
                    with s2:
                        st.markdown(metric_card("检测人数", stats["total_persons"], "", "当前", "success"), unsafe_allow_html=True)
                    with s3:
                        st.markdown(metric_card("佩戴安全帽", stats["helmet_count"], "", "当前", "success"), unsafe_allow_html=True)
                    with s4:
                        st.markdown(metric_card("违规人数", stats["no_helmet_count"], "", "当前", "warning"), unsafe_allow_html=True)

                time.sleep(0.05)

            cap.release()
            progress_bar_widget.progress(1.0)
            st.success(f"视频检测完成！共处理 {len(all_stats)} 帧。")

            # 汇总统计
            st.markdown(section_header("视频检测汇总", "综合数据分析"), unsafe_allow_html=True)
            total_persons = sum(s["total_persons"] for s in all_stats)
            total_violations = sum(s["no_helmet_count"] for s in all_stats)
            avg_rate = total_violations / max(total_persons, 1) * 100

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(metric_card("总检测人数", total_persons, "", "累计", "primary"), unsafe_allow_html=True)
            with col2:
                st.markdown(metric_card("总违规次数", total_violations, "", "累计", "warning"), unsafe_allow_html=True)
            with col3:
                st.markdown(metric_card("平均违规率", f"{avg_rate:.1f}%", "", "综合",
                                        "success" if avg_rate < 10 else "warning"), unsafe_allow_html=True)
else:
    st.markdown(section_header("上传视频开始检测", "无视频时显示示例"), unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(glass_card(
            title="监控录像 1",
            content="基坑区域",
            variant="success",
            extra_html=f'<div style="margin-top:1rem;">{progress_bar(95, "佩戴率", "success")}</div>',
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(glass_card(
            title="监控录像 2",
            content="脚手架区域",
            variant="warning",
            extra_html=f'<div style="margin-top:1rem;">{progress_bar(78, "佩戴率", "warning")}</div>',
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(glass_card(
            title="监控录像 3",
            content="出入口区域",
            variant="primary",
            extra_html=f'<div style="margin-top:1rem;">{progress_bar(88, "佩戴率", "primary")}</div>',
        ), unsafe_allow_html=True)
