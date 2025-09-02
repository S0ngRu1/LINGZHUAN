from utils.file_utils import get_project_root
import os

# 项目根目录
PROJECT_ROOT = get_project_root()

# 甘特图图片配置
GANTT_CONFIG = {
    "fig_size": (16, 0.6),  # 画布大小（宽，高/任务数），高会根据任务数量动态调整
    "dpi": 300,             # 图片清晰度（300为高清，适合打印）
    "font_sans_serif": ["SimHei", "DejaVu Sans"],  # 中文字体支持
    "task_bar_height": 0.6, # 任务条形高度
    "task_name_max_len": 15, # 任务名称最大长度（超过会截断加“...”）
    "x_axis_label": "计划工作日（共40天）",  # X轴标签
    "title": "绩效评价工作甘特图（按阶段颜色区分）",  # 图表标题
    "x_axis_limit": (0, 41), # X轴范围（留出余量）
    "legend_loc": "upper right",  # 图例位置
    "legend_bbox_to_anchor": (1.25, 1),  # 图例偏移（避免遮挡）
    "font_size": {
        "title": 12,
        "axis_label": 10,
        "task_name": 8,
        "legend": 8,
        "ytick_labels": 8
    }
}

# 甘特图图片保存配置
GANTT_IMAGE_NAME = "temp_gantt_chart.png"
GANTT_IMAGE_PATH = os.path.join(PROJECT_ROOT, "resources", "temp", GANTT_IMAGE_NAME)