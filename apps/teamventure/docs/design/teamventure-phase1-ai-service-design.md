# TeamVenture Phase 1 - Python AI服务详细设计

> **版本**: v1.0
> **日期**: 2026-01-04
> **状态**: 正式版本（基于实际实现反向工程）
> **重要性**: ⭐⭐⭐⭐⭐ 本文档描述AI服务的实际架构与实现

---

## 📋 文档导航

| 章节 | 内容 | 页码范围 |
|------|------|---------|
| 第1章 | 整体架构与技术栈 | 1-50 |
| 第2章 | LangGraph工作流设计 | 51-150 |
| 第3章 | 核心服务模块详解 | 151-350 |
| 第4章 | LLM集成与Prompt工程 | 351-500 |
| 第5章 | 消息队列集成 | 501-600 |
| 第6章 | 数据模型与验证 | 601-700 |
| 第7章 | 错误处理与监控 | 701-800 |
| 第8章 | 部署与配置管理 | 801-900 |

---

## 第1章 整体架构与技术栈

### 1.1 服务定位

TeamVenture Python AI服务是整个系统的**智能核心**，负责：
1. **方案智能生成**：基于用户需求生成3套团建方案（经济型/标准型/品质型）
2. **供应商智能匹配**：根据预算、城市、偏好匹配合适的供应商
3. **需求理解与解析**：将结构化输入转换为AI可理解的上下文
4. **异步任务处理**：通过RabbitMQ实现与Java服务的解耦

**设计原则**:
- ✅ **可运行性优先**：即使没有OpenAI API Key，也能通过stub模式生成演示方案
- ✅ **轻量级实现**：不依赖重型LangGraph框架，使用简洁的Python异步流程
- ✅ **快速失败**：错误明确传递，便于调试
- ✅ **可观测性**：完整的日志记录，支持Prometheus监控

### 1.2 技术栈

| 技术 | 版本 | 用途 | 选型理由 |
|------|------|------|---------|
| **Python** | 3.11+ | 主语言 | 异步支持、AI生态完善 |
| **FastAPI** | 0.109+ | Web框架 | 高性能、自动文档、异步原生 |
| **OpenAI SDK** | 1.x | LLM调用 | 官方SDK、稳定可靠 |
| **pydantic** | 2.x | 数据验证 | 类型安全、运行时验证 |
| **aio-pika** | 9.x | RabbitMQ客户端 | 异步AMQP客户端 |
| **httpx** | 0.27+ | HTTP客户端 | 异步HTTP请求（调用Java服务） |
| **python-dotenv** | 1.0+ | 配置管理 | 环境变量加载 |
| **uvicorn** | 0.27+ | ASGI服务器 | 生产级ASGI服务器 |

**不使用的技术**（刻意决策）:
- ❌ **LangGraph框架本身**：过于重型，简单场景不需要
- ❌ **LangChain Agent**：当前流程固定，不需要动态规划
- ❌ **Celery**：已有RabbitMQ，无需额外任务队列框架

### 1.3 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    Python AI Service (FastAPI)                   │
│                        端口: 8000                                 │
└─────────────────────────────────────────────────────────────────┘
         ▲                           │                        ▲
         │                           │                        │
         │ HTTP                      │ AMQP                   │ HTTP
         │ /health                   │ Consumer               │ /internal/plans/batch
         │                           │                        │
         │                           ▼                        │
    ┌────────┐              ┌──────────────┐        ┌────────────────┐
    │  User  │              │  RabbitMQ    │        │  Java Service  │
    │  (Dev) │              │  Exchange:   │        │  (Callback)    │
    └────────┘              │  plan.gen    │        └────────────────┘
                            │              │
                            │  Queue:      │
                            │  ai.gen.req  │
                            └──────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   内部流程（Workflow）                            │
│                                                                   │
│   parse_requirements  →  match_suppliers  →  generate_three_plans│
│         ↓                      ↓                       ↓          │
│   计算衍生字段            供应商匹配              OpenAI GPT-4     │
│   (duration_days, etc)   (演示模式/LLM增强)    或stub fallback   │
└─────────────────────────────────────────────────────────────────┘
                                   ▼
                          ┌──────────────┐
                          │  OpenAI API  │
                          │  gpt-4-turbo │
                          └──────────────┘
```

### 1.4 服务入口与生命周期

**主应用文件**: `src/main.py`

#### 1.4.1 FastAPI应用初始化

```python
from fastapi import FastAPI
from src.services.mq_consumer import MQConsumer

app = FastAPI(
    title="TeamVenture AI Service",
    version="1.0.0",
    description="LangGraph-based plan generation service",
)

# 全局MQ消费者实例
mq_consumer: MQConsumer | None = None
```

**关键端点**:
- `GET /` - 服务信息
- `GET /health` - 健康检查（Kubernetes liveness probe）
- `POST /trigger-generation` - 手动触发生成（开发调试用）

#### 1.4.2 生命周期管理

```python
@app.on_event("startup")
async def startup_event():
    """启动时连接RabbitMQ并开始消费"""
    global mq_consumer
    mq_consumer = MQConsumer(
        rabbitmq_url=settings.rabbitmq_url,
        queue_name="ai.generation.request",
    )
    await mq_consumer.start()
    logger.info("MQ consumer started")

@app.on_event("shutdown")
async def shutdown_event():
    """优雅关闭MQ连接"""
    if mq_consumer:
        await mq_consumer.stop()
    logger.info("MQ consumer stopped")
```

**启动流程**:
1. FastAPI应用初始化
2. 加载环境变量配置（`settings`）
3. 建立RabbitMQ连接
4. 绑定队列 `ai.generation.request` 到 exchange `plan-generation`
5. 开始消费消息（每条消息触发workflow）
6. Uvicorn监听8000端口，提供HTTP健康检查

---

## 第2章 LangGraph工作流设计

### 2.1 工作流概览

TeamVenture的方案生成流程设计为**三阶段串行Pipeline**：

```
用户请求 (MQ消息)
    ↓
