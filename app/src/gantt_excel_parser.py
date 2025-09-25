# -*- coding: utf-8 -*-
# @Time : 2025/9/15 10:10
# @File : gantt_excel_parser.py

"""
甘特图功能的表格提取
"""
import re
from loguru import logger
from datetime import datetime
import pandas as pd
from typing import Optional,List,Dict

def _parse_date_range(text: str) -> tuple:
    if not isinstance(text, str):
        return (None, None)
    start_str, end_str = None, None
    range_match = re.search(r'[（\(](\d{1,2}\.\d{1,2})-(\d{1,2}\.\d{1,2})[）\)]', text)
    if range_match:
        start_str, end_str = range_match.groups()
    else:
        single_match = re.search(r'[（\(](\d{1,2}\.\d{1,2})[）\)]', text)
        if single_match:
            date_str = single_match.group(1)
            start_str = date_str
            end_str = date_str
        else:
            try:
                single_date = pd.to_datetime(text, errors='coerce')
                if pd.notna(single_date):
                    date_str_formatted = single_date.strftime('%Y-%m-%d')
                    return (date_str_formatted, date_str_formatted)
            except Exception:
                pass
            return (None, None)
    if start_str is None:
        return (None, None)
    current_year = datetime.now().year
    try:
        start_month, start_day = map(int, start_str.split('.'))
        end_month, end_day = map(int, end_str.split('.'))
        start_date = datetime(current_year, start_month, start_day)
        end_year = current_year + 1 if end_month < start_month else current_year
        end_date = datetime(end_year, end_month, end_day)
        return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    except (ValueError, AttributeError):
        logger.warning(f"在文本 '{text}' 中发现无效日期，已忽略。")
        return (None, None)


def parse_excel_to_records(file_path: str) -> Optional[List[Dict]]:
    try:
        df = pd.read_excel(file_path, sheet_name=0, header=1)
        column_mapping = {
            "工作步骤": "阶段", "工作内容": "工作子项", "成果文件": "成果文件",
            "主责单位": "主责单位/负责人", "完成时限": "完成时限"
        }
        required_input_cols = list(column_mapping.keys())
        if not all(col in df.columns for col in required_input_cols):
            missing_cols = [col for col in required_input_cols if col not in df.columns]
            logger.error(f"Excel文件中缺少必需的列: {', '.join(missing_cols)}")
            return None
        df.rename(columns=column_mapping, inplace=True)
        df[['开始日期', '结束日期']] = df['完成时限'].apply(lambda x: pd.Series(_parse_date_range(x)))
        target_columns = ["阶段", "工作子项", "成果文件", "主责单位/负责人", "开始日期", "结束日期"]
        df = df[target_columns]
        columns_to_fill = ["阶段", "主责单位/负责人"]
        df[columns_to_fill] = df[columns_to_fill].ffill()
        df = df.where(pd.notna(df), None)
        records = df.to_dict('records')
        return records
    except Exception as e:
        logger.error(f"直接解析Excel文件失败: {e}")
        return None