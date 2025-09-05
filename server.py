# -*- coding: utf-8 -*-
# @Time : 2025/9/5 23:01
# @Author : CSR
# @File : server.py

# server.py
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from loguru import logger
from app.utils.file_handler import read_file_content
from app.src.llm_parser import parse_schedule_from_text

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求，以便前端可以调用后端

# 设置一个用于临时存放上传文件的目录
UPLOAD_FOLDER = 'resources'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/api/parse-file', methods=['POST'])
def parse_file():
    """
    API端点，用于接收上传的文件，解析并返回结构化数据。
    """
    # 1. 检查是否有文件在请求中
    if 'file' not in request.files:
        return jsonify({"error": "请求中未找到文件部分"}), 400

    file = request.files['file']

    # 2. 检查文件名
    if file.filename == '':
        return jsonify({"error": "未选择任何文件"}), 400

    if file:
        # 3. 保存上传的文件
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # 4. 读取文件内容
            print(f"正在读取文件: {filepath}")
            content = read_file_content(filepath)
            if content is None:
                return jsonify({"error": "不支持的文件类型或文件读取失败"}), 400

            # 5. 调用LLM进行解析
            logger.info("文件读取成功，正在调用LLM进行解析...")
            parsed_data = parse_schedule_from_text(content)

            # 清理上传的临时文件
            os.remove(filepath)

            # 6. 检查解析结果并返回
            if parsed_data:
                logger.info("LLM解析成功，返回数据。")
                return jsonify(parsed_data)
            else:
                logger.error("LLM解析失败或未返回有效数据。")
                return jsonify({"error": "AI内容解析失败，请检查文件内容或API配置"}), 500

        except Exception as e:
            # 清理上传的临时文件
            if os.path.exists(filepath):
                os.remove(filepath)
            logger.error(f"处理过程中发生错误: {e}")
            return jsonify({"error": f"服务器内部错误: {e}"}), 500

    return jsonify({"error": "未知错误"}), 500


if __name__ == '__main__':
    # 启动服务器，监听在本地5000端口
    app.run(host='0.0.0.0', port=5000, debug=True)
