import pandas as pd
import xlsxwriter
from itertools import cycle
from datetime import date, timedelta

# ===============================================================
# === 数据区: 请直接在这里修改任务的开始和结束日期 ===
# ===============================================================
work_data = [
    # 绩效自评阶段
    {"阶段": "绩效自评阶段", "工作子项": "明确抽查目的", "开始日期": "2025-10-01", "结束日期": "2025-10-06"},
    {"阶段": "绩效自评阶段", "工作子项": "确定抽查对象和内容", "开始日期": "2025-10-01", "结束日期": "2025-10-06"},
    {"阶段": "绩效自评阶段", "工作子项": "执行评价方法", "开始日期": "2025-10-01", "结束日期": "2025-10-06"},
    {"阶段": "绩效自评阶段", "工作子项": "评审核验", "开始日期": "2025-10-01", "结束日期": "2025-10-06"},
    # 启动阶段
    {"阶段": "启动阶段", "工作子项": "明确评价任务", "开始日期": "2025-10-01", "结束日期": "2025-10-01"},
    {"阶段": "启动阶段", "工作子项": "组建评价团队", "开始日期": "2025-10-01", "结束日期": "2025-10-01"},
    {"阶段": "启动阶段", "工作子项": "召开启动会议", "开始日期": "2025-10-02", "结束日期": "2025-10-02"},
    # 评价准备阶段
    {"阶段": "评价准备阶段", "工作子项": "制定沟通计划", "开始日期": "2025-10-03", "结束日期": "2025-10-03"},
    {"阶段": "评价准备阶段", "工作子项": "开展沟通工作", "开始日期": "2025-10-04", "结束日期": "2025-10-05"},
    {"阶段": "评价准备阶段", "工作子项": "制定资料收集清单", "开始日期": "2025-10-06", "结束日期": "2025-10-06"},
    {"阶段": "评价准备阶段", "工作子项": "收集项目资料", "开始日期": "2025-10-07", "结束日期": "2025-10-08"},
    {"阶段": "评价准备阶段", "工作子项": "审核与整理资料", "开始日期": "2025-10-08", "结束日期": "2025-10-08"},
    {"阶段": "评价准备阶段", "工作子项": "设计绩效评价指标体系", "开始日期": "2025-10-09", "结束日期": "2025-10-09"},
    {"阶段": "评价准备阶段", "工作子项": "制定评价方案", "开始日期": "2025-10-09", "结束日期": "2025-10-09"},
    {"阶段": "评价准备阶段", "工作子项": "审核与完善评价方案", "开始日期": "2025-10-10", "结束日期": "2025-10-10"},
    # 实施评价阶段
    {"阶段": "实施评价阶段", "工作子项": "开展文献研究", "开始日期": "2025-10-11", "结束日期": "2025-10-12"},
    {"阶段": "实施评价阶段", "工作子项": "制定实地调研计划", "开始日期": "2025-10-13", "结束日期": "2025-10-13"},
    {"阶段": "实施评价阶段", "工作子项": "实施实地调研", "开始日期": "2025-10-14", "结束日期": "2025-10-16"},
    {"阶段": "实施评价阶段", "工作子项": "数据分析与初步结论", "开始日期": "2025-10-17", "结束日期": "2025-10-22"},
    {"阶段": "实施评价阶段", "工作子项": "与项目方沟通初步结果", "开始日期": "2025-10-23", "结束日期": "2025-10-25"},
    # 报告撰写阶段
    {"阶段": "报告撰写阶段", "工作子项": "撰写绩效评价报告初稿", "开始日期": "2025-10-26", "结束日期": "2025-10-28"},
    {"阶段": "报告撰写阶段", "工作子项": "内部评审与修改", "开始日期": "2025-10-29", "结束日期": "2025-10-29"},
    {"阶段": "报告撰写阶段", "工作子项": "定稿并提交报告", "开始日期": "2025-10-30", "结束日期": "2025-10-30"},
]
# ===============================================================

# 1. 数据准备
df = pd.DataFrame(work_data)
# 将日期字符串转换为datetime.date对象，便于比较
df['开始日期'] = pd.to_datetime(df['开始日期']).dt.date
df['结束日期'] = pd.to_datetime(df['结束日期']).dt.date

