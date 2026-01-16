#!/bin/bash
# 服务器配置检查脚本
# 用于检查 agent.tomo-ai.cn 服务器的配置信息

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SERVER="agent.tomo-ai.cn"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  服务器配置检查: ${SERVER}${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 检查 SSH 连接
echo -e "${GREEN}[1] 检查 SSH 连接配置...${NC}"
if ssh -o ConnectTimeout=5 -o BatchMode=yes $SERVER "echo 'SSH连接成功'" 2>/dev/null; then
    echo -e "✓ SSH 连接正常\n"
else
    echo -e "${YELLOW}⚠ SSH 需要密码认证，将尝试交互式连接...${NC}\n"
fi

# 执行远程命令检查配置
echo -e "${GREEN}[2] 系统信息...${NC}"
ssh $SERVER << 'EOF'
    echo "--- 系统信息 ---"
    hostname
    uname -a
    echo ""
    echo "--- 系统资源 ---"
    free -h 2>/dev/null || vm_stat | head -10
    df -h | head -5
    echo ""
    echo "--- Docker 信息 ---"
    docker --version 2>/dev/null || echo "Docker 未安装"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "无运行中的容器"
    echo ""
    echo "--- Docker Compose 服务 ---"
    docker compose ps 2>/dev/null || docker-compose ps 2>/dev/null || echo "Docker Compose 未安装或未配置"
    echo ""
    echo "--- 网络配置 ---"
    docker network ls 2>/dev/null || echo "Docker 网络信息不可用"
    echo ""
    echo "--- 端口监听 ---"
    netstat -tuln 2>/dev/null | grep LISTEN | head -20 || ss -tuln 2>/dev/null | grep LISTEN | head -20 || echo "端口信息不可用"
    echo ""
    echo "--- 服务状态 ---"
    systemctl list-units --type=service --state=running 2>/dev/null | head -10 || echo "systemd 不可用"
EOF

echo ""
echo -e "${GREEN}[3] 检查应用服务配置...${NC}"
ssh $SERVER << 'EOF'
    echo "--- 查找应用目录 ---"
    find /root -maxdepth 3 -type d -name "apps" -o -name "teamventure" -o -name "nginx" 2>/dev/null | head -10
    echo ""
    echo "--- 查找 docker-compose.yml ---"
    find /root -name "docker-compose.yml" 2>/dev/null | head -5
    echo ""
    echo "--- 查找 nginx.conf ---"
    find /root -name "nginx.conf" 2>/dev/null | head -5
EOF

echo ""
echo -e "${GREEN}✓ 配置检查完成${NC}"
echo ""
echo -e "${BLUE}提示: 如需查看详细配置，请手动连接服务器:${NC}"
echo -e "  ssh ${SERVER}"
