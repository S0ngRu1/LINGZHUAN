# -*- coding: utf-8 -*-
# @Time : 2025/9/12 17:54
# @Author : CSR
# @File : llm_analyze_document.py
import os
import json
from app.config import settings
from openai import OpenAI

if not settings.MOONSHOT_API_KEY or settings.MOONSHOT_API_KEY == "YOUR_MOONSHOT_API_KEY_HERE":
    raise ValueError("错误: MOONSHOT_API_KEY 未设置。请在 app/config/settings.py 或环境变量中配置。")

api_key = settings.MOONSHOT_API_KEY
base_url = settings.MOONSHOT_BASE_URL


client = OpenAI(
    api_key=api_key,
    base_url=base_url,
)


def analyze_documents(content1: str, content2: str) -> dict:
    """
    调用大模型分析两个文档，提取关键信息并进行对比。
    """
    # 截取部分内容以防文本过长超出模型限制
    max_length = 8000
    content1_snippet = content1[:max_length]
    content2_snippet = content2[:max_length]

    prompt = f"""
    你是一个专业的政策分析助理。请仔细阅读并分析以下两份文件，然后严格按照指定的JSON格式输出分析结果。

    文件一内容:
    ---
    {content1_snippet}
    ---

    文件二内容:
    ---
    {content2_snippet}
    ---

    请根据上述内容，提取以下信息并进行对比：
    1.  为每份文件提取“发文日期”、“发文机构”和“文件主要内容”的摘要。
    2.  总结并列出“两个文件的主要区别点”。

    输出格式要求:
    - 必须是一个单独的、完整的JSON对象。
    - JSON对象必须包含三个键: "document1", "document2", "comparison"。
    - "document1" 和 "document2" 的值也必须是JSON对象，包含 "publish_date", "agency", "summary" 三个键。
    - "publish_date" 的值必须是 "YYYY-MM-DD" 格式的字符串。
    - "summary" 和 "comparison" 的值必须是详细的、总结性的文本字符串。
    - 不要包含任何JSON格式之外的解释、注释或文字。
    """

    try:
        response = client.chat.completions.create(
            # 建议使用支持长文本和稳定JSON输出的模型
            model="moonshot-v1-8k",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,  # 使用较低的温度以获得更精确的格式化输出
            response_format={"type": "json_object"}  # 请求JSON格式输出
        )

        response_text = response.choices[0].message.content
        return json.loads(response_text)

    except Exception as e:
        print(f"调用大模型API时发生错误: {e}")
        # 在真实错误中，可以尝试不请求JSON格式作为备用方案
        # 这里我们直接返回None
        return None
