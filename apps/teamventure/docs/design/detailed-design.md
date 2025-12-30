# TeamVenture 一期（小程序）详细设计

> **版本**: v1.0
> **日期**: 2025-12-30
> **状态**: 开发前最终版本
> **重要性**: ⭐⭐⭐⭐⭐ 本文档是开发实施的唯一标准，所有代码必须严格遵循本设计

---

## 📋 文档导航

| 章节 | 内容 | 附录文档 |
|------|------|---------|
| 第1章 | 整体架构设计 | 本文档 |
| 第2章 | 服务拆分与通信 | 本文档 |
| 第3章 | 数据库详细设计 | [database-design.md](./teamventure-phase1-database-design.md) |
| 第4章 | Python AI服务设计 | [ai-service-design.md](./teamventure-phase1-ai-service-design.md) |
| 第5章 | Java业务服务设计 | [business-service-design.md](./teamventure-phase1-business-service-design.md) |
| 第6章 | 小程序前端设计 | [miniapp-design.md](./teamventure-phase1-miniapp-design.md) |
| 第7章 | 部署架构设计 | 本文档 |
| 第8章 | 开发规范 | 本文档 |

---

## 第1章 整体架构设计

### 1.1 架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                        微信小程序前端                              │
│                    (UniApp/原生小程序)                            │
│                                                                   │
│  pages/                components/           utils/              │
│  ├─ generate/          ├─ PlanCard/        ├─ request.js        │
│  ├─ compare/           ├─ SupplierCard/    ├─ auth.js           │
│  ├─ detail/            └─ BudgetChart/     └─ logger.js         │
│  └─ my-plans/                                                    │
└─────────────────────────────────────────────────────────────────┘
                                ▼ HTTPS
