#!/bin/bash
# 测试飞书通知的各种场景

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo "========================================="
echo "飞书通知功能测试"
echo "========================================="
echo ""

# 加载环境变量
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)
fi

PYTHON="$PROJECT_DIR/venv/bin/python"
TODAY=$(date +%Y-%m-%d)

# 测试1: 成功通知
echo "📝 测试1: 发送成功通知"
$PYTHON scripts/notify_feishu.py \
    --date "$TODAY" \
    --article-count 10 \
    --status success

echo ""
echo "✅ 测试1完成，检查飞书是否收到蓝色卡片"
echo ""
read -p "按回车继续下一个测试..."

# 测试2: 失败通知
echo ""
echo "📝 测试2: 发送失败通知"
$PYTHON scripts/notify_feishu.py \
    --date "$TODAY" \
    --status failed \
    --error "测试错误: 模拟网络超时"

echo ""
echo "✅ 测试2完成，检查飞书是否收到红色卡片"
echo ""
read -p "按回车继续下一个测试..."

# 测试3: 离线队列（模拟网络断开）
echo ""
echo "📝 测试3: 模拟离线场景"
echo "   (临时禁用网络连接，消息会加入队列)"
echo ""
echo "⚠️  请手动断开网络（关闭WiFi），然后按回车..."
read

$PYTHON scripts/notify_feishu.py \
    --date "$TODAY" \
    --article-count 8 \
    --status success || echo "预期失败（网络已断开）"

echo ""
echo "✅ 测试3完成，消息应该已加入队列"
echo "   查看队列文件: logs/notification_queue/pending_messages.json"
cat logs/notification_queue/pending_messages.json 2>/dev/null || echo "（队列文件不存在）"
echo ""
read -p "按回车继续下一个测试..."

# 测试4: 网络恢复重试
echo ""
echo "📝 测试4: 模拟网络恢复"
echo ""
echo "⚠️  请重新连接网络（打开WiFi），然后按回车..."
read

$PYTHON scripts/notify_feishu.py --retry-queue

echo ""
echo "✅ 测试4完成，检查飞书是否收到队列中的消息"
echo "   查看队列文件（应该为空）:"
cat logs/notification_queue/pending_messages.json 2>/dev/null || echo "（队列已清空）"
echo ""

# 测试总结
echo "========================================="
echo "测试总结"
echo "========================================="
echo ""
echo "✅ 所有测试完成！"
echo ""
echo "预期结果："
echo "1. 收到蓝色卡片（成功通知）"
echo "2. 收到红色卡片（失败通知）"
echo "3. 网络断开时消息进入队列"
echo "4. 网络恢复后队列消息自动发送"
echo ""
echo "如果全部符合预期，说明功能正常 🎉"
