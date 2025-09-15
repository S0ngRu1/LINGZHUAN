# -*- coding: utf-8 -*-
# @Time : 2025/9/5 15:45
# @Author : CSR
# @File : settings.py
import os

# --- Moonshot AI API 配置 ---
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")

if not MOONSHOT_API_KEY:
    raise ValueError("错误：环境变量 MOONSHOT_API_KEY 未设置。请在项目根目录创建 .env 文件并填入您的 API Key。")

MOONSHOT_BASE_URL = "https://api.moonshot.cn/v1"
MOONSHOT_MODEL = "kimi-k2-turbo-preview"

# --- 文本处理配置 ---
CHUNK_SIZE = 1e4
CHUNK_OVERLAP = 200