┌─────────────────────────────────────────────────────────────────┐
│                         Nginx (API Gateway)                       │
│                    域名: api.teamventure.com                      │
│                                                                   │
│  路由规则:                                                         │
│  /api/v1/auth/*        → Java Service (SpringBoot)              │
│  /api/v1/plans/*       → Java Service (增删改查)                 │
│  /api/v1/ai/*          → Python Service (AI生成)                 │
│  /api/v1/suppliers/*   → Java Service (查询)                     │
└─────────────────────────────────────────────────────────────────┘
         ▼                           ▼                        ▼
┌──────────────────┐    ┌──────────────────────┐    ┌──────────────┐
│  Java Service    │    │  Python AI Service   │    │  RabbitMQ    │
│  (SpringBoot)    │◄──►│     (FastAPI)        │◄──►│  消息队列     │
│                  │    │                      │    │              │
│  端口: 8080      │    │  端口: 8000          │    │ 端口: 5672   │
│                  │    │                      │    │              │
│  模块:           │    │  LangGraph 流程:     │    │ Exchange:    │
│  - 认证/会话     │    │  - 需求解析          │    │ - plan.gen   │
│  - 方案CRUD      │    │  - 供应商匹配        │    │ - analytics  │
│  - 供应商目录    │    │  - 方案生成          │    │              │
│  - 事件记录      │    │  - 描述优化          │    │ Queue:       │
│  - 埋点上报      │    │                      │    │ - ai.gen.req │
│  - 数据校验      │    │  AI调用:             │    │ - ai.gen.res │
│                  │    │  - OpenAI GPT-4      │    │              │
│  COLA架构:       │    │  - Claude (备用)     │    │              │
│  - Adapter       │    │                      │    │              │
│  - App           │    │  框架:               │    │              │
│  - Domain        │    │  - LangGraph         │    │              │
│  - Infrastructure│    │  - LangChain         │    │              │
└──────────────────┘    └──────────────────────┘    └──────────────┘
         ▼                           ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                        MySQL 主从集群                             │
│                                                                   │
│  主库 (Master)                    从库 (Slave)                   │
│  端口: 3306                       端口: 3307                     │
│  - 写入 (INSERT/UPDATE/DELETE)    - 读取 (SELECT)               │
│  - 实时同步 Binlog                - 只读模式                     │
│                                                                   │
│  数据库:                                                          │
│  - teamventure_main (主业务库)                                   │
│    ├─ users (用户表)                                             │
│    ├─ sessions (会话表)                                          │
│    ├─ plan_requests (方案请求表)                                 │
│    ├─ plans (方案表)                                             │
│    ├─ suppliers (供应商表)                                       │
│    ├─ supplier_contact_logs (联系记录表)                         │
│    └─ domain_events (领域事件表)                                 │
└─────────────────────────────────────────────────────────────────┘
         ▼                           ▼                        ▼
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Redis      │         │    OSS       │         │  日志中心     │
│   缓存层      │         │  对象存储     │         │  (ELK)       │
│              │         │              │         │              │
│ - Session    │         │ - 方案截图    │         │ - 应用日志    │
│ - 幂等Token  │         │ - 分享卡片    │         │ - 访问日志    │
│ - 供应商缓存  │         │ - 用户头像    │         │ - 错误日志    │
└──────────────┘         └──────────────┘         └──────────────┘
```

### 1.2 技术栈总览

#### 前端
| 技术 | 版本 | 用途 | 备注 |
|------|------|------|------|
| 微信小程序 | 最新基础库 | 运行时环境 | 目标兼容 iOS 12+ / Android 5+ |
| 原生框架 | - | UI开发 | WXML/WXSS/JavaScript |
| TypeScript | 4.9+ | 类型安全 | 可选，建议使用 |
| Vant Weapp | 1.11+ | UI组件库 | 按需引入 |

#### 后端 - Java 服务
| 技术 | 版本 | 用途 | 备注 |
|------|------|------|------|
| Java | 17 LTS | 运行时 | 必须 |
| SpringBoot | 3.2+ | 应用框架 | 主框架 |
| Spring MVC | 6.1+ | Web框架 | SpringBoot自带 |
| MyBatis | 3.5+ | ORM框架 | 数据库访问 |
| MyBatis-Plus | 3.5+ | MyBatis增强 | 可选，提高效率 |
| COLA | 4.3+ | 架构框架 | 阿里COLA架构 |
| Lombok | 1.18+ | 代码简化 | 必须 |
| Hutool | 5.8+ | 工具类库 | 推荐 |

#### 后端 - Python AI 服务
| 技术 | 版本 | 用途 | 备注 |
|------|------|------|------|
| Python | 3.11+ | 运行时 | 必须 |
| FastAPI | 0.109+ | Web框架 | 主框架 |
| LangGraph | 0.0.40+ | AI编排 | 核心框架 |
| LangChain | 0.1.0+ | AI工具链 | LangGraph依赖 |
| OpenAI SDK | 1.10+ | GPT调用 | 主模型 |
| Anthropic SDK | 0.8+ | Claude调用 | 备用模型 |
| Pydantic | 2.5+ | 数据校验 | FastAPI内置 |
| SQLAlchemy | 2.0+ | ORM | 可选，建议用 |

#### 数据库与中间件
| 技术 | 版本 | 用途 | 备注 |
|------|------|------|------|
| MySQL | 8.0+ | 主数据库 | InnoDB引擎 |
| Redis | 7.0+ | 缓存/Session | 单实例即可 |
| RabbitMQ | 3.12+ | 消息队列 | 异步通信 |
| Nginx | 1.24+ | 反向代理/负载均衡 | API Gateway |

### 1.3 服务职责划分

#### Java Service 职责（业务服务）
```
负责：业务逻辑、数据持久化、权限校验、事件记录

具体模块：
1. Identity & Session Context（身份与会话）
   - 微信登录（code换session）
   - Session管理（Redis）
   - 用户信息维护

2. Planning Context - Write（方案写操作）
   - 创建PlanRequest（COLA架构）
   - 更新Plan状态（确认方案）
   - 记录供应商联系行为
   - 领域事件持久化

3. Planning Context - Read（方案读操作）
   - 我的方案列表（三层架构）
   - 方案详情查询
   - 方案对比数据

4. Supplier Catalog Context（供应商目录）
   - 供应商列表查询（只读）
   - 供应商详情查询
   - 供应商搜索

5. Analytics（埋点与分析）
   - 埋点事件收集
   - 上报到分析平台
```

#### Python AI Service 职责（AI服务）
```
负责：AI推理、方案生成、LLM调用

具体模块：
1. 需求解析 (Requirement Parser)
   - 解析用户输入的自然语言需求
   - 提取结构化参数
   - 校验参数合法性

2. 供应商匹配 (Supplier Matcher)
   - 从MySQL读取供应商目录
   - 基于规则+AI混合匹配
   - 返回Top N供应商列表

3. 方案生成 (Plan Generator)
   - 生成3套方案（budget/standard/premium）
   - 生成行程安排
   - 生成预算明细
   - LLM调用（GPT-4）

4. 描述优化 (Description Optimizer)
   - 优化方案标题与描述
   - 生成亮点摘要
   - 优化用户体验文案

5. 编排引擎 (Orchestrator)
   - LangGraph状态机
   - 流程编排与错误处理
   - 超时控制与降级
```

### 1.4 数据流向

#### 写操作流程（COLA架构）
```
小程序 → Nginx → Java Service

示例：确认方案
1. POST /api/v1/plans/{planId}/confirm
2. Nginx → Java:8080
3. Java:
   ┌─ Adapter层: PlanController
   │  └─ 参数校验、鉴权
   ┌─ App层: ConfirmPlanUseCase
   │  ├─ 加载Plan聚合
   │  ├─ 执行Domain逻辑
   │  └─ 发布DomainEvent
   ┌─ Domain层: Plan聚合根
   │  ├─ confirm() 业务方法
   │  ├─ 状态机校验
   │  └─ 发布PlanConfirmed事件
   └─ Infrastructure层: MyBatis
      ├─ 更新plans表
      ├─ 插入domain_events表
      └─ 事务提交
4. 返回成功响应
```

#### 读操作流程（三层架构）
```
小程序 → Nginx → Java Service

示例：我的方案列表
1. GET /api/v1/plans?page=1&pageSize=10
2. Nginx → Java:8080
3. Java:
   ┌─ Controller: PlanQueryController
   │  └─ 参数校验、鉴权
   ┌─ Service: PlanQueryService
   │  ├─ 构建查询条件
   │  └─ 调用DAO
   └─ DAO: PlanMapper (MyBatis)
      ├─ SELECT从MySQL从库
      └─ 返回DTO列表
4. 返回分页数据
```

#### AI生成流程（异步）
```
小程序 → Nginx → Java → RabbitMQ → Python → MySQL

示例：生成方案
1. POST /api/v1/plans/generate
2. Nginx → Java:8080
3. Java:
   ┌─ 创建PlanRequest聚合
   ┌─ 持久化到MySQL
   └─ 发送MQ消息到 ai.gen.req
4. 立即返回 { plan_request_id, status: "generating" }

5. RabbitMQ → Python:8000
6. Python (LangGraph):
   ┌─ State: 需求解析
   ┌─ State: 供应商匹配
   ┌─ State: 方案生成（3套）
   │  └─ 并发调用GPT-4
   └─ State: 描述优化
7. Python:
   └─ 通过HTTP回写Java（POST /internal/plans/batch）
8. Java:
   ├─ 持久化3个Plan到MySQL
   ├─ 更新PlanRequest状态
   └─ 发布PlanGenerated事件
9. 小程序:
   └─ 轮询或WebSocket接收完成通知
```

### 1.5 工程结构设计

#### 单体仓库（Monorepo）结构
```
teamventure-monorepo/
├─ README.md
├─ docs/                          # 文档目录
│  ├─ api/                        # API文档
│  ├─ database/                   # 数据库文档
│  └─ deployment/                 # 部署文档
│
├─ backend-java/                  # Java后端服务
│  ├─ pom.xml                     # Maven配置
│  ├─ src/
│  │  ├─ main/
│  │  │  ├─ java/com/teamventure/
│  │  │  │  ├─ adapter/           # COLA Adapter层
│  │  │  │  │  ├─ web/            # REST Controller
│  │  │  │  │  └─ mq/             # MQ Consumer
│  │  │  │  ├─ app/               # COLA App层
│  │  │  │  │  ├─ command/        # 写命令
│  │  │  │  │  ├─ query/          # 读查询
│  │  │  │  │  └─ event/          # 事件处理
│  │  │  │  ├─ domain/            # COLA Domain层
│  │  │  │  │  ├─ plan/           # Plan聚合
│  │  │  │  │  ├─ supplier/       # Supplier聚合
│  │  │  │  │  └─ user/           # User聚合
│  │  │  │  └─ infrastructure/    # COLA Infrastructure层
│  │  │  │     ├─ persistence/    # MyBatis Mapper
│  │  │  │     ├─ cache/          # Redis
│  │  │  │     └─ mq/             # RabbitMQ
│  │  │  └─ resources/
│  │  │     ├─ application.yml
│  │  │     └─ mapper/            # MyBatis XML
│  │  └─ test/
│  └─ Dockerfile
│
├─ backend-python/                # Python AI服务
│  ├─ pyproject.toml              # Poetry配置
│  ├─ src/
│  │  ├─ main.py                  # FastAPI入口
│  │  ├─ api/                     # API路由
│  │  │  ├─ __init__.py
│  │  │  ├─ generation.py         # 生成接口
│  │  │  └─ internal.py           # 内部接口
│  │  ├─ langgraph/               # LangGraph流程
│  │  │  ├─ __init__.py
│  │  │  ├─ state.py              # 状态定义
│  │  │  ├─ nodes.py              # 节点实现
│  │  │  └─ graph.py              # 流程编排
│  │  ├─ services/                # 业务服务
│  │  │  ├─ requirement_parser.py
│  │  │  ├─ supplier_matcher.py
│  │  │  └─ plan_generator.py
│  │  ├─ integrations/            # 外部集成
│  │  │  ├─ openai_client.py
│  │  │  └─ java_client.py
│  │  ├─ models/                  # 数据模型
│  │  │  ├─ request.py
│  │  │  └─ response.py
│  │  └─ core/                    # 核心配置
│  │     ├─ config.py
│  │     └─ logger.py
│  ├─ tests/
│  └─ Dockerfile
│
├─ frontend-miniapp/              # 小程序前端
│  ├─ package.json
│  ├─ project.config.json         # 小程序配置
│  ├─ app.js
│  ├─ app.json
│  ├─ app.wxss
│  ├─ pages/                      # 页面目录
│  │  ├─ generate/                # 生成方案页
│  │  │  ├─ index.js
│  │  │  ├─ index.json
│  │  │  ├─ index.wxml
│  │  │  └─ index.wxss
│  │  ├─ compare/                 # 对比方案页
│  │  ├─ detail/                  # 方案详情页
│  │  └─ my-plans/                # 我的方案页
│  ├─ components/                 # 组件目录
│  │  ├─ PlanCard/
│  │  ├─ SupplierCard/
│  │  └─ BudgetChart/
│  └─ utils/                      # 工具类
│     ├─ request.js               # 网络请求封装
│     ├─ auth.js                  # 鉴权工具
│     └─ logger.js                # 日志工具
│
├─ database/                      # 数据库脚本
│  ├─ schema/                     # 表结构
│  │  ├─ V1.0.0__init.sql
│  │  ├─ V1.0.1__add_indexes.sql
│  │  └─ V1.0.2__add_events.sql
│  ├─ data/                       # 初始数据
│  │  └─ suppliers_seed.sql
│  └─ migration/                  # 迁移脚本
│
├─ scripts/                       # 运维脚本
│  ├─ deploy.sh                   # 部署脚本
│  ├─ backup.sh                   # 备份脚本
│  └─ start-dev.sh                # 本地启动
│
└─ docker-compose.yml             # 本地开发环境
```

---

## 第2章 服务拆分与通信

### 2.1 服务列表

| 服务名 | 技术栈 | 端口 | 职责 | 依赖 |
|--------|--------|------|------|------|
| **backend-java** | Java 17 + SpringBoot | 8080 | 业务逻辑、数据持久化 | MySQL, Redis, RabbitMQ |
| **backend-python** | Python 3.11 + FastAPI | 8000 | AI推理、方案生成 | MySQL(读), RabbitMQ, OpenAI |
| **frontend-miniapp** | 微信小程序 | - | 用户交互界面 | 无 |
| **nginx** | Nginx 1.24 | 80/443 | API网关、反向代理 | 无 |
| **mysql-master** | MySQL 8.0 | 3306 | 主库（写） | 无 |
| **mysql-slave** | MySQL 8.0 | 3307 | 从库（读） | mysql-master |
| **redis** | Redis 7.0 | 6379 | 缓存、Session | 无 |
| **rabbitmq** | RabbitMQ 3.12 | 5672 | 消息队列 | 无 |

### 2.2 服务间通信协议

#### HTTP 同步通信
```yaml
# Java ← 小程序
协议: HTTPS
格式: JSON
认证: Bearer Token (session_token)
超时: 30s

# Python → Java (内部回调)
协议: HTTP
格式: JSON
认证: Internal Secret (X-Internal-Secret header)
超时: 10s
```

#### RabbitMQ 异步通信
```yaml
# Java → Python (生成请求)
Exchange: plan.generation.topic
RoutingKey: ai.generate.request
Queue: ai.gen.req.queue
消息格式:
  {
    "plan_request_id": "plan_req_01JH...",
    "user_id": "user_01JH...",
    "inputs": { ... },
    "trace_id": "uuid"
  }

# Python → Java (生成完成)
方式: HTTP回调
URL: http://backend-java:8080/internal/plans/batch
认证: X-Internal-Secret
```

### 2.3 数据一致性策略

#### 最终一致性（生成方案场景）
```
1. Java创建PlanRequest (CREATING)
2. Java发送MQ消息
3. Java立即返回202 Accepted
4. Python消费消息，生成方案
5. Python回调Java，写入3个Plan
6. Java更新PlanRequest (COMPLETED)
7. 小程序轮询或推送获取结果

失败处理：
- MQ消息重试（3次）
- 超时（60s）标记为FAILED
- 用户可重新发起
```

#### 强一致性（确认方案场景）
```
1. Java收到确认请求
2. 在单一事务中：
   - 更新Plan状态（CONFIRMED）
   - 插入DomainEvent（PlanConfirmed）
3. 事务提交成功后返回200
4. 异步发送MQ通知（不影响主流程）
```

### 2.4 接口清单

#### 小程序 → Java 接口

| 接口 | 方法 | 路径 | 用途 | 认证 |
|------|------|------|------|------|
| 微信登录 | POST | /api/v1/auth/wechat/login | 换取session | 否 |
| 创建方案请求 | POST | /api/v1/plans/generate | 发起生成 | 是 |
| 方案列表 | GET | /api/v1/plans | 我的方案 | 是 |
| 方案详情 | GET | /api/v1/plans/{id} | 查看详情 | 是 |
| 确认方案 | POST | /api/v1/plans/{id}/confirm | 确认 | 是 |
| 联系供应商 | POST | /api/v1/plans/{id}/supplier-contacts | 记录联系 | 是 |
| 供应商列表 | GET | /api/v1/suppliers | 搜索供应商 | 是 |

#### Python → Java 内部接口

| 接口 | 方法 | 路径 | 用途 | 认证 |
|------|------|------|------|------|
| 批量创建Plan | POST | /internal/plans/batch | AI生成完成回写 | Internal Secret |
| 更新PlanRequest状态 | PUT | /internal/plan-requests/{id}/status | 更新状态 | Internal Secret |

#### Java → MySQL 操作

| 操作 | 库 | 表 | 说明 |
|------|----|----|------|
| INSERT/UPDATE/DELETE | 主库 | 所有表 | 写操作 |
| SELECT (实时) | 主库 | domain_events | 事件查询 |
| SELECT (历史) | 从库 | plans, suppliers | 读操作 |

---

## 第3章 数据库详细设计

> 完整的数据库DDL、索引设计、分表策略见附录文档：
> [teamventure-phase1-database-design.md](./teamventure-phase1-database-design.md)

### 3.1 核心表概览

| 表名 | 行数估算 | 分表 | 说明 |
|------|---------|------|------|
| `users` | 10万 | 否 | 用户基础信息 |
| `sessions` | 10万 | 否 | 会话管理（Redis为主） |
| `plan_requests` | 50万 | 按月 | 方案请求 |
| `plans` | 150万 | 按月 | 方案（1个request → 3个plan） |
| `suppliers` | 5000 | 否 | 供应商目录 |
| `supplier_contact_logs` | 100万 | 按月 | 联系记录 |
| `domain_events` | 500万 | 按月 | 领域事件流 |

### 3.2 表关系图
```
users (1) ──────< (N) plan_requests
                         │
                         │ (1 request → 3 plans)
                         │
                         ├──< (N) plans
                         │         │
                         │         └──< (N) supplier_contact_logs
                         │
                         └─── suppliers (N:M through plans.supplier_snapshots)

domain_events (记录所有领域事件)
  - PlanRequestCreated
  - PlanGenerated
  - PlanConfirmed
  - SupplierContacted
```

---

## 第4章 Python AI服务设计

> 完整的LangGraph流程、Prompt设计、错误处理见附录文档：
> [teamventure-phase1-ai-service-design.md](./teamventure-phase1-ai-service-design.md)

### 4.1 LangGraph 状态机

```python
# 状态定义
class GenerationState(TypedDict):
    plan_request_id: str
    user_inputs: dict
    parsed_requirements: dict
    matched_suppliers: list
    generated_plans: list[dict]  # 3套方案
    error: Optional[str]

# 流程图
START
  → parse_requirements (需求解析)
  → match_suppliers (供应商匹配)
  → generate_plans (方案生成，并发3个分支)
    ├─ generate_budget_plan
    ├─ generate_standard_plan
    └─ generate_premium_plan
  → optimize_descriptions (描述优化)
  → save_to_java (回写Java)
  → END
```

### 4.2 核心节点设计

#### Node 1: parse_requirements
```python
def parse_requirements(state: GenerationState) -> GenerationState:
    """
    解析用户输入，提取结构化参数

    输入: state.user_inputs
      {
        "people_count": 50,
        "budget_min": 35000,
        "budget_max": 50000,
        "departure_city": "北京",
        "preferences": {...}
      }

    输出: state.parsed_requirements
      {
        "people_count": 50,
        "budget_per_person_range": [700, 1000],
        "duration_days": 2,
        "activity_types": ["team_building", "outdoor"],
        "accommodation_level": "standard"
      }

    AI调用: 无（纯规则解析）
    """
    pass
```

#### Node 2: match_suppliers
```python
def match_suppliers(state: GenerationState) -> GenerationState:
    """
    匹配供应商

    策略: 规则匹配 + AI排序

    规则匹配:
      1. 城市过滤（departure_city 或周边200km）
      2. 品类过滤（住宿、餐饮、活动）
      3. 价格区间过滤
      4. 评分过滤（>= 4.0）

    AI排序:
      调用GPT-4，根据用户偏好对候选供应商排序
      Prompt: "根据用户偏好 {preferences}，对以下供应商排序..."

    输出: state.matched_suppliers (Top 20)
    """
    pass
```

#### Node 3: generate_plans (并发)
```python
def generate_budget_plan(state: GenerationState) -> dict:
    """
    生成经济型方案

    AI调用: GPT-4
    Prompt:
      '''
      角色：你是专业的团建策划师
      任务：为50人团队生成2天1夜经济型团建方案

      约束：
      - 总预算：¥35,000 (¥700/人)
      - 供应商：{matched_suppliers前10个}
      - 偏好：{preferences}

      输出格式：JSON
      {
        "plan_name": "...",
        "summary": "...",
        "itinerary": [...],
        "budget_breakdown": {...},
        "supplier_ids": [...]
      }
      '''

    后处理:
      - 校验预算不超标
      - 补全supplier_snapshots
      - 生成highlight摘要
    """
    pass

# generate_standard_plan 和 generate_premium_plan 类似
# 区别在于预算范围和供应商选择
```

---

## 第5章 Java业务服务设计

> 完整的COLA架构实现、MyBatis Mapper、单元测试见附录文档：
> [teamventure-phase1-business-service-design.md](./teamventure-phase1-business-service-design.md)

### 5.1 COLA 四层架构（写操作）

#### Adapter 层（适配器层）
```java
@RestController
@RequestMapping("/api/v1/plans")
public class PlanController {

    @PostMapping("/{planId}/confirm")
    public Response<Void> confirmPlan(
        @PathVariable String planId,
        @RequestHeader("Authorization") String token
    ) {
        // 1. 鉴权
        String userId = authService.getUserId(token);

        // 2. 构建Command
        ConfirmPlanCmd cmd = ConfirmPlanCmd.builder()
            .planId(planId)
            .userId(userId)
            .build();

        // 3. 调用App层
        confirmPlanUseCase.execute(cmd);

        return Response.success();
    }
}
```

#### App 层（应用层）
```java
@Service
@Transactional
public class ConfirmPlanUseCase {

    @Resource
    private PlanRepository planRepository;

    @Resource
    private DomainEventPublisher eventPublisher;

    public void execute(ConfirmPlanCmd cmd) {
        // 1. 加载聚合
        Plan plan = planRepository.findById(cmd.getPlanId());
        if (plan == null) {
            throw new BizException("PLAN_NOT_FOUND");
        }

        // 2. 权限校验
        if (!plan.getUserId().equals(cmd.getUserId())) {
            throw new BizException("UNAUTHORIZED");
        }

        // 3. 执行Domain逻辑
        plan.confirm();

        // 4. 持久化
        planRepository.save(plan);

        // 5. 发布领域事件
        eventPublisher.publish(plan.getDomainEvents());
    }
}
```

#### Domain 层（领域层）
```java
@Data
@Aggregate
public class Plan {
    private PlanId id;
    private UserId userId;
    private PlanType type;  // BUDGET, STANDARD, PREMIUM
    private PlanStatus status;  // DRAFT, CONFIRMED
    private Instant confirmedTime;

    private List<DomainEvent> domainEvents = new ArrayList<>();

    /**
     * 确认方案（核心业务逻辑）
     */
    public void confirm() {
        // 不变式校验
        if (this.status == PlanStatus.CONFIRMED) {
            return; // 幂等
        }

        // 状态变更
        this.status = PlanStatus.CONFIRMED;
        this.confirmedTime = Instant.now();

        // 发布事件
        this.addDomainEvent(new PlanConfirmedEvent(
            this.id.getValue(),
            this.userId.getValue(),
            this.confirmedTime
        ));
    }

    private void addDomainEvent(DomainEvent event) {
        this.domainEvents.add(event);
    }

    public List<DomainEvent> getDomainEvents() {
        return Collections.unmodifiableList(domainEvents);
    }
}
```

#### Infrastructure 层（基础设施层）
```java
@Repository
public class PlanRepositoryImpl implements PlanRepository {