┌──────────────────────────────────────────────────┐
│  Stage 1: parse_requirements                     │
│  - 解析用户输入                                   │
│  - 计算衍生字段 (duration_days, budget_per_person)│
│  - 结构化偏好数据                                 │
└──────────────────────────────────────────────────┘
    ↓ (parsed_requirements)
┌──────────────────────────────────────────────────┐
│  Stage 2: match_suppliers                        │
│  - 匹配供应商 (当前演示模式)                      │
│  - 未来: LLM增强的语义匹配                        │
└──────────────────────────────────────────────────┘
    ↓ (matched_suppliers)
┌──────────────────────────────────────────────────┐
│  Stage 3: generate_three_plans                   │
│  - 调用OpenAI GPT-4生成3套方案                    │
│  - 或使用stub fallback (无API key时)             │
│  - 归一化输出格式                                 │
└──────────────────────────────────────────────────┘
    ↓ (generated_plans)
回调Java服务 (/internal/plans/batch)
```

**设计特点**:
1. **轻量级实现**：没有使用LangGraph框架本身，而是用简单的异步函数串联
2. **状态传递**：通过`GenerationState` TypedDict传递各阶段产物
3. **错误容错**：任何阶段异常都会捕获并记录到`state["error"]`
4. **可观测**：每个节点都有日志输出

### 2.2 状态机定义

**文件**: `src/langgraph/state.py`

```python
from typing import Any, Optional, TypedDict

class GenerationState(TypedDict, total=False):
    # 输入
    plan_request_id: str          # 方案请求ID（来自Java）
    user_id: str                   # 用户ID
    user_inputs: dict[str, Any]    # 原始MQ消息

    # Stage 1输出
    parsed_requirements: dict[str, Any]

    # Stage 2输出
    matched_suppliers: list[dict[str, Any]]

    # Stage 3输出
    generated_plans: list[dict[str, Any]]

    # 错误记录
    error: Optional[str]
```

**字段说明**:
- `total=False`：允许字段逐步填充，各阶段只填充自己产生的字段
- `plan_request_id`：全局追踪ID，贯穿整个流程
- `user_inputs`：保留原始输入，便于错误回溯
- `error`：任何阶段失败都会设置此字段，workflow提前终止

### 2.3 工作流执行函数

**文件**: `src/langgraph/workflow.py`

```python
async def run_generation_workflow(message: dict[str, Any]) -> GenerationState:
    """
    Minimal workflow that matches the detailed design phases:
    parse requirements → match suppliers → generate plans.

    This is intentionally a lightweight implementation that can run without LLM keys.
    """
    state: GenerationState = {
        "plan_request_id": message["plan_request_id"],
        "user_id": message["user_id"],
        "user_inputs": message,
    }

    try:
        logger.info("workflow start plan_request_id=%s", state["plan_request_id"])

        # Stage 1: 解析需求
        state["parsed_requirements"] = parse_requirements(message)
        logger.info("requirements parsed plan_request_id=%s", state["plan_request_id"])

        # Stage 2: 匹配供应商
        state["matched_suppliers"] = await match_suppliers(state["parsed_requirements"])
        logger.info(
            "suppliers matched plan_request_id=%s count=%s",
            state["plan_request_id"],
            len(state.get("matched_suppliers") or []),
        )

        # Stage 3: 生成方案
        state["generated_plans"] = await generate_three_plans(
            plan_request_id=state["plan_request_id"],
            user_id=state["user_id"],
            inputs=state["parsed_requirements"],
            matched_suppliers=state["matched_suppliers"],
        )
        logger.info(
            "plans generated plan_request_id=%s count=%s",
            state["plan_request_id"],
            len(state.get("generated_plans") or []),
        )

        return state

    except Exception as exc:
        logger.exception("Generation workflow failed")
        state["error"] = str(exc)
        return state
```

**执行保证**:
- ✅ 即使某阶段抛异常，也会返回`state`（包含`error`字段）
- ✅ 所有阶段日志记录，便于追踪
- ✅ 每个阶段都是异步函数（支持I/O密集操作）

### 2.4 时序图

```
MQ Consumer        │  Workflow         │  OpenAI API    │  Java Service
───────────────────┼───────────────────┼────────────────┼──────────────
    │              │                   │                │
    ├─ 接收消息     │                   │                │
    │ (plan_req_id) │                   │                │
    │              │                   │                │
    ├──────────────>│ run_workflow()   │                │
    │              │                   │                │
    │              ├─ Stage 1:         │                │
    │              │  parse_requirements()             │
    │              │  (同步计算)        │                │
    │              │                   │                │
    │              ├─ Stage 2:         │                │
    │              │  match_suppliers() │               │
    │              │  (返回stub)        │                │
    │              │                   │                │
    │              ├─ Stage 3:         │                │
    │              │  generate_plans() │                │
    │              │                   │                │
    │              ├───────────────────>│ Chat Completion│
    │              │                   │  (GPT-4)       │
    │              │<───────────────────┤ JSON Response  │
    │              │                   │                │
    │              ├─ normalize plans  │                │
    │              │                   │                │
    │<──────────────┤ return state     │                │
    │              │  (3 plans)        │                │
    │              │                   │                │
    ├──────────────────────────────────────────────────>│
    │              │                   │  POST /internal/│
    │              │                   │  plans/batch   │
    │<──────────────────────────────────────────────────┤
    │              │                   │  200 OK        │
    │              │                   │                │
