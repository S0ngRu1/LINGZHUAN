# -*- coding: utf-8 -*-
# @Time : 2025/9/5 17:49
# @Author : CSR
# @File : llm_parser.py

# app/src/llm_parser.py

import json
from loguru import logger
from typing import List, Dict, Optional, Tuple, Set
from openai import OpenAI
from app.config import settings


def _split_text_into_chunks(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """
    将长文本分割成更小的、有重叠的块。
    会尝试在换行符处分割以保持上下文的完整性。
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start_index = 0
    while start_index < len(text):
        end_index = start_index + chunk_size

        # 如果不是最后一个块，则寻找一个合适的分割点（换行符）来避免切断句子
        if end_index < len(text):
            split_point = text.rfind('\n', start_index, end_index)
            if split_point != -1 and split_point > start_index:
                end_index = split_point

        chunks.append(text[start_index:end_index])

        # 计算下一个块的起始位置，确保有重叠
        next_start = start_index + chunk_size - chunk_overlap
        # 防止因分割点前移和重叠导致原地踏步
        if next_start <= start_index:
            next_start = start_index + 1

        start_index = next_start

    return chunks


def _parse_single_chunk(client: OpenAI, chunk_content: str, chunk_num: int, total_chunks: int) -> Optional[List[Dict]]:
    """
    为单个文本块调用 LLM API 并进行解析。
    """
    prompt = f"""
        你是一个专业的项目管理助理。请从以下文本中提取所有的项目任务安排，并严格按照指定的JSON格式输出。

        文本内容 (这是第 {chunk_num}/{total_chunks} 部分):
        ---
        {chunk_content}
        ---

        输出格式要求:
        1. 必须是一个JSON数组（列表）。
        2. 数组中的每个元素都是一个JSON对象（字典）。
        3. 每个对象必须包含且仅包含以下四个键："阶段", "工作子项", "开始日期", "结束日期"。
        4. "开始日期" 和 "结束日期" 的值必须是 "YYYY-MM-DD" 格式的字符串。
        5. 如果文本中没有可提取的任务，请返回一个空数组 `[]`。
        6. 不要包含任何JSON格式之外的解释、注释或文字。只输出纯净的JSON。
    """
    try:
        response = client.chat.completions.create(
            model=settings.MOONSHOT_MODEL,
            messages=[
                {"role": "system", "content": "你是一个精准的数据提取助手，严格遵循用户的指令输出纯净的JSON数据。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )

        json_content = response.choices[0].message.content.strip()

        if json_content.startswith("```json"):
            json_content = json_content[7:-3].strip()

        # 尝试修复因截断导致的JSON不完整问题
        if not json_content.endswith("]"):
            # 找到最后一个有效的 '}' 并在此处截断，然后补全 ']'
            last_brace = json_content.rfind('}')
            if last_brace != -1:
                json_content = json_content[:last_brace + 1] + "]"

        parsed_data = json.loads(json_content)

        if not isinstance(parsed_data, list):
            logger.warning(f"警告: 第 {chunk_num} 部分返回的数据不是一个列表，已忽略。")
            return None

        return parsed_data

    except json.JSONDecodeError:
        logger.warning(f"警告: 第 {chunk_num} 部分返回的内容不是有效的JSON格式，已忽略。内容预览: '{json_content[:150]}...'")
        return None
    except Exception as e:
        logger.error(f"警告: 调用API处理第 {chunk_num} 部分时发生错误: {e}")
        return None


def _deduplicate_tasks(tasks: List[Dict]) -> List[Dict]:
    """
    由于块之间有重叠，需要对最终结果进行去重。
    """
    unique_tasks: List[Dict] = []
    seen_tasks: Set[Tuple] = set()

    for task in tasks:
        # 创建一个可哈希的项（元组）来代表这个任务字典
        task_tuple = tuple(sorted(task.items()))
        if task_tuple not in seen_tasks:
            seen_tasks.add(task_tuple)
            unique_tasks.append(task)

    return unique_tasks


def parse_schedule_from_text(file_content: str) -> Optional[List[Dict]]:
    """
    使用 Moonshot AI API 从文本内容中解析出项目计划。
    对于长文本，会自动分块处理并对结果去重。
    """
    if not settings.MOONSHOT_API_KEY or settings.MOONSHOT_API_KEY == "YOUR_MOONSHOT_API_KEY_HERE":
        logger.error("错误: MOONSHOT_API_KEY 未设置。请在 app/config/settings.py 或环境变量中配置。")
        return None

    client = OpenAI(api_key=settings.MOONSHOT_API_KEY, base_url=settings.MOONSHOT_BASE_URL)

    text_chunks = _split_text_into_chunks(
        file_content,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )
    total_chunks = len(text_chunks)

    if total_chunks > 1:
        logger.info(f"文本过长，已自动分割成 {total_chunks} 个部分进行处理。")

    all_tasks = []
    for i, chunk in enumerate(text_chunks):
        if total_chunks > 1:
            logger.info(f"--- 正在处理第 {i + 1}/{total_chunks} 部分 ---")

        parsed_chunk = _parse_single_chunk(client, chunk, i + 1, total_chunks)

        if parsed_chunk:
            all_tasks.extend(parsed_chunk)

    if not all_tasks:
        logger.error("错误: 所有部分均未能成功解析或未提取到任何任务。")
        return None

    logger.info(f"\n所有部分处理完毕，共提取到 {len(all_tasks)} 个任务（去重前）。")

    # 对结果进行去重
    unique_tasks = _deduplicate_tasks(all_tasks)

    logger.info(f"去重后，最终获得 {len(unique_tasks)} 个独立任务。")
    return unique_tasks