    @Resource
    private PlanMapper planMapper;

    @Resource
    private DomainEventMapper eventMapper;

    @Override
    public Plan findById(String planId) {
        PlanPO po = planMapper.selectById(planId);
        return toDomain(po);
    }

    @Override
    @Transactional
    public void save(Plan plan) {
        // 1. 保存聚合状态
        PlanPO po = toPO(plan);
        planMapper.updateById(po);

        // 2. 保存领域事件
        for (DomainEvent event : plan.getDomainEvents()) {
            DomainEventPO eventPO = new DomainEventPO();
            eventPO.setEventId(UUID.randomUUID().toString());
            eventPO.setEventType(event.getClass().getSimpleName());
            eventPO.setAggregateId(plan.getId().getValue());
            eventPO.setPayload(JSON.toJSONString(event));
            eventPO.setOccurredAt(event.getOccurredAt());

            eventMapper.insert(eventPO);
        }
    }
}
```

### 5.2 三层架构（读操作）

#### Controller 层
```java
@RestController
@RequestMapping("/api/v1/plans")
public class PlanQueryController {

    @Resource
    private PlanQueryService planQueryService;

    @GetMapping
    public Response<PageResult<PlanDTO>> listPlans(
        @RequestParam(defaultValue = "1") int page,
        @RequestParam(defaultValue = "10") int pageSize,
        @RequestHeader("Authorization") String token
    ) {
        String userId = authService.getUserId(token);

        PageResult<PlanDTO> result = planQueryService.listByUser(
            userId, page, pageSize
        );

        return Response.success(result);
    }
}
```

#### Service 层
```java
@Service
public class PlanQueryService {

