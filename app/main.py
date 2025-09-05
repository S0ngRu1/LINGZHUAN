# -*- coding: utf-8 -*-
# @Time : 2025/9/5 17:49
# @Author : CSR
# @File : main.py

import os
from app.utils.file_handler import read_file_content
from app.src.llm_parser import parse_schedule_from_text
from app.src.gantt_generator import create_gantt_chart
from app.config import settings


def main():
    """
    主函数，协调整个流程：
    1. 读取输入文件。
    2. 调用LLM解析内容。
    3. 如果解析成功，则生成甘特图。
    """
    # --- 1. 定义输入和输出路径 ---
    input_file_path = "../resources/XX私募股权投资基金项目工作计划.pdf"

    # 确保输出目录存在
    if not os.path.exists(settings.OUTPUT_DIR):
        os.makedirs(settings.OUTPUT_DIR)

    # --- 2. 读取文件内容 ---
    print(f"--- 步骤 1: 读取输入文件: {input_file_path} ---")
    file_content = read_file_content(input_file_path)
    if not file_content:
        return

    # --- 3. 调用 LLM 解析 ---
    print("\n--- 步骤 2: 使用 AI 模型解析文件内容 ---")
    work_data = parse_schedule_from_text(file_content)

    # --- 4. 生成甘特图 ---
    if work_data:
        print("\n--- 步骤 3: 基于解析结果生成甘特图 ---")
        create_gantt_chart(work_data, settings.DEFAULT_GANTT_FILENAME)
    else:
        print("\n解析失败，无法生成甘特图。")


if __name__ == "__main__":
    main()
