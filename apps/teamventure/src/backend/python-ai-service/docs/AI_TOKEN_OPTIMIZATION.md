# AI Token 消耗优化指南

## 概述

TeamVenture AI服务在开发测试阶段可能消耗大量GPT-4 tokens（约3000 input + 2000 output per request）。本文档说明如何通过Mock模式和缓存机制减少token消耗。

## Token消耗分析

### 主要消耗点

| 场景 | Input Tokens | Output Tokens | 成本估算 |
|------|-------------|---------------|---------|
| 单次方案生成 | ~2500-3000 | ~2000 | ¥0.8-1.2 |
| 10次测试 | ~30,000 | ~20,000 | ¥8-12 |
| 100次测试 | ~300,000 | ~200,000 | ¥80-120 |

### 消耗来源
- `plan_generation.py:generate_three_plans()` - 每次生成3套完整方案
- Prompt包含：用户输入、季节信息、目的地POI、预算约束、输出契约
- 无缓存时，相同输入每次都重新调用LLM

---

## 优化方案

### 方案1: Mock模式（推荐用于功能测试）

**适用场景**：
- 测试前端交互流程
- 测试数据库读写
- 测试API接口格式
- 快速验证新功能

**启用方式**：
```bash
# 方式1: 修改 .env.local
ENABLE_AI_MOCK=true

# 方式2: 环境变量
export ENABLE_AI_MOCK=true

# 方式3: Docker Compose
docker compose --env-file .env.local up -d
```

**效果**：
- ✅ **Token消耗**: 0（完全不调用OpenAI）
- ✅ **响应速度**: <100ms（无网络请求）
- ✅ **数据质量**: 确定性mock数据（符合schema）
- ❌ **限制**: 无法测试AI生成质量

**Mock数据示例**：
```json
{
  "plan_type": "standard",
  "plan_name": "STANDARD·杭州千岛湖3天团建",
  "summary": "从上海市出发，前往杭州千岛湖，人均¥800，3天行程",
  "highlights": ["人均¥800", "上海市 → 杭州千岛湖", "可对比三套方案"],
  "itinerary": {
    "days": [...]
  }
}
```

---

### 方案2: 缓存机制（自动生效）

**适用场景**：
- 相同参数的重复测试
- QA回归测试
- 演示demo时复用结果

**工作原理**：
1. 基于输入参数（人数、天数、出发地、目的地、预算、偏好）生成hash
2. 首次请求调用LLM并缓存结果（24小时TTL）
3. 后续相同输入直接返回缓存（跳过LLM调用）

**配置**：
```bash
# .env.local
AI_CACHE_ENABLED=true
AI_CACHE_TTL_SECONDS=86400  # 24小时
```

**效果**：
- ✅ **首次**: 正常token消耗（~3000 input + ~2000 output）
- ✅ **后续24h内**: Token消耗为0
- ✅ **数据质量**: 与首次调用完全一致
- ⚠️ **限制**: 修改输入参数会触发新的LLM调用

**缓存Key示例**：
```
ai:plan:f7a2b3c4d5e6f7a8  （基于输入hash）
```

**手动清理缓存**：
```bash
# 进入Redis容器
docker compose exec redis redis-cli -a redis123456

# 查看所有AI缓存key
KEYS ai:plan:*

# 删除特定缓存
DEL ai:plan:f7a2b3c4d5e6f7a8

# 清空所有AI缓存
KEYS ai:plan:* | xargs redis-cli -a redis123456 DEL
```

---

### 方案3: Prompt优化（已实施）

**优化措施**：
- ❌ **优化前**: 传递完整的 `prompt_payload` JSON（~2000 tokens）
- ✅ **优化后**: 只传递关键信息（~800 tokens）
- 减少了 **60%** 的输入token

**优化细节**：
- 移除冗余的JSON dump（`prompt_payload`）
- 压缩JSON schema说明（单行格式）
- 只传递POI名称列表（不传完整对象）
- 合并重复的约束条件

**效果对比**：
| 项目 | 优化前 | 优化后 | 节省 |
|------|-------|-------|------|
| Input Tokens | ~2500 | ~1000 | 60% |
| Output Tokens | ~2000 | ~2000 | 0% |
| 单次成本 | ¥1.0 | ¥0.4 | 60% |

---

## 使用建议

### 开发阶段（推荐配置）
```bash
# .env.local
ENABLE_AI_MOCK=true          # 启用Mock模式
AI_CACHE_ENABLED=true        # 启用缓存
OPENAI_API_KEY=sk-xxx        # 可不填（Mock模式下不使用）
```

**预期token消耗**: 0

---

### 集成测试阶段
```bash
# .env.local
ENABLE_AI_MOCK=false         # 关闭Mock，使用真实AI
AI_CACHE_ENABLED=true        # 启用缓存
OPENAI_API_KEY=sk-real-key   # 必须填写真实key
```

**预期token消耗**:
- 首次测试: ~1000 input + ~2000 output
- 后续24h内重复测试: 0

---

### 生产环境（beta/prod）
```bash
# .env.beta / .env.prod
ENABLE_AI_MOCK=false         # 必须关闭Mock
AI_CACHE_ENABLED=true        # 启用缓存
AI_CACHE_TTL_SECONDS=3600    # 缓存1小时（避免过期数据）
OPENAI_API_KEY=sk-prod-key   # 生产key
```

**预期token消耗**:
- 每个唯一输入组合: ~1000 input + ~2000 output
- 相同输入1小时内: 0

---

## 测试验证