    @Resource
    private PlanMapper planMapper;

    public PageResult<PlanDTO> listByUser(String userId, int page, int pageSize) {
        // 1. 构建查询条件
        Page<PlanPO> pageParam = new Page<>(page, pageSize);
        QueryWrapper<PlanPO> query = new QueryWrapper<>();
        query.eq("user_id", userId);
        query.orderByDesc("create_time");

        // 2. 查询（从库）
        Page<PlanPO> result = planMapper.selectPage(pageParam, query);

        // 3. 转换DTO
        List<PlanDTO> dtos = result.getRecords().stream()
            .map(this::toDTO)
            .collect(Collectors.toList());

        return PageResult.of(result.getTotal(), dtos);
    }
}
```

#### DAO 层 (MyBatis)
```java
@Mapper
public interface PlanMapper extends BaseMapper<PlanPO> {
    // MyBatis-Plus提供基础CRUD
    // 自定义复杂查询在XML中实现
}
```

```xml
<!-- PlanMapper.xml -->
<mapper namespace="com.teamventure.infrastructure.persistence.PlanMapper">

    <select id="selectWithSuppliers" resultMap="PlanWithSuppliersMap">
        SELECT
            p.plan_id,
            p.user_id,
            p.plan_type,
            p.status,
            p.plan_name,
            p.summary,
            p.budget_total,
            p.supplier_snapshots,  -- JSONB字段
            p.itinerary,           -- JSONB字段
            p.budget_breakdown,    -- JSONB字段
            p.create_time,
            p.confirmed_time
        FROM
            plans p
        WHERE
            p.plan_id = #{planId}
    </select>