# 自动计算项目的整体开始、结束日期和总天数
project_start_date = df['开始日期'].min()
project_end_date = df['结束日期'].max()
total_days = (project_end_date - project_start_date).days + 1

unique_phases = df['阶段'].unique()
colors = cycle(['#B7DEE8', '#FCD5B4', '#C4D79B', '#D8BFD8', '#B7DDE8', '#FFDFDD', '#FFFACD'])
phase_color_map = {phase: next(colors) for phase in unique_phases}

output_filename = '项目日期进度表_V2.xlsx'

# 2. 创建Excel工作簿和工作表
workbook = xlsxwriter.Workbook(output_filename)
worksheet_gantt = workbook.add_worksheet("项目进度")
worksheet_data = workbook.add_worksheet("原始数据")

# 3. 格式化定义
format_cache = {}
def get_format(properties):
    key = tuple(sorted(properties.items()))
    if key not in format_cache:
        format_cache[key] = workbook.add_format(properties)
    return format_cache[key]

header_format = get_format({
    'bold': True, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#D9D9D9',
    'top': 1, 'bottom': 1, 'left': 1, 'right': 1
})
date_header_format = get_format({
    'bold': True, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#D9D9D9',
    'top': 1, 'bottom': 1, 'left': 1, 'right': 1, 'num_format': 'm/d'
})
full_date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})

# 4. 绘制“项目进度”工作表
worksheet_gantt.hide_gridlines(2)

worksheet_gantt.merge_range(0, 2, 0, total_days + 1, '项目日历', header_format)
worksheet_gantt.write('A1', '', get_format({'top': 1, 'left': 1}))
worksheet_gantt.write('B1', '', get_format({'top': 1, 'right': 1}))
worksheet_gantt.write('A2', '阶段', header_format)
worksheet_gantt.write('B2', '工作子项', header_format)

date_range = [project_start_date + timedelta(days=i) for i in range(total_days)]
for i, current_date in enumerate(date_range):
    worksheet_gantt.write(1, i + 2, current_date, date_header_format)

row_offset = 2
for phase, group in df.groupby('阶段', sort=False):
    start_row = row_offset
    end_row = row_offset + len(group) - 1
    phase_task_border = {'left': 1, 'right': 1, 'bottom': 1}

    phase_format = get_format({**phase_task_border, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
    if len(group) > 1:
        worksheet_gantt.merge_range(start_row, 0, end_row, 0, phase, phase_format)
    else:
        worksheet_gantt.write(start_row, 0, phase, phase_format)

    for i in range(len(group)):
        task = group.iloc[i]
        current_row = row_offset + i

        task_name_format = get_format({**phase_task_border, 'align': 'left', 'valign': 'vcenter'})
        worksheet_gantt.write(current_row, 1, task['工作子项'], task_name_format)

        for day_idx, current_date in enumerate(date_range):
            props = {'right': 1, 'bottom': 1}
            if task['开始日期'] <= current_date <= task['结束日期']:
                props['bg_color'] = phase_color_map[task['阶段']]
            worksheet_gantt.write(current_row, day_idx + 2, '', get_format(props))
    row_offset += len(group)

worksheet_gantt.set_column('A:A', 15)
worksheet_gantt.set_column('B:B', 30)
worksheet_gantt.set_column(2, total_days + 1, 6)
worksheet_gantt.freeze_panes(2, 2)

# 5. 写入“原始数据”工作表
data_header_format = workbook.add_format({'bold': True, 'fg_color': '#D9D9D9'})
for col_num, value in enumerate(df.columns.values):
    worksheet_data.write(0, col_num, value, data_header_format)
for row_num, row_data in enumerate(df.itertuples(index=False)):
     worksheet_data.write_row(row_num + 1, 0, row_data)

# 格式化日期列
worksheet_data.set_column('C:D', 12, full_date_format)
worksheet_data.autofit()

# 6. 保存并关闭文件
workbook.close()

print(f"日期版单元格甘特图已成功生成，文件名为: {output_filename}")

