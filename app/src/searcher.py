# -*- coding: utf-8 -*-
# @Time : 2025/9/12 19:22
# @Author : CSR
# @File : searcher.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

def search_website(website: str, keyword: str) -> list:
    """
    根据网站标识和关键词，执行搜索并返回结果列表。
    """
    if website == "shaanxi":
        return search_shaanxi(keyword)
    elif website == "sasac":
        return search_sasac(keyword)
    elif website == "mot":
        return search_mot(keyword)
    else:
        return []

def search_shaanxi(keyword: str):
    """搜索陕西省政府网站"""
    encoded_keyword = quote(keyword)
    url = f"https://www.shaanxi.gov.cn/sxsearch/search.html?tenantId=16711&code=1920ae4af69&searchWord={encoded_keyword}"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for item in soup.select('.result-item'):
            title_tag = item.select_one('a')
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href')
                if title and link:
                    results.append({"title": title, "url": urljoin(url, link)})
        return results
    except Exception as e:
        print(f"搜索陕西网站出错: {e}")
        return []

def search_sasac(keyword: str):
    """搜索国资委网站"""
    url = "http://xxgk.sasac.gov.cn/gdnps/pc/search.jsp"
    try:
        # 国资委网站搜索需要POST请求
        response = requests.post(url, data={'searchword': keyword}, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for item in soup.select('ul.list_con_items li.clearfix'):
            title_tag = item.select_one('a')
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href')
                if title and link:
                    # 链接是相对路径，需要拼接
                    results.append({"title": title, "url": urljoin("http://xxgk.sasac.gov.cn/gdnps/pc/", link)})
        return results
    except Exception as e:
        print(f"搜索国资委网站出错: {e}")
        return []

def search_mot(keyword: str):
    """搜索交通运输部网站"""
    encoded_keyword = quote(keyword)
    url = f"https://sou.mot.gov.cn/s?qt={encoded_keyword}"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for item in soup.select('div.result'):
            title_tag = item.select_one('h3 a')
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href')
                if title and link:
                    results.append({"title": title, "url": link}) # 链接是完整的
        return results
    except Exception as e:
        print(f"搜索交通运输部网站出错: {e}")
        return []
