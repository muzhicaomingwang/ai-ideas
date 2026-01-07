#!/bin/bash
# 启动带调试端口的 Chrome（独立实例，不影响正常 Chrome）

CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DEBUG_PORT=9222
USER_DATA_DIR="$HOME/.chrome-playwright-debug"

# 检查端口是否已被占用
if lsof -i:$DEBUG_PORT > /dev/null 2>&1; then
    echo "✓ Chrome 调试端口 $DEBUG_PORT 已在监听"
    echo "  可以直接连接: http://localhost:$DEBUG_PORT"
    echo ""
    echo "如需重启，请先运行: kill \$(lsof -t -i:$DEBUG_PORT)"
    exit 0
fi

echo "=========================================="
echo "启动 Chrome 调试实例"
echo "=========================================="
echo ""
echo "调试端口: $DEBUG_PORT"
echo "用户目录: $USER_DATA_DIR"
echo ""
echo "注意: 这是一个独立的 Chrome 实例"
echo "      不会影响你正常使用的 Chrome"
echo ""

# 创建用户数据目录
mkdir -p "$USER_DATA_DIR"

# 启动独立的 Chrome 实例
"$CHROME_PATH" \
    --remote-debugging-port=$DEBUG_PORT \
    --user-data-dir="$USER_DATA_DIR" \
    --no-first-run \
    --no-default-browser-check \
    --disable-background-networking \
    --disable-sync \
    "https://www.xiaohongshu.com" \
    &

sleep 3

if lsof -i:$DEBUG_PORT > /dev/null 2>&1; then
    echo ""
    echo "=========================================="
    echo "✓ Chrome 调试实例已启动"
    echo "=========================================="
    echo ""
    echo "下一步操作："
    echo "  1. 在打开的 Chrome 中登录小红书"
    echo "  2. 登录成功后，运行 Python 脚本："
    echo ""
    echo "     cd $(dirname "$0")/.."
    echo "     python3 scripts/connect_chrome.py"
    echo ""
else
    echo "✗ Chrome 启动失败"
    exit 1
fi
