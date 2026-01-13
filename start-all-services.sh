#!/bin/bash
# 统一启动所有docker-compose服务(后台常驻模式)
# 用途: 启动Nginx网关 + TeamVenture应用

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  启动所有后台服务${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 1. 启动 Nginx 网关
echo -e "${GREEN}[1/2] 启动 Nginx 网关...${NC}"
cd /Users/qitmac001395/workspace/QAL/ideas/apps/nginx
docker compose up -d
echo -e "✓ Nginx 已启动\n"

# 2. 启动 TeamVenture 应用
echo -e "${GREEN}[2/2] 启动 TeamVenture 应用...${NC}"
cd /Users/qitmac001395/workspace/QAL/ideas/apps/teamventure
make up
echo -e "✓ TeamVenture 已启动\n"

# 显示所有运行的容器
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  所有服务状态${NC}"
echo -e "${BLUE}================================${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo -e "${GREEN}✓ 所有服务已启动并后台运行${NC}"
echo ""
echo -e "${BLUE}快速访问:${NC}"
echo -e "  - Nginx:              http://localhost"
echo -e "  - TeamVenture Java:   http://localhost:8080"
echo -e "  - TeamVenture Python: http://localhost:8000"
echo -e "  - RabbitMQ管理界面:   http://localhost:15672 (admin/admin123456)"
echo ""
echo -e "${BLUE}查看日志:${NC}"
echo -e "  cd apps/teamventure && make logs"
echo -e "  cd apps/nginx && docker compose logs -f"
echo ""
echo -e "${BLUE}停止所有服务:${NC}"
echo -e "  ./stop-all-services.sh"
echo ""
