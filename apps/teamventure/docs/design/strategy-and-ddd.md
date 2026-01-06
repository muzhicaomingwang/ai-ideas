# TeamVenture 一期（小程序）战略设计 + DDD 战术设计

> 面向教学：先用最小可行的 BC/聚合跑通闭环，再逐步演进为多服务/更细粒度。
>
> 参考：`docs/event-storming/teamventure-phase1-event-storming.md`

---

## 1) 战略设计（Strategic Design）

### 1.1 一句话定位（Strategy）
- **TeamVenture 小程序一期**：让 HR 在 10–15 分钟内生成 3 套可对比的团建方案，并能完成“确认方案 + 联系供应商”的行动闭环。

### 1.2 北极星与护栏指标
- 北极星：`Weekly Confirmed Plans`（每周确认方案数）
- 护栏：生成耗时 P95、失败率、投诉/纠错率、供应商联系转化率

### 1.3 一期 Bounded Context（BC）定义

**BC-1：Identity & Session**
- 目标：最低成本完成“可信身份 + 会话”
- 输入/输出：WeChat code → userId + session token

**BC-2：Planning**
- 目标：跑通“需求→生成→对比→确认→联系”的主闭环
- 关键资产：PlanRequest、Plan、SupplierSnapshot

**BC-3：Supplier Catalog**
- 目标：提供可查询的供应商目录与基础匹配素材（一期可人工录入）
- 关键资产：Supplier

### 1.4 Context Map（关系）
- Planning 依赖 Identity（认证）
- Planning 依赖 Supplier Catalog（查询/匹配）
- Analytics 作为横切能力，先落在 Planning/Identity 的事件日志与埋点

---

## 2) 战术设计（Tactical Design）

> 重点：聚合边界 + 不变式 + 用例（应用服务）+ 事件。
>
> **基于实际实现版本**：参考 `PlanService.java`、`AuthService.java`、`InternalPlanCallbackService.java`

### 2.1 聚合与实体/值对象（实际实现）

#### 聚合：User（聚合根，Identity BC）
**作用**：管理用户身份与基本信息

**实体字段**（基于 `UserPO.java`）：
- `user_id`（PRIMARY KEY）：ULID 格式，前缀 "user_"
- `wechat_openid`（UNIQUE）：微信唯一标识（一期使用 SHA-256 哈希模拟）
- `nickname`：用户昵称（登录时提交或更新）
- `avatar_url`：头像 URL（支持微信头像或 OSS 上传）
- `phone`、`company`：可选字段（一期未强制）
- `role`：固定为 "HR"
- `status`：固定为 "ACTIVE"

**不变式**：
- `wechat_openid` 必须唯一（数据库 UNIQUE 约束）
- `nickname` 不能为空（默认 "微信用户"）
- `user_id` 使用 ULID 生成，保证分布式唯一性

**业务行为**：
- `loginWithWeChat(code, nickname, avatarUrl)`：登录时创建或更新用户
- `updateProfile(nickname, avatarUrl)`：更新用户信息

---

#### 聚合：PlanRequest（聚合根，Planning BC）
**作用**：承载一次"用户需求输入"的事实快照与校验结果

**实体字段**（基于 `PlanRequestPO.java`）：
- `plan_request_id`（PRIMARY KEY）：ULID 格式，前缀 "plan_req_"
- `user_id`：关联 User（非外键，逻辑关联）
- `people_count`：参与人数（> 0）
- `budget_min`、`budget_max`：预算区间（单位：分）
- `start_date`、`end_date`：活动日期（DATE 类型）
- `departure_city`：出发城市
- `preferences_json`：偏好设置（JSONB）
- `status`：`GENERATING` → `COMPLETED` / `FAILED`
- `generation_started_at`、`generation_completed_at`：生成时间戳

**不变式**：
- `budget_max` >= `budget_min`
- `end_date` >= `start_date`
- `people_count` > 0
- 状态机：`GENERATING` → (`COMPLETED` | `FAILED`)，不可回退

**值对象**：
- `BudgetRange(min, max)`：预算区间
- `DateRange(start, end)`：日期区间
- `Preferences(activityTypes[], accommodationLevel, diningStyle[], specialRequirements)`：偏好设置（JSON 存储）

**业务行为**：
- `createPlanRequest(userId, inputs)`：创建请求并发送 MQ
- `markCompleted()`：AI 回调后标记完成
- `markFailed(errorCode)`：生成失败时标记（一期未实现）

