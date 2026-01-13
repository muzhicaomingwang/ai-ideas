#!/bin/bash
# 统一停止所有docker-compose服务

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  停止所有服务${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 1. 停止 TeamVenture 应用
echo -e "${GREEN}[1/2] 停止 TeamVenture 应用...${NC}"
cd /Users/qitmac001395/workspace/QAL/ideas/apps/teamventure
make down
echo -e "✓ TeamVenture 已停止\n"

# 2. 停止 Nginx 网关
echo -e "${GREEN}[2/2] 停止 Nginx 网关...${NC}"
cd /Users/qitmac001395/workspace/QAL/ideas/apps/nginx
docker compose down
echo -e "✓ Nginx 已停止\n"

echo -e "${GREEN}✓ 所有服务已停止${NC}"
echo ""
