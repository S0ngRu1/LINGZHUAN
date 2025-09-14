# -*- coding: utf-8 -*-
# @Time : 2025/9/12 17:49
# @Author : CSR
# @File : server.py
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# 导入我们自定义的模块
from app.src.scrape_content import scrape_content
from app.src.llm_analyze_document import analyze_single_document, compare_summaries
from app.src.searcher import search_website  # 导入新的搜索模块

# 初始化Flask应用
app = Flask(__name__, template_folder='.')
CORS(app)


@app.route('/')
def index():
    """渲染主页面"""
    return render_template('index.html')


@app.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.json
        website = data.get('website')
        keyword = data.get('keyword')
        if not website or not keyword:
            return jsonify({"error": "缺少网站或关键词参数"}), 400

        results = search_website(website, keyword)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": f"服务器内部错误: {e}"}), 500


# --- 新的、拆分后的API端点 ---

@app.route('/api/analyze-document', methods=['POST'])
def analyze_document_endpoint():
    try:
        data = request.json
        doc_url = data.get('doc_url')
        if not doc_url:
            return jsonify({"error": "缺少文档URL"}), 400

        print(f"正在分析单个文档: {doc_url}")
        content = scrape_content(doc_url)
        if not content:
            return jsonify({"error": "抓取网页内容失败"}), 500

        analysis = analyze_single_document(content)
        if not analysis:
            return jsonify({"error": "AI分析文档失败"}), 500

        return jsonify(analysis)
    except Exception as e:
        print(f"分析单个文档时发生错误: {e}")
        return jsonify({"error": f"服务器内部错误: {e}"}), 500


@app.route('/api/compare-summaries', methods=['POST'])
def compare_summaries_endpoint():
    try:
        data = request.json
        summary1 = data.get('summary1')
        summary2 = data.get('summary2')
        if summary1 is None or summary2 is None:  # 允许空字符串
            return jsonify({"error": "缺少摘要内容"}), 400

        print("正在对比摘要...")
        comparison = compare_summaries(summary1, summary2)
        if not comparison:
            return jsonify({"error": "AI对比摘要失败"}), 500

        return jsonify(comparison)
    except Exception as e:
        print(f"对比摘要时发生错误: {e}")
        return jsonify({"error": f"服务器内部错误: {e}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

