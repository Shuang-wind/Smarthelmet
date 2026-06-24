"""
危险区域检测页面 —— 多边形绘制 + 区域内违规检测
"""
import streamlit as st
import cv2
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="危险区域检测 - 安全帽检测系统",
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
        key="page_theme_selector_7",
    )
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    st.markdown("---")

# 懒加载
@st.cache_resource
def load_zone_checker():
    from utils.zone_check import HelmetZoneChecker
    return HelmetZoneChecker(model_path='models/best.pt', zone_polygon=[])

# 标题
st.markdown('<h1 class="main-header">危险区域检测</h1>', unsafe_allow_html=True)
st.caption("在图片上绘制危险区域多边形，检测区域内未佩戴安全帽的人员")
st.markdown('<hr class="glow-divider" />', unsafe_allow_html=True)

# 上传区
col_upload, col_info = st.columns([2, 1])

with col_upload:
    st.markdown(glass_card(
        title="选择监控图片",
        content="上传现场图片，在图片上绘制危险区域",
        variant="warning",
        extra_html="",
    ), unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "选择图片文件",
        type=["jpg", "jpeg", "png", "bmp"],
        help="支持 JPG / PNG / BMP 格式",
        label_visibility="collapsed",
    )

with col_info:
    usage_extra = '<div style="line-height:1.8;"><div>1. 上传施工现场监控图片</div><div>2. 在图片上点击绘制危险区域（至少 3 点）</div><div>3. 点击开始检测按钮分析区域内安全帽佩戴情况</div><div>4. 红色高亮区域内未佩戴安全帽的人员</div></div>'
    st.markdown(glass_card(
        title="使用说明",
        content="",
        variant="primary",
        extra_html=usage_extra,
    ), unsafe_allow_html=True)

