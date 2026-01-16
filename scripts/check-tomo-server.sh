#!/bin/bash
# TOMO 服务器配置检查脚本
# 使用方法: ./scripts/check-tomo-server.sh
# 注意: 需要手动输入 SSH 密码

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SERVER="agent.tomo-ai.cn"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  TOMO 服务器配置检查${NC}"
echo -e "${BLUE}  服务器: ${SERVER}${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 检查 SSH 配置
echo -e "${GREEN}[1] SSH 配置检查${NC}"
if [ -f ~/.ssh/config ]; then
    echo "✓ SSH 配置文件存在"
    if grep -q "agent.tomo-ai.cn" ~/.ssh/config; then
        echo "✓ TOMO 服务器配置已存在"
        echo ""
        echo "配置内容:"
        grep -A 15 "agent.tomo-ai.cn" ~/.ssh/config | head -15
    else
        echo -e "${YELLOW}⚠ TOMO 服务器配置未找到${NC}"
    fi
else
    echo -e "${YELLOW}⚠ SSH 配置文件不存在${NC}"
fi
echo ""

# 尝试连接并获取配置信息
echo -e "${GREEN}[2] 连接服务器并获取配置信息${NC}"
echo -e "${YELLOW}提示: 需要输入跳板机 OTP 和目标服务器密码${NC}"
echo ""

ssh -t $SERVER << 'REMOTE_SCRIPT'
    echo "=========================================="
    echo "系统信息"
    echo "=========================================="
    echo "主机名: $(hostname)"
    echo "系统: $(uname -a)"
    echo "时间: $(date)"
    echo ""
    
    echo "=========================================="
    echo "系统资源"
    echo "=========================================="
    if command -v free >/dev/null 2>&1; then
        free -h
    else
        echo "内存信息:"
        vm_stat | head -5
    fi
    echo ""
    echo "磁盘使用:"
    df -h | head -6
    echo ""
    
    echo "=========================================="
    echo "Docker 信息"
    echo "=========================================="
    if command -v docker >/dev/null 2>&1; then
        echo "Docker 版本:"
        docker --version
        echo ""
        echo "运行中的容器:"
        docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
        echo ""
        echo "所有容器:"
        docker ps -a --format "table {{.Names}}\t{{.Status}}" | head -15
        echo ""
        echo "Docker 网络:"
        docker network ls
        echo ""
        echo "Docker 卷:"
        docker volume ls | head -10
    else
        echo "Docker 未安装"
    fi
    echo ""
    
    echo "=========================================="
    echo "Docker Compose 服务"
    echo "=========================================="
    if command -v docker-compose >/dev/null 2>&1 || docker compose version >/dev/null 2>&1; then
        echo "查找 docker-compose.yml 文件:"
        find /root -maxdepth 4 -name "docker-compose.yml" 2>/dev/null | head -10
        echo ""
        echo "检查服务状态:"
        for compose_file in $(find /root -maxdepth 4 -name "docker-compose.yml" 2>/dev/null | head -5); do
            echo "--- $compose_file ---"
            cd $(dirname "$compose_file")
            docker compose ps 2>/dev/null || docker-compose ps 2>/dev/null || echo "无法获取服务状态"
            echo ""
        done
    else
        echo "Docker Compose 未安装"
    fi
    echo ""
    
    echo "=========================================="
    echo "端口监听"
    echo "=========================================="
    if command -v netstat >/dev/null 2>&1; then
        netstat -tuln | grep LISTEN | head -20
    elif command -v ss >/dev/null 2>&1; then
        ss -tuln | grep LISTEN | head -20
    else
        echo "无法获取端口信息"
    fi
    echo ""
    
    echo "=========================================="
    echo "应用目录结构"
    echo "=========================================="
    if [ -d /root/apps ]; then
        echo "/root/apps 目录:"
        ls -la /root/apps/ 2>/dev/null | head -20
    fi
    if [ -d /root/workspace ]; then
        echo "/root/workspace 目录:"
        ls -la /root/workspace/ 2>/dev/null | head -20
    fi
    echo ""
    
    echo "=========================================="
    echo "Nginx 配置"
    echo "=========================================="
    find /root -name "nginx.conf" 2>/dev/null | head -5
    if [ -f /etc/nginx/nginx.conf ]; then
        echo "系统 Nginx 配置: /etc/nginx/nginx.conf"
    fi
    echo ""
    
    echo "=========================================="
    echo "服务进程"
    echo "=========================================="
    ps aux | grep -E "(nginx|java|python|node)" | grep -v grep | head -10
    echo ""
    
    echo "=========================================="
    echo "系统服务状态"
    echo "=========================================="
    if systemctl list-units >/dev/null 2>&1; then
        systemctl list-units --type=service --state=running | head -15
    else
        echo "systemd 不可用"
    fi
REMOTE_SCRIPT

echo ""
echo -e "${GREEN}✓ 配置检查完成${NC}"
