#!/bin/bash
# 部署到 TOMO 服务器脚本
# 使用方法: ./scripts/deploy-to-tomo.sh

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SERVER="agent.tomo-ai.cn"
APPS_DIR="/root/apps"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  部署到 TOMO 服务器${NC}"
echo -e "${BLUE}  目标服务器: ${SERVER}${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 检查本地SSH配置
echo -e "${GREEN}[1] 检查SSH配置...${NC}"
if [ ! -f ~/.ssh/config ] || ! grep -q "agent.tomo-ai.cn" ~/.ssh/config; then
    echo -e "${RED}✗ SSH配置不完整，请先配置SSH跳板机${NC}"
    echo -e "${YELLOW}参考: docs/ssh-jump-host-config.md${NC}"
    exit 1
fi
echo -e "✓ SSH配置正常\n"

# 检查服务器连接
echo -e "${GREEN}[2] 测试服务器连接...${NC}"
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes $SERVER "echo '连接测试成功'" >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ 无法自动连接，需要手动输入密码${NC}"
    echo -e "${YELLOW}请手动运行: ssh ${SERVER}${NC}"
    echo -e "${YELLOW}然后输入跳板机OTP和服务器密码${NC}"
    exit 1
fi
echo -e "✓ 服务器连接正常\n"

# 部署前的准备
echo -e "${GREEN}[3] 部署前准备...${NC}"

# 创建部署目录
ssh $SERVER "mkdir -p ${APPS_DIR}"

# 同步配置文件
echo "同步基础配置文件..."
rsync -avz --exclude='.git' --exclude='__pycache__' \
    --exclude='*.log' --exclude='cache/' \
    apps/nginx/ ${SERVER}:${APPS_DIR}/nginx/

rsync -avz --exclude='.git' --exclude='__pycache__' \
    --exclude='*.log' --exclude='cache/' --exclude='output/' \
    apps/teamventure/ ${SERVER}:${APPS_DIR}/teamventure/

rsync -avz --exclude='.git' --exclude='__pycache__' \
    --exclude='*.log' --exclude='cache/' --exclude='output/' \
    apps/zhimeng-agent/ ${SERVER}:${APPS_DIR}/zhimeng-agent/

echo -e "✓ 配置文件同步完成\n"

# 服务器端部署
echo -e "${GREEN}[4] 服务器端部署...${NC}"
ssh -t $SERVER << EOF
    cd ${APPS_DIR}

    echo "=========================================="
    echo "检查Docker环境"
    echo "=========================================="
    docker --version
    docker compose version 2>/dev/null || docker-compose --version

    echo ""
    echo "=========================================="
    echo "创建共享网络"
    echo "=========================================="
    docker network create apps-shared-network 2>/dev/null || echo "网络已存在"

    echo ""
    echo "=========================================="
    echo "启动 Nginx 网关"
    echo "=========================================="
    cd nginx
    docker compose down 2>/dev/null || true
    docker compose up -d
    docker compose ps

    echo ""
    echo "=========================================="
    echo "启动 TeamVenture 应用"
    echo "=========================================="
    cd ../teamventure/src
    make down 2>/dev/null || true
    make up
    make status

    echo ""
    echo "=========================================="
    echo "启动 Zhimeng Agent"
    echo "=========================================="
    cd ../../zhimeng-agent
    docker compose down 2>/dev/null || true
    docker compose up -d
    docker compose ps

    echo ""
    echo "=========================================="
    echo "所有服务状态"
    echo "=========================================="
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
EOF

echo ""
echo -e "${GREEN}✓ 部署完成！${NC}"
echo ""
echo -e "${BLUE}服务访问地址:${NC}"
echo -e "  - Nginx 网关:         http://${SERVER}"
echo -e "  - TeamVenture API:    http://${SERVER}/api/v1/"
echo -e "  - AI 服务:           http://${SERVER}/ai/"
echo -e "  - XHS 抓取服务:       http://${SERVER}/xhs/"
echo -e "  - Zhimeng Agent:      http://${SERVER}:8001"
echo ""
echo -e "${BLUE}管理命令:${NC}"
echo -e "  - 查看状态: ssh ${SERVER} 'docker ps'"
echo -e "  - 查看日志: ssh ${SERVER} 'cd ${APPS_DIR}/teamventure/src && make logs'"
echo -e "  - 重启服务: ssh ${SERVER} '${APPS_DIR}/start-all-services.sh'"
echo -e "  - 停止服务: ssh ${SERVER} '${APPS_DIR}/stop-all-services.sh'"
echo ""
echo -e "${GREEN}部署成功完成！${NC}"