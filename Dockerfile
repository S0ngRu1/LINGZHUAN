# 使用官方的 Python 3.10 slim 版本作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖，--no-cache-dir 选项可以减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目所有文件到工作目录
COPY . .

# 声明容器将监听的端口
EXPOSE 5000

# 容器启动时运行的命令
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "server:app"]