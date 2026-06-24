import re
import streamlit as st


def _html(s):
    s = re.sub(r'[\r\n\t]+', ' ', s)
    s = re.sub(r'>\s+<', '><', s)
    s = re.sub(r'\s{2,}', ' ', s)
    return s.strip()


def render_html(s):
    st.markdown(_html(s), unsafe_allow_html=True)


def get_theme_styles(theme="light"):
    if theme == "dark":
        bg_main = "#0a0e1a"
        bg_sidebar = "rgba(15,20,35,0.95)"
        bg_card = "rgba(255,255,255,0.05)"
        bg_card_strong = "rgba(255,255,255,0.08)"
        text_primary = "#f1f5f9"
        text_secondary = "#cbd5e1"
        text_muted = "#94a3b8"
        border_color = "rgba(255,255,255,0.12)"
        glow_color = "rgba(59,130,246,0.25)"
        accent_gradient = "linear-gradient(135deg,#3b82f6,#8b5cf6,#22d3ee)"
        nav_text = "#ffffff"
        nav_hover = "rgba(255,255,255,0.08)"
        widget_bg = "rgba(255,255,255,0.06)"
        widget_border = "rgba(255,255,255,0.15)"
        upload_bg = "rgba(255,255,255,0.04)"
        alert_bg = "rgba(255,255,255,0.04)"
        info_bg = "rgba(59,130,246,0.12)"
        success_bg = "rgba(16,185,129,0.12)"
        warning_bg = "rgba(245,158,11,0.12)"
        error_bg = "rgba(244,63,94,0.12)"
        code_bg = "rgba(0,0,0,0.3)"
        caption_color = "#94a3b8"
        theme_mode = "dark"
    else:
        bg_main = "#f8fafc"
        bg_sidebar = "rgba(241,245,249,0.95)"
        bg_card = "rgba(255,255,255,0.85)"
        bg_card_strong = "rgba(255,255,255,1)"
        text_primary = "#1e293b"
        text_secondary = "#475569"
        text_muted = "#64748b"
        border_color = "rgba(15,23,42,0.1)"
        glow_color = "rgba(59,130,246,0.15)"
        accent_gradient = "linear-gradient(135deg,#3b82f6,#8b5cf6)"
        nav_text = "#1e293b"
        nav_hover = "rgba(59,130,246,0.1)"
        widget_bg = "rgba(255,255,255,0.95)"
        widget_border = "rgba(15,23,42,0.15)"
        upload_bg = "rgba(255,255,255,0.8)"
        alert_bg = "rgba(255,255,255,0.8)"
        info_bg = "rgba(59,130,246,0.08)"
        success_bg = "rgba(16,185,129,0.08)"
        warning_bg = "rgba(245,158,11,0.08)"
        error_bg = "rgba(244,63,94,0.08)"
        code_bg = "rgba(15,23,42,0.05)"
        caption_color = "#64748b"
        theme_mode = "light"

    # 深浅主题共用 —— 输入控件的样式由变量决定，深浅模式统一覆盖
    nav_selected_text = "#ffffff" if theme_mode == "dark" else "#1e293b"
    nav_selected_shadow = "rgba(59,130,246,0.3)" if theme_mode == "dark" else "rgba(59,130,246,0.18)"
    nav_selected_bg = "rgba(59,130,246,0.18)" if theme_mode == "dark" else "rgba(59,130,246,0.12)"

    # 深色模式下主容器的基础背景与文字色（浅色模式依赖 config.toml 的默认浅色基调 + 下方组件层覆盖）
    if theme_mode == "dark":
        root_override = f"""
        [data-testid="stAppViewContainer"],[data-testid="stAppViewContainer"]>.main {{ background:{bg_main} !important; color:{text_primary} !important; }}
        [data-testid="stAppViewContainer"] .block-container,[data-testid="stAppViewContainer"] .stMarkdown,[data-testid="stAppViewContainer"] p,[data-testid="stAppViewContainer"] li,[data-testid="stAppViewContainer"] span,[data-testid="stAppViewContainer"] h1,[data-testid="stAppViewContainer"] h2,[data-testid="stAppViewContainer"] h3,[data-testid="stAppViewContainer"] h4,[data-testid="stAppViewContainer"] h5,[data-testid="stAppViewContainer"] h6,[data-testid="stAppViewContainer"] div {{ color:{text_primary} !important; }}
        [data-testid="stSidebar"] {{ background:{bg_sidebar} !important; color:{text_primary} !important; }}
        [data-testid="stSidebar"] * {{ color:{text_primary} !important; }}
        .stTextInput>label,.stNumberInput>label,.stSelectbox>label,.stTextArea>label,.stSlider>label,.stDateInput>label,.stTimeInput>label,.stFileUploader>label,.stMultiSelect>label {{ color:{text_primary} !important; }}
        [data-testid="stHeader"] {{ background:{bg_main} !important; color:{text_primary} !important; }}
        [data-testid="stMetricValue"] {{ color:{text_primary} !important; }}
        [data-testid="stMetricDelta"]>div,[data-testid="stMetricDelta"] span {{ color:#22c55e !important; }}
        [data-testid="stMetricLabel"] p,[data-testid="stMetricLabel"] span {{ color:{text_muted} !important; font-size:0.75rem !important; }}
        small,.stCaption,[data-testid="stCaptionContainer"] {{ color:{caption_color} !important; }}
        code {{ background:{code_bg} !important; color:#60a5fa !important; border-radius:4px; padding:1px 6px; }}
        hr {{ border-color:{border_color} !important; background:{border_color} !important; }}
        """
    else:
        root_override = f"""
        [data-testid="stSidebar"] {{ background:{bg_sidebar} !important; }}
        small,.stCaption,[data-testid="stCaptionContainer"] {{ color:{caption_color} !important; }}
        code {{ background:{code_bg} !important; color:#2563eb !important; border-radius:4px; padding:1px 6px; }}
        hr {{ border-color:{border_color} !important; background:{border_color} !important; }}
        """

    # 输入控件层（深浅模式都覆盖，颜色由变量决定）
    widgets_override = f"""
    .stTextInput input,.stNumberInput input,.stTextArea textarea,.stDateInput input,.stTimeInput input {{ background-color:{widget_bg} !important; color:{text_primary} !important; border-color:{widget_border} !important; border-radius:10px !important; }}
    .stTextInput input::placeholder,.stNumberInput input::placeholder,.stTextArea textarea::placeholder {{ color:{text_muted} !important; }}
    .stSelectbox [data-baseweb="select"]>div:first-child,.stMultiSelect [data-baseweb="select"]>div:first-child {{ background-color:{widget_bg} !important; border-color:{widget_border} !important; border-radius:10px !important; }}
    .stSelectbox [data-baseweb="select"] div,.stSelectbox [data-baseweb="select"] span,.stSelectbox input,.stSelectbox [role="combobox"] div, .stSelectbox [role="combobox"] span, .stSelectbox [data-baseweb="select"] [role="combobox"] div, .stMultiSelect [data-baseweb="select"] div,.stMultiSelect [data-baseweb="select"] span,.stMultiSelect input {{ color:{text_primary} !important; }}
    .stSelectbox [data-baseweb="select"] ul li,.stMultiSelect [data-baseweb="select"] ul li {{ background-color:{widget_bg} !important; color:{text_primary} !important; }}
    .stSelectbox [data-baseweb="select"] ul li:hover,.stMultiSelect [data-baseweb="select"] ul li:hover {{ background-color:{nav_hover} !important; }}
    .stSlider [data-baseweb="slider"] [role="slider"] {{ background:#3b82f6 !important; }}
    .stSlider [data-testid="stTickBar"] {{ background:{widget_border} !important; }}
    div[data-testid="stFileUploader"], [data-testid="stFileUploader"] {{ background:{upload_bg} !important; background-color:{upload_bg} !important; background-image:none !important; border:1.5px dashed {widget_border} !important; border-radius:16px !important; backdrop-filter:blur(12px); padding:0.2rem 0.8rem; }}
    div[data-testid="stFileUploader"] section, div[data-testid="stFileUploader"] div, div[data-testid="stFileUploader"] button, div[data-testid="stFileUploader"] span, div[data-testid="stFileUploader"] small, div[data-testid="stFileUploader"] p, div[data-testid="stFileUploader"] label, div[data-testid="stFileUploader"] [data-testid], div[data-testid="stFileUploader"] [role], div[data-testid="stFileUploader"] [class] {{ background:transparent !important; background-color:transparent !important; background-image:none !important; color:{text_primary} !important; }}
    div[data-testid="stFileUploader"] [style] {{ background:transparent !important; background-color:transparent !important; background-image:none !important; }}
    [data-testid="stAlert"] {{ background:{alert_bg} !important; border-color:{border_color} !important; }}
    [data-testid="stAlertContainer"][data-testid*="info"] {{ background:{info_bg} !important; }}
    [data-testid="stAlertContainer"][data-testid*="success"] {{ background:{success_bg} !important; }}
    [data-testid="stAlertContainer"][data-testid*="warning"] {{ background:{warning_bg} !important; }}
    [data-testid="stAlertContainer"][data-testid*="error"] {{ background:{error_bg} !important; }}
    """

    css = f"""
    <style>
    {root_override}
    {widgets_override}

    .stApp {{ background:{bg_main} !important; }}
    .stApp::before {{ content:""; position:fixed; top:-20%; left:-10%; width:500px; height:500px; background:radial-gradient(circle,{glow_color},transparent 70%); border-radius:50%; filter:blur(120px); pointer-events:none; z-index:0; }}
    .stApp::after {{ content:""; position:fixed; bottom:-10%; right:-5%; width:600px; height:600px; background:radial-gradient(circle,rgba(168,85,247,0.08),transparent 70%); border-radius:50%; filter:blur(140px); pointer-events:none; z-index:0; }}
    .block-container {{ z-index:1; padding-top:2rem !important; }}

    .main-header {{ font-size:2.2rem !important; font-weight:800 !important; background:{accent_gradient}; -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; letter-spacing:-0.02em; margin-bottom:0.5rem; }}
    .section-title {{ font-size:1.35rem !important; font-weight:700 !important; color:{text_primary}; margin-top:1rem; }}
    .glow-divider {{ height:1px; background:linear-gradient(90deg,transparent,rgba(99,179,237,0.5),transparent); margin:1.2rem 0; border:none; }}

    [data-testid="stSidebar"] {{ background:{bg_sidebar} !important; border-right:1px solid {border_color} !important; box-shadow:4px 0 30px rgba(0,0,0,0.08); }}
    [data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 {{ background:{accent_gradient}; -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-weight:700; }}
    [data-testid="stSidebarNavLink"] {{ border-radius:12px !important; margin:4px 8px; padding:12px 16px !important; transition:all 0.25s; color:{nav_text} !important; border:1px solid transparent !important; font-size:1rem !important; font-weight:600 !important; }}
    [data-testid="stSidebarNavLink"]:hover {{ background:{nav_hover} !important; color:{nav_text} !important; transform:translateX(4px); border-color:rgba(99,179,237,0.3) !important; }}
    [data-testid="stSidebarNavLink"][aria-selected="true"] {{ background:{nav_selected_bg} !important; color:{nav_selected_text} !important; border:1px solid rgba(99,179,237,0.4) !important; backdrop-filter:blur(20px) saturate(180%); -webkit-backdrop-filter:blur(20px) saturate(180%); box-shadow:0 8px 32px {nav_selected_shadow}, inset 0 1px 0 rgba(255,255,255,0.1); }}
    [data-testid="stSidebarNavLink"][aria-selected="true"]:hover {{ background:rgba(59,130,246,0.25) !important; }}

    .stButton > button, .stFormSubmitButton > button {{ background:{widget_bg} !important; border:1px solid {widget_border} !important; border-radius:12px !important; color:{text_primary} !important; font-weight:600 !important; padding:0.5rem 1.2rem !important; transition:all 0.25s !important; }}
    .stButton > button:hover {{ transform:translateY(-2px) !important; border-color:rgba(99,179,237,0.4) !important; box-shadow:0 8px 28px rgba(59,130,246,0.25) !important; }}

    [data-testid="stAlert"] {{ background:{alert_bg} !important; backdrop-filter:blur(16px); border:1px solid {border_color} !important; border-left:4px solid #3b82f6 !important; border-radius:14px !important; box-shadow:0 4px 20px rgba(0,0,0,0.1); padding:1rem 1.2rem !important; }}

    .glass-card {{ background:{bg_card}; backdrop-filter:blur(20px) saturate(180%); -webkit-backdrop-filter:blur(20px) saturate(180%); border:1px solid {border_color}; border-radius:20px; padding:1.3rem; margin-bottom:14px; box-shadow:0 8px 32px rgba(0,0,0,0.08),inset 0 1px 0 rgba(255,255,255,0.08); transition:all 0.3s cubic-bezier(0.4,0,0.2,1); position:relative; overflow:hidden; color:{text_primary}; }}
    .glass-card:hover {{ transform:translateY(-3px); box-shadow:0 20px 50px rgba(0,0,0,0.12),0 0 40px rgba(59,130,246,0.08),inset 0 1px 0 rgba(255,255,255,0.1); border-color:rgba(99,179,237,0.3); }}
    .glass-card-primary {{ background:linear-gradient(135deg,rgba(59,130,246,0.15),rgba(139,92,246,0.1)) !important; border-color:rgba(59,130,246,0.3) !important; box-shadow:0 8px 32px rgba(59,130,246,0.15) !important; }}
    .glass-card-success {{ background:linear-gradient(135deg,rgba(16,185,129,0.15),rgba(34,211,238,0.1)) !important; border-color:rgba(16,185,129,0.3) !important; }}
    .glass-card-warning {{ background:linear-gradient(135deg,rgba(245,158,11,0.15),rgba(239,68,68,0.1)) !important; border-color:rgba(245,158,11,0.3) !important; }}
    .glass-card-danger {{ background:linear-gradient(135deg,rgba(244,63,94,0.15),rgba(239,68,68,0.1)) !important; border-color:rgba(244,63,94,0.3) !important; }}

    .card-label {{ font-size:0.78rem; color:{text_secondary}; text-transform:uppercase; letter-spacing:0.05em; font-weight:600; }}
    .card-title {{ font-size:1.05rem; font-weight:700; color:{text_primary}; margin:0.2rem 0; }}
    .glow-number {{ font-size:2.2rem; font-weight:800; background:{accent_gradient}; -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; line-height:1.1; margin:0.3rem 0; }}
    .glow-number-success {{ background:linear-gradient(135deg,#10b981,#22d3ee); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }}
    .glow-number-warning {{ background:linear-gradient(135deg,#f59e0b,#ef4444); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }}
    .glow-number-danger {{ background:linear-gradient(135deg,#f43f5e,#ef4444); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }}

    .progress-track {{ width:100%; height:8px; background:rgba(0,0,0,0.06); border:1px solid {border_color}; border-radius:999px; overflow:hidden; position:relative; margin-top:4px; }}
    .bar-chart-row {{ display:flex; align-items:flex-end; gap:12px; height:180px; padding:1rem 0; position:relative; }}
    .bar-chart-bar {{ flex:1; border-radius:10px 10px 4px 4px; min-height:6px; position:relative; transition:all 0.4s ease; }}
    .bar-chart-label {{ text-align:center; font-size:0.72rem; color:{text_secondary}; margin-top:0.5rem; }}
    .donut-chart {{ width:160px; height:160px; border-radius:50%; position:relative; box-shadow:0 0 40px {glow_color}; margin:0 auto; }}
    .donut-chart::after {{ content:""; position:absolute; inset:20px; background:{bg_main}; border-radius:50%; backdrop-filter:blur(20px); }}

    #MainMenu, footer, .stDeployButton, [data-testid="stDecoration"], [data-testid="stStatusWidget"] {{ visibility:hidden; display:none !important; }}
    [data-testid="stHeader"] {{ background:{bg_main} !important; border-bottom:1px solid {border_color} !important; height:0 !important; min-height:0 !important; }}
    </style>
    """
    return _html(css)


