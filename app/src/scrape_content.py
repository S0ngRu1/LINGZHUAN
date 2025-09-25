import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote
import re
import json
import time
from loguru import logger

"""
解析网页代码
"""

def _scrape_shaanxi(soup: BeautifulSoup) -> str:
    """专门负责解析陕西省政府网站不同版式页面的函数。"""
    text = ""
    # 尝试解析第一种布局 (2018版)
    is_page1 = bool(soup.find("div", class_="biaoti")) and bool(soup.find("div", class_="TRS_UEDITOR"))
    if is_page1:
        logger.info("检测到陕西网站布局 1 (2018版)...")
        content_tag = soup.find("div", class_="view TRS_UEDITOR trs_paper_default trs_word")
        if content_tag:
            p_tags = content_tag.find_all("p")
            text = "\n".join([p.get_text(strip=True) for p in p_tags if p.get_text(strip=True)])
        return text

    # 如果不是第一种，尝试解析第二种布局 (2023版)
    is_page2 = bool(soup.find("div", class_="public-title-nav")) and bool(soup.find("div", class_="text_content"))
    if is_page2:
        logger.info("检测到陕西网站布局 2 (2023版)...")
        content_tag = soup.find("div", class_="text_content")
        if content_tag:
            p_tags = content_tag.find_all("p")
            text = "\n".join(
                [p.get_text(strip=True) for p in p_tags if p.get_text(strip=True) and "扫一扫" not in p.get_text()])
        return text

    # 如果以上精确解析都失败，则回退到通用选择器
    logger.warning("未能使用精确选择器找到内容，正在尝试通用布局选择器...")
    general_selectors = 'div.text_content, div.main-content, div#zcwjk_container'
    content_div = soup.select_one(general_selectors)
    if content_div:
        text = content_div.get_text(separator='\n', strip=True)

    return text


def _clean_sasac_html(html: str) -> str:
    """辅助函数：专门清理国资委接口返回的HTML正文。"""
    if not html: return ""
    html = re.sub(r"<!--[\s\S]*?-->", "", html)
    html = re.sub(r"<br\s*\/?>", "\n", html)
    soup = BeautifulSoup(html, "lxml")
    return soup.get_text(separator="\n", strip=True)


def _scrape_sasac(url: str) -> str:
    """
    专门负责解析国资委网站页面的函数。
    此函数通过调用网站的后端数据接口来获取内容，非常稳定。
    """
    try:
        # 1. 从URL提取page_id
        id_match = re.search(r"[?&]id=(\d+)", url)
        if not id_match:
            logger.warning(f"警告: 在国资委URL中未找到id参数: {url}")
            return ""
        page_id = id_match.group(1)
        logger.info(f"从国资委URL中提取到ID: {page_id}")

        # 2. 构造请求参数并发起API请求
        params = {"goPage": 1, "orderBy": [{"orderBy": "orderTime", "reverse": True}], "pageSize": 20,
                  "queryParam": [{"shortName": "id", "value": page_id}]}
        params_encoded = quote(quote(json.dumps(params, ensure_ascii=False)))
        data_url = f"http://xxgk.sasac.gov.cn/gdnps/searchIndex.jsp?params={params_encoded}&callback=jsonpCallback"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": url,
        }

        time.sleep(0.5)  # 轻微延迟
        response = requests.get(data_url, headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = "utf-8"

        # 3. 解析JSONP响应
        jsonp_content = response.text.strip()
        if not (jsonp_content.startswith("jsonpCallback(") and jsonp_content.endswith(");")):
            raise ValueError("国资委接口返回非标准JSONP格式")

        pure_json = jsonp_content[len("jsonpCallback("):-2]
        data = json.loads(pure_json)

        if "resultMap" not in data or len(data["resultMap"]) == 0:
            raise ValueError("国资委接口未返回有效政策数据")

        # 4. 提取并清理正文HTML
        html_content = data["resultMap"][0].get("htmlContent", "")
        return _clean_sasac_html(html_content)

    except Exception as e:
        logger.error(f"错误: 抓取国资委内容失败 (URL: {url}): {e}")
        return ""


def _scrape_mot(soup: BeautifulSoup) -> str:
    """
    专门负责解析交通运输部网站页面的函数（兼容新旧两种布局）。
    """
    content_container = None
    # 优先找旧页面的TRS_UEDITOR容器
    old_container = soup.find("div", class_="view TRS_UEDITOR")
    if old_container:
        logger.info("检测到交通运输部网站布局 1 (旧版)...")
        content_container = old_container
    else:
        # 找不到再找新页面的Zoom容器
        new_container = soup.find("div", id="Zoom")
        if new_container:
            logger.info("检测到交通运输部网站布局 2 (新版)...")
            content_container = new_container

    # 如果找到了特定的内容容器，则精确提取
    if content_container:
        # 提取所有<p>标签文本，保留段落结构
        para_elems = content_container.find_all("p")
        full_content = []
        for para in para_elems:
            para_text = para.get_text(strip=True)
            if para_text:
                full_content.append(para_text)
        return "\n".join(full_content)

    # 如果都找不到，回退到最初的通用选择器
    logger.warning("未能使用精确选择器找到内容，正在尝试通用布局选择器...")
    general_container = soup.select_one('div.xxgk_content')
    if general_container:
        return general_container.get_text(separator='\n', strip=True)

    return ""


def scrape_content(url: str) -> str:
    """
    根据给定的政府网站URL，智能抓取其主要文本内容。
    这是一个调度函数，它会自动选择合适的解析器。
    """
    try:
        hostname = urlparse(url).hostname

        if 'sasac.gov.cn' in hostname:
            return _scrape_sasac(url)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        if 'shaanxi.gov.cn' in url:
            headers['Referer'] = 'https://www.shaanxi.gov.cn/'

        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'lxml')

        text = ""

        # 根据域名路由到对应的解析函数
        if 'shaanxi.gov.cn' in hostname or 'sxgz.shaanxi.gov.cn' in hostname:
            text = _scrape_shaanxi(soup)
        elif 'mot.gov.cn' in hostname:
            text = _scrape_mot(soup)

        if text:
            logger.info(f"成功抓取URL内容: {url}")
            return text
        else:
            logger.warning(f"警告: 在 {url} 上未找到任何预期的内容容器。将尝试抓取整个页面body作为备用。")
            body = soup.find('body')
            return body.get_text(separator='\n', strip=True) if body else ""

    except requests.RequestException as e:
        logger.error(f"错误: 抓取URL时发生网络错误 {url}: {e}")
        return ""
    except Exception as e:
        logger.error(f"错误: 解析URL时发生未知错误 {url}: {e}")
        return ""