```

---

## 第3章 核心服务模块详解

### 3.1 需求解析服务 (RequirementParser)

**文件**: `src/services/requirement_parser.py`

#### 3.1.1 功能职责

将Java服务发送的**结构化JSON消息**转换为AI可理解的**需求上下文**，包括：
1. **计算衍生字段**：
   - `duration_days`：根据start_date和end_date计算天数
   - `budget_per_person_range`：根据总预算和人数计算人均预算范围
2. **数据类型转换**：确保字段类型正确（int, float, str）
3. **缺失值处理**：为可选字段提供默认值
4. **日期解析**：ISO格式字符串 → Python date对象 → 计算差值

#### 3.1.2 实现细节

```python
def parse_requirements(message: dict[str, Any]) -> dict[str, Any]:
    """
    Rule-based parsing per detailed-design: no LLM call.
    """
    # 1. 提取基础字段
    people_count = int(message["people_count"])
    budget_min = float(message["budget_min"])
    budget_max = float(message["budget_max"])

    # 2. 解析日期并计算天数
    start_date = date.fromisoformat(message["start_date"])  # "2026-02-01" → date(2026, 2, 1)
    end_date = date.fromisoformat(message["end_date"])      # "2026-02-03" → date(2026, 2, 3)
    duration_days = (end_date - start_date).days + 1        # 3天

    # 3. 计算人均预算
    budget_per_person_min = budget_min / max(people_count, 1)
    budget_per_person_max = budget_max / max(people_count, 1)

    # 4. 提取偏好（可选）
    preferences = message.get("preferences") or {}

    # 5. 返回结构化需求
    return {
        "people_count": people_count,
        "budget_min": budget_min,
        "budget_max": budget_max,
        "budget_per_person_range": [
            round(budget_per_person_min, 2),
            round(budget_per_person_max, 2)
        ],
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "duration_days": duration_days,
        "departure_city": message.get("departure_city", ""),
        "preferences": preferences,
    }