**关联实现**：
- `PlanService.createPlanRequestAndPublish()` (src/backend/java-business-service/.../PlanService.java:53-85)

---

#### 聚合：Plan（聚合根，Planning BC）
**作用**：承载一套可执行方案（行程/预算/供应商），并管理状态流转

**实体字段**（基于 `PlanPO.java`）：
- `plan_id`（PRIMARY KEY）：ULID 格式，前缀 "plan_"
- `plan_request_id`：关联 PlanRequest
- `user_id`：关联 User
- `plan_type`：`budget` / `standard` / `premium`（三选一）
- `plan_name`：方案名称（如 "北京2天1夜团建经济型方案"）
- `departure_city`：出发城市（团队从哪里出发，如：上海市）
- `destination`：目的地（团建活动举办地点，如：杭州千岛湖）
- `status`：`DRAFT`（默认） → `CONFIRMED`（不可回退）
- `itinerary`：行程安排（JSON）
- `budget_breakdown`：预算明细（JSON）
- `supplier_snapshots`：供应商快照数组（JSON，避免 join）
- `confirmed_time`：确认时间（`status=CONFIRMED` 时必填）

**状态机**：
```
DRAFT ──confirm()──> CONFIRMED
  │                      │
  └──────────────────────┘
       （不可回退）
```

**不变式**：
- `plan_type` ∈ {budget, standard, premium}
- `status=CONFIRMED` 时必须有 `confirmed_time`
- `suppliers_json` 至少包含 1 个供应商快照（否则标记为"资源不足降级方案"）

**值对象**：
- `Itinerary(days[])`：行程安排，按天拆分
  ```json
  {
    "days": [
      {
        "day": 1,
        "date": "2026-02-01",
        "activities": [
          {"time": "09:00", "activity": "集合出发", "location": "公司门口"}
        ]
      }
    ]
  }
  ```

- `BudgetBreakdown(categories[])`：预算明细
  ```json
  {
    "total": 15000,
    "categories": [
      {"name": "交通", "amount": 5000},
      {"name": "住宿", "amount": 7000},
      {"name": "餐饮", "amount": 3000}
    ]
  }
  ```

- `SupplierSnapshot[]`：供应商快照（不可变副本）
  ```json
  [
    {
      "supplier_id": "supp_01JHTXXXXXXX",
      "name": "怀柔山水农家院",
      "category": "accommodation",
      "price_range": "200-500/人/天",
      "contact_phone": "010-12345678"
    }
  ]
  ```

**业务行为**：
- `confirmPlan(userId)`：确认方案（幂等，重复调用不报错）
- `viewDetail(userId)`：查看详情（权限校验）
- `generateFromRequest(planRequest)`：从 PlanRequest 生成（AI 服务调用）

**关联实现**：
- `PlanService.confirmPlan()` (src/backend/java-business-service/.../PlanService.java:107-122)
- `InternalPlanCallbackService.handleGeneratedPlans()` (src/backend/java-business-service/.../InternalPlanCallbackService.java:31-49)

---

#### 聚合：Supplier（聚合根，Supplier Catalog BC，一期只读）
**作用**：供应商目录与匹配素材

**实体字段**（基于 `SupplierPO.java`）：
- `supplier_id`（PRIMARY KEY）：ULID 格式，前缀 "supp_"
- `name`：供应商名称
- `category`：`accommodation` / `dining` / `activity` / `transportation`
- `city`：所在城市
- `price_min`、`price_max`：价格区间（单位：分）
- `rating`：评分（0-5 分）
- `contact_phone`、`contact_wechat`、`contact_email`：联系方式
- `tags_json`：标签（JSONB，如 ["亲子友好", "团建推荐"]）
- `coordinates`：地理坐标（POINT 类型，支持地理查询）

**不变式**：
- `price_max` >= `price_min`
- `category` ∈ {accommodation, dining, activity, transportation}
- `rating` ∈ [0, 5]
- `city` 不能为空

**值对象**：
- `GeoLocation(lat, lng, address)`：地理位置
- `PriceRange(min, max)`：价格区间
- `ContactInfo(phone, wechat, email)`：联系方式

**业务行为**（一期未实现增删改）：
- `searchSuppliers(city, category, priceRange, sortBy)`：搜索供应商
- `getDetail(supplierId)`：查看详情

---

#### 聚合：SupplierContactLog（聚合根 / 事件流，Planning BC）
**作用**：记录供应商联系行为（支持转化漏斗与运营）

