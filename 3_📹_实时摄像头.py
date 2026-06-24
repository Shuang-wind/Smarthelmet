"""
实时摄像头检测页面 —— 玻璃质感 Bento 风格
"""
import streamlit as st
import cv2
import numpy as np
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="实时摄像头 - 安全帽检测系统",
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
        key="page_theme_selector_3",
    )
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    st.markdown("---")

# 标题
st.markdown('<h1 class="main-header">实时摄像头检测</h1>', unsafe_allow_html=True)
st.caption("接入摄像头，实时检测施工现场安全帽佩戴情况")
st.markdown('<hr class="glow-divider" />', unsafe_allow_html=True)

# 懒加载
@st.cache_resource
def load_detector():
    from utils.detect import detect
    from utils.get_statistics import get_statistics
    return detect, get_statistics

# 控制面板
col_ctrl, col_status = st.columns([1, 2])

with col_ctrl:
    st.markdown(glass_card(
        title="控制面板",
        content="",
        variant="primary",
        extra_html="",
    ), unsafe_allow_html=True)
    camera_source = st.selectbox(
        "摄像头来源",
        ["默认摄像头 (0)", "摄像头 (1)", "摄像头 (2)"],
        index=0,
    )
    camera_idx = int(camera_source.split("(")[1].split(")")[0])
    conf_threshold = st.slider("置信度阈值", 0.1, 1.0, 0.5)
    show_labels = st.toggle("显示标签", value=True)
    alert_sound = st.toggle("违规声音提醒", value=False)

    start_btn = st.button("开始检测", type="primary", key="start_camera")
    stop_btn = st.button("停止检测", key="stop_camera")

with col_status:
    st.markdown(glass_card(
        title="实时状态",
        content="检测到的人数、佩戴、违规数据",
        variant="success",
        extra_html="",
    ), unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card("FPS", "--", "", "实时", "primary"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("检测人数", "--", "", "实时", "success"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("佩戴安全帽", "--", "", "实时", "success"), unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card("违规人数", "--", "", "实时", "warning"), unsafe_allow_html=True)

# 状态机
if "camera_running" not in st.session_state:
    st.session_state.camera_running = False

if start_btn:
    st.session_state.camera_running = True

if stop_btn:
    st.session_state.camera_running = False

if st.session_state.camera_running:
    cap = cv2.VideoCapture(camera_idx)
    if not cap.isOpened():
        st.error("无法打开摄像头，请检查设备连接或其他程序是否占用。")
        st.session_state.camera_running = False
    else:
        frame_placeholder = st.empty()
        stats_placeholder = st.empty()
        frame_count = 0
        start_time = time.time()
        detect_fn, get_stats_fn = load_detector()

        while st.session_state.camera_running:
            ret, frame = cap.read()
            if not ret:
                st.warning("摄像头读取失败，尝试重连...")
                time.sleep(1)
                continue
            frame_count += 1

            if frame_count % 3 == 0:
                detections = detect_fn(frame, conf_threshold=conf_threshold)
                stats = get_stats_fn(detections)

                # 画发光框
                for det in detections:
                    x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
                    color = (16, 185, 129) if det["class"] == "helmet" else (239, 68, 68)
                    overlay = frame.copy()
                    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 6)
                    cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    if show_labels:
                        label = f"Helmet {det['confidence']:.0%}" if det["class"] == "helmet" else f"NO Helmet {det['confidence']:.0%}"
                        cv2.putText(frame, label, (x1, y1 - 5),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                elapsed = time.time() - start_time
                fps_display = frame_count / elapsed if elapsed > 0 else 0

                frame_placeholder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)

                with stats_placeholder.container():
                    s1, s2, s3, s4 = st.columns(4)
                    with s1:
                        st.markdown(metric_card("FPS", f"{fps_display:.1f}", "", "实时", "primary"), unsafe_allow_html=True)
                    with s2:
                        st.markdown(metric_card("检测人数", stats["total_persons"], "", "当前", "success"), unsafe_allow_html=True)
                    with s3:
                        st.markdown(metric_card("佩戴", stats["helmet_count"], "", "当前", "success"), unsafe_allow_html=True)
                    with s4:
                        st.markdown(metric_card("违规", stats["no_helmet_count"], "", "当前", "warning"), unsafe_allow_html=True)

            time.sleep(0.01)

        cap.release()
        st.info("摄像头已停止。")
else:
    st.markdown(section_header("点击「开始检测」启动摄像头", "预览画面将在启动后显示"), unsafe_allow_html=True)
    placeholder_img = np.zeros((420, 1280, 3), dtype=np.uint8)
    # 渐变背景
    for i in range(placeholder_img.shape[0]):
        alpha = i / placeholder_img.shape[0]
        placeholder_img[i, :] = [int(30 + 40 * alpha), int(20 + 30 * alpha), int(15 + 25 * alpha)]
    cv2.putText(placeholder_img, "Camera Preview - Click Start", (400, 220),
                cv2.FONT_HERSHEY_SIMPLEX, 1.3, (200, 200, 220), 2)
    st.image(placeholder_img, use_container_width=True)

    warning_extra = '<div style="line-height:1.9;"><div>确保摄像头已正确连接</div><div>关闭其他占用摄像头的程序</div><div>建议在光线充足的环境下使用</div><div>检测过程中请勿关闭页面</div></div>'
    st.markdown(glass_card(
        title="注意事项",
        content="",
        variant="warning",
        extra_html=warning_extra,
    ), unsafe_allow_html=True)
