# -*- coding: utf-8 -*-
# @Time : 2025/9/5 17:48
# @Author : CSR
# @File : gantt_generator.py

import os
import pandas as pd
import xlsxwriter
from itertools import cycle
from typing import List, Dict, Optional
from app.config import settings

# 使用字典缓存格式，避免重复创建，提升效率
format_cache = {}


def _get_format(workbook: xlsxwriter.Workbook, properties: Dict) -> xlsxwriter.format.Format:
    """获取或创建一个缓存的单元格格式。"""
    key = tuple(sorted(properties.items()))
    if key not in format_cache:
        format_cache[key] = workbook.add_format(properties)
    return format_cache[key]


def create_gantt_chart(work_data: List[Dict[str, str]], output_filename: str) -> bool:
    """
    根据解析出的工作数据，创建一个单元格渲染的Excel甘特图。
    """
    if not work_data:
        print("错误：没有提供用于生成甘特图的数据。")
        return False

    try:
        df = pd.DataFrame(work_data)
        df['开始日期'] = pd.to_datetime(df['开始日期'])
        df['结束日期'] = pd.to_datetime(df['结束日期'])
    except (KeyError, pd.errors.ParserError) as e:
        print(f"错误: 输入数据格式不正确或日期无法解析 - {e}")
        return False

    # 1. 收集所有唯一的开始和结束日期
    all_task_dates = pd.to_datetime(pd.concat([df['开始日期'], df['结束日期']]).unique())
    # 2. 排序后形成我们的日历
    calendar_dates = sorted(all_task_dates)
    if not calendar_dates:
        print("错误：未能从任务中提取任何有效日期。")
        return False

    unique_phases = df['阶段'].unique()
    colors = cycle(['#B7DEE8', '#FCD5B4', '#C4D79B', '#D8BFD8', '#B7DDE8', '#FFDFDD', '#FFFACD'])
    phase_color_map = {phase: next(colors) for phase in unique_phases}

    output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)

    workbook = xlsxwriter.Workbook(output_path)
    worksheet_gantt = workbook.add_worksheet("项目进度")
    worksheet_data = workbook.add_worksheet("原始数据")

    # 清空上一轮的格式缓存
    format_cache.clear()

    # --- 绘制甘特图 ---
    worksheet_gantt.hide_gridlines(2)

    header_format = _get_format(workbook, {
        'bold': True, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#D9D9D9',
        'top': 1, 'bottom': 1, 'left': 1, 'right': 1
    })

    # 写入总标题，其宽度由日历中的日期数量决定
    worksheet_gantt.merge_range(0, 2, 0, len(calendar_dates) + 1, '工作日', header_format)
    worksheet_gantt.write('A1', '', _get_format(workbook, {'top': 1, 'left': 1}))
    worksheet_gantt.write('B1', '', _get_format(workbook, {'top': 1, 'right': 1}))

    # 写入列标题
    worksheet_gantt.write('A2', '阶段', header_format)
    worksheet_gantt.write('B2', '工作子项', header_format)
    for i, date in enumerate(calendar_dates):
        worksheet_gantt.write(1, i + 2, date.strftime('%Y/%m/%d'), header_format)

    # 写入主体内容
    row_offset = 2
    for phase, group in df.groupby('阶段', sort=False):
        start_row = row_offset
        end_row = row_offset + len(group) - 1

        # --- 修改: 为所有单元格定义统一的完整边框 ---
        full_border_props = {'top': 1, 'bottom': 1, 'left': 1, 'right': 1}

        # 阶段单元格格式
        phase_props = {
            **full_border_props,
            'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True
        }
        phase_format = _get_format(workbook, phase_props)
        if len(group) > 1:
            worksheet_gantt.merge_range(start_row, 0, end_row, 0, phase, phase_format)
        else:
            worksheet_gantt.write(start_row, 0, phase, phase_format)

        for i in range(len(group)):
            task = group.iloc[i]
            current_row = row_offset + i

            # 工作子项单元格格式
            task_name_props = {**full_border_props, 'align': 'left', 'valign': 'vcenter'}
            worksheet_gantt.write(current_row, 1, task['工作子项'], _get_format(workbook, task_name_props))

            # 日期单元格格式
            for j, calendar_date in enumerate(calendar_dates):
                # 从完整边框开始
                props = {**full_border_props}

                # 如果在任务范围内，则添加背景色
                if task['开始日期'] <= calendar_date <= task['结束日期']:
                    props['bg_color'] = phase_color_map[task['阶段']]

                worksheet_gantt.write(current_row, j + 2, '', _get_format(workbook, props))

        row_offset += len(group)

    worksheet_gantt.set_column('A:A', 15)
    worksheet_gantt.set_column('B:B', 30)
    worksheet_gantt.set_column(2, len(calendar_dates) + 1, 11)
    worksheet_gantt.freeze_panes(2, 2)

    # --- 写入原始数据 ---
    df_original = pd.DataFrame(work_data)
    data_header_format = _get_format(workbook, {'bold': True, 'fg_color': '#D9D9D9'})
    for col_num, value in enumerate(df_original.columns.values):
        worksheet_data.write(0, col_num, value, data_header_format)
    for row_num, row_data in enumerate(df_original.values):
        worksheet_data.write_row(row_num + 1, 0, row_data)
    worksheet_data.autofit()

    try:
        workbook.close()
        print(f"甘特图已成功生成: {output_path}")
        return True
    except xlsxwriter.exceptions.FileCreateError as e:
        print(f"错误: 无法写入Excel文件。请检查文件是否被其他程序占用。 - {e}")
        return False