</mapper>
```

---

## 第6章 小程序前端设计

> 完整的页面设计、组件设计、状态管理见附录文档：
> [teamventure-phase1-miniapp-design.md](./teamventure-phase1-miniapp-design.md)

### 6.1 页面结构

```
TabBar:
├─ 生成方案 (pages/generate/index)
└─ 我的方案 (pages/my-plans/index)

非TabBar页面:
├─ 登录授权 (pages/auth/index)
├─ 方案对比 (pages/compare/index)
├─ 方案详情 (pages/detail/index)
└─ 供应商详情 (pages/supplier/index)
```

### 6.2 核心页面设计

#### 生成方案页 (Step 1 + Step 2)
```javascript
Page({
  data: {
    step: 1,  // 1: 基础信息, 2: 偏好
    form: {
      peopleCount: 50,
      budgetMin: 35000,
      budgetMax: 50000,
      startDate: '',
      endDate: '',
      departureCity: '北京',
      preferences: {
        activityTypes: [],
        accommodationLevel: 'standard',
        diningStyle: [],
        specialRequirements: ''
      }
    },
    generating: false
  },

  onNextStep() {
    // 校验Step 1
    if (!this.validateBasicInfo()) {
      return;
    }
    this.setData({ step: 2 });
  },

  async onSubmit() {
    // 调用生成接口
    this.setData({ generating: true });

    try {
      const res = await api.generatePlans(this.data.form);

      // 跳转到对比页
      wx.navigateTo({
        url: `/pages/compare/index?requestId=${res.plan_request_id}`
      });
    } catch (err) {
      wx.showToast({ title: '生成失败', icon: 'none' });
    } finally {
      this.setData({ generating: false });
    }
  }
});
```

#### 方案对比页
```javascript
Page({
  data: {
    planRequestId: '',
    status: 'generating',  // generating / completed / failed
    plans: [],  // 3套方案
    selectedPlanId: ''
  },

  onLoad(options) {
    this.setData({ planRequestId: options.requestId });
    this.startPolling();
  },

  startPolling() {
    this.pollTimer = setInterval(async () => {
      const status = await api.getPlanRequestStatus(this.data.planRequestId);

      if (status === 'completed') {
        clearInterval(this.pollTimer);
        this.loadPlans();
      } else if (status === 'failed') {
        clearInterval(this.pollTimer);
        this.setData({ status: 'failed' });
      }
    }, 2000);  // 2秒轮询一次
  },

  async loadPlans() {
    const plans = await api.getPlansByRequest(this.data.planRequestId);
    this.setData({
      status: 'completed',
      plans: plans
    });
  },

  onViewDetail(e) {
    const planId = e.currentTarget.dataset.planId;
    wx.navigateTo({
      url: `/pages/detail/index?planId=${planId}`
    });
  }
});
```

### 6.3 网络请求封装

```javascript
// utils/request.js
const BASE_URL = 'https://api.teamventure.com';

