# -*- coding: utf-8 -*-
# @Time : 2025/9/12 17:49
# @Author : CSR
# @File : server.py
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# 导入我们自定义的模块
from app.src import scrape_content
from app.src.llm_analyze_document import analyze_documents
from app.src.searcher import search_website  # 导入新的搜索模块

# 初始化Flask应用
app = Flask(__name__, template_folder='templates')
CORS(app)


@app.route('/')
def index():
    """渲染主页面"""
    return render_template('index.html')


@app.route('/api/search', methods=['POST'])
def search_api():
    """
    新的API端点，用于根据关键词在指定网站上搜索。
    """
    data = request.get_json()
    website = data.get('website')
    keyword = data.get('keyword')

    if not all([website, keyword]):
        return jsonify({"error": "缺少网站来源或关键词"}), 400

    try:
        print(f"收到搜索请求: 网站='{website}', 关键词='{keyword}'")
        search_results = search_website(website, keyword)
        print(f"搜索到 {len(search_results)} 条结果。")
        return jsonify(search_results)
    except Exception as e:
        print(f"搜索过程中发生错误: {e}")
        return jsonify({"error": f"服务器搜索时发生错误: {e}"}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_api():
    """
    更新后的API端点，用于对比前端传入的两个URL。
    """
    data = request.get_json()
    doc1_url = data.get('doc1_url')
    doc2_url = data.get('doc2_url')

    if not all([doc1_url, doc2_url]):
        return jsonify({"error": "必须提供两个URL进行对比"}), 400
    try:
        print(f"正在抓取并分析:\n1: {doc1_url}\n2: {doc2_url}")
        content1 = scrape_content(doc1_url)
        content2 = scrape_content(doc2_url)

        if not content1 or not content2:
            return jsonify({"error": "无法抓取一个或两个URL的内容"}), 500

        analysis_result = analyze_documents(content1, content2)

        if not analysis_result:
            return jsonify({"error": "AI模型分析失败"}), 500

        print("分析成功，返回结果。")
        return jsonify(analysis_result)

    except Exception as e:
        print(f"分析过程中发生错误: {e}")
        return jsonify({"error": f"服务器分析时发生错误: {e}"}), 500


if __name__ == '__main__':
    if not os.path.exists('app'): os.makedirs('app')
    app.run(host='0.0.0.0', port=5000, debug=True)


