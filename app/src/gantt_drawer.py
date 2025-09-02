import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pandas as pd
from config.gantt_config import GANTT_CONFIG, GANTT_IMAGE_PATH
from config.color_config import STAGE_COLOR_MAP, TEXT_COLOR_MAP
from utils.file_utils import delete_file_if_exist
from utils.log_utils import logger

def draw_gantt_chart(processed_data: pd.DataFrame) -> str:
    """
    根据处理后的数据绘制甘特图，并保存为图片
    :param processed_data: 处理后的工作数据（含阶段、开始日、结束日等）
    :return: 甘特图图片保存路径
    """
    # 1. 初始化Matplotlib配置（中文字体、负号显示）
    plt.rcParams['font.sans-serif'] = GANTT_CONFIG["font_sans_serif"]
    plt.rcParams['axes.unicode_minus'] = False
    
    # 2. 准备绘图数据（反向排序，让第一个任务在最上方）
    df_sorted = processed_data.iloc[::-1].reset_index(drop=True)
    task_count = len(df_sorted)
    # 动态调整画布高度（基础高度 + 任务数*单任务高度）
    fig_height = GANTT_CONFIG["fig_size"][1] * task_count
    fig, ax = plt.subplots(figsize=(GANTT_CONFIG["fig_size"][0], fig_height))
    
    # 3. 绘制甘特图任务条形
    for idx, (_, row) in enumerate(df_sorted.iterrows()):
        # 获取当前任务的颜色（默认黑色，避免配置缺失导致报错）
        stage_color = STAGE_COLOR_MAP.get(row["阶段"], "#000000")
        text_color = TEXT_COLOR_MAP.get(row["阶段"], "black")
        
        # 计算条形宽度（持续天数）和左起点（开始日 - 0.5，确保居中对齐）
        bar_width = row["持续天数"]
        bar_left = row["开始日"] - 0.5
        
        # 绘制条形
        ax.barh(
            y=idx,
            width=bar_width,
            left=bar_left,
            height=GANTT_CONFIG["task_bar_height"],
            color=stage_color,
            alpha=0.8,
            edgecolor="white",
            linewidth=0.5
        )
        
        # 处理任务名称（超过最大长度则截断）
        task_name = row["工作子项"]
        if len(task_name) > GANTT_CONFIG["task_name_max_len"]:
            task_name = task_name[:GANTT_CONFIG["task_name_max_len"]] + "..."
        
        # 在条形中间添加任务名称
        ax.text(
            x=bar_left + bar_width / 2,
            y=idx,
            s=task_name,
            ha="center",
            va="center",
            fontsize=GANTT_CONFIG["font_size"]["task_name"],
            color=text_color
        )
    
    # 4. 配置坐标轴和图表样式
    # Y轴：显示任务名称
    ax.set_yticks(range(task_count))
    ax.set_yticklabels(df_sorted["工作子项"], fontsize=GANTT_CONFIG["font_size"]["ytick_labels"])
    # X轴：显示工作日，设置范围
    ax.set_xlabel(GANTT_CONFIG["x_axis_label"], fontsize=GANTT_CONFIG["font_size"]["axis_label"], fontweight="bold")
    ax.set_xlim(GANTT_CONFIG["x_axis_limit"])
    # 标题
    ax.set_title(GANTT_CONFIG["title"], fontsize=GANTT_CONFIG["font_size"]["title"], fontweight="bold", pad=20)
    
    # 隐藏上、右坐标轴（更简洁）
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 5. 添加阶段颜色图例（去重，避免重复显示）
    legend_elements = [
        Rectangle((0, 0), 1, 1, facecolor=color, alpha=0.8, label=stage)
        for stage, color in STAGE_COLOR_MAP.items()
    ]
    ax.legend(
        handles=legend_elements,
        loc=GANTT_CONFIG["legend_loc"],
        bbox_to_anchor=GANTT_CONFIG["legend_bbox_to_anchor"],
        fontsize=GANTT_CONFIG["font_size"]["legend"]
    )
    
    # 6. 保存图片（先删除旧图，避免覆盖问题）
    delete_file_if_exist(GANTT_IMAGE_PATH)
    plt.tight_layout()  # 自动调整布局，避免文字截断
    plt.savefig(GANTT_IMAGE_PATH, dpi=GANTT_CONFIG["dpi"], bbox_inches="tight")
    plt.close(fig)  # 关闭画布，释放内存
    
    logger.info(f"甘特图绘制完成，保存路径：{GANTT_IMAGE_PATH}")
    return GANTT_IMAGE_PATH