function request(options) {
  return new Promise((resolve, reject) => {
    // 自动添加token
    const token = wx.getStorageSync('session_token');
    const header = {
      'Content-Type': 'application/json',
      ...options.header
    };

    if (token) {
      header['Authorization'] = `Bearer ${token}`;
    }

    wx.request({
      url: `${BASE_URL}${options.url}`,
      method: options.method || 'GET',
      data: options.data,
      header: header,
      success: (res) => {
        if (res.data.success) {
          resolve(res.data.data);
        } else {
          // 统一错误处理
          if (res.data.error.code === 'UNAUTHENTICATED') {
            // 跳转登录
            wx.redirectTo({ url: '/pages/auth/index' });
          }
          reject(res.data.error);
        }
      },
      fail: reject
    });
  });
}

module.exports = {
  // 登录
  wechatLogin: (code) => request({
    url: '/api/v1/auth/wechat/login',
    method: 'POST',
    data: { code }
  }),

  // 生成方案
  generatePlans: (inputs) => request({
    url: '/api/v1/plans/generate',
    method: 'POST',
    data: inputs
  }),

  // 查询方案列表
  getPlans: (page, pageSize) => request({
    url: `/api/v1/plans?page=${page}&pageSize=${pageSize}`,
    method: 'GET'
  }),

  // 查询方案详情
  getPlanDetail: (planId) => request({
    url: `/api/v1/plans/${planId}`,
    method: 'GET'
  }),

  // 确认方案
  confirmPlan: (planId) => request({
    url: `/api/v1/plans/${planId}/confirm`,
    method: 'POST',
    data: { confirm: true }
  }),

  // 联系供应商
  contactSupplier: (planId, supplierId, channel) => request({
    url: `/api/v1/plans/${planId}/supplier-contacts`,
    method: 'POST',
    data: { supplier_id: supplierId, channel }
  })
};
```

---

## 第7章 部署架构设计

### 7.1 本地开发环境

```yaml
# docker-compose.yml
version: '3.8'

services:
  mysql-master:
    image: mysql:8.0
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: teamventure2025
      MYSQL_DATABASE: teamventure_main
    volumes:
      - ./database/schema:/docker-entrypoint-initdb.d
      - mysql-master-data:/var/lib/mysql
    command: --default-authentication-plugin=mysql_native_password

  mysql-slave:
    image: mysql:8.0
    ports:
      - "3307:3306"
    environment:
      MYSQL_ROOT_PASSWORD: teamventure2025
    volumes:
      - mysql-slave-data:/var/lib/mysql
    depends_on:
      - mysql-master

  redis:
    image: redis:7.0-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

  rabbitmq:
    image: rabbitmq:3.12-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: teamventure
      RABBITMQ_DEFAULT_PASS: teamventure2025

  backend-java:
    build: ./backend-java
    ports:
      - "8080:8080"
    environment:
      SPRING_PROFILES_ACTIVE: dev
      MYSQL_HOST: mysql-master
      REDIS_HOST: redis
      RABBITMQ_HOST: rabbitmq
    depends_on:
      - mysql-master
      - redis
      - rabbitmq

  backend-python:
    build: ./backend-python
    ports:
      - "8000:8000"
    environment:
      ENV: dev
      MYSQL_HOST: mysql-master
      RABBITMQ_HOST: rabbitmq
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      - mysql-master
      - rabbitmq

  nginx:
    image: nginx:1.24-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend-java
      - backend-python

volumes:
  mysql-master-data:
  mysql-slave-data:
  redis-data:
```

### 7.2 生产环境部署架构

```
┌─────────────────────────────────────────────────────────────┐
│                     阿里云/腾讯云 VPC                          │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  SLB/CLB (负载均衡)                                   │   │
│  │  - HTTPS证书                                          │   │
│  │  - 健康检查                                           │   │
│  └───────────────┬─────────────────────────────────────┘   │
│                  │                                           │
│      ┌───────────┴───────────┐                              │
│      ▼                       ▼                              │
│  ┌────────┐            ┌────────┐                           │
│  │ Nginx1 │            │ Nginx2 │                           │
│  │ (主)   │            │ (备)   │                           │
│  └───┬────┘            └────────┘                           │
│      │                                                       │
│  ┌───┴───────────────────────────┐                          │
│  │         K8s集群                │                          │
│  │                                │                          │
│  │  ┌──────────────────────────┐ │                          │
│  │  │  backend-java (Pod×3)    │ │                          │
│  │  │  - CPU: 2核               │ │                          │
│  │  │  - Mem: 4GB               │ │                          │
│  │  │  - 副本数: 3              │ │                          │
│  │  └──────────────────────────┘ │                          │
│  │                                │                          │
│  │  ┌──────────────────────────┐ │                          │
│  │  │  backend-python (Pod×2)  │ │                          │
│  │  │  - CPU: 4核 (AI密集)     │ │                          │
│  │  │  - Mem: 8GB               │ │                          │
│  │  │  - GPU: 可选              │ │                          │
│  │  │  - 副本数: 2              │ │                          │
│  │  └──────────────────────────┘ │                          │
│  └────────────────────────────────┘                          │
│                                                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │  MySQL 主从集群 (RDS)                               │     │
│  │  ┌──────────┐       ┌──────────┐                   │     │
│  │  │  Master  │──────>│  Slave   │                   │     │
│  │  │  (写)    │ Binlog│  (读)    │                   │     │
│  │  │  4核8GB  │       │  4核8GB  │                   │     │
│  │  └──────────┘       └──────────┘                   │     │
│  │  - 自动备份                                         │     │
│  │  - 慢查询监控                                       │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   Redis    │  │  RabbitMQ  │  │    OSS     │            │
│  │   主从     │  │   集群     │  │  对象存储   │            │
│  │  2核4GB    │  │  2×2核4GB  │  │            │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│                                                               │
└─────────────────────────────────────────────────────────────┘

监控与日志:
- Prometheus + Grafana (监控)
- ELK Stack (日志聚合)
- Sentry (错误追踪)
```

### 7.3 资源配置清单

| 组件 | 规格 | 数量 | 成本(月) | 备注 |
|------|------|------|---------|------|
| SLB | 标准型 | 1 | ¥200 | 公网带宽另计 |
| ECS (Nginx) | 2核4GB | 2 | ¥400 | 高可用 |
| K8s Node | 4核8GB | 3 | ¥1,500 | 运行业务Pod |
| RDS MySQL | 4核8GB | 1主1从 | ¥1,200 | 包含备份 |
| Redis | 2核4GB | 主从 | ¥300 | - |
| RabbitMQ | 2核4GB | 集群 | ¥600 | 3节点 |
| OSS | 标准存储 | - | ¥100 | 按量 |
| 域名+证书 | - | - | ¥100 | 年付 |
| **合计** | - | - | **¥4,400** | 不含带宽 |

---

## 第8章 开发规范

### 8.1 代码规范

#### Java 规范
```java
// 1. 命名规范
// 类名: 大驼峰
public class PlanController {}

// 方法名: 小驼峰
public void confirmPlan() {}

// 常量: 全大写下划线
public static final String PLAN_STATUS_CONFIRMED = "CONFIRMED";

// 包名: 全小写
package com.teamventure.domain.plan;

// 2. 注释规范
/**
 * 确认方案
 *
 * @param planId 方案ID
 * @param userId 用户ID
 * @throws BizException 业务异常
 */
public void confirmPlan(String planId, String userId) {
    // 具体实现
}

// 3. 异常处理
// 业务异常使用BizException
if (plan == null) {
    throw new BizException("PLAN_NOT_FOUND", "方案不存在");
}

// 系统异常向上抛出
try {
    // ...
} catch (SQLException e) {
    log.error("数据库错误", e);
    throw new SystemException("DB_ERROR", e);
}
```

#### Python 规范
```python
# 1. 命名规范
# 类名: 大驼峰
class PlanGenerator:
    pass

# 函数名: 小写下划线
def generate_plan():
    pass

# 常量: 全大写下划线
PLAN_STATUS_CONFIRMED = "CONFIRMED"

# 模块名: 小写下划线
# plan_generator.py

# 2. 类型注解（必须）
def parse_requirements(inputs: dict) -> dict:
    """
    解析需求

    Args:
        inputs: 用户输入

    Returns:
        解析后的结构化需求
    """
    pass

# 3. 异常处理
from fastapi import HTTPException

if plan is None:
    raise HTTPException(status_code=404, detail="PLAN_NOT_FOUND")
```

#### 小程序规范
```javascript
// 1. 命名规范
// 文件名: 小写中划线
// plan-card.js

// 变量名: 小驼峰
let planList = [];

// 常量: 全大写下划线
const API_BASE_URL = 'https://api.teamventure.com';

// 2. 注释规范
/**
 * 确认方案
 * @param {string} planId - 方案ID
 */
function confirmPlan(planId) {
  // 具体实现
}

// 3. 异步处理（优先async/await）
async function loadPlans() {
  try {
    const plans = await api.getPlans();
    this.setData({ plans });
  } catch (err) {
    wx.showToast({ title: '加载失败', icon: 'none' });
  }
}
```

### 8.2 Git 提交规范

```bash
# 格式: <type>(<scope>): <subject>

# type类型:
# - feat: 新功能
# - fix: bug修复
# - docs: 文档更新
# - style: 代码格式（不影响功能）
# - refactor: 重构
# - test: 测试用例
# - chore: 构建/工具变动

# 示例:
feat(plan): 实现方案确认功能

fix(auth): 修复session过期后401错误

docs(api): 更新API文档

refactor(java): 重构Plan聚合为COLA架构
```

### 8.3 数据库变更规范

```sql
-- 1. 所有DDL必须通过Flyway/Liquibase管理
-- 2. 文件命名: V{版本号}__{描述}.sql
--    示例: V1.0.1__add_plan_status_index.sql

-- 3. 每个变更必须可回滚
-- 正向变更
ALTER TABLE plans ADD COLUMN confirmed_by VARCHAR(64);

-- 回滚脚本（单独文件）
-- U1.0.1__rollback_add_plan_status_index.sql
ALTER TABLE plans DROP COLUMN confirmed_by;