def inject_common_styles(theme="light"):
    st.markdown(get_theme_styles(theme), unsafe_allow_html=True)


def glass_card(title="", content="", icon="", variant="default", extra_html=""):
    vmap = {"primary": "glass-card-primary", "success": "glass-card-success",
            "warning": "glass-card-warning", "danger": "glass-card-danger"}
    vc = vmap.get(variant, "")
    icon_part = ('<span style="font-size:1.8rem;filter:drop-shadow(0 0 10px rgba(59,130,246,0.6));display:inline-block;">' + icon + '</span>') if icon else ""
    title_part = ('<div class="card-title">' + title + '</div>') if title else ""
    content_part = ('<div style="margin-top:0.3rem;line-height:1.7;">' + content + '</div>') if content else ""
    extra_part = ('<div style="margin-top:0.8rem;">' + extra_html + '</div>') if extra_html else ""
    return _html('<div class="glass-card ' + vc + '">' + icon_part + title_part + content_part + extra_part + '</div>')


def metric_card(label, value, icon="", delta="", variant="primary"):
    gmap = {"primary": "", "success": "glow-number-success",
            "warning": "glow-number-warning", "danger": "glow-number-danger"}
    cmap = {"success": "glass-card-success", "warning": "glass-card-warning",
            "danger": "glass-card-danger", "primary": "glass-card-primary"}
    gc = gmap.get(variant, "")
    cc = cmap.get(variant, "")
    icon_part = ('<span style="font-size:1.8rem;filter:drop-shadow(0 0 10px rgba(59,130,246,0.6));display:inline-block;">' + icon + '</span>') if icon else ""
    delta_part = ('<span style="display:inline-block;padding:2px 10px;border-radius:999px;font-size:0.72rem;font-weight:600;background:linear-gradient(135deg,#3b82f6,#22d3ee);color:#fff;margin-top:4px;">' + delta + '</span>') if delta else ""
    return _html('<div class="glass-card ' + cc + '"><div style="display:flex;align-items:center;justify-content:space-between;gap:8px;"><div><div class="card-label">' + label + '</div><div class="glow-number ' + gc + '">' + str(value) + '</div>' + delta_part + '</div>' + icon_part + '</div></div>')


