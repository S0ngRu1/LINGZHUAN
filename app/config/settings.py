# -*- coding: utf-8 -*-
# @Time : 2025/9/5 15:45
# @Author : CSR
# @File : settings.py
import os

# --- Moonshot AI API 配置 ---
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY", "sk-rEigbFYiLqzHtt45zk4jN6FEnLwWYUpmLBhK6f7ONQGoq2br")
MOONSHOT_BASE_URL = "https://api.moonshot.cn/v1"
# 使用 Kimi 智能体进行内容解析
MOONSHOT_MODEL = "kimi-k2-turbo-preview"
# --- 输出文件配置 ---
OUTPUT_DIR = "../output"
DEFAULT_GANTT_FILENAME = "项目甘特图1.xlsx"
# --- 文本处理配置 ---
# 为处理大文件，文本将被分割成块。
# CHUNK_SIZE: 每个文本块的目标大小（以字符为单位）。
# CHUNK_OVERLAP: 块与块之间的重叠字符数，以防止任务描述被切断。
CHUNK_SIZE = 1e4
CHUNK_OVERLAP = 200