"""
安全帽智能检测系统 - 主入口
Helmet Detection System — Streamlit Frontend
"""
import streamlit as st
import sys
from pathlib import Path

# 确保 utils 可导入
sys.path.insert(0, str(Path(__file__).parent))

# ============================================================
# 页面全局配置（必须在第一个 st 命令之前）
# ============================================================
st.set_page_config(
    page_title="安全帽智能检测系统",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 主题（必须放在侧边栏之前，以读取 session_state）
# ============================================================
if "theme" not in st.session_state or st.session_state.theme not in ["dark", "light", "system"]:
    st.session_state.theme = "light"

from utils.styles import inject_common_styles, metric_card, glass_card, section_header, progress_bar, bar_chart, donut_chart, divider

if st.session_state.theme == "system":
    import platform
    if platform.system() == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            st.session_state.theme = "light" if value == 1 else "dark"
        except:
            st.session_state.theme = "dark"
    else:
        st.session_state.theme = "dark"

inject_common_styles(theme=st.session_state.theme)

st.markdown(f'<script>document.documentElement.setAttribute("data-theme", "{st.session_state.theme}"); document.body.setAttribute("data-theme", "{st.session_state.theme}");</script>', unsafe_allow_html=True)

# ============================================================
# 侧边栏 —— 玻璃质感 + 主题切换
# ============================================================
with st.sidebar:
    # 品牌标题
    st.markdown("## 安全帽检测系统")
    st.caption("AI Powered · YOLOv8 · Glassmorphism UI")
    st.markdown("---")

    # 主题切换器
    st.markdown("### 主题设置")
    new_theme = st.selectbox(
        "选择主题",
        options=["dark", "light", "system"],
        format_func=lambda x: {
            "dark": "深色主题（推荐）",
            "light": "浅色主题",
            "system": "跟随系统",
        }.get(x, x),
        label_visibility="collapsed",
        index=["dark", "light", "system"].index(st.session_state.theme),
        key="sidebar_theme_selector",
    )
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    st.markdown("---")

    # 系统状态卡片 —— 玻璃质感
    st.markdown("### 系统状态")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("模型", "YOLOv8", delta="就绪")
    with col2:
        st.metric("GPU", "可用", delta="正常")

    st.markdown("---")

    # 快捷导航说明
    st.info("使用左侧 **文件导航** 在各功能页面之间切换。")

    st.markdown("---")
    st.markdown("### 关于")
    st.caption("""
    **安全帽智能检测系统 v2.0**

    基于 YOLOv8 深度学习模型，
    实现施工场景安全帽佩戴检测。

    AI 驱动 · 实时检测 · 智能分析
    """)

# ============================================================
# 首页内容 —— 玻璃质感 Bento 风格
# ============================================================


# 主标题
st.markdown('<h1 class="main-header">安全帽智能检测系统</h1>', unsafe_allow_html=True)
st.caption("实时监控 · AI 驱动 · 全方位安全守护")
st.markdown('<hr class="glow-divider" />', unsafe_allow_html=True)

# ============================================================
# 顶部统计卡片 (Bento 风格 —— 4 列大指标卡)
# ============================================================
st.markdown(section_header("今日概览", "核心指标实时监控"), unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(metric_card("今日检测", "1,284", "", "↑ 12%", "primary"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("违规次数", "37", "", "↓ 5%", "warning"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("佩戴率", "97.1%", "", "↑ 2.3%", "success"), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card("在线时长", "8h 32m", "", "运行中", "primary"), unsafe_allow_html=True)

# ============================================================
# 第二行：欢迎 + 进度条 (Bento 风格 —— 左大右小)
# ============================================================
st.markdown(section_header("系统简介", "功能一览"), unsafe_allow_html=True)

col_welcome, col_progress = st.columns([2, 1])

with col_welcome:
    st.markdown(glass_card(
        title="欢迎来到新一代安全监控平台",
        content="本系统基于 **YOLOv8** 深度学习模型，针对建筑施工场景实现：**图片检测** —— 上传图片自动识别；**视频检测** —— 逐帧分析；**实时摄像头** —— 实时检测与预警；**统计看板** —— 可视化展示；**AI 报告** —— 自动生成报告；**历史记录** —— 浏览检测历史",
        icon="",
        variant="primary",
    ), unsafe_allow_html=True)

with col_progress:
    pb1 = progress_bar(97.1, "综合佩戴率", "success")
    pb2 = progress_bar(85.0, "区域合规度", "primary")
    pb3 = progress_bar(12.5, "高危风险占比", "warning")
    st.markdown(glass_card(
        title="安全评分",
        content="综合佩戴率与违规趋势，系统为您打分",
        icon="",
        variant="success",
        extra_html=f'<div style="margin-top:1rem;">{pb1}</div><div style="margin-top:1rem;">{pb2}</div><div style="margin-top:1rem;">{pb3}</div>',
    ), unsafe_allow_html=True)

# ============================================================
# 第三行：区域柱状图 + 环形数据卡
# ============================================================
st.markdown(section_header("各区域违规率", "基于今日真实检测数据"), unsafe_allow_html=True)

col_bar, col_donut1, col_donut2 = st.columns([2, 1, 1])

with col_bar:
    areas = ["A区-基坑", "B区-脚手架", "C区-材料区", "D区-塔吊", "E区-电梯井"]
    rates = [2.1, 5.8, 3.2, 1.5, 7.3]
    st.markdown(glass_card(
        title="各区域违规率（%）",
        content="",
        variant="default",
        extra_html=bar_chart(values=rates, labels=areas, max_val=10.0, variant="primary"),
    ), unsafe_allow_html=True)

with col_donut1:
    st.markdown(glass_card(
        title="佩戴率",
        content="",
        variant="success",
        extra_html=donut_chart(97.1, "佩戴合规", "97.1%"),
    ), unsafe_allow_html=True)

with col_donut2:
    st.markdown(glass_card(
        title="AI 报告",
        content="",
        variant="primary",
        extra_html=donut_chart(75, "报告完成度", "75%"),
    ), unsafe_allow_html=True)

# ============================================================
# 第四行：功能入口卡片
# ============================================================
st.markdown(section_header("快速开始", "选择功能模块开始使用"), unsafe_allow_html=True)

col_feat_1, col_feat_2, col_feat_3, col_feat_4 = st.columns(4)
with col_feat_1:
    st.markdown(metric_card("图片检测", "上传 · 识别", icon="", variant="primary"), unsafe_allow_html=True)
with col_feat_2:
    st.markdown(metric_card("视频检测", "逐帧 · 分析", icon="", variant="success"), unsafe_allow_html=True)
with col_feat_3:
    st.markdown(metric_card("实时摄像头", "预警 · 直播", icon="", variant="warning"), unsafe_allow_html=True)
with col_feat_4:
    st.markdown(metric_card("AI 报告", "一键生成", icon="", variant="primary"), unsafe_allow_html=True)

# 底部提示
st.markdown('<hr class="glow-divider" />', unsafe_allow_html=True)
st.info("使用左侧导航栏切换功能页面。第一周使用模拟数据演示，第二周将接入真实 YOLOv8 模型。")
