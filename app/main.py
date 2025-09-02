from app.src.data_processor import process_work_data
from app.src.gantt_drawer import draw_gantt_chart
from app.src.excel_exporter import export_to_excel
from app.utils.log_utils import logger
from app.utils.file_utils import delete_dir_contents, TEMP_DIR


def main():
    """
    程序主入口：协调各模块执行完整流程
    流程：数据处理 → 绘制甘特图 → 导出Excel → 清理临时文件
    """
    # 日志初始化（标记程序启动）
    logger.info("=" * 60)
    logger.info("【绩效评价甘特图生成工具】程序启动")
    logger.info("=" * 60)

    try:
        # --------------------------
        # 1. 数据处理：加载原始数据 + 计算持续天数 + 关联阶段颜色
        # --------------------------
        logger.info("开始执行数据处理...")
        processed_data = process_work_data()
        logger.info(f"数据处理完成，共包含 {len(processed_data)} 个工作任务")

        # --------------------------
        # 2. 绘制甘特图：基于处理后的数据生成可视化图片
        # --------------------------
        logger.info("开始绘制甘特图...")
        gantt_image_path = draw_gantt_chart(processed_data)
        logger.info(f"甘特图绘制完成，图片临时路径：{gantt_image_path}")

        # --------------------------
        # 3. 导出Excel：整合数据明细 + 甘特图图片
        # --------------------------
        logger.info("开始导出Excel文件...")
        excel_file_path = export_to_excel(processed_data, gantt_image_path)
        logger.info(f"Excel文件导出完成，最终路径：{excel_file_path}")

        # --------------------------
        # 4. 清理临时文件：删除甘特图临时图片，避免目录污染
        # --------------------------
        logger.info("开始清理临时文件...")
        delete_dir_contents(TEMP_DIR)  # 清空temp目录内容（保留目录本身）
        logger.info("临时文件清理完成")

        # --------------------------
        # 程序执行成功：输出最终结果提示
        # --------------------------
        logger.info("=" * 60)
        logger.info("【程序执行成功】")
        logger.info(f"✅ 最终Excel文件：{excel_file_path}")
        logger.info(f"✅ 运行日志文件：{logger.handlers[1].baseFilename}")  # 输出日志文件路径
        logger.info("=" * 60)

    except Exception as e:
        # 捕获异常：记录错误日志并退出程序
        logger.error("=" * 60)
        logger.error("【程序执行失败】", exc_info=True)  # exc_info=True 记录完整异常堆栈
        logger.error(f"错误原因：{str(e)}")
        logger.error("=" * 60)
        exit(1)  # 非0退出码，标识程序异常终止（便于脚本调用时识别状态）


# 程序入口：仅当直接运行main.py时执行
if __name__ == "__main__":
    main()