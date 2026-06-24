# Smart Helmet Guard - 安全帽检测系统

基于 YOLOv8 的安全帽佩戴检测系统，支持图片、视频、实时摄像头检测，并集成 AI 报告生成。

## 项目结构

```
Elegent-main/
├── app.py                 # Streamlit 主程序（v2.0 玻璃质感 UI）
├── pages/                 # 各功能页面
│   ├── 1_📸_图片检测.py
│   ├── 2_🎥_视频检测.py
│   ├── 3_📹_实时摄像头.py
│   ├── 4_📊_统计看板.py
│   ├── 5_🤖_AI报告.py
│   ├── 6_📁_历史记录.py
│   └── 7_🚨_危险区域检测.py
├── utils/                 # 工具模块
│   ├── detect.py          # YOLO 检测核心
│   ├── zone_check.py      # 危险区域判定
│   ├── llm_report.py      # AI 报告生成
│   ├── get_statistics.py  # 统计计算
│   ├── styles.py          # UI 样式（玻璃质感）
│   └── fake_data.py       # 模拟数据
├── models/                # 模型权重（运行时放入 best.pt）
├── training/              # 训练相关
│   ├── train.py           # 本地训练脚本
│   ├── colab_train.ipynb  # Google Colab 训练
│   ├── download_dataset.py
│   └── remove_person.py
├── assets/                # 静态资源（训练可视化图片）
├── outputs/               # 检测输出
├── reports/               # 生成的报告
├── requirements.txt        # Python 依赖
└── .gitignore            # Git 排除规则
```

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 下载模型
将训练好的 `best.pt` 放入 `models/` 目录。
> 模型权重约 22MB，请从百度网盘（待补充链接）下载后放入 `models/` 目录。

### 3. 运行应用
```bash
streamlit run app.py
```

## 模型训练

### 本地训练
```bash
python training/train.py
```

### Google Colab 训练
上传 `training/colab_train.ipynb` 到 Google Colab，使用免费 T4 GPU 训练。

## 训练结果

### 训练配置

| 项目 | 配置 |
|------|------|
| 模型 | YOLOv8s（平衡精度与速度） |
| 训练环境 | Google Colab T4 GPU |
| Epochs | 50 |
| 优化器 | SGD |
| 学习率 | 0.01 |
| 输入尺寸 | 640×640 |
| 数据集 | Hard Hat Workers（Roboflow） |

### 综合指标

| 指标 | 数值 |
|------|:----:|
| mAP50 | **94.95%** |
| mAP50-95 | 63.33% |
| Precision | 92.80% |
| Recall | 89.70% |
| 单帧推理耗时 | 8.0 ms |

### 各类别表现

| 类别 | mAP50 | Precision | Recall |
|------|:-----:|:---------:|:------:|
| 安全帽 (helmet) | **96.1%** | 94.1% | 90.6% |
| 头部 (head) | **93.8%** | 91.5% | 88.8% |

> **说明**：初始 3 类设置（含 person）因样本不足（仅34张）导致整体 mAP 仅 63.3%。经消融实验验证，移除 person 类后 mAP50 跃升至 **94.95%**，模型效果优异。详见项目报告。

### 训练可视化

#### 训练过程曲线
![训练曲线](assets/results.png)

> 从上到下依次为：Box Loss、Cls Loss、DFL Loss、mAP50、mAP50-95。训练在第 30 轮后趋于收敛，验证集指标稳定。

#### 混淆矩阵
![混淆矩阵](assets/confusion_matrix.png)

> 混淆矩阵显示 `helmet` 和 `head` 分类准确，基本无混淆。`person` 类因样本不足已在最终版本中移除。

#### P-R 曲线
![P-R曲线](assets/PR_curve_dark.png)

> P-R 曲线显示 `helmet` 和 `head` 两类在 mAP0.5 阈值下均达到 0.9 以上，曲线下面积大，模型对这两类的检测非常可靠。

## 功能特性

- 🎨 **玻璃质感 UI（v2.0）**：Bento 风格布局，支持深色/浅色/跟随系统三种主题
- 📸 **多模式检测**：图片、视频、实时摄像头三种输入
- 📊 **实时统计看板**：Plotly 交互式图表，违规趋势可视化
- 🤖 **AI 报告生成**：基于大语言模型自动生成安全分析报告
- 🚨 **危险区域自定义**：支持任意多边形区域划定与违规判定
- 📁 **历史记录**：保存每次检测数据，支持回溯对比

## 技术栈

- **检测模型**: YOLOv8 (Ultralytics)
- **前端框架**: Streamlit（v2.0 玻璃质感 UI）
- **AI 报告**: 大语言模型集成（支持 Ollama 本地 / 通义千问 API）
- **可视化**: Plotly, Matplotlib

## 团队

- **A（周欣然）**：模型训练、检测核心模块、危险区域判定、消融实验设计
- **B（谭艺）**：Streamlit 前端界面、玻璃质感 UI 设计、可视化看板
- **C（陈依婷）**：LLM 报告模块、项目报告撰写、演示视频录制

## 许可证

本项目为课程作业项目，仅供学习交流使用。
