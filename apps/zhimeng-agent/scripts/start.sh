#!/bin/bash
# 飞书长连接服务启动脚本
# 用于 LaunchAgent 自动启动

# 设置工作目录
cd /Users/qitmac001395/workspace/QAL/ideas/apps/zhimeng-agent

# 使用 Poetry 虚拟环境中的 Python 直接运行
# 这样可以避免 launchd 环境下 poetry run 无法正确激活虚拟环境的问题
VENV_PYTHON="/Users/qitmac001395/Library/Caches/pypoetry/virtualenvs/zhimeng-agent-ORFMGT-6-py3.12/bin/python"

# 检查 Python 是否存在
if [ ! -f "$VENV_PYTHON" ]; then
    echo "错误: 找不到 Python 虚拟环境: $VENV_PYTHON"
    echo "请运行: cd /Users/qitmac001395/workspace/QAL/ideas/apps/zhimeng-agent && poetry install"
    exit 1
fi

# 启动服务
exec "$VENV_PYTHON" src/feishu_ws.py