def progress_bar(percent, label="", variant="primary"):
    percent = max(0.0, min(100.0, float(percent)))
    bg_map = {"primary": "linear-gradient(135deg,#3b82f6,#8b5cf6,#22d3ee)",
              "success": "linear-gradient(135deg,#10b981,#22d3ee)",
              "warning": "linear-gradient(135deg,#f59e0b,#ef4444)",
              "danger": "linear-gradient(135deg,#f43f5e,#ef4444)"}
    bg = bg_map.get(variant, bg_map["primary"])
    label_part = ('<div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:6px;"><span>' + label + '</span><span style="font-weight:700;">' + str(round(percent, 1)) + '%</span></div>') if label else ""
    return _html(label_part + '<div class="progress-track"><div style="width:' + str(percent) + '%;height:100%;border-radius:999px;background:' + bg + ';box-shadow:0 0 12px rgba(59,130,246,0.7);"></div></div>')


def bar_chart(values, labels=None, max_val=None, variant="primary"):
    labels = labels or ["#" + str(i + 1) for i in range(len(values))]
    if max_val is None:
        max_val = max(values) if values else 1
    if max_val <= 0:
        max_val = 1
    grad_map = {"primary": "linear-gradient(180deg,#60a5fa,#3b82f6,#8b5cf6)",
                "success": "linear-gradient(180deg,#34d399,#10b981,#22d3ee)",
                "warning": "linear-gradient(180deg,#fbbf24,#f59e0b,#f43f5e)",
                "danger": "linear-gradient(180deg,#fb7185,#ef4444)"}
    grad = grad_map.get(variant, grad_map["primary"])
    bars_html = ""
    for v, lbl in zip(values, labels):
        h = max(4, (v / max_val) * 160)
        bars_html += '<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:6px;"><div style="font-size:0.72rem;font-weight:600;">' + str(round(v, 1)) + '%</div><div style="flex:1;width:100%;min-height:' + str(h) + 'px;border-radius:10px 10px 4px 4px;background:' + grad + ';box-shadow:0 0 14px rgba(59,130,246,0.45);"></div><div class="bar-chart-label">' + str(lbl) + '</div></div>'
    return _html('<div class="bar-chart-row">' + bars_html + '</div>')