### 验证Mock模式
```bash
# 1. 启用Mock模式
echo "ENABLE_AI_MOCK=true" >> .env.local

# 2. 重启服务
docker compose restart python-ai-service

# 3. 发送测试请求
curl -X POST http://localhost:8000/api/plans/generate \
  -H "Content-Type: application/json" \
  -d '{
    "people_count": 20,
    "duration_days": 3,
    "departure_city": "上海市",
    "destination": "杭州千岛湖"
  }'

# 4. 检查日志（应看到 "AI Mock模式已启用"）
docker compose logs python-ai-service | grep "Mock模式"
```

### 验证缓存机制
```bash
# 1. 关闭Mock，启用缓存
echo "ENABLE_AI_MOCK=false" >> .env.local
echo "AI_CACHE_ENABLED=true" >> .env.local

# 2. 重启服务
docker compose restart python-ai-service

# 3. 首次请求（会调用LLM）
curl -X POST http://localhost:8000/api/plans/generate \
  -H "Content-Type: application/json" \
  -d @test_request.json

# 4. 第二次相同请求（应命中缓存）
curl -X POST http://localhost:8000/api/plans/generate \
  -H "Content-Type: application/json" \
  -d @test_request.json

# 5. 检查日志
docker compose logs python-ai-service | grep "AI缓存命中"
```

### 验证Prompt优化
```bash
# 查看Prometheus metrics（token使用统计）
curl http://localhost:8000/metrics | grep llm_tokens

# 预期结果（优化后）：
# llm_tokens_input_total ~1000
# llm_tokens_output_total ~2000
```

---

## 成本预估

### Mock模式
- **Token消耗**: 0
- **月成本**: ¥0
- **适用**: 功能开发、单元测试、UI测试

### 缓存模式（24小时TTL）
假设每天100个唯一请求（不同的人数/地点/预算组合）：
- **Token消耗**: 100 × (1000 input + 2000 output) = 300K tokens/day
- **月成本**: ~¥360（100次 × ¥0.4 × 30天 ÷ 10 重复率）
- **适用**: 集成测试、预发布验证

### 生产环境（1小时TTL）
假设每天1000个请求，其中20%是重复（缓存命中）：
- **Token消耗**: 800 × (1000 input + 2000 output) = 2.4M tokens/day
- **月成本**: ~¥960（800次 × ¥0.4 × 30天）
- **适用**: 正式上线后

---

## 故障排查

### Mock模式未生效
```bash
# 检查配置
docker compose exec python-ai-service env | grep ENABLE_AI_MOCK

# 检查日志
docker compose logs python-ai-service | grep -i "mock\|stub"

# 可能原因：
# 1. .env.local未生效（检查docker-compose.yml的env_file配置）
# 2. 环境变量拼写错误（应为ENABLE_AI_MOCK，不是ENABLE_MOCK_AI）
```

### 缓存未命中
```bash
# 检查Redis连接
docker compose exec python-ai-service python -c "
import redis
r = redis.Redis(host='localhost', port=6379, password='redis123456')
print(r.ping())
"

# 查看缓存key
docker compose exec redis redis-cli -a redis123456 KEYS "ai:plan:*"

# 可能原因：
# 1. Redis未启动
# 2. 输入参数有微小差异（导致hash不同）
# 3. TTL已过期
```

### Token仍然很高
```bash
# 检查是否有其他LLM调用点
grep -r "client.generate_json" src/

# 检查Amap是否也在调用LLM（目前不应该）
grep -r "openai" src/integrations/amap_client.py

# 检查每日创意生成是否启用
docker compose exec python-ai-service env | grep DAILY_IDEA_ENABLED
```

---

## 最佳实践

### 开发阶段
1. **默认开启Mock模式**（`ENABLE_AI_MOCK=true`）
2. **需要真实AI测试时**，临时关闭Mock并重启服务
3. **每周五清理一次缓存**，避免测试数据污染

### 测试阶段
1. **功能测试**: 使用Mock模式（验证流程正确性）
2. **AI质量测试**: 关闭Mock，启用缓存（验证生成质量）
3. **性能测试**: 关闭缓存（验证真实响应时间）

### 生产环境
1. **必须关闭Mock**（`ENABLE_AI_MOCK=false`）
2. **启用缓存**，TTL设为1小时（平衡成本与数据新鲜度）
3. **监控token使用**（Prometheus + Grafana）
4. **设置预算告警**（单日超过1000次调用）

---

## 附录：配置快速切换

### 创建配置profile
```bash
# .env.dev（开发模式）
ENABLE_AI_MOCK=true
AI_CACHE_ENABLED=true

# .env.test（测试模式）
ENABLE_AI_MOCK=false
AI_CACHE_ENABLED=true
AI_CACHE_TTL_SECONDS=86400

# .env.prod（生产模式）
ENABLE_AI_MOCK=false
AI_CACHE_ENABLED=true
AI_CACHE_TTL_SECONDS=3600
```

### 快速切换
```bash
# 开发模式
cp .env.dev .env && docker compose restart python-ai-service

# 测试模式
cp .env.test .env && docker compose restart python-ai-service

# 生产模式
cp .env.prod .env && docker compose restart python-ai-service
```

---

## 更新日志

- **2026-01-15**: 初始版本，添加Mock模式、缓存机制、Prompt优化
  - 实现 `ENABLE_AI_MOCK` 环境变量
  - 添加基于Redis的AI响应缓存（24小时TTL）
  - 优化Prompt减少60% input tokens（2500 → 1000）
