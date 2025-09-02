import logging
from utils.file_utils import LOG_DIR
import os
from datetime import datetime

def init_logger() -> logging.Logger:
    """
    初始化日志配置（同时输出到控制台和文件）
    :return: 日志对象
    """
    # 日志文件名（含日期，避免覆盖）
    log_file_name = f"performance_gantt_{datetime.now().strftime('%Y%m%d')}.log"
    log_file_path = os.path.join(LOG_DIR, log_file_name)
    
    # 日志格式配置
    log_format = "%(asctime)s - %(levelname)s - %(module)s:%(funcName)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # 创建日志对象
    logger = logging.getLogger("performance_gantt_logger")
    logger.setLevel(logging.INFO)  # 日志级别（INFO及以上会被记录）
    
    # 避免重复添加处理器
    if not logger.handlers:
        # 控制台处理器（输出到屏幕）
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format, date_format))
        
        # 文件处理器（输出到日志文件）
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        
        # 添加处理器到日志对象
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger

# 初始化日志对象（供其他模块直接导入使用）
logger = init_logger()