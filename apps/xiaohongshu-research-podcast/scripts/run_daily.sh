#!/bin/bash
#
# 每日小红书研究播客生成脚本
# 由 launchd 定时调用
#

set -e  # 遇到错误立即退出

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# 日志目录
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"

# 日志文件
DATE_STR=$(date +"%Y-%m-%d")
LOG_FILE="$LOG_DIR/daily-${DATE_STR}.log"

# 记录开始时间
echo "================================================" | tee -a "$LOG_FILE"
echo "🎙️ 小红书研究播客生成 - $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 加载环境变量
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
    echo "✓ 环境变量已加载" | tee -a "$LOG_FILE"
else
    echo "⚠️ 未找到 .env 文件，使用默认配置" | tee -a "$LOG_FILE"
fi

# 检查必需的环境变量
if [ -z "$GOOGLE_API_KEY" ] && [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ 错误: GOOGLE_API_KEY 或 GEMINI_API_KEY 未设置" | tee -a "$LOG_FILE"
    exit 1
fi

if [ -z "$ELEVENLABS_API_KEY" ]; then
    echo "⚠️ 警告: ELEVENLABS_API_KEY 未设置，将跳过音频生成" | tee -a "$LOG_FILE"
    SKIP_AUDIO="--skip-audio"
else
    SKIP_AUDIO=""
fi

# 检查Poetry是否安装
if ! command -v poetry &> /dev/null; then
    echo "❌ 错误: Poetry 未安装" | tee -a "$LOG_FILE"
    echo "  安装命令: curl -sSL https://install.python-poetry.org | python3 -" | tee -a "$LOG_FILE"
    exit 1
fi

# 检查依赖是否安装
echo "检查依赖..." | tee -a "$LOG_FILE"
if ! poetry run python -c "import google.generativeai" 2>/dev/null; then
    echo "  安装Python依赖..." | tee -a "$LOG_FILE"
    poetry install --no-dev 2>&1 | tee -a "$LOG_FILE"
fi

# 运行生成脚本
echo "" | tee -a "$LOG_FILE"
echo "开始生成播客..." | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

poetry run python scripts/daily_generate.py \
    --date "$DATE_STR" \
    $SKIP_AUDIO \
    2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

# 记录结果
echo "" | tee -a "$LOG_FILE"
echo "================================================" | tee -a "$LOG_FILE"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 生成成功 - $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"

    # 列出生成的文件
    OUTPUT_DIR="$PROJECT_ROOT/output/$DATE_STR"
    if [ -d "$OUTPUT_DIR" ]; then
        echo "" | tee -a "$LOG_FILE"
        echo "生成的文件:" | tee -a "$LOG_FILE"
        ls -lh "$OUTPUT_DIR" | tail -n +2 | awk '{print "  - " $9 " (" $5 ")"}' | tee -a "$LOG_FILE"
    fi
else
    echo "❌ 生成失败（退出码: $EXIT_CODE）" | tee -a "$LOG_FILE"
fi
echo "================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

exit $EXIT_CODE
