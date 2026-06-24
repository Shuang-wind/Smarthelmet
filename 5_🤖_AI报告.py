"""
AI 报告页面 —— 玻璃质感 Bento 风格
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="AI 报告 - 安全帽检测系统",
    page_icon="",
    layout="wide",
)

if "theme" not in st.session_state or st.session_state.theme not in ["dark", "light", "system"]:
    st.session_state.theme = "light"

from utils.styles import inject_common_styles, metric_card, glass_card, section_header, progress_bar, bar_chart, donut_chart, divider
inject_common_styles(theme=st.session_state.theme)

# 标题
st.markdown('<h1 class="main-header">AI 安全分析报告</h1>', unsafe_allow_html=True)
st.caption("基于 LLM 大语言模型，自动生成安全帽佩戴情况分析报告")
st.markdown('<hr class="glow-divider" />', unsafe_allow_html=True)

# 控制区
col_ctrl, col_preview = st.columns([1, 2])

with col_ctrl:
    st.markdown(glass_card(
        title="报告配置",
        content="选择报告类型与时间范围",
        variant="primary",
        extra_html="",
    ), unsafe_allow_html=True)
    report_type = st.selectbox("报告类型", ["日报", "周报", "月报", "专项报告"], index=0)
    time_range = st.selectbox("时间范围", ["今日", "近3天", "近7天", "近30天"], index=0)

    # 数据汇总 / 示例数据
    if "detection_history" in st.session_state and st.session_state.detection_history:
        latest_stats = st.session_state.detection_history[-1]
        st.success(f"已加载最新检测数据（{latest_stats.get('timestamp', '未知时间')}）")
    else:
        st.warning("暂无检测数据，将使用示例数据生成报告")
        latest_stats = {
            'total_persons': 12,
            'helmet_count': 10,
            'head_count': 2,
            'violation_rate': 16.7,
            'timestamp': '2026-06-10 10:00:00',
        }

    stats_for_llm = {
        'total_workers': latest_stats.get('total_persons', 0),
        'helmet_count': latest_stats.get('helmet_count', 0),
        'head_count': latest_stats.get('no_helmet_count', latest_stats.get('head_count', 0)),
        'violation_rate': latest_stats.get('violation_rate', 0) / 100.0
        if latest_stats.get('violation_rate', 0) > 1
        else latest_stats.get('violation_rate', 0),
    }

    generate_btn = st.button("生成 AI 报告", type="primary", key="gen_report")

with col_preview:
    report_info_extra = '<div style="line-height:1.9;"><div>检测数据统计与分析</div><div>风险评估与预警</div><div>改进建议与措施</div><div>趋势分析与预测</div><div style="margin-top:0.5rem;opacity:0.7;font-size:0.85rem;">技术栈：Ollama + qwen:4b 本地大模型<br>服务地址：http://localhost:11434</div></div>'
    st.markdown(glass_card(
        title="报告说明",
        content="",
        variant="success",
        extra_html=report_info_extra,
    ), unsafe_allow_html=True)

    # 显示关键指标
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(metric_card("检测人数", stats_for_llm['total_workers'], icon="", variant="primary"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("佩戴安全帽", stats_for_llm['helmet_count'], icon="", variant="success"), unsafe_allow_html=True)
    with c3:
        rate_pct = stats_for_llm['violation_rate'] * 100 if stats_for_llm['violation_rate'] <= 1 else stats_for_llm['violation_rate']
        st.markdown(metric_card("违规率", f"{rate_pct:.1f}%", icon="",
                                variant="warning" if rate_pct > 5 else "success"), unsafe_allow_html=True)

if generate_btn:
    with st.spinner("AI 正在分析数据并生成报告..."):
        try:
            from utils.llm_report import generate_report
            report = generate_report(stats_for_llm)

            # 检查是否返回了错误信息
            if report.startswith("[错误]"):
                has_error = True
                error_msg = report
            else:
                has_error = False
                error_msg = None
        except Exception as e:
            report = f"""
# 安全帽智能检测系统 —— {report_type}

> **生成时间**：自动生成
> **时间范围**：{time_range}
> **检测总人数**：{stats_for_llm['total_workers']} 人
> **佩戴安全帽人数**：{stats_for_llm['helmet_count']} 人
> **未佩戴人数**：{stats_for_llm['head_count']} 人
> **违规率**：{rate_pct:.1f}%

---

## 一、数据概览

本次检测共识别 {stats_for_llm['total_workers']} 名人员，其中 {stats_for_llm['helmet_count']} 人正确佩戴安全帽，{stats_for_llm['head_count']} 人存在未佩戴安全帽的违规行为，综合违规率为 **{rate_pct:.1f}%**。

## 二、风险评估

- **整体安全等级**：{ '优' if rate_pct < 5 else '良' if rate_pct < 15 else '中' if rate_pct < 30 else '高' }
- **建议关注区域**：脚手架作业区、材料堆放区、电梯井口
- **高风险时段**：上午 8:00-10:00 / 下午 14:00-16:00

## 三、改进建议

1. 对未佩戴安全帽人员进行现场提醒与教育
2. 在脚手架与塔吊区域加强巡查与广播提醒
3. 对工人进行安全培训，完善考勤与入场登记制度
4. 每日生成安全报告并公示

## 四、趋势预测

若维持当前趋势，预计未来一周违规率将 {"下降 5%" if rate_pct > 10 else "保持稳定"}。

> *报告由本地 LLM 自动生成，仅供安全管理参考。*
>
> *错误信息：{e}*
"""
            has_error = True
            error_msg = str(e)

    # 只有在没有错误时才显示报告
    if not has_error:
        st.markdown(section_header("报告预览", f"{report_type} · {time_range}"), unsafe_allow_html=True)
        st.markdown(glass_card(
            title="AI 报告内容",
            content="",
            variant="primary",
            extra_html="",
        ), unsafe_allow_html=True)
        st.markdown(report)

        c_sav, c_cpy = st.columns(2)
        with c_sav:
            if st.button("保存报告"):
                try:
                    from utils.llm_report import save_report
                    fp = save_report(report, stats_for_llm)
                    st.success(f"报告已保存到：{fp}")
                except Exception as e:
                    st.warning(f"保存失败：{e}")
        with c_cpy:
            if st.button("复制报告"):
                st.toast("报告内容已复制到剪贴板！")
    else:
        st.error(f"报告生成失败：{error_msg}")
        st.info("请确保 Ollama 服务正在运行 (http://localhost:11434)，并已安装 qwen:4b 模型")
else:
    st.markdown(section_header("使用说明", "请点击左侧「生成 AI 报告」按钮"), unsafe_allow_html=True)
    flow_extra = '<div style="line-height:1.9;"><div>1. 先在图片检测或视频检测页面进行检测，数据会自动汇总</div><div>2. 回到本页面，点击生成 AI 报告按钮</div><div>3. AI 将基于最新检测数据生成安全分析报告</div><div>4. 报告可保存为 Markdown 文件或复制到剪贴板</div><div style="margin-top:0.5rem;opacity:0.7;font-size:0.85rem;">需要本地安装并运行 Ollama（qwen:4b 模型）</div></div>'
    st.markdown(glass_card(
        title="生成流程",
        content="",
        variant="success",
        extra_html=flow_extra,
    ), unsafe_allow_html=True)