def donut_chart(percent, center_label="", center_value=""):
    percent = max(0.0, min(100.0, float(percent)))
    return _html('<div style="display:flex;flex-direction:column;align-items:center;gap:0.5rem;"><div class="donut-chart" style="background:conic-gradient(#22d3ee 0%,#3b82f6 ' + str(percent) + '%,rgba(0,0,0,0.08) ' + str(percent) + '%,rgba(0,0,0,0.08) 100%);"><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;z-index:2;flex-direction:column;"><div style="font-size:2rem;font-weight:800;background:linear-gradient(135deg,#3b82f6,#8b5cf6,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">' + str(center_value) + '</div><div style="font-size:0.72rem;">' + center_label + '</div></div></div></div>')


def section_header(title, subtitle="", emoji=""):
    emoji_part = ('<span style="font-size:1.4rem;margin-right:8px;">' + emoji + '</span>') if emoji else ""
    subtitle_part = ('<div style="font-size:0.82rem;margin-top:0.2rem;">' + subtitle + '</div>') if subtitle else ""
    return _html('<div style="margin:1.2rem 0 0.6rem 0;"><div class="section-title">' + emoji_part + title + '</div>' + subtitle_part + '</div><hr class="glow-divider"/>')


def divider():
    return '<hr class="glow-divider"/>'
