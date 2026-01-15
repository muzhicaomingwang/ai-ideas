#!/bin/bash
# Daily Podcast AI - 每日自动执行脚本
# 用于 macOS launchd 定时任务

set -e

# 项目路径
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

# 日志文件
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/daily-$(date +%Y-%m-%d).log"

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

# 检查 API 密钥
if [ -z "$ELEVENLABS_API_KEY" ]; then
    echo "❌ 错误: ELEVENLABS_API_KEY 未设置" >> "$LOG_FILE"
    exit 1
fi

# Python 解释器路径
PYTHON="$PROJECT_DIR/venv/bin/python"

if [ ! -f "$PYTHON" ]; then
    echo "❌ 错误: Python venv 不存在: $PYTHON" >> "$LOG_FILE"
    exit 1
fi

# 获取今天的日期
TODAY=$(date +%Y-%m-%d)
OUTPUT_DIR="$PROJECT_DIR/output/$TODAY"

echo "📅 生成日期: $TODAY" >> "$LOG_FILE"
echo "📁 输出目录: $OUTPUT_DIR" >> "$LOG_FILE"

# 步骤0: 重试离线队列中的消息（网络恢复时自动发送）
echo "" >> "$LOG_FILE"
echo "🔄 步骤0: 检查并重试离线队列..." >> "$LOG_FILE"

if [ -n "$FEISHU_APP_ID" ] && [ "$FEISHU_APP_ID" != "your_feishu_app_id_here" ]; then
    $PYTHON scripts/notify_feishu.py --retry-queue >> "$LOG_FILE" 2>&1 || true
fi

# 步骤1: 生成播客（讲稿+音频）- 使用全天收集的新闻缓存
echo "" >> "$LOG_FILE"
echo "🎙️ 步骤1: 生成播客讲稿和音频（从缓存优选）..." >> "$LOG_FILE"
$PYTHON scripts/daily_generate.py --date "$TODAY" --from-cache >> "$LOG_FILE" 2>&1

if [ $? -ne 0 ]; then
    echo "❌ 播客生成失败" >> "$LOG_FILE"

    # 发送失败通知
    if [ -n "$FEISHU_APP_ID" ] && [ "$FEISHU_APP_ID" != "your_feishu_app_id_here" ]; then
        ERROR_MSG=$(tail -20 "$LOG_FILE" | grep -E "(Error|Exception|失败)" | head -5 | tr '\n' '; ')
        $PYTHON scripts/notify_feishu.py \
            --date "$TODAY" \
            --status failed \
            --error "播客生成失败: $ERROR_MSG" \
            >> "$LOG_FILE" 2>&1 || true
    fi

    exit 1
fi

echo "✅ 播客生成完成" >> "$LOG_FILE"

# 步骤2: 生成封面图片
echo "" >> "$LOG_FILE"
echo "🎨 步骤2: 生成封面图片..." >> "$LOG_FILE"

# 从讲稿中获取新闻数量
SCRIPT_FILE="$OUTPUT_DIR/script-$TODAY.md"
if [ -f "$SCRIPT_FILE" ]; then
    # 提取文章数（从 **文章数**: 10 这样的行中）
    ARTICLE_COUNT=$(grep -oE '^\*\*文章数\*\*: [0-9]+' "$SCRIPT_FILE" | grep -oE '[0-9]+' || echo "10")
    echo "📊 新闻数量: $ARTICLE_COUNT" >> "$LOG_FILE"
else
    ARTICLE_COUNT=10
    echo "⚠️ 讲稿文件不存在，使用默认新闻数量: $ARTICLE_COUNT" >> "$LOG_FILE"
fi

$PYTHON scripts/generate_cover.py --date "$TODAY" --count "$ARTICLE_COUNT" >> "$LOG_FILE" 2>&1

if [ $? -ne 0 ]; then
    echo "⚠️ 封面生成失败（非致命错误，继续流程）" >> "$LOG_FILE"

    # 发送警告通知（不中断流程）
    if [ -n "$FEISHU_APP_ID" ] && [ "$FEISHU_APP_ID" != "your_feishu_app_id_here" ]; then
        $PYTHON scripts/notify_feishu.py \
            --date "$TODAY" \
            --status failed \
            --error "封面生成失败（音频正常），请手动生成封面" \
            >> "$LOG_FILE" 2>&1 || true
    fi
else
    echo "✅ 封面生成完成" >> "$LOG_FILE"
fi

# 输出结果摘要
echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "📋 生成结果摘要:" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

if [ -d "$OUTPUT_DIR" ]; then
    echo "输出目录内容:" >> "$LOG_FILE"
    ls -la "$OUTPUT_DIR" >> "$LOG_FILE" 2>&1
fi

echo "" >> "$LOG_FILE"
echo "✅ 每日任务完成: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 步骤3: 发送飞书通知（成功通知，失败会自动加入队列）
echo "" >> "$LOG_FILE"
echo "📱 步骤3: 发送飞书通知..." >> "$LOG_FILE"

if [ -n "$FEISHU_APP_ID" ] && [ "$FEISHU_APP_ID" != "your_feishu_app_id_here" ]; then
    $PYTHON scripts/notify_feishu.py \
        --date "$TODAY" \
        --article-count "$ARTICLE_COUNT" \
        --status success \
        >> "$LOG_FILE" 2>&1

    if [ $? -eq 0 ]; then
        echo "✅ 飞书通知发送成功" >> "$LOG_FILE"
    else
        echo "⚠️ 飞书通知发送失败（已加入离线队列，网络恢复后自动重试）" >> "$LOG_FILE"
    fi
else
    echo "ℹ️  跳过飞书通知（未配置 FEISHU_APP_ID）" >> "$LOG_FILE"
fi

# 输出到终端（用于手动执行时查看）
echo "✅ 每日播客生成完成！"
echo "📁 输出目录: $OUTPUT_DIR"
echo "📝 日志文件: $LOG_FILE"
