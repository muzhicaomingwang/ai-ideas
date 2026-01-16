#!/bin/bash
# 快速部署脚本 - 一键部署到 TOMO 服务器
# 使用方法: ./scripts/quick-deploy.sh

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SERVER="root@agent.tomo-ai.cn"
APPS_DIR="/root/apps"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  🚀 快速部署到 TOMO 服务器${NC}"
echo -e "${BLUE}  目标服务器: agent.tomo-ai.cn${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 检查本地环境
echo -e "${GREEN}[1] 检查本地环境...${NC}"

# 检查 rsync
if ! command -v rsync >/dev/null 2>&1; then
    echo -e "${RED}✗ 需要安装 rsync${NC}"
    exit 1
fi

# 检查配置文件
if [ ! -d "apps/nginx" ] || [ ! -d "apps/teamventure" ] || [ ! -d "apps/zhimeng-agent" ]; then
    echo -e "${RED}✗ 应用配置目录不存在${NC}"
    exit 1
fi

echo -e "✓ 本地环境检查通过\n"

# 部署应用
echo -e "${GREEN}[2] 部署应用到服务器...${NC}"

# 创建服务器目录
echo "创建服务器目录结构..."
ssh -t $SERVER "mkdir -p ${APPS_DIR}/{nginx,teamventure,zhimeng-agent}"

# 同步配置文件
echo "同步 Nginx 配置..."
rsync -avz --exclude='.git' --exclude='__pycache__' \
    --exclude='*.log' --exclude='cache/' \
    apps/nginx/ ${SERVER}:${APPS_DIR}/nginx/

echo "同步 TeamVenture 配置..."
rsync -avz --exclude='.git' --exclude='__pycache__' \
    --exclude='*.log' --exclude='cache/' --exclude='output/' \
    apps/teamventure/ ${SERVER}:${APPS_DIR}/teamventure/

echo "同步 Zhimeng Agent 配置..."
rsync -avz --exclude='.git' --exclude='__pycache__' \
    --exclude='*.log' --exclude='cache/' \
    apps/zhimeng-agent/ ${SERVER}:${APPS_DIR}/zhimeng-agent/

echo -e "✓ 配置同步完成\n"

# 服务器端部署
echo -e "${GREEN}[3] 服务器端部署...${NC}"
ssh -t $SERVER << EOF
    echo "=========================================="
    echo "服务器端部署开始"
    echo "=========================================="

    cd ${APPS_DIR}

    # 创建共享网络
    echo "创建 Docker 共享网络..."
    docker network create apps-shared-network 2>/dev/null || echo "网络已存在"

    echo ""
    echo "=========================================="
    echo "启动 Nginx 网关"
    echo "=========================================="
    cd nginx
    echo "停止旧服务..."
    docker compose down 2>/dev/null || true
    echo "启动新服务..."
    docker compose up -d
    echo "Nginx 服务状态:"
    docker compose ps

    echo ""
    echo "=========================================="
    echo "启动 TeamVenture 应用"
    echo "=========================================="
    cd ../teamventure/src
    echo "停止旧服务..."
    make down 2>/dev/null || true
    echo "启动新服务..."
    make up
    echo "TeamVenture 服务状态:"
    make status

    echo ""
    echo "=========================================="
    echo "启动 Zhimeng Agent"
    echo "=========================================="
    cd ../../zhimeng-agent
    echo "停止旧服务..."
    docker compose down 2>/dev/null || true
    echo "启动新服务..."
    docker compose up -d
    echo "Zhimeng Agent 服务状态:"
    docker compose ps

    echo ""
    echo "=========================================="
    echo "所有服务状态总览"
    echo "=========================================="
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

    echo ""
    echo "=========================================="
    echo "服务健康检查"
    echo "=========================================="
    echo "测试 Nginx 网关:"
    curl -s http://localhost | head -5

    echo ""
    echo "测试 TeamVenture 健康检查:"
    curl -s http://localhost/actuator/health

    echo ""
    echo "测试 AI 服务:"
    curl -s http://localhost/ai/health

    echo ""
    echo "=========================================="
    echo "部署完成！"
    echo "=========================================="
EOF

echo ""
echo -e "${GREEN}✓ 部署完成！${NC}"
echo ""
echo -e "${BLUE}🎉 服务访问地址:${NC}"
echo -e "  🌐 Nginx 网关:         http://agent.tomo-ai.cn"
echo -e "  🚀 TeamVenture API:    http://agent.tomo-ai.cn/api/v1/"
echo -e "  🤖 AI 服务:           http://agent.tomo-ai.cn/ai/"
echo -e "  📱 XHS 抓取服务:       http://agent.tomo-ai.cn/xhs/"
echo -e "  💬 Zhimeng Agent:      http://agent.tomo-ai.cn:8001"
echo ""
echo -e "${BLUE}🔧 管理命令:${NC}"
echo -e "  📊 查看状态:  ssh ${SERVER} 'docker ps'"
echo -e "  📝 查看日志:  ssh ${SERVER} 'cd ${APPS_DIR}/teamventure/src && make logs'"
echo -e "  🔄 重启服务:  ssh ${SERVER} '${APPS_DIR}/start-all-services.sh'"
echo -e "  ⏹️  停止服务:  ssh ${SERVER} '${APPS_DIR}/stop-all-services.sh'"
echo ""
echo -e "${GREEN}🎊 落地部署成功！所有服务已启动并运行！${NC}"