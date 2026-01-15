#!/bin/bash
# 播客发布到小宇宙 - 快捷脚本
# 用法: ./publish.sh [日期]
# 示例: ./publish.sh 2026-01-14

set -e

# 项目根目录
PROJECT_ROOT="/Users/qitmac001395/workspace/QAL/ideas/apps/daily-podcast-ai"
cd "$PROJECT_ROOT"

# 获取日期参数（默认今天）
DATE=${1:-$(date +%Y-%m-%d)}

echo "🎙️ 开始发布播客: $DATE"
echo ""

# 检查环境变量
if [ ! -f .env ]; then
    echo "❌ 错误: .env 文件不存在"
    echo "   请复制 .env.example 并填入API密钥"
    exit 1
fi

# 加载环境变量
export $(grep -v '^#' .env | xargs)

if [ -z "$RSS_COM_API_KEY" ] || [ -z "$RSS_COM_PODCAST_ID" ]; then
    echo "❌ 错误: RSS.com 凭证未配置"
    echo "   请在 .env 中设置:"
    echo "   - RSS_COM_API_KEY"
    echo "   - RSS_COM_PODCAST_ID"
    exit 1
fi

# 检查播客文件是否存在
OUTPUT_DIR="output/$DATE/dailyReport"
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "❌ 错误: 播客文件不存在: $OUTPUT_DIR"
    echo "   请先运行: python scripts/daily_generate.py --date $DATE"
    exit 1
fi

# 执行发布
echo "📤 发布到 RSS.com..."
python scripts/publish_to_rss.py --date "$DATE"

RESULT=$?
if [ $RESULT -eq 0 ]; then
    echo ""
    echo "🎉 发布成功!"
    echo "   RSS Feed: https://rss.com/podcasts/$RSS_COM_PODCAST_ID/feed.xml"
    echo "   小宇宙: https://podcaster.xiaoyuzhoufm.com/podcasts/695e1e64e0970c835fb2e784/home"
    echo ""
    echo "💡 提示: 小宇宙将在1小时内自动同步新单集"
else
    echo ""
    echo "❌ 发布失败，请查看错误日志:"
    echo "   tail -50 logs/daily_error.log"
    exit 1
fi
