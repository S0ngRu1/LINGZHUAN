
# 灵篆

## 绩效评价甘特图生成工具

一款基于AI的自动化工具，用于生成绩效评价工作甘特图，并导出含数据明细+可视化图片的Excel文件。

### 功能特点

1. 按绩效评价阶段自动区分甘特图颜色
2. 导出Excel包含「数据明细」和「甘特图可视化」两个工作表
3. 支持参数配置（颜色、Excel格式、甘特图样式），无需修改核心代码
4. 自动清理临时文件，避免目录污染

### 环境搭建

1. 安装Python 3.9+（推荐3.10版本）
2. 安装依赖库：

```bash
   pip install -r requirements.txt
```

### 使用步骤

1. （可选）修改配置文件（如需调整颜色、Excel 路径等）：

    颜色配置：config/color_config.py
    Excel 配置：config/excel_config.py
    甘特图配置：config/gantt_config.py

2. 运行程序：

```bash
    python main.py
```

3. 查看结果：

- Excel 文件默认路径：resources/绩效评价甘特图导出文件.xlsx
- 运行日志：resources/performance_gantt.log

