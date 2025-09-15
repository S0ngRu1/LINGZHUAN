# 灵篆 (Ling Zhuan)

这是一个集成了政策文件分析与项目计划管理功能的 Web 应用，通过 AI 技术帮助用户快速对比政策文件差异，并提供甘特图生成等项目管理工具。

“灵篆”旨在成为您的智能助理，将繁琐的文档比对和项目排期工作自动化、智能化，让您专注于更高价值的决策与管理。

## ✨ 核心功能

应用分为两大核心模块：**政策智能分析** 和 **项目计划管理**。

### 政策智能分析模块

  - **智能搜索**：对接政府官方网站，根据关键词快速检索相关政策文件。
  - **AI文档解析**：利用大语言模型（LLM）对单个政策文件进行深度分析，自动提取：
      - **核心摘要**：一句话总结文件主旨。
      - **关键信息**：如发文机构、发文日期等。
      - **文件大纲**：生成层级清晰的思维导图，可视化文档结构。
  - **AI对比分析**：选中两份文件，AI将自动进行多维度对比，生成清晰的对比表格，高亮显示两份文件之间的异同点。
  - **可视化与导出**：文件大纲以可交互的思维导图（Tree Chart）形式展现，对比结果支持一键下载为 Excel 文件。

### 项目计划管理模块

  - **智能文件解析**：颠覆传统手动录入，可直接上传多种格式的计划文件：
      - **Excel 文件**：直接解析预定格式的 Excel 表格。
      - **纯文本/Word/PDF**：利用 LLM 自动识别并解析非结构化文本中的任务、时间、依赖关系等信息。
  - **自动化甘特图生成**：根据解析出的任务数据，一键生成专业的 Excel 项目计划文件，包含：
      - **动态甘特图**：清晰展示任务时间轴、进度和依赖关系。
      - **多维度分析图表**：自动生成任务状态分布饼图、负责人工作量柱状图等，辅助项目决策。
  - **Web端便捷操作**：提供友好的网页界面，用户只需上传文件、确认数据、点击生成，即可下载最终的 Excel 成果。

## 📁 项目结构

```
.
├── app.py                  # 主 Flask 应用
├── gantt_chart_webapp.html # 甘特图前端页面
├── policy_analyzer_html.html# 政策分析前端页面
├── uploads/                # 临时文件上传目录
├── app/
│   ├── src/
│   │   ├── gantt_excel_parser.py     # Excel 格式化解析
│   │   ├── gantt_generator.py        # 甘特图及图表生成
│   │   ├── llm_parser.py             # LLM 解析任务计划
│   │   ├── llm_analyze_document.py   # LLM 分析政策文件
│   │   ├── searcher.py               # 网站搜索逻辑
│   │   ├── scrape_content.py         # 网页内容抓取
│   └── utils/
│       └── file_handler.py         # 文件读写工具
└── README.md               # 本文档
```


## 📡 API 接口文档

所有接口均接受 JSON 格式的请求体，并返回 JSON 格式的响应（文件生成接口除外）。

| 路径                        | 方法 | 描述                                       | 请求体 (`Body`)                                            | 成功响应                                                     |
| --------------------------- | ---- | ------------------------------------------ | ---------------------------------------------------------- | ------------------------------------------------------------ |
| `/api/search`               | POST | 搜索政策文件                               | `{"website": "shaanxi", "keyword": "关键词"}`                | `[{"title": "...", "url": "..."}, ...]`                       |
| `/api/analyze-document`     | POST | 分析单个政策文件                           | `{"doc_url": "http://..."}`                                | `{"summary": "...", "outline": [...], "agency": "..."}`      |
| `/api/compare-summaries`    | POST | 对比两份文件的摘要                         | `{"summary1": "...", "summary2": "..."}`                     | `{"comparison": [{"dimension": "...", "document1_point": "...", "document2_point": "..."}]}` |
| `/api/parse-file`           | POST | 解析上传的计划文件 (`multipart/form-data`) | `file`: 上传的文件                                         | `[{"task": "...", "start": "...", "end": "...", ...}]`        |
| `/api/generate-excel`       | POST | 根据任务数据生成Excel甘特图                | `[{"task": "...", "start": "...", "end": "...", ...}]`        | 返回 `.xlsx` 文件流供下载                                    |




## 🚀 快速开始

### 🐳 Docker 快速部署指南
本项目已封装为 Docker 镜像，您无需关心 Python 环境和复杂的依赖安装。只需在您的电脑上安装 Docker，即可一键启动应用。

### 环境要求
Docker 和 Docker Compose (通常 Docker Desktop 会自带)

一个可用的大语言模型 API Key

### 部署步骤
1. 克隆仓库

    将本项目的代码下载到您的本地电脑。
    ```Bash
        git clone https://github.com/your-username/lingzhuan.git
        cd lingzhuan
    ```

2. 配置您的 API Key

   在项目的根目录创建一个名为 .env 的文件。然后，将您的 AI 服务信息填入该文件，格式如下：

    ```text
    # .env 文件内容示例
    API_PROVIDER="OpenAI"
    API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    请将 sk-xxxxxxxxxx 替换为您自己的真实 API Key。程序将自动读取此文件中的配置。
    ```
3. 启动应用

    打开终端（命令提示符或 PowerShell），在项目根目录下，运行以下命令：

    ```Bash
    docker-compose up --build -d
    ```

     第一次启动时，Docker 会下载基础镜像并安装所有依赖，可能需要几分钟。成功后，您会看到类似 lingzhuan_service is up-to-date 的提示。

4. 访问应用

    部署成功！现在打开您的浏览器，即可开始使用：

    政策分析工具: http://localhost:5000/policy
    
    甘特图生成工具: http://localhost:5000/gantt

### 如何停止服务
如果您想停止应用，只需在项目目录的终端中运行以下命令：

```Bash
  docker-compose down
```

### 如何使用

1.  **政策分析**：浏览器访问 `http://localhost:5000/policy`

      - 在页面上方选择网站来源，输入关键词并搜索。
      - 从搜索结果中勾选两份需要对比的文件。
      - 点击“对比已选两项”按钮，等待 AI 分析完成。
      - 查看生成的摘要、思维导图和对比表格。

2.  **甘特图生成**：浏览器访问 `http://localhost:5000/gantt` 

      - 点击或拖拽上传您的项目计划文件（如 `.txt`, `.docx`, `.xlsx`）。
      - 系统会自动解析文件内容，并在下方表格中展示任务数据。
      - 确认数据无误后，点击“生成 Excel 甘特图”按钮。
      - 浏览器将自动下载生成的包含甘特图和分析图表的 `.xlsx` 文件。
