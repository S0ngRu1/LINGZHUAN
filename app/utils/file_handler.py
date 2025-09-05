# -*- coding: utf-8 -*-
# @Time : 2025/9/5 17:53
# @Author : CSR
# @File : file_handler.py

import os
from typing import Optional
import docx
import pdfplumber


def read_file_content(file_path: str) -> Optional[str]:
    """
    智能读取多种格式的文件内容（txt, docx, pdf）。

    Args:
        file_path (str): 文件的完整路径。

    Returns:
        Optional[str]: 提取出的纯文本内容，如果文件格式不支持或读取失败则返回 None。
    """
    try:
        # 获取文件扩展名
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()

        print(f"尝试读取文件: {file_path}, 格式: {file_extension}")

        if file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

        elif file_extension == '.docx':
            doc = docx.Document(file_path)
            full_text = [para.text for para in doc.paragraphs]
            return '\n'.join(full_text)

        elif file_extension == '.pdf':
            full_text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    # extract_text() 能够很好地处理大多数文本型PDF
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
            return full_text

        else:
            print(f"错误: 不支持的文件格式 '{file_extension}'。目前仅支持 .txt, .docx, .pdf。")
            return None

    except FileNotFoundError:
        print(f"错误: 文件未找到 -> {file_path}")
        return None
    except Exception as e:
        print(f"处理文件时发生错误: {e}")
        return None