-- 4. 禁止直接修改生产数据库
-- 必须走变更流程: 提交SQL → Review → 测试环境验证 → 生产发布
```

### 8.4 API 接口规范

```yaml
# 1. RESTful设计
GET    /api/v1/plans          # 列表
GET    /api/v1/plans/{id}     # 详情
POST   /api/v1/plans          # 创建
PUT    /api/v1/plans/{id}     # 更新
DELETE /api/v1/plans/{id}     # 删除

# 2. 响应格式统一
# 成功:
{
  "success": true,
  "data": { ... }
}

# 失败:
{
  "success": false,
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "参数校验失败",
    "details": [
      {"field": "people_count", "issue": "must be > 0"}
    ]
  }
}

# 3. HTTP状态码
200 OK               # 成功
201 Created          # 创建成功
202 Accepted         # 异步任务已接受
400 Bad Request      # 参数错误
401 Unauthorized     # 未认证
403 Forbidden        # 无权限
404 Not Found        # 资源不存在
500 Internal Error   # 服务器错误
503 Service Unavailable  # 服务不可用
```

### 8.5 测试规范

#### 单元测试
```java
// Java - JUnit 5
@SpringBootTest
class PlanServiceTest {

    @Resource
    private PlanService planService;

    @Test
    @DisplayName("确认方案 - 成功场景")
    void testConfirmPlan_Success() {
        // Given
        String planId = "plan_test_001";
        String userId = "user_test_001";

        // When
        planService.confirmPlan(planId, userId);

        // Then
        Plan plan = planService.getById(planId);
        assertEquals(PlanStatus.CONFIRMED, plan.getStatus());
        assertNotNull(plan.getConfirmedTime());
    }

    @Test
    @DisplayName("确认方案 - 方案不存在")
    void testConfirmPlan_PlanNotFound() {
        assertThrows(BizException.class, () -> {
            planService.confirmPlan("non_existent", "user_001");
        });
    }
}
```

```python
# Python - pytest
def test_generate_plan_success():
    """测试方案生成 - 成功场景"""
    # Given
    inputs = {
        "people_count": 50,
        "budget_min": 35000,
        "budget_max": 50000
    }

    # When
    result = plan_generator.generate(inputs)

    # Then
    assert len(result) == 3
    assert result[0]["plan_type"] == "budget"
    assert result[0]["budget_total"] <= 35000
```

#### 集成测试
```java
// Java - SpringBoot Test
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
class PlanControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void testConfirmPlanAPI() throws Exception {
        mockMvc.perform(post("/api/v1/plans/plan_001/confirm")
                .header("Authorization", "Bearer test_token")
                .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.success").value(true));
    }
}
```

---

## 第9章 开发排期与里程碑

### 9.1 一期开发计划（7周）

| 周 | 时间 | 里程碑 | 交付物 | 责任人 |
|----|------|--------|--------|--------|
| W1 | Week 1 | 基础设施搭建 | Docker环境、数据库初始化、CI/CD | DevOps |
| W2 | Week 2 | Java服务框架 | COLA架构、MyBatis配置、基础API | Java团队 |
| W3 | Week 3 | Python AI服务 | LangGraph流程、GPT集成 | Python团队 |
| W4 | Week 4 | 核心功能开发 | 登录、生成、查询接口 | 全员 |
| W5 | Week 5 | 小程序开发 | 生成页、对比页、详情页 | 前端团队 |
| W6 | Week 6 | 联调与测试 | E2E测试、性能测试 | QA团队 |
| W7 | Week 7 | 上线准备 | 灰度发布、监控接入 | 全员 |

### 9.2 关键检查点（每周五）

```
Week 1 验收:
- ✅ Docker Compose 本地环境可启动
- ✅ MySQL 主从复制正常
- ✅ RabbitMQ Exchange/Queue 创建成功

Week 2 验收:
- ✅ Java Service 启动成功（8080端口）
- ✅ Swagger文档可访问
- ✅ 微信登录接口联调通过

Week 3 验收:
- ✅ Python Service 启动成功（8000端口）
- ✅ LangGraph流程可运行
- ✅ GPT-4 调用成功（测试用例）

Week 4 验收:
- ✅ 生成方案E2E流程打通（Java → MQ → Python → Java）
- ✅ 方案列表、详情接口可用
- ✅ 确认方案状态流转正确

Week 5 验收:
- ✅ 小程序4个核心页面完成
- ✅ 小程序可调用后端API
- ✅ 用户可完成"生成→对比→确认"主流程

Week 6 验收:
- ✅ 所有TC测试用例通过
- ✅ 性能测试达标（P95 < 60s）
- ✅ 无P0/P1 Bug

Week 7 验收:
- ✅ 灰度10%用户无异常
- ✅ 全量发布
- ✅ 监控大盘正常
```

---

## 附录索引

### 完整详细设计文档

1. **数据库详细设计**
   - 文件: [teamventure-phase1-database-design.md](./teamventure-phase1-database-design.md)
   - 内容: 完整DDL、索引设计、分表策略、查询优化

2. **Python AI服务详细设计**
   - 文件: [teamventure-phase1-ai-service-design.md](./teamventure-phase1-ai-service-design.md)
   - 内容: LangGraph流程、Prompt工程、错误处理、性能优化

3. **Java业务服务详细设计**
   - 文件: [teamventure-phase1-business-service-design.md](./teamventure-phase1-business-service-design.md)
   - 内容: COLA架构实现、MyBatis配置、事务管理、缓存策略

4. **小程序前端详细设计**
   - 文件: [teamventure-phase1-miniapp-design.md](./teamventure-phase1-miniapp-design.md)
   - 内容: 页面设计、组件设计、状态管理、网络封装

---

## 版本历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v1.0 | 2025-12-30 | 初始版本，开发前最终设计 | Claude + Team |

---

**重要提醒**:
1. 本文档是开发实施的唯一标准，所有代码必须严格遵循本设计
2. 任何偏离设计的实现必须经过架构师Review
3. 文档变更需要同步更新代码，反之亦然
4. 每周五进行设计Review，确保文档与实现一致

**文档状态**: ✅ 已锁定（开发中禁止随意修改）