```

**输入示例** (MQ消息):
```json
{
  "plan_request_id": "plan_req_01ke3cnw4t5dvp8jhjvfdafq1v",
  "user_id": "user_01ke3abc123",
  "people_count": 50,
  "budget_min": 10000,
  "budget_max": 15000,
  "start_date": "2026-02-01",
  "end_date": "2026-02-03",
  "departure_city": "Beijing",
  "preferences": {
    "activity_types": ["team_building"],
    "accommodation": "standard",
    "dining": ["local"]
  }
}
```

**输出示例** (parsed_requirements):
```json
{
  "people_count": 50,
  "budget_min": 10000.0,
  "budget_max": 15000.0,
  "budget_per_person_range": [200.0, 300.0],
  "start_date": "2026-02-01",
  "end_date": "2026-02-03",
  "duration_days": 3,
  "departure_city": "Beijing",
  "preferences": {
    "activity_types": ["team_building"],
    "accommodation": "standard",
    "dining": ["local"]
  }
}
```

**关键设计点**:
- ✅ **无LLM调用**：纯规则计算，快速且确定性强
- ✅ **防除零**：`max(people_count, 1)` 避免人数为0的边界情况
- ✅ **精度控制**：`round(..., 2)` 确保金额为2位小数
- ✅ **ISO日期**：统一使用ISO格式字符串，便于JSON序列化

### 3.2 供应商匹配服务 (SupplierMatcher)

**文件**: `src/services/supplier_matcher.py`

#### 3.2.1 当前实现（演示模式）

```python
async def match_suppliers(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Demo mode: return hardcoded suppliers.
    Future: semantic matching via LLM or vector DB.
    """
    # 演示供应商列表
    return [
        {
            "supplier_id": "sup_hotel_001",
            "name": "北京怀柔雁栖湖国际会展中心",
            "type": "accommodation",
            "price_range": "¥800-1500/间夜",
            "rating": 4.5,
            "tags": ["会议室", "团建场地", "湖景", "大型活动"],
        },
        {
            "supplier_id": "sup_activity_001",
            "name": "密云古北水镇户外拓展基地",
            "type": "activity",
            "price_range": "¥150-300/人",
            "rating": 4.7,
            "tags": ["团队协作", "户外拓展", "长城景观"],
        },
        {
            "supplier_id": "sup_dining_001",
            "name": "怀柔农家院特色餐饮",
            "type": "dining",
            "price_range": "¥80-150/人",
            "rating": 4.3,
            "tags": ["农家菜", "有机食材", "烤全羊"],
        },
    ]
```

#### 3.2.2 未来增强方向

**方案A: 基于MySQL查询**
```python
async def match_suppliers_db(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Query suppliers table by city and category.
    """
    city = inputs.get("departure_city")
    budget_range = inputs.get("budget_per_person_range")

    # 伪代码示例
    suppliers = await db.query(
        "SELECT * FROM suppliers WHERE city = ? AND price_min <= ? AND price_max >= ? AND status = 'ACTIVE'",
        (city, budget_range[1], budget_range[0])
    )
    return suppliers
```

**方案B: LLM语义匹配**
```python
async def match_suppliers_llm(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Use LLM to semantically match suppliers based on preferences.
    """
    preferences = inputs.get("preferences", {})
    prompt = f"""
    Based on these preferences: {preferences},
    rank the following suppliers by relevance:
    ...
    """
    # LLM调用返回排序后的供应商ID列表
```

**方案C: 向量数据库语义搜索**
- 使用Embedding向量存储供应商描述
- 查询时生成需求Embedding
- 余弦相似度匹配Top K供应商

**当前状态**: 演示模式满足一期需求，二期可根据实际数据量选择方案A/B/C

### 3.3 方案生成服务 (PlanGeneration)

**文件**: `src/services/plan_generation.py`

这是AI服务的**最核心模块**，负责调用OpenAI GPT-4生成3套方案。

#### 3.3.1 整体流程

```python
async def generate_three_plans(
    *,
    plan_request_id: str,
    user_id: str,
    inputs: dict[str, Any],
    matched_suppliers: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Generate 3 plans via LLM (preferred) with deterministic fallback.
    """
    # 1. 计算预算目标
    targets = _budget_targets(inputs)  # {budget: min, standard: mid, premium: max}

    # 2. 检查OpenAI配置
    client = OpenAIClient()
    if not client.is_configured():
        logger.warning("OPENAI_API_KEY not configured; using stub plan generation")
        return await _generate_three_plans_stub(...)  # fallback到演示方案

    # 3. 构建Prompt
    prompt_payload = {
        "plan_request_id": plan_request_id,
        "user_id": user_id,
        "inputs": inputs,
        "matched_suppliers": matched_suppliers,
        "constraints": {
            "people_count": people,
            "duration_days": duration_days,
            "departure_city": city,
            "budget_targets_total": targets,
        },
        "output_contract": {
            "plans_length": 3,
            "plan_types": ["budget", "standard", "premium"],
        },
    }

    prompt = f"""
    Generate exactly 3 corporate team-building plans in Chinese.
    Return JSON ONLY with this shape:
    {{
      "plans": [
        {{
          "plan_type": "budget|standard|premium",
          "plan_name": "string",
          ...
        }}
      ]
    }}
    Rules:
    - budget_total must be close to constraints.budget_targets_total for each plan.
    - budget_per_person = budget_total / people_count.

    Input JSON:
    {json.dumps(prompt_payload, ensure_ascii=False)}
    """

    # 4. 调用OpenAI
    raw = await client.generate_json(prompt)

    # 5. 归一化输出
    return _normalize_generated_plans(
        raw=raw,
        plan_request_id=plan_request_id,
        user_id=user_id,
        duration_days=duration_days,
    )
```

#### 3.3.2 预算目标计算

```python
def _budget_targets(inputs: dict[str, Any]) -> dict[str, float]:
    budget_min = float(inputs["budget_min"])
    budget_max = float(inputs["budget_max"])
    return {
        "budget": budget_min,              # 经济型：最低预算
        "standard": (budget_min + budget_max) / 2.0,  # 标准型：中间值
        "premium": budget_max,             # 品质型：最高预算
    }
```

**示例**:
- 输入: budget_min=10000, budget_max=15000
- 输出: {budget: 10000, standard: 12500, premium: 15000}

#### 3.3.3 Stub方案生成（Fallback模式）

```python
async def _generate_three_plans_stub(...) -> list[dict[str, Any]]:
    """
    Deterministic plan generation fallback.
    Keeps the Java → MQ → Python → Java path usable without LLM credentials.
    """
    people = int(inputs["people_count"])
    duration_days = int(inputs["duration_days"])
    city = inputs.get("departure_city") or "目的地"
    targets = _budget_targets(inputs)

    def make_plan(plan_type: str, budget_total: float) -> dict[str, Any]:
        plan_id = new_prefixed_id("plan")
        per_person = round(budget_total / max(people, 1), 2)

        return {
            "plan_id": plan_id,
            "plan_request_id": plan_request_id,
            "user_id": user_id,
            "plan_type": plan_type,
            "plan_name": f"{plan_type.upper()}·{city}{duration_days}天团建",
            "summary": f"人均¥{per_person}，{duration_days}天行程，含住宿/活动/餐饮",
            "highlights": [f"人均¥{per_person}", "可对比三套方案", "供应商信息透明"],
            "itinerary": {
                "days": [
                    {
                        "day": 1,
                        "items": [
                            {"time_start": "09:00", "time_end": "11:00", "activity": "出发前往目的地"},
                            {"time_start": "11:30", "time_end": "13:00", "activity": "午餐"},
                            {"time_start": "14:00", "time_end": "17:00", "activity": "团队活动"},
                        ],
                    }
                ]
            },
            "budget_breakdown": {
                "total": round(budget_total, 2),
                "per_person": per_person,
                "categories": [
                    {"category": "交通", "subtotal": round(budget_total * 0.25, 2)},
                    {"category": "住宿", "subtotal": round(budget_total * 0.35, 2)},
                    {"category": "餐饮", "subtotal": round(budget_total * 0.25, 2)},
                    {"category": "活动", "subtotal": round(budget_total * 0.15, 2)},
                ],
            },
            "supplier_snapshots": matched_suppliers[:],  # 使用匹配的供应商
            "budget_total": round(budget_total, 2),
            "budget_per_person": per_person,
            "duration_days": duration_days,
            "departure_city": city,
            "status": "draft",
        }

    # 生成3套方案
    plans = []
    for plan_type in ["budget", "standard", "premium"]:
        plans.append(make_plan(plan_type, targets[plan_type]))
    return plans
```

**Stub模式的价值**:
- ✅ **本地开发友好**：无需配置OpenAI API Key即可运行
- ✅ **快速验证**：端到端流程验证不依赖外部API
- ✅ **数据格式参考**：Stub输出是LLM输出的标准模板
- ✅ **降级兜底**：生产环境OpenAI故障时的临时降级方案

#### 3.3.4 方案归一化

```python
def _normalize_generated_plans(
    *,
    raw: dict[str, Any],
    plan_request_id: str,
    user_id: str,
    duration_days: int,
) -> list[dict[str, Any]]:
    plans = raw.get("plans")
    if not isinstance(plans, list) or len(plans) != 3:
        raise ValueError("LLM response must include plans: [..3 items..]")

    normalized = []
    for plan in plans:
        if not isinstance(plan, dict):
            raise ValueError("Each plan must be an object")

        normalized.append({
            "plan_id": new_prefixed_id("plan"),  # 生成新的ULID
            "plan_request_id": plan_request_id,
            "user_id": user_id,
            "plan_type": str(plan.get("plan_type", "")),
            "plan_name": str(plan.get("plan_name", "")),
            "summary": str(plan.get("summary", "")),
            "highlights": plan.get("highlights", []),
            "itinerary": plan.get("itinerary", {}),
            "budget_breakdown": plan.get("budget_breakdown", {}),
            "supplier_snapshots": plan.get("supplier_snapshots", []),
            "budget_total": float(plan.get("budget_total", 0.0) or 0.0),
            "budget_per_person": float(plan.get("budget_per_person", 0.0) or 0.0),
            "duration_days": duration_days,
            "departure_city": plan.get("departure_city"),
            "status": "draft",
        })
    return normalized
```

**归一化目的**:
1. **强制类型转换**：确保JSON字段类型正确（str, float, list, dict）
2. **生成plan_id**：为每个方案分配唯一ID（ULID格式）
3. **补充元数据**：添加plan_request_id, user_id, duration_days等
4. **默认值填充**：缺失字段使用空值/零值
5. **验证数量**：必须恰好3个方案，否则抛异常

---

## 第4章 LLM集成与Prompt工程

### 4.1 OpenAI客户端封装

**文件**: `src/integrations/openai_client.py`

#### 4.1.1 类定义

```python
class OpenAIClient:
    """
    Minimal OpenAI client wrapper.

    Note: This repo may run without valid OPENAI_API_KEY in local dev; callers should
    gracefully fall back to deterministic stub generation when keys are missing.
    """

    def __init__(self) -> None:
        self._api_key = settings.openai_api_key
        self._model = settings.openai_model
        self._temperature = settings.openai_temperature
        self._max_tokens = settings.openai_max_tokens

    def is_configured(self) -> bool:
        """检查API Key是否有效配置"""
        return bool(self._api_key and not self._api_key.startswith("sk-xxxx"))
```

**配置读取** (from `src/models/config.py`):
```python
class Settings(BaseSettings):
    openai_api_key: str = "sk-xxxx"  # 占位值，未配置时触发stub模式
    openai_model: str = "gpt-4-turbo-preview"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 4000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

#### 4.1.2 JSON生成方法

```python
async def generate_json(self, prompt: str) -> dict[str, Any]:
    if not self.is_configured():
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = AsyncOpenAI(api_key=self._api_key)

    try:
        response = await client.chat.completions.create(
            model=self._model,                      # gpt-4-turbo-preview
            temperature=self._temperature,          # 0.7
            max_tokens=self._max_tokens,            # 4000
            response_format={"type": "json_object"},  # 强制返回JSON
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful assistant. "
                        "Return ONLY valid JSON that matches the user's requested shape. "
                        "Do not wrap in markdown."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
    except Exception:
        logger.exception("OpenAI call failed")
        raise

    # 提取响应内容
    content = (response.choices[0].message.content or "").strip()
    if not content:
        raise RuntimeError("OpenAI returned empty content")

    # 解析JSON
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        logger.error("OpenAI returned non-JSON content: %r", content[:500])
        raise RuntimeError("OpenAI returned invalid JSON") from exc

    if not isinstance(parsed, dict):
        raise RuntimeError("OpenAI JSON root must be an object")

    return parsed
```

**关键设计点**:
- ✅ **强制JSON模式**：`response_format={"type": "json_object"}` 确保模型输出JSON
- ✅ **System Prompt约束**：明确要求返回纯JSON，不包含markdown代码块
- ✅ **异常详细记录**：解析失败时记录前500字符便于调试
- ✅ **类型验证**：确保根节点是dict（对象），而非数组或字符串

### 4.2 Prompt工程策略

#### 4.2.1 Prompt结构设计

```
┌─────────────────────────────────────────────────┐
│  Prompt 组成（三段式）                           │
├─────────────────────────────────────────────────┤
│  1. 任务描述 (Task Description)                 │
│     - Generate exactly 3 corporate team-building│
│       plans in Chinese                          │
│     - Return JSON ONLY with this shape: ...     │
├─────────────────────────────────────────────────┤
│  2. 输出约束 (Output Constraints)               │
│     - 严格的JSON Schema定义                     │
│     - 字段类型、必填性、值范围                   │
│     - 业务规则 (预算匹配、人均计算等)            │
├─────────────────────────────────────────────────┤
│  3. 输入上下文 (Input Context)                  │
│     - 完整的用户需求JSON                         │
│     - 供应商列表                                 │
│     - 预算目标                                   │
└─────────────────────────────────────────────────┘
```

#### 4.2.2 完整Prompt示例

```python
prompt = """
Generate exactly 3 corporate team-building plans in Chinese.
Return JSON ONLY with this shape:
{
  "plans": [
    {
      "plan_type": "budget|standard|premium",
      "plan_name": "string",
      "summary": "string",
      "highlights": ["string"],
      "itinerary": {
        "days": [
          {
            "day": 1,
            "items": [
              {
                "time_start": "HH:MM",
                "time_end": "HH:MM",
                "activity": "string"
              }
            ]
          }
        ]
      },
      "budget_breakdown": {
        "total": number,
        "per_person": number,
        "categories": [
          {
            "category": "string",
            "subtotal": number
          }
        ]
      },
      "supplier_snapshots": [
        {
          "supplier_id": "string",
          "name": "string",
          "type": "string",
          "price_range": "string"
        }
      ],
      "budget_total": number,
      "budget_per_person": number,
      "departure_city": "string"
    }
  ]
}

Rules:
- plans must match plan_types budget/standard/premium in order.
- budget_total must be close to constraints.budget_targets_total for each plan.
- budget_per_person = budget_total / people_count.
- Keep itinerary duration_days days.

Input JSON:
{
  "plan_request_id": "plan_req_01ke3cnw4t5dvp8jhjvfdafq1v",
  "user_id": "user_01ke3abc123",
  "inputs": {
    "people_count": 50,
    "budget_min": 10000.0,
    "budget_max": 15000.0,
    "duration_days": 3,
    "departure_city": "Beijing",
    "preferences": {
      "activity_types": ["team_building"],
      "accommodation": "standard",
      "dining": ["local"]
    }
  },
  "matched_suppliers": [
    {
      "supplier_id": "sup_hotel_001",
      "name": "北京怀柔雁栖湖国际会展中心",
      "type": "accommodation",
      "price_range": "¥800-1500/间夜"
    },
    ...
  ],
  "constraints": {
    "people_count": 50,
    "duration_days": 3,
    "departure_city": "Beijing",
    "budget_targets_total": {
      "budget": 10000,
      "standard": 12500,
      "premium": 15000
    }
  }
}
"""
```

#### 4.2.3 Prompt优化技巧

**1. JSON Schema约束**
- ✅ **明确字段类型**：`"budget_total": number` 而不是 `"budget_total": "number"`
- ✅ **示例值说明**：`"HH:MM"` 比 `"时间格式"` 更明确
- ✅ **数组示例**：`["string"]` 说明数组元素类型

**2. 业务规则强调**
- ✅ **预算约束**：`budget_total must be close to constraints.budget_targets_total`
- ✅ **计算公式**：`budget_per_person = budget_total / people_count`
- ✅ **排序要求**：`in order` 确保budget/standard/premium顺序

**3. 上下文完整性**
- ✅ **供应商列表**：提供真实数据而非"自行想象"
- ✅ **用户偏好**：activity_types, accommodation, dining等
- ✅ **约束条件**：duration_days, people_count等

**4. 输出质量控制**
```python
# 在System Prompt中强调
"Return ONLY valid JSON that matches the user's requested shape."
"Do not wrap in markdown."

# 在User Prompt中重申
"Return JSON ONLY with this shape:"
```

#### 4.2.4 Prompt迭代历史

| 版本 | 主要改进 | 效果 |
|------|---------|------|
| v0.1 | 简单描述："生成3个方案" | ❌ 返回格式不稳定 |
| v0.2 | 添加JSON Schema | ⚠️ 仍有字段缺失 |
| v0.3 | 强制`response_format=json_object` | ✅ 格式稳定，但预算不准 |
| v0.4 | 添加预算约束规则 | ✅ 预算匹配度提升 |
| v0.5 | 完整上下文（供应商、偏好） | ✅ 当前版本，质量稳定 |

### 4.3 LLM配置参数

**模型选择**:
- **生产环境**: `gpt-4-turbo-preview` (128k上下文，JSON模式支持)
- **测试环境**: `gpt-3.5-turbo` (成本优化)
- **备选模型**: Claude 3 Opus (Anthropic)

**参数调优**:
```python
temperature = 0.7  # 平衡创意性与稳定性
max_tokens = 4000  # 足够生成3套完整方案
top_p = 1.0        # 默认值，temperature已足够
presence_penalty = 0.0  # 无需惩罚重复
frequency_penalty = 0.0 # 无需惩罚频率
```

**成本估算** (以gpt-4-turbo为例):
- 输入Token: 约1500 tokens (prompt + 上下文)
- 输出Token: 约2000 tokens (3套方案JSON)
- 单次调用成本: $0.01 * 1.5 + $0.03 * 2 = $0.075
- 日请求量1000次: $75/天

### 4.4 降级策略

```python
# 1. 优先级降级链
try:
    # Level 1: GPT-4 Turbo (最佳质量)
    plans = await generate_with_gpt4(...)
except OpenAIError:
    try:
        # Level 2: GPT-3.5 Turbo (降级)
        plans = await generate_with_gpt35(...)
    except OpenAIError:
        # Level 3: Stub方案 (保底)
        plans = await generate_stub(...)

# 2. 超时控制
async with timeout(30):  # 30秒超时
    plans = await client.generate_json(prompt)
```

**降级触发条件**:
- OpenAI API响应超时（>30s）
- API返回5xx错误
- API Key配额耗尽
- API返回非JSON内容（解析失败）

---

## 第5章 消息队列集成

### 5.1 RabbitMQ架构

```
Java Service                    Python AI Service
     │                                 │
     │  1. 发布消息                     │
     ├───────────────────────────────> │
     │  Exchange: plan-generation      │
     │  Routing Key: plan.request      │
     │  Payload: {plan_request_id, ...}│
     │                                 │
     │                                 │  2. 消费消息
     │                                 │  Queue: ai.generation.request
     │                                 │
     │                                 ├─> run_workflow()
     │                                 │
     │                                 │  3. 生成方案
     │                                 │  (3 plans)
     │                                 │
     │  4. 回调写入                     │
     │ <───────────────────────────────┤
     │  POST /internal/plans/batch     │
     │  Body: [{plan_id, ...}, ...]    │
     │                                 │
     │  5. 更新PlanRequest状态         │
     │  status: COMPLETED              │
```

### 5.2 MQ消费者实现

**文件**: `src/services/mq_consumer.py`

#### 5.2.1 消费者类定义

```python
class MQConsumer:
    def __init__(self, rabbitmq_url: str, queue_name: str):
        self.rabbitmq_url = rabbitmq_url
        self.queue_name = queue_name
        self.connection: AbstractRobustConnection | None = None
        self.channel: AbstractRobustChannel | None = None

    async def start(self):
        """建立连接并开始消费"""
        self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
        self.channel = await self.connection.channel()

        # 设置QoS：一次只预取1条消息（避免内存占用过高）
        await self.channel.set_qos(prefetch_count=1)

        # 声明队列（幂等操作）
        queue = await self.channel.declare_queue(
            self.queue_name,
            durable=True,  # 持久化队列
        )

        # 开始消费
        await queue.consume(self._on_message, no_ack=False)
        logger.info("MQ consumer listening on queue=%s", self.queue_name)

    async def stop(self):
        """优雅关闭连接"""
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
        logger.info("MQ consumer stopped")
```

#### 5.2.2 消息处理函数

```python
async def _on_message(self, message: AbstractIncomingMessage):
    """
    处理单条MQ消息：
    1. 解析JSON
    2. 运行workflow
    3. 回调Java服务
    4. ACK消息
    """
    async with message.process():  # 自动ACK/NACK
        try:
            # 1. 解析消息体
            body = message.body.decode("utf-8")
            payload = json.loads(body)
            logger.info("Received message plan_request_id=%s", payload.get("plan_request_id"))

            # 2. 运行生成流程
            state = await run_generation_workflow(payload)

            # 3. 检查错误
            if state.get("error"):
                logger.error("Workflow failed: %s", state["error"])
                # TODO: 通知Java服务生成失败
                return

            # 4. 回调Java服务
            plans = state.get("generated_plans", [])
            await self._callback_java_service(
                plan_request_id=payload["plan_request_id"],
                plans=plans,
            )

            logger.info("Plan generation completed plan_request_id=%s", payload["plan_request_id"])

        except Exception as exc:
            logger.exception("Message processing failed")
            # 消息会自动NACK并重新入队
```

#### 5.2.3 Java服务回调

```python
async def _callback_java_service(self, plan_request_id: str, plans: list[dict]):
    """
    调用Java的/internal/plans/batch接口批量写入方案
    """
    java_url = settings.java_service_url + "/internal/plans/batch"

    payload = {
        "plan_request_id": plan_request_id,
        "plans": plans,
    }

    headers = {
        "Content-Type": "application/json",
        "X-Internal-Secret": settings.internal_secret,  # 内部接口密钥
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                java_url,
                json=payload,
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()
            logger.info("Java callback succeeded plan_request_id=%s", plan_request_id)

        except httpx.HTTPError as exc:
            logger.error("Java callback failed: %s", exc)
            raise
```

### 5.3 消息格式

**发布消息** (Java → RabbitMQ):
```json
{
  "plan_request_id": "plan_req_01ke3cnw4t5dvp8jhjvfdafq1v",
  "user_id": "user_01ke3abc123",
  "people_count": 50,
  "budget_min": 10000,
  "budget_max": 15000,
  "start_date": "2026-02-01",
  "end_date": "2026-02-03",
  "departure_city": "Beijing",
  "preferences": {
    "activity_types": ["team_building"],
    "accommodation": "standard",
    "dining": ["local"]
  },
  "trace_id": "trace_01ke3xyz"
}
```

**回调消息** (Python → Java):
```json
{
  "plan_request_id": "plan_req_01ke3cnw4t5dvp8jhjvfdafq1v",
  "plans": [
    {
      "plan_id": "plan_01ke3d123",
      "plan_type": "budget",
      "plan_name": "BUDGET·Beijing3天团建",
      "summary": "人均¥200，3天行程，含住宿/活动/餐饮",
      "highlights": ["人均¥200", "可对比三套方案"],
      "itinerary": {...},
      "budget_breakdown": {...},
      "supplier_snapshots": [...],
      "budget_total": 10000.0,
      "budget_per_person": 200.0,
      "duration_days": 3,
      "status": "draft"
    },
    {/* standard plan */},
    {/* premium plan */}
  ]
}
```

### 5.4 错误处理与重试

**消息ACK策略**:
```python
async with message.process():
    # 成功处理 → 自动ACK
    # 抛异常 → 自动NACK + requeue
```

**重试配置** (RabbitMQ层面):
```yaml
# 队列声明时配置
x-message-ttl: 1800000  # 消息TTL 30分钟
x-max-length: 1000      # 队列最大长度
x-dead-letter-exchange: dlx.plan-generation  # 死信交换机
x-max-delivery-count: 3  # 最大重试次数
```

**幂等性保证**:
- Java服务的`/internal/plans/batch`接口是**幂等**的
- 使用`plan_request_id`作为幂等键
- 重复调用会覆盖旧方案（而非插入重复记录）

---

## 第6章 数据模型与验证

### 6.1 配置模型

**文件**: `src/models/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # OpenAI配置
    openai_api_key: str = "sk-xxxx"
    openai_model: str = "gpt-4-turbo-preview"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 4000

    # RabbitMQ配置
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"

    # Java服务配置
    java_service_url: str = "http://java-business-service:8080/api/v1"
    internal_secret: str = "change-this-in-production"

    # 服务配置
    log_level: str = "INFO"
    environment: str = "local"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

**.env文件示例**:
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=4000

RABBITMQ_URL=amqp://teamventure:teamventure123@rabbitmq:5672/
JAVA_SERVICE_URL=http://java-business-service:8080/api/v1
INTERNAL_SECRET=super-secret-key-change-in-production

LOG_LEVEL=INFO
ENVIRONMENT=production
```

### 6.2 ID生成器

**文件**: `src/services/id_generator.py`

```python
import ulid

def new_prefixed_id(prefix: str) -> str:
    """
    生成前缀+ULID格式的分布式ID

    示例: "plan_01HZC8K9DXF6B8M9S5Z7Q2W0E3"
    """
    ulid_str = ulid.new().str
    return f"{prefix}_{ulid_str}"
```

**ULID优势**:
- ✅ 时间排序性：按生成时间自然排序
- ✅ 分布式安全：无需中心化ID生成器
- ✅ 可读性：Base32编码，URL友好
- ✅ 唯一性：128位熵，碰撞概率极低

### 6.3 输入验证

虽然当前实现没有使用Pydantic请求模型（直接处理dict），但推荐的最佳实践：

```python
from pydantic import BaseModel, Field, validator

class PlanGenerationRequest(BaseModel):
    plan_request_id: str = Field(..., min_length=26, max_length=64)
    user_id: str = Field(..., min_length=26, max_length=64)
    people_count: int = Field(..., ge=1, le=500)
    budget_min: float = Field(..., gt=0)
    budget_max: float = Field(..., gt=0)
    start_date: str = Field(..., regex=r"^\d{4}-\d{2}-\d{2}$")
    end_date: str = Field(..., regex=r"^\d{4}-\d{2}-\d{2}$")
    departure_city: str = Field(..., min_length=1, max_length=50)
    preferences: dict = Field(default_factory=dict)

    @validator("budget_max")
    def budget_max_must_be_gte_min(cls, v, values):
        if "budget_min" in values and v < values["budget_min"]:
            raise ValueError("budget_max must be >= budget_min")
        return v

    @validator("end_date")
    def end_date_must_be_after_start(cls, v, values):
        if "start_date" in values and v <= values["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v
```

---

## 第7章 错误处理与监控

### 7.1 日志记录

**日志配置**:
```python
import logging

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),  # 输出到stdout（Docker日志收集）
    ],
)

logger = logging.getLogger(__name__)
```

**关键日志点**:
```python
# 1. Workflow开始
logger.info("workflow start plan_request_id=%s", state["plan_request_id"])

# 2. 各阶段完成
logger.info("requirements parsed plan_request_id=%s", state["plan_request_id"])
logger.info("suppliers matched plan_request_id=%s count=%s", state["plan_request_id"], len(suppliers))
logger.info("plans generated plan_request_id=%s count=%s", state["plan_request_id"], len(plans))

# 3. 错误记录
logger.exception("Generation workflow failed")  # 自动包含堆栈追踪

# 4. OpenAI调用
logger.error("OpenAI returned non-JSON content: %r", content[:500])
```

### 7.2 Prometheus监控

**暴露metrics端点** (FastAPI):
```python
from prometheus_client import Counter, Histogram, generate_latest

# 定义指标
workflow_runs_total = Counter("workflow_runs_total", "Total workflow runs", ["status"])
workflow_duration_seconds = Histogram("workflow_duration_seconds", "Workflow duration")
openai_calls_total = Counter("openai_calls_total", "Total OpenAI calls", ["status"])

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

**记录指标**:
```python
with workflow_duration_seconds.time():
    state = await run_generation_workflow(payload)

if state.get("error"):
    workflow_runs_total.labels(status="failed").inc()
else:
    workflow_runs_total.labels(status="success").inc()
```

### 7.3 错误分类

| 错误类型 | 处理策略 | 重试 | 告警 |
|---------|---------|------|------|
| **网络错误** (OpenAI超时) | fallback到stub | ✅ | ⚠️ P2 |
| **API密钥错误** | fallback到stub | ❌ | 🔴 P0 |
| **JSON解析失败** | 抛异常，NACK消息 | ✅ | ⚠️ P2 |
| **预算计算错误** | 抛异常，NACK消息 | ✅ | 🔴 P1 |
| **Java回调失败** | 抛异常，NACK消息 | ✅ | 🔴 P0 |

---

## 第8章 部署与配置管理

### 8.1 Docker部署

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY src/ ./src/

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose配置**:
```yaml
services:
  python-ai-service:
    build: ./backend/python-ai-service
    container_name: teamventure-python
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - RABBITMQ_URL=amqp://teamventure:teamventure123@rabbitmq:5672/
      - JAVA_SERVICE_URL=http://java-business-service:8080/api/v1
    depends_on:
      rabbitmq:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
```

### 8.2 配置管理最佳实践

**环境分离**:
```bash
# 本地开发
.env.local

# 测试环境
.env.test

# 生产环境
.env.production (不入库，通过K8s ConfigMap/Secret注入)
```

**敏感信息管理**:
- ✅ **使用环境变量**：不将API Key硬编码
- ✅ **Kubernetes Secret**：生产环境通过Secret挂载
- ✅ **AWS Secrets Manager**：云环境推荐方案

### 8.3 性能优化

**并发配置**:
```bash
# Uvicorn多worker
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# Gunicorn + Uvicorn worker
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**资源限制** (Kubernetes):
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

---

## 附录A: 完整文件清单

```
src/
├── main.py                        # FastAPI应用入口
├── langgraph/
│   ├── __init__.py
│   ├── workflow.py                # 工作流执行函数
│   └── state.py                   # 状态定义
├── services/
│   ├── __init__.py
│   ├── requirement_parser.py      # 需求解析
│   ├── supplier_matcher.py        # 供应商匹配
│   ├── plan_generation.py         # 方案生成（核心）
│   ├── mq_consumer.py             # RabbitMQ消费者
│   └── id_generator.py            # ID生成器
├── integrations/
│   ├── __init__.py
│   ├── openai_client.py           # OpenAI客户端
│   └── java_client.py             # Java服务回调
├── models/
│   ├── __init__.py
│   └── config.py                  # 配置模型
└── __init__.py

requirements.txt                   # Python依赖
Dockerfile                         # Docker构建文件
.env.example                       # 环境变量示例
```

---

## 附录B: API接口文档

### B.1 健康检查

```
GET /health
```

**响应**:
```json
{
  "status": "UP",
  "version": "1.0.0"
}
```

### B.2 手动触发生成（开发调试）

```
POST /trigger-generation
Content-Type: application/json

{
  "plan_request_id": "plan_req_test_001",
  "user_id": "user_test_001",
  "people_count": 50,
  "budget_min": 10000,
  "budget_max": 15000,
  "start_date": "2026-02-01",
  "end_date": "2026-02-03",
  "departure_city": "Beijing"
}
```

**响应**:
```json
{
  "status": "success",
  "plans_count": 3
}
```

---

## 附录C: 故障排查指南

### C.1 常见问题

**问题1: OpenAI调用失败**
```
OpenAI call failed: APIConnectionError
```
**解决方案**:
- 检查网络连接（是否需要代理）
- 验证API Key有效性
- 检查API配额是否耗尽

**问题2: RabbitMQ连接失败**
```
Cannot connect to RabbitMQ
```
**解决方案**:
- 检查RabbitMQ服务状态: `docker ps | grep rabbitmq`
- 验证URL配置: `RABBITMQ_URL=amqp://user:pass@host:5672/`
- 检查网络连通性: `telnet rabbitmq 5672`

**问题3: Java回调失败**
```
Java callback failed: 500 Internal Server Error
```
**解决方案**:
- 检查Java服务日志
- 验证回调URL配置
- 检查`X-Internal-Secret`密钥是否匹配

---

**文档版本**: v1.0
**最后更新**: 2026-01-04
**维护者**: TeamVenture开发团队
