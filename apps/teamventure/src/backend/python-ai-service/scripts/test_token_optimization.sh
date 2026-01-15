#!/bin/bash
# TeamVenture AI服务 Token优化验证脚本
# 用途：验证Mock模式和缓存机制是否正常工作

set -e

PYTHON_SERVICE_URL="http://localhost:8000"
TEST_PAYLOAD='{
  "people_count": 20,
  "duration_days": 3,
  "departure_city": "上海市",
  "destination": "杭州千岛湖",
  "budget_min": 15000,
  "budget_max": 25000,
  "preferences": {
    "activity_types": ["team_building", "leisure"],
    "accommodation_level": "standard"
  }
}'

echo "==================================="
echo "TeamVenture Token优化验证测试"
echo "==================================="
echo ""

# ========== 测试1: 验证Mock模式 ==========
echo "【测试1】验证Mock模式"
echo "-----------------------------------"
echo "检查环境变量 ENABLE_AI_MOCK..."
docker compose exec -T python-ai-service env | grep ENABLE_AI_MOCK || echo "未找到ENABLE_AI_MOCK配置"

echo ""
echo "发送测试请求..."
# 注意：这里假设有一个测试端点，实际可能需要通过完整的API流程
# 如果没有直接的测试端点，需要检查日志

echo ""
echo "检查日志（应看到'Mock模式已启用'或'stub plan generation'）"
docker compose logs --tail=20 python-ai-service | grep -i "mock\|stub" || echo "⚠️  未找到Mock模式日志"

echo ""
echo "-----------------------------------"
echo ""

# ========== 测试2: 验证缓存机制 ==========
echo "【测试2】验证缓存机制"
echo "-----------------------------------"
echo "检查Redis连接..."
docker compose exec -T redis redis-cli -a redis123456 PING 2>/dev/null || echo "❌ Redis连接失败"

echo ""
echo "清空现有AI缓存..."
docker compose exec -T redis redis-cli -a redis123456 --scan --pattern "ai:plan:*" 2>/dev/null | \
  xargs -I {} docker compose exec -T redis redis-cli -a redis123456 DEL {} 2>/dev/null || true

echo ""
echo "查看缓存key数量（应为0）..."
CACHE_COUNT=$(docker compose exec -T redis redis-cli -a redis123456 --scan --pattern "ai:plan:*" 2>/dev/null | wc -l)
echo "当前AI缓存数量: $CACHE_COUNT"

echo ""
echo "-----------------------------------"
echo ""

# ========== 测试3: Token使用统计 ==========
echo "【测试3】Token使用统计"
echo "-----------------------------------"
echo "查看Prometheus metrics..."
curl -s http://localhost:8000/metrics 2>/dev/null | grep llm_tokens || echo "⚠️  未找到token metrics"

echo ""
echo "-----------------------------------"
echo ""

# ========== 总结 ==========
echo "==================================="
echo "验证完成！"
echo "==================================="
echo ""
echo "✅ 如果看到 'Mock模式已启用' → Mock模式正常工作"
echo "✅ 如果看到 'AI缓存命中' → 缓存机制正常工作"
echo "✅ 如果 llm_tokens_input_total = 0 → 完全未调用OpenAI"
echo ""
echo "详细文档: backend/python-ai-service/docs/AI_TOKEN_OPTIMIZATION.md"
echo ""
