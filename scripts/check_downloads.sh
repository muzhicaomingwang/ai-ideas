#!/bin/bash
# 诊断脚本：输出 Downloads 当前状态

OUTPUT="/Users/qitmac001395/workspace/QAL/ideas/scripts/downloads_status.txt"

cd ~/Downloads

{
    echo "=== Downloads 目录结构 ==="
    echo ""
    ls -la
    echo ""
    echo "=== 顶层散落文件 ==="
    find . -maxdepth 1 -type f -exec basename {} \;
    echo ""
    echo "=== 各子目录文件数量 ==="
    for dir in */; do
        count=$(find "$dir" -type f 2>/dev/null | wc -l | tr -d ' ')
        echo "$dir: $count 个文件"
    done
} > "$OUTPUT" 2>&1

echo "✅ 已输出到: $OUTPUT"