**实体字段**（基于 `SupplierContactLogPO.java`）：
- `contact_id`（PRIMARY KEY）：ULID 格式，前缀 "contact_"
- `plan_id`：关联 Plan
- `supplier_id`：关联 Supplier
- `user_id`：关联 User
- `channel`：`PHONE` / `WECHAT` / `EMAIL`（联系方式）
- `notes`：备注（可选）
- `contact_time`：联系时间（默认当前时间）

**不变式**：
- `channel` ∈ {PHONE, WECHAT, EMAIL}
- `plan_id` 必须存在
- `supplier_id` 必须存在

**业务行为**：
- `logContact(userId, planId, supplierId, channel, notes)`：记录联系行为

**关联实现**：
- `PlanService.logSupplierContact()` (src/backend/java-business-service/.../PlanService.java:124-140)

---

### 2.2 领域事件（实际实现 vs 设计）

> 基于 `DomainEventPO.java` 与 `recordEvent()` 方法的实际调用。

#### 已实现的事件（✅）

| 事件类型 | 聚合根 | 触发代码位置 | Payload | 用途 |
|---------|--------|-------------|---------|------|
| `PlanRequestCreated` | PlanRequest | `PlanService.createPlanRequestAndPublish():69` | `{plan_request_id}` | 审计日志 + 埋点 |
| `PlanGenerated` | Plan | `InternalPlanCallbackService.handleGeneratedPlans():43` | `{plan_id}` | 生成成功埋点 |
| `PlanConfirmed` | Plan | `PlanService.confirmPlan():121` | `{plan_id}` | 北极星指标数据源 |
| `SupplierContacted` | SupplierContactLog | `PlanService.logSupplierContact():133-139` | `{plan_id, supplier_id, channel}` | 转化漏斗分析 |

#### 未实现的事件（⚠️ 设计意图，二期补充）

| 事件类型 | 聚合根 | 预期触发时机 | 缺失原因 |
|---------|--------|-------------|---------|
| `WeChatLoginSucceeded` | User | 登录成功后 | `AuthService.loginWithWeChat()` 未记录事件 |
| `WeChatLoginFailed` | User | 登录失败后 | 异常直接抛出，无事件记录 |
| `PlanGenerationStarted` | PlanRequest | MQ 发送成功后 | 未在 Java 服务记录，可在 AI 服务补充 |
| `PlanGenerationFailed` | PlanRequest | AI 生成失败后 | 一期未处理失败回调 |
| `PlanViewed` | Plan | 打开详情页 | 一期未做用户行为埋点 |
| `PlanCompared` | Plan | 对比页查看 | 一期未做用户行为埋点 |
| `PlanShared` | Plan | 分享方案 | 一期未实现分享功能 |

#### 事件存储结构（`domain_events` 表）

```sql
CREATE TABLE domain_events (
    event_id VARCHAR(64) PRIMARY KEY,    -- ULID, 前缀 "evt_"
    event_type VARCHAR(100) NOT NULL,    -- 事件类型（如 "PlanConfirmed"）
    aggregate_type VARCHAR(50),          -- 聚合类型（如 "Plan"）
    aggregate_id VARCHAR(64),            -- 聚合实例 ID
    user_id VARCHAR(64),                 -- 用户 ID（用于分析）
    payload TEXT,                        -- JSON 格式的事件详情
    occurred_at TIMESTAMP DEFAULT NOW(), -- 事件发生时间
    processed BOOLEAN DEFAULT FALSE      -- 是否已被消费（预留）
);
```

**事件记录示例**（`PlanService.recordEvent()` 实现）：
```java
private void recordEvent(String eventType, String aggregateType,
                        String aggregateId, String userId,
                        Map<String, Object> payload) {
    DomainEventPO evt = new DomainEventPO();
    evt.setEventId(IdGenerator.newId("evt"));
    evt.setEventType(eventType);              // "PlanConfirmed"
    evt.setAggregateType(aggregateType);      // "Plan"
    evt.setAggregateId(aggregateId);          // "plan_01JHTXXXXXXX"
    evt.setUserId(userId);                    // "user_01JHTXXXXXXX"
    evt.setPayloadJson(Jsons.toJson(payload)); // {"plan_id": "plan_01..."}
    evt.setOccurredAt(Instant.now());
    evt.setProcessed(false);
    eventMapper.insert(evt);
}
```

---

### 2.3 应用服务（Use Cases）实际实现

> 对应 COLA 架构的 `application` 层。

#### Planning BC - PlanService.java

**已实现用例**：

