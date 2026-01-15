#!/bin/bash
# GMailHelper - 每日自动执行脚本
# 用于 macOS launchd 定时任务（每天上午 9:00）

set -e

# 项目路径
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

# 日志文件
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"
TODAY=$(date +%Y-%m-%d)
LOG_FILE="$LOG_DIR/daily-$TODAY.log"

# 记录开始时间
echo "========================================" >> "$LOG_FILE"
echo "开始执行: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 加载环境变量
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)
    echo "✅ 环境变量已加载" >> "$LOG_FILE"
else
    echo "❌ 错误: .env 文件不存在" >> "$LOG_FILE"
    exit 1
fi

# 检查必要的环境变量
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ 错误: ANTHROPIC_API_KEY 未设置" >> "$LOG_FILE"
    exit 1
fi

if [ -z "$FEISHU_APP_SECRET" ]; then
    echo "⚠️ 警告: FEISHU_APP_SECRET 未设置，飞书通知将被禁用" >> "$LOG_FILE"
fi

# Python 解释器路径
PYTHON="$PROJECT_DIR/venv/bin/python"

if [ ! -f "$PYTHON" ]; then
    echo "❌ 错误: Python venv 不存在: $PYTHON" >> "$LOG_FILE"
    exit 1
fi

echo "📅 执行日期: $TODAY" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 执行主清理脚本
echo "🧹 开始清理邮件..." >> "$LOG_FILE"

# 默认使用模拟模式（安全）
# 如需实际执行，删除 --dry-run 参数
$PYTHON scripts/daily_cleanup.py --dry-run >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "" >> "$LOG_FILE"
    echo "✅ 邮件清理完成" >> "$LOG_FILE"
else
    echo "" >> "$LOG_FILE"
    echo "❌ 邮件清理失败" >> "$LOG_FILE"
    exit 1
fi

# 输出结果摘要
echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "📋 执行结果摘要:" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

OUTPUT_DIR="$PROJECT_DIR/output/$TODAY"
if [ -d "$OUTPUT_DIR" ]; then
    echo "输出目录内容:" >> "$LOG_FILE"
    ls -la "$OUTPUT_DIR" >> "$LOG_FILE" 2>&1
fi

echo "" >> "$LOG_FILE"
echo "✅ 每日任务完成: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 输出到终端（用于手动执行时查看）
echo "✅ GMailHelper 执行完成！"
echo "📁 输出目录: $OUTPUT_DIR"
echo "📝 日志文件: $LOG_FILE"
