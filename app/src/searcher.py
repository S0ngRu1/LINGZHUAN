# -*- coding: utf-8 -*-
# @Time : 2025/9/12 19:22
# @Author : CSR
# @File : searcher.py

def search_website(website: str, keyword: str) -> list:
    """
    根据网站标识和关键词，返回固定的测试结果列表。
    参数 'keyword' 在此版本中被忽略。
    """
    print(f"收到模拟搜索请求: 网站='{website}', 关键词='{keyword}'")
    if website == "shaanxi":
        return get_mock_shaanxi_results()
    elif website == "sasac":
        return get_mock_sasac_results()
    elif website == "mot":
        return get_mock_mot_results()
    else:
        return []

def get_mock_shaanxi_results():
    """返回陕西省政府的固定测试数据"""
    return [
        {
            "title": "陕西省国资委关于印发《陕西省省属企业投资监督管理办法》的通知",
            "url": "https://sxgz.shaanxi.gov.cn/zfxxgk/zc/qtwj/202310/t20231013_2411969.html"
        },
        {
            "title": "关于印发《陕西省省属企业投资监督管理办法》的通知",
            "url": "https://www.shaanxi.gov.cn/zfxxgk/fdzdgknr/zcwj/gfxwj/202208/t20220815_2245993.html"
        }
    ]

def get_mock_sasac_results():
    """返回国资委的固定测试数据"""
    return [
        {
            "title": "关于做好2023年中央企业违规经营投资责任追究工作的通知",
            "url": "http://xxgk.sasac.gov.cn/gdnps/pc/content.jsp?id=27700648"
        },
        {
            "title": "关于做好2022年中央企业违规经营投资责任追究工作的通知",
            "url": "http://xxgk.sasac.gov.cn/gdnps/pc/content.jsp?id=23800565"
        }
    ]

def get_mock_mot_results():
    """返回交通运输部的固定测试数据"""
    return [
        {
            "title": "交通运输部办公厅 国家发展改革委办公厅关于印发《收费公路政府和社会资本合作新机制操作指南》的通知",
            "url": "https://xxgk.mot.gov.cn/2020/jigou/cwsjs/202504/t20250410_4166702.html"
        },
        {
            "title": "关于在收费公路领域推广运用政府和社会资本合作模式的实施意见",
            "url": "https://xxgk.mot.gov.cn/2020/jigou/cwsjs/202006/t20200623_3310441.html"
        }
    ]