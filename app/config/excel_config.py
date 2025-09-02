from utils.file_utils import get_project_root
import os

# 项目根目录（通过工具函数获取，确保跨平台兼容）
PROJECT_ROOT = get_project_root()

# Excel工作表名称配置
EXCEL_SHEET_NAMES = {
    "data_detail": "甘特图数据明细",  # 数据明细页
    "gantt_image": "甘特图可视化"     # 图片页
}

# Excel列宽配置（对应“数据明细”表的列）
EXCEL_COLUMN_WIDTH = {
    "A": 15,  # 阶段
    "B": 25,  # 工作子项
    "C": 8,   # 开始日
    "D": 8,   # 结束日
    "E": 8,   # 持续天数
    "F": 35,  # 关键产出物
    "G": 20   # 阶段颜色（十六进制）
}

# Excel导出路径配置（默认存放在resources目录下）
EXCEL_FILE_NAME = "绩效评价甘特图导出文件.xlsx"
EXCEL_EXPORT_PATH = os.path.join(PROJECT_ROOT, "resources", EXCEL_FILE_NAME)

# Excel表头配置
EXCEL_HEADERS = [
    "阶段", "工作子项", "开始日", "结束日", "持续天数", "关键产出物", "阶段颜色（十六进制）"
]