if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if image is not None:
        h, w = image.shape[:2]
        if "zone_points" not in st.session_state:
            st.session_state.zone_points = []
        if "zone_done" not in st.session_state:
            st.session_state.zone_done = False

        st.markdown(section_header("步骤 1：绘制危险区域", f"图片尺寸 {w} x {h}"), unsafe_allow_html=True)

        col_img, col_ctrl = st.columns([2, 1])
        with col_img:
            st.markdown(glass_card(
                title="原始图片",
                content="",
                variant="primary",
                extra_html="",
            ), unsafe_allow_html=True)
            st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), use_container_width=True)

        with col_ctrl:
            st.markdown(glass_card(
                title="输入区域顶点",
                content="在图片上找到危险区域的顶点，输入坐标",
                variant="warning",
                extra_html="",
            ), unsafe_allow_html=True)
            c_x, c_y = st.columns(2)
            with c_x:
                new_x = st.number_input("X 坐标", min_value=0, max_value=w, value=w // 2, step=10)
            with c_y:
                new_y = st.number_input("Y 坐标", min_value=0, max_value=h, value=h // 2, step=10)

            if st.button("添加顶点", type="secondary"):
                st.session_state.zone_points.append((int(new_x), int(new_y)))
                st.rerun()

            # 已添加的点
            if st.session_state.zone_points:
                st.markdown(f"**已添加 {len(st.session_state.zone_points)} 个顶点：**")
                for i, (px, py) in enumerate(st.session_state.zone_points):
                    cc1, cc2 = st.columns([3, 1])
                    cc1.markdown(f"`#{i+1}: ({px}, {py})`")
                    if cc2.button("", key=f"del_{i}"):
                        st.session_state.zone_points.pop(i)
                        st.rerun()

            if st.button("完成绘制", type="primary", disabled=len(st.session_state.zone_points) < 3):
                st.session_state.zone_done = True
                st.rerun()
            if st.button("重新绘制"):
                st.session_state.zone_points = []
                st.session_state.zone_done = False
                st.rerun()

        # 预览区
        if st.session_state.zone_points:
            preview = image.copy()
            pts = np.array(st.session_state.zone_points, np.int32).reshape((-1, 1, 2))
            cv2.polylines(preview, [pts], st.session_state.zone_done, (0, 165, 255), 3)
            for i, (px, py) in enumerate(st.session_state.zone_points):
                cv2.circle(preview, (px, py), 7, (0, 255, 255), -1)
                cv2.putText(preview, str(i + 1), (px + 10, py - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            if st.session_state.zone_done:
                overlay = preview.copy()
                cv2.fillPoly(overlay, [pts], (0, 0, 255))
                preview = cv2.addWeighted(overlay, 0.25, preview, 0.75, 0)

            st.markdown(section_header("区域预览", "检查绘制的多边形是否准确"), unsafe_allow_html=True)
            st.image(cv2.cvtColor(preview, cv2.COLOR_BGR2RGB), use_container_width=True)

        # 检测区
        if st.session_state.zone_done and st.session_state.zone_points:
            st.markdown(section_header("步骤 2：开始检测", "AI 识别区域内违规人员"), unsafe_allow_html=True)
            if st.button("开始检测", type="primary"):
                with st.spinner("YOLOv8 正在检测危险区域..."):
                    checker = load_zone_checker()
                    checker.set_zone(st.session_state.zone_points)
                    det_list = []
                    try:
                        from utils.detect import detect as _detect_fn
                        from shapely.geometry import Point, Polygon
                        detections = _detect_fn(image)
                        poly = Polygon(st.session_state.zone_points)
                        helmet_in_zone = 0
                        head_in_zone = 0
                        zone_violations = []
                        for d in detections:
                            x1, y1, x2, y2 = [int(v) for v in d["bbox"]]
                            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                            if poly.contains(Point(cx, cy)):
                                if d["class"] == "helmet":
                                    helmet_in_zone += 1
                                else:
                                    head_in_zone += 1
                                    zone_violations.append(d)
                        total_helmet = sum(1 for d in detections if d["class"] == "helmet")
                        total_head = sum(1 for d in detections if d["class"] != "helmet")
                        r = {
                            "helmet_in_zone": helmet_in_zone,
                            "head_in_zone": head_in_zone,
                            "violation_count": head_in_zone,
                            "total_helmet": total_helmet,
                            "total_head": total_head,
                            "zone_violations": zone_violations,
                            "detections": detections,
                        }
                    except Exception as e:
                        r = {"helmet_in_zone": 0, "head_in_zone": 0, "violation_count": 0,
                             "total_helmet": 0, "total_head": 0, "zone_violations": [],
                             "detections": []}
                        st.warning(f"危险区域检测逻辑回退：{e}")

                    # 绘制
                    result_img = image.copy()
                    pts = np.array(st.session_state.zone_points, np.int32).reshape((-1, 1, 2))
                    cv2.polylines(result_img, [pts], True, (0, 165, 255), 3)
                    overlay = result_img.copy()
                    cv2.fillPoly(overlay, [pts], (0, 0, 255))
                    result_img = cv2.addWeighted(overlay, 0.2, result_img, 0.8, 0)

                    try:
                        from shapely.geometry import Point, Polygon
                        poly = Polygon(st.session_state.zone_points)
                    except Exception:
                        poly = None

                    for d in r.get("detections", []):
                        x1, y1, x2, y2 = [int(v) for v in d["bbox"]]
                        in_zone = True
                        if poly is not None:
                            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                            in_zone = poly.contains(Point(cx, cy))
                        if d["class"] == "helmet":
                            color = (16, 185, 129)
                        else:
                            color = (239, 68, 68) if in_zone else (180, 180, 200)
                        o = result_img.copy()
                        cv2.rectangle(o, (x1, y1), (x2, y2), color, 6)
                        cv2.addWeighted(o, 0.35, result_img, 0.65, 0, result_img)
                        cv2.rectangle(result_img, (x1, y1), (x2, y2), color, 2)
                        label = f"{'OK' if d['class'] == 'helmet' else 'VIOLATION'} {d['confidence']:.0%}"
                        cv2.putText(result_img, label, (x1, y1 - 5),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                col_res, col_stat = st.columns([2, 1])
                with col_res:
                    st.markdown(glass_card(
                        title="检测结果",
                        content="红色高亮区域内违规人员",
                        variant="warning",
                        extra_html="",
                    ), unsafe_allow_html=True)
                    st.image(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB), use_container_width=True)

                with col_stat:
                    st.markdown(glass_card(
                        title="区域统计",
                        content="",
                        variant="primary",
                        extra_html="",
                    ), unsafe_allow_html=True)
                    st.markdown(metric_card("区域内人数", r["helmet_in_zone"] + r["head_in_zone"],
                                            icon="", variant="primary"), unsafe_allow_html=True)
                    st.markdown(metric_card("戴安全帽", r["helmet_in_zone"], icon="", variant="success"), unsafe_allow_html=True)
                    st.markdown(metric_card("违章人数", r["violation_count"], icon="", variant="warning"), unsafe_allow_html=True)
                    st.markdown(metric_card("全图人头", r["total_head"], icon="", variant="primary"), unsafe_allow_html=True)

                    total_in_zone = r["helmet_in_zone"] + r["head_in_zone"]
                    if total_in_zone > 0:
                        rate = r["violation_count"] / total_in_zone * 100
                        rate_variant = "danger" if rate > 15 else "warning" if rate > 5 else "success"
                        st.markdown(glass_card(
                            title="区域违规率",
                            content=f"{rate:.1f}%",
                            variant=rate_variant,
                            extra_html=f'<div style="margin-top:0.8rem;">{progress_bar(rate, "违规率", rate_variant)}</div>',
                        ), unsafe_allow_html=True)

                # 违规详情
                if r.get("zone_violations"):
                    with st.expander("违规详情", expanded=True):
                        for i, v in enumerate(r["zone_violations"]):
                            st.error(f"违章 #{i+1}: 位置 {v['bbox']} | 置信度 {v['confidence']:.1%}")
                else:
                    st.success("危险区域内未发现违章人员！")

                # 保存到 session_state
                if "detection_history" not in st.session_state:
                    st.session_state.detection_history = []
                from utils.get_statistics import get_statistics
                stats = get_statistics(r.get("detections", []))
                st.session_state.detection_history.append(stats)

    else:
        st.error("无法解析图片文件。")
else:
    st.markdown(section_header("上传图片开始绘制危险区域", "请先选择一张监控图片"), unsafe_allow_html=True)
