# -*- coding: utf-8 -*-
# @Time : 2025/9/12 17:52
# @Author : CSR
# @File : scrape_content.py
import requests
from bs4 import BeautifulSoup
import time


def scrape_content(url: str) -> str:
    """
    根据不同的URL结构，抓取并返回网页的核心文本内容。
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # 添加一个小的延迟，避免请求过于频繁
        time.sleep(1)
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()  # 如果请求失败则抛出异常
        response.encoding = response.apparent_encoding  # 自动检测并设置编码

        soup = BeautifulSoup(response.text, 'html.parser')

        content_div = None
        # 针对不同网站使用不同的CSS选择器
        if "sasac.gov.cn" in url:
            content_div = soup.select_one('.z-content')
        elif "mot.gov.cn" in url:
            content_div = soup.select_one('#UCAP-CONTENT')
        elif "shaanxi.gov.cn" in url or "sxgz.shaanxi.gov.cn" in url:
            # 陕西省政府网站可能有多种内容容器
            content_div = soup.select_one('#Zoom') or \
                          soup.select_one('.TRS_UEDITOR') or \
                          soup.select_one('article')

        if content_div:
            # 提取纯文本，使用换行符分隔，并移除多余的空白
            return content_div.get_text(separator='\n', strip=True)
        else:
            print(f"警告: 在 {url} 未找到匹配的内容容器。")
            # 作为备用方案，尝试提取body的文本
            return soup.body.get_text(separator='\n', strip=True) if soup.body else ""

    except requests.exceptions.RequestException as e:
        print(f"抓取 {url} 时发生网络错误: {e}")
        return ""
    except Exception as e:
        print(f"解析 {url} 时发生未知错误: {e}")
        return ""