1. **CreatePlanRequestUseCase**
   - 方法：`createPlanRequestAndPublish(userId, req)`
   - 职责：
     1. 创建 PlanRequest 记录（状态：GENERATING）
     2. 记录 `PlanRequestCreated` 事件
     3. 发送 RabbitMQ 消息到 AI 服务
   - 代码位置：`PlanService.java:53-85`

2. **ListPlansUseCase**
   - 方法：`listPlans(userId, page, pageSize)`
   - 职责：分页查询用户的历史方案（按创建时间倒序）
   - 返回：MyBatis Plus `Page<PlanPO>` 对象
   - 代码位置：`PlanService.java:87-94`

3. **GetPlanDetailUseCase**
   - 方法：`getPlanDetail(userId, planId)`
   - 职责：
     1. 权限校验（`userId` 匹配）
     2. 返回方案详情（行程、预算、供应商）
   - 代码位置：`PlanService.java:96-105`

4. **ConfirmPlanUseCase**
   - 方法：`confirmPlan(userId, planId)`
   - 职责：
     1. 权限校验
     2. 幂等处理（已确认则直接返回）
     3. 更新状态为 CONFIRMED
     4. 记录 `PlanConfirmed` 事件
   - 代码位置：`PlanService.java:107-122`

5. **LogSupplierContactUseCase**
   - 方法：`logSupplierContact(userId, planId, req)`
   - 职责：
     1. 创建 SupplierContactLog 记录
     2. 记录 `SupplierContacted` 事件
   - 代码位置：`PlanService.java:124-140`

#### Planning BC - InternalPlanCallbackService.java

6. **HandleGeneratedPlansUseCase**（AI 回调专用）
   - 方法：`handleGeneratedPlans(req)`
   - 职责：
     1. 批量插入 3 套 Plan（budget/standard/premium）
     2. 为每套方案记录 `PlanGenerated` 事件
     3. 更新 PlanRequest 状态为 COMPLETED
   - 事务：`@Transactional` 保证原子性
   - 代码位置：`InternalPlanCallbackService.java:31-49`

#### Identity BC - AuthService.java

7. **LoginWithWeChatUseCase**
   - 方法：`loginWithWeChat(code, nickname, avatarUrl)`
   - 职责：
     1. 将 `code` 哈希为 `openid`（一期模拟）
     2. 查询或创建 User 记录
     3. 更新昵称/头像（如果提供）
     4. 生成 JWT Token（有效期 24 小时）
     5. 存储 session 到 Redis（key: `session:{token}`）
     6. 返回 Token + 完整 UserInfo
   - 代码位置：`AuthService.java:39-88`

8. **GetUserIdFromAuthorizationUseCase**（鉴权中间件）
   - 方法：`getUserIdFromAuthorization(authorization)`
   - 职责：
     1. 解析 `Bearer {token}`
     2. 从 Redis 读取 `userId`（优先）
     3. Fallback：解析 JWT（stateless 模式）
   - 代码位置：`AuthService.java:95-110`

#### Supplier Catalog BC - SupplierService.java

9. **SearchSuppliersUseCase**（已定义接口，实现简化）
   - 方法：`searchSuppliers(city, category, priceRange, sortBy)`
   - 职责：按城市/品类/价格筛选供应商
   - 实现状态：✅ 控制器已定义，Service 层简化实现

10. **GetSupplierDetailUseCase**
    - 方法：`getSupplierDetail(supplierId)`
    - 职责：返回供应商详情
    - 实现状态：✅ 控制器已定义，Service 层简化实现

---

### 2.4 COLA 架构层次映射（实际代码）

