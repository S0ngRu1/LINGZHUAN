
import os
import logging
import re
from datetime import datetime
from typing import Optional, List, Dict
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pandas as pd

from app.utils.file_handler import read_file_content
from app.src.llm_parser import parse_schedule_from_text
# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 设置一个用于临时存放上传文件的目录
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def _parse_date_range(text: str) -> tuple:
    """
    辅助函数，用于从 "2天\n(9.1-9.2)" 或 "(9.1)" 这样的字符串中解析出开始和结束日期。
    """
    if not isinstance(text, str):
        return (None, None)

    start_str, end_str = None, None

    # 1. 优先匹配日期范围格式，例如 (9.1-9.2)，兼容全角和半角括号
    range_match = re.search(r'[（\(](\d{1,2}\.\d{1,2})-(\d{1,2}\.\d{1,2})[）\)]', text)
    if range_match:
        start_str, end_str = range_match.groups()
    else:
        # 2. 如果没有范围，再匹配单个日期格式，例如 (9.1)
        single_match = re.search(r'[（\(](\d{1,2}\.\d{1,2})[）\)]', text)
        if single_match:
            # 正确获取第一个捕获组的内容
            date_str = single_match.group(1)
            start_str = date_str
            end_str = date_str
        else:
            # 3. 如果两种括号格式都找不到，尝试直接解析整个文本作为单个日期
            try:
                single_date = pd.to_datetime(text, errors='coerce')
                if pd.notna(single_date):
                    date_str_formatted = single_date.strftime('%Y-%m-%d')
                    return (date_str_formatted, date_str_formatted)
            except Exception:
                pass  # 忽略解析错误，将在最后返回None
            return (None, None)

    # 如果 start_str 是 None (意味着没有匹配到任何日期)，直接返回
    if start_str is None:
        return (None, None)

    # 假设日期为当前年份
    current_year = datetime.now().year

    try:
        start_month, start_day = map(int, start_str.split('.'))
        end_month, end_day = map(int, end_str.split('.'))

        start_date = datetime(current_year, start_month, start_day)

        # 智能处理跨年份的日期范围，例如 (12.25-1.5)
        end_year = current_year + 1 if end_month < start_month else current_year
        end_date = datetime(end_year, end_month, end_day)

        return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    except (ValueError, AttributeError):
        # 如果日期无效 (例如 2月30日)或split失败, 返回None
        logger.warning(f"在文本 '{text}' 中发现无效日期，已忽略。")
        return (None, None)



def parse_excel_to_records(file_path: str) -> Optional[List[Dict]]:
    """
    直接将Excel文件的第一个工作表解析为与LLM输出格式一致的 list[dict]。
    - 智能跳过顶部的标题行。
    - 智能映射指定列名。
    - 通过向前填充(forward-fill)正确处理合并单元格。
    - 智能解析复杂的日期范围字符串。
    """
    try:
        df = pd.read_excel(file_path, sheet_name=0, header=1)

        column_mapping = {
            "工作步骤": "阶段",
            "工作内容": "工作子项",
            "成果文件": "成果文件",
            "主责单位": "主责单位/负责人",
            "完成时限": "完成时限"
        }

        required_input_cols = list(column_mapping.keys())
        if not all(col in df.columns for col in required_input_cols):
            missing_cols = [col for col in required_input_cols if col not in df.columns]
            logger.error(f"Excel文件中缺少必需的列: {', '.join(missing_cols)}")
            return None

        df.rename(columns=column_mapping, inplace=True)

        # 将解析出的元组 (start, end) 分配给两个新列
        df[['开始日期', '结束日期']] = df['完成时限'].apply(lambda x: pd.Series(_parse_date_range(x)))

        target_columns = ["阶段", "工作子项", "成果文件", "主责单位/负责人", "开始日期", "结束日期"]
        df = df[target_columns]

        columns_to_fill = ["阶段", "主责单位/负责人"]
        df[columns_to_fill] = df[columns_to_fill].ffill()

        # 注意：日期格式化已在_parse_date_range中完成，这里只需处理NaN
        df = df.where(pd.notna(df), None)

        records = df.to_dict('records')

        return records
    except Exception as e:
        logger.error(f"直接解析Excel文件失败: {e}")
        return None


@app.route('/api/parse-file', methods=['POST'])
def parse_file():
    """
    API端点，智能判断文件类型。
    如果是Excel，直接解析；否则，调用LLM解析。
    """
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
            parsed_data = None

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


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000, debug=True)
    parse_excel_to_records('resources/甘特图&爬虫资料/1.注销-xxxc（修改）.xlsx')
