#!/bin/bash
# 每日播客生成脚本 v2.0
# 使用优化后的参数：植萌高激情模式 + 小雅女声

set -e

# 获取日期参数（默认今天）
DATE=${1:-$(date +%Y-%m-%d)}

echo "=================================================="
echo "🎙️  每日播客生成 v2.0"
echo "=================================================="
echo "📅 日期: $DATE"
echo ""
echo "⚙️  配置标准："
echo "  - 植萌: stability=0.0 (最激情) + style=0.8 + speed=1.2"
echo "  - 小雅: Jessica女声 + stability=0.5 + style=0.6 + speed=1.1"
echo "  - 模式: Deep Dive 双人对话"
echo "  - 文章数: 10篇（AI优选）"
echo ""

# 清理旧音频（避免使用缓存）
if [ -d "output/$DATE/dailytechnews/audio" ]; then
    echo "🗑️  清理旧音频..."
    rm -rf output/$DATE/dailytechnews/audio
    rm -f output/$DATE/dailytechnews/podcast-*.mp3
fi

# 执行生成
echo "🚀 开始生成..."
echo ""
python scripts/daily_generate.py \
    --date "$DATE" \
    --from-cache \
    --max-articles 10

# 验证结果
echo ""
echo "=================================================="
echo "✅ 生成完成！验证结果："
echo "=================================================="

AUDIO_FILE="output/$DATE/dailytechnews/podcast-$DATE-zhimeng-xiaoya.mp3"
if [ -f "$AUDIO_FILE" ]; then
    DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$AUDIO_FILE")
    SIZE=$(ls -lh "$AUDIO_FILE" | awk '{print $5}')
    ZHIMENG_COUNT=$(ls -1 output/$DATE/dailytechnews/audio/*植萌* 2>/dev/null | wc -l)
    XIAOYA_COUNT=$(ls -1 output/$DATE/dailytechnews/audio/*小雅* 2>/dev/null | wc -l)

    echo "📁 音频文件: $AUDIO_FILE"
    echo "⏱️  时长: ${DURATION%.*}秒"
    echo "📊 大小: $SIZE"
    echo "🎭 片段数: 植萌 $ZHIMENG_COUNT + 小雅 $XIAOYA_COUNT"
    echo ""

    # 验证小雅音频
    if [ $XIAOYA_COUNT -gt 0 ]; then
        echo "✅ 小雅女声片段已生成"
    else
        echo "⚠️  警告：未找到小雅的音频片段"
    fi
else
    echo "❌ 生成失败：未找到音频文件"
    exit 1
fi

echo ""
echo "🎉 全部完成！可以试听或发布了"