```
src/backend/java-business-service/src/main/java/com/teamventure/

├── adapter/                    # Adapter 层（输入适配）
│   ├── web/                    # HTTP 控制器
│   │   ├── auth/AuthController.java
│   │   ├── plans/PlanController.java
│   │   ├── suppliers/SupplierController.java
│   │   └── internal/InternalPlanController.java
│   └── filter/                 # 鉴权过滤器
│       └── JwtAuthFilter.java
│
├── app/                        # Application 层（用例编排）
│   ├── service/
│   │   ├── AuthService.java              # Identity BC 用例
│   │   ├── PlanService.java              # Planning BC 用例
│   │   ├── InternalPlanCallbackService.java  # AI 回调用例
│   │   ├── SupplierService.java          # Supplier BC 用例
│   │   └── OssService.java               # 横切：OSS 服务
│   └── support/
│       ├── BizException.java             # 业务异常
│       ├── IdGenerator.java              # ULID 生成器
│       └── JwtSupport.java               # JWT 工具类
│
├── domain/                     # Domain 层（聚合、值对象）
│   └── model/                  # 一期未显式定义（直接使用 PO）
│       └── （预留：二期重构为独立 Domain Model）
│
└── infrastructure/             # Infrastructure 层（外部依赖）
    ├── persistence/
    │   ├── mapper/             # MyBatis Mapper 接口
    │   │   ├── UserMapper.java
    │   │   ├── PlanMapper.java
    │   │   ├── PlanRequestMapper.java
    │   │   ├── SupplierMapper.java
    │   │   ├── SupplierContactLogMapper.java
    │   │   └── DomainEventMapper.java
    │   └── po/                 # 持久化对象（PO）
    │       ├── UserPO.java
    │       ├── PlanPO.java
    │       ├── PlanRequestPO.java
    │       ├── SupplierPO.java
    │       ├── SupplierContactLogPO.java
    │       └── DomainEventPO.java
    └── config/                 # 配置类
        ├── DruidConfig.java
        ├── RedisConfig.java
        └── RabbitMQConfig.java
```

**说明**：
- 一期为了快速实现，Domain 层与 Infrastructure 层合并（PO 直接作为聚合）
- 二期重构建议：引入独立的 Domain Model，PO 仅作为持久化映射

---

## 3) 架构落地实践（基于实际代码）

### 3.1 分层策略（Ports & Adapters 变体）

**实际实现**（一期简化版）：
- `adapter/`：HTTP 控制器 + 参数校验 + 鉴权过滤器
- `app/`：应用服务（用例编排） + 业务异常 + 工具类
- `domain/`：（一期未显式分离，PO 承担聚合职责）
- `infrastructure/`：MyBatis Mapper + PO + Redis/RabbitMQ 配置

**二期重构方向**：
```
domain/
  ├── model/
  │   ├── Plan.java              # 聚合根（业务逻辑）
  │   ├── PlanRequest.java
  │   └── User.java
  ├── repository/
  │   ├── PlanRepository.java    # 仓储接口（domain 定义）
  │   └── UserRepository.java
  └── event/
      ├── DomainEvent.java       # 事件基类
      └── PlanConfirmed.java     # 具体事件

infrastructure/
  └── persistence/
      └── repository/
          └── PlanRepositoryImpl.java  # 仓储实现（infra 提供）
```

---

### 3.2 数据一致性策略（实际实现）

#### 单聚合事务（✅ 已实现）
- **PlanRequest + domain_events**：同一事务内写入（`PlanService.createPlanRequestAndPublish()`）
- **Plan + domain_events**：同一事务内写入（`InternalPlanCallbackService.handleGeneratedPlans()`）
- **SupplierContactLog + domain_events**：同一事务内写入（`PlanService.logSupplierContact()`）

#### 跨聚合最终一致性（✅ 已实现）
- **PlanRequest → Plan 生成**：通过 RabbitMQ 异步解耦
  - Java 服务发送 MQ 后立即返回
  - Python AI 服务消费 MQ 并回调
  - 回调失败则 PlanRequest 保持 GENERATING 状态（可手动重试）

#### 幂等性保证（✅ 已实现）
- **confirmPlan**：重复调用不报错（代码：`PlanService.java:115-117`）
  ```java
  if ("CONFIRMED".equalsIgnoreCase(plan.getStatus())) {
      return; // 幂等：已确认则直接返回
  }
  ```

#### 数据快照策略（✅ 已实现）
- **Plan 中的 suppliers_json**：存储供应商快照，避免历史方案因外部数据变更失效
- **PlanRequest 中的 preferences_json**：保存原始输入，支持复现生成逻辑

---

### 3.3 领域事件实践（一期 vs 二期）

**一期（当前）**：
- 事件仅落库到 `domain_events` 表
- `processed` 字段预留但未消费
- 用途：审计日志 + 离线分析

**二期（演进）**：
- 引入 EventBus 或 Kafka 实现异步消费
- 消费场景：
  1. **北极星指标实时统计**：消费 `PlanConfirmed` 事件，实时更新 Redis 计数器
  2. **转化漏斗分析**：`PlanConfirmed` → `SupplierContacted` 转化率计算
  3. **慢查询监控**：`PlanGenerationStarted` → `PlanGenerated` 耗时 P95/P99
  4. **Event Sourcing**：重建聚合历史状态（用于审计或回溯）

