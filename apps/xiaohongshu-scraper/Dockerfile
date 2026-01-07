# 小红书抓取服务 Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    # Playwright 依赖
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    # 字体支持
    fonts-noto-cjk \
    # 工具
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Poetry
RUN pip install --no-cache-dir poetry

# 复制依赖文件
COPY pyproject.toml ./

# 安装依赖
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# 安装 Playwright 浏览器
RUN playwright install chromium

# 复制源代码
COPY src/ ./src/

# 创建输出目录
RUN mkdir -p /app/output /app/data

# 环境变量
ENV HOST=0.0.0.0
ENV PORT=8100
ENV HEADLESS=true
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 8100

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8100/health || exit 1

# 启动命令
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8100"]
