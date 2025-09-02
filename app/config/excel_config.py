# Excel工作表名称
EXCEL_SHEET_NAMES = {
    "data": "甘特图数据明细",
    "image": "甘特图可视化"
}
# Excel列宽配置（对应“数据明细”表）
EXCEL_COLUMN_WIDTH = {
    "A": 15,  # 阶段
    "B": 25,  # 工作子项
    "C": 8,   # 开始日
    "D": 8,   # 结束日
    "E": 8,   # 持续天数
    "F": 35,  # 关键产出物
    "G": 20   # 阶段颜色
}
# Excel导出路径（默认存放在resources目录下）
EXCEL_EXPORT_PATH = "resources/绩效评价甘特图导出文件.xlsx"