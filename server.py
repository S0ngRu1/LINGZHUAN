import os
from dotenv import load_dotenv
load_dotenv()

from loguru import logger
from datetime import datetime
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from app.src.gantt_excel_parser import parse_excel_to_records
from app.src.gantt_generator import generate_gantt_and_charts_excel
from app.src.llm_parser import parse_schedule_from_text
from app.src.scrape_content import scrape_content
from app.src.llm_analyze_document import analyze_single_document, compare_summaries
from app.src.searcher import search_website
from app.utils.file_handler import read_file_content

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 设置一个用于临时存放上传文件的目录
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 添加静态文件路由
@app.route('/')
def index():
    return send_from_directory('.', 'gantt_chart_webapp.html')  # 默认显示甘特图页面

@app.route('/gantt')
def gantt_page():
    return send_from_directory('.', 'gantt_chart_webapp.html')  # 甘特图页面

@app.route('/policy')
def policy_page():
    return send_from_directory('.', 'policy_analyzer_html.html')  # 政策分析页面

@app.route('/api/parse-file', methods=['POST'])
def parse_file():
    if 'file' not in request.files:
        return jsonify({"error": "请求中未找到文件部分"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未选择任何文件"}), 400
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        _, file_extension = os.path.splitext(filename)
        file_extension = file_extension.lower()
        file.save(filepath)
        try:
            if file_extension in ['.xlsx', '.xls']:
                logger.info("检测到Excel文件，进行直接解析...")
                parsed_data = parse_excel_to_records(filepath)
                if parsed_data is None:
                    return jsonify({"error": "无法直接解析此Excel文件，请检查文件格式和内容。"}), 500
            else:
                logger.info(f"检测到 {file_extension} 文件，使用LLM进行解析...")
                content = read_file_content(filepath)
                if content is None:
                    return jsonify({"error": "不支持的文件类型或文件读取失败"}), 400

                parsed_data = parse_schedule_from_text(content)

            os.remove(filepath)
            if parsed_data:
                logger.info("解析成功，返回数据。")
                return jsonify(parsed_data)
            else:
                logger.error("解析失败或未返回有效数据。")
                return jsonify({"error": "内容解析失败，请检查文件内容或API配置"}), 500

        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            logger.error(f"处理过程中发生错误: {e}")
            return jsonify({"error": f"服务器内部错误: {e}"}), 500
    return jsonify({"error": "未知错误"}), 500

@app.route('/api/generate-excel', methods=['POST'])
def generate_excel_endpoint():
    """
    接收前端发来的JSON格式任务数据，生成包含图表的Excel文件并返回给用户下载。
    """
    # 1. 从请求体中获取JSON数据
    work_data = request.get_json()

    # 2. 验证数据有效性
    if not isinstance(work_data, list) or not work_data:
        logger.error("接收到的生成请求数据无效或为空")
        return jsonify({"error": "无效或空的数据"}), 400

    try:
        # 3. 调用核心函数在内存中生成Excel文件
        logger.info("开始生成包含图表的Excel文件...")
        excel_buffer = generate_gantt_and_charts_excel(work_data)
        logger.info("文件生成成功，准备发送给客户端。")

        # 4. 使用send_file将内存中的文件作为附件发送给前端
        filename = f"项目计划甘特图_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"

        return send_file(
            excel_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        logger.error(f"生成Excel文件时发生严重错误: {e}", exc_info=True)
        return jsonify({"error": "服务器在生成Excel文件时发生内部错误"}), 500


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
    # 在实际部署时，请关闭debug模式
    app.run(host='0.0.0.0', port=5000, debug=False)