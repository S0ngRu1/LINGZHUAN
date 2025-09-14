# -*- coding: utf-8 -*-
# @Time : 2025/9/12 17:54
# @Author : CSR
# @File : llm_analyze_document.py

import json
from app.config import settings
from openai import OpenAI
from typing import Dict, Optional

if not settings.MOONSHOT_API_KEY or settings.MOONSHOT_API_KEY == "YOUR_MOONSHOT_API_KEY_HERE":
    raise ValueError("错误: MOONSHOT_API_KEY 未设置。请在 app/config/settings.py 或环境变量中配置。")

api_key = settings.MOONSHOT_API_KEY
base_url = settings.MOONSHOT_BASE_URL
client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

def analyze_single_document(doc_content: str) -> Optional[Dict]:
    """
    调用LLM API，仅分析单个文档，提取摘要和大纲。
    """
    prompt = f"""
    你是一个专业的政策研究助理。你的任务是深入阅读并分析以下政策文件的全文，然后严格按照指定的JSON格式，结构化地输出你的分析结果。

    文件全文:
    ---
    {doc_content}
    ---

    输出格式要求:
    1.  必须是一个单一的、格式完全正确的JSON对象。
    2.  所有键 (key) 和字符串值 (string value) 都必须使用双引号 `"`，绝对不能使用单引号 `'`。
    3.  对象必须包含以下四个键: "publish_date", "agency", "summary", "outline"。
        * "publish_date": "发文日期 (YYYY-MM-DD格式)"
        * "agency": "发文机构"
        * "summary": "对文件主要内容的精炼摘要，约150字。"
        * "outline": 一个JSON数组，代表文件的层级大纲。数组中的每个元素都是一个对象，必须包含 "name" (章节标题) 和 "children" (一个包含子章节对象的数组) 两个键。请至少分析到三级结构（例如：章 -> 条 -> 款）。如果某个章节没有子项，则 "children" 的值应为一个空数组 `[]`。
    4.  确保整个输出是纯净的JSON，不包含任何解释、注释或Markdown标记。

    下面是一个正确的输出格式示例:
    {{
      "publish_date": "2023-10-13",
      "agency": "陕西省国资委",
      "summary": "这是一个关于文件的摘要...",
      "outline": [
        {{
          "name": "第一章 总则",
          "children": [
            {{"name": "第一条", "children": []}}
          ]
        }}
      ]
    }}
    """
    try:
        response = client.chat.completions.create(
            model=settings.MOONSHOT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=4096
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"分析单个文档时出错: {e}")
        return None

def compare_summaries(summary1: str, summary2: str) -> Optional[Dict]:
    """
    调用LLM API，仅对比两个摘要，提取区别点。
    """
    prompt = f"""
    你是一个专业的政策分析师。请对比以下两份政策文件的摘要，找出它们之间的核心区别，并严格按照指定的JSON格式输出。

    文件一摘要:
    ---
    {summary1}
    ---

    文件二摘要:
    ---
    {summary2}
    ---

    输出格式要求:
    1.  必须是一个单一的JSON对象，且只包含一个顶级键 "comparison"。
    2.  "comparison" 键对应一个JSON数组（列表）。
    3.  数组中的每个元素都是一个JSON对象，代表一个具体的对比维度。每个对象必须包含以下三个键：
        * "dimension": 对比的维度或方面。
        * "document1_point": 文件一在这个维度上的具体要点。
        * "document2_point": 文件二在这个维度上的具体要点。
    4.  请找出至少5个关键的区别点进行对比。
    5.  确保整个输出是纯净的、格式正确的JSON。
    """
    try:
        response = client.chat.completions.create(
            model=settings.MOONSHOT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2048
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"对比摘要时出错: {e}")
        return None
