# TeamVenture 一期（小程序）事件风暴产物

> 目标：用事件风暴确定一期限界上下文（Bounded Context）与核心业务闭环，并为后续战略/战术设计、接口设计与交互设计提供统一语言。
>
> 参考 PRD：`docs/prds/teamventure-team-building-assistant-prd.md`

---

## 0. 一期范围（小程序 MVP 切片）

### P0（一期必须交付）
- 微信登录：`wx.login` → 后端换取 session（不做账号密码）
- “生成团建方案”：输入需求 → 生成 3 套方案（经济/平衡/品质）
- “查看/对比方案”：方案卡片 + 对比表 + 进入详情
- “确认方案”：将某套方案标记为确认（便于后续跟踪/复用）
- “联系供应商”：展示供应商联系方式，记录“已联系/联系渠道”（用于漏斗与运营）
- “我的方案”：按时间查看历史方案（最小列表 + 详情）

### P1（一期可选）
- 分享方案卡片/链接（小程序内分享）
- 导出（先做“长图/分享卡片”，PDF 放二期）

### 非目标（一期不做）
- 供应商入驻/审核体系、在线下单/履约、支付/发票
- 参与者问卷收集与满意度追踪
- 实时应急与 24/7 客服

---

## 1. 领域共同语言（Ubiquitous Language）

> DDD 核心原则：团队使用统一的术语，从业务讨论、代码命名到文档表述保持一致，避免"翻译损耗"。

### 1.1 核心概念定义

#### 方案相关（Planning Domain）

| 术语 | 英文 | 定义 | 示例 | 边界说明 |
|------|------|------|------|---------|
| **团建方案** | Plan | HR 针对一次团建活动的完整执行方案，包含行程、预算、供应商信息 | "怀柔2天1夜拓展方案" | 一个 Plan 对应一次完整的团建活动 |
| **方案请求** | Plan Request | HR 提交的团建需求输入，作为生成方案的原始材料 | 人数50、预算¥3.5万、2天1夜 | PlanRequest 是输入，Plan 是输出 |
| **方案类型** | Plan Type | 方案的定位档次，分为经济/平衡/品质三档 | `budget` / `standard` / `premium` | 一次生成必须产出3种类型 |
| **方案状态** | Plan Status | 方案的生命周期状态 | `draft`（草稿）/ `confirmed`（已确认） | 状态不可回退（一期） |
| **出发城市** | Departure City | 团队从哪里出发，通常是公司所在城市 | "上海市" | 用于行程起点规划、交通费用估算 |
| **目的地** | Destination | 团建活动举办地点，团队前往的地方 | "杭州千岛湖" | 用于供应商匹配、活动安排、住宿费用估算 |
| **行程** | Itinerary | 按天拆分的活动安排与时间表 | Day1: 09:00 出发 → 12:00 午餐... | 以"天"为单位组织 |
| **预算明细** | Budget Breakdown | 按类目拆分的费用构成 | 交通¥5000、住宿¥15000... | 分类：交通/住宿/餐饮/活动/其他 |
| **数据快照** | Snapshot | 方案生成时对外部数据（如供应商信息）的副本存储 | 供应商当时的价格、联系方式 | 避免历史方案因外部数据变更失效 |

> **显示格式约定**：前端展示"出发城市"与"目的地"时，统一使用箭头格式：`{departure_city} → {destination}`，例如："上海市 → 杭州千岛湖"

#### 供应商相关（Supplier Catalog Domain）

| 术语 | 英文 | 定义 | 示例 | 边界说明 |
|------|------|------|------|---------|
| **供应商** | Supplier | 提供团建相关服务的第三方机构或个人 | "怀柔山水农家院" | 一期只读，不支持入驻 |
| **品类** | Category | 供应商提供的服务类型 | `accommodation`（住宿）/ `dining`（餐饮）/ `activity`（活动）/ `transportation`（交通） | 一个供应商可属于多品类 |
| **价格区间** | Price Range | 供应商的报价范围 | ¥200-500/人/天 | 用于匹配筛选 |
| **联系渠道** | Contact Channel | 联系供应商的方式 | `PHONE`（电话）/ `WECHAT`（微信）/ `EMAIL` | 记录用户使用哪种方式联系 |
| **供应商快照** | Supplier Snapshot | Plan 中存储的供应商数据副本 | 包含名称、联系方式、价格的不可变副本 | 不随供应商主数据变化 |

#### 用户与会话相关（Identity Domain）

| 术语 | 英文 | 定义 | 示例 | 边界说明 |
|------|------|------|------|---------|
| **用户** | User | 使用 TeamVenture 的 HR/行政人员 | user_01JHXXXXXXX | 一期仅微信身份，不做角色权限 |
| **会话** | Session | 用户登录后的有效身份凭证 | session_token 有效期 24h | 过期需重新微信登录 |
| **微信代码** | WeChat Code | 微信小程序 `wx.login` 返回的临时凭证 | 5分钟有效期 | 用于后端换取 openid/unionid |

### 1.2 业务流程术语

| 术语 | 英文 | 定义 | 触发时机 | 结果 |
|------|------|------|---------|------|
| **生成方案** | Generate Plans | 系统根据 PlanRequest 自动生成 3 套方案的过程 | 用户提交需求后 | 产出 3 个 Plan（budget/standard/premium） |
| **对比方案** | Compare Plans | 用户在对比页查看多套方案的差异 | 生成完成后 | 帮助用户决策选择哪套方案 |
| **确认方案** | Confirm Plan | 用户将某套方案标记为"已确认"，表示采纳 | 用户在详情页点击确认 | 状态变更为 confirmed，纳入北极星指标 |
| **联系供应商** | Contact Supplier | 用户通过电话/微信联系方案中的供应商 | 用户点击联系按钮 | 记录联系行为（用于转化漏斗） |
| **方案降级** | Plan Degradation | 供应商资源不足时，使用模板生成兜底方案 | 匹配供应商 < 5 家 | 方案质量降低，但确保可用 |

### 1.3 度量与指标术语

| 术语 | 英文 | 定义 | 计算方式 | 用途 |
|------|------|------|---------|------|
| **北极星指标** | North Star Metric | 衡量产品核心价值的唯一关键指标 | `Weekly Confirmed Plans`（每周确认方案数） | 产品战略对齐 |
| **生成耗时** | Generation Duration | 从提交需求到展示对比页的时间 | P50 / P95 / P99 | 性能监控 |
| **供应商联系率** | Supplier Contact Rate | 确认方案后联系供应商的比例 | 联系次数 / 确认方案数 | 转化漏斗分析 |
| **方案复用率** | Plan Reuse Rate | 用户再次查看历史方案的比例 | 打开详情 / 历史方案总数 | 留存指标 |

### 1.4 技术实现术语

| 术语 | 英文 | 定义 | 使用场景 | 技术要求 |
|------|------|------|---------|---------|
| **幂等** | Idempotency | 同一操作重复执行，结果保持一致 | CreatePlanRequest 防重复提交 | 60s 内相同输入返回缓存 |
| **编排** | Orchestration | 协调多个服务/模块完成复杂流程 | GeneratePlans 调用 LLM + 供应商匹配 + 预算校验 | 使用应用服务层统一编排 |
| **CQRS** | Command Query Responsibility Segregation | 命令（写）与查询（读）分离 | 写用聚合，读用专门的读模型 | 一期可同表，但接口分离 |
| **事件溯源** | Event Sourcing | 通过事件序列重建聚合状态 | 一期不做完整实现，但事件记录为埋点/日志 | 为二期演进预留 |

### 1.5 反模式与禁用术语

> 这些术语容易引起歧义，团队应避免使用。

| ❌ 禁用术语 | ✅ 应使用 | 原因 |
|-----------|---------|------|
| "订单" | Plan（方案） | 一期不涉及支付/履约，避免混淆 |
| "预订" | Confirm（确认） | 确认≠预订，只是标记采纳 |
| "支付" | （不使用） | 一期不做支付闭环 |
| "审核" | （不使用） | 一期无审批流程 |
| "取消" | （不使用） | 状态不可回退（二期再加） |
| "模板" | Degraded Plan（降级方案） | "模板生成"易误解为用户选模板 |

### 1.6 跨团队术语映射

> 不同角色可能用不同词汇表达同一概念，需要显式映射。

| 产品/业务术语 | 技术术语 | 数据库字段 | API 字段 | 前端展示 |
|-------------|---------|-----------|---------|---------|
| 团建方案 | Plan | `plans` 表 | `plan` | "方案" |
| 方案名称 | PlanName | `plan_name` | `plan_name` | "方案名称" |
| 方案类型（经济/平衡/品质） | PlanType | `plan_type` | `plan_type: budget/standard/premium` | "经济型"/"平衡型"/"品质型" |
| 出发城市 | DepartureCity | `departure_city` | `departure_city` | "出发地点" |
| 目的地 | Destination | `destination` | `destination` | "目的地" |
| 确认方案 | ConfirmPlan | `status='confirmed'` | `POST /plans/{id}/confirm` | "确认此方案" |
| 供应商快照 | SupplierSnapshot | `supplier_snapshots` | `supplier_snapshots` | "供应商信息" |
| 生成时间 | GenerationDuration | `generation_time_ms` | `generation_time_ms` | "已为您生成方案（耗时 45 秒）" |

> **注意**：前端字段 `departureLocation` 对应 API/数据库的 `departure_city`，需显式映射

---

## 2. 参与者（Actors）

- HR/行政（主用户）：发起生成、对比、确认、联系供应商、分享
- 系统（TeamVenture）：编排 LLM、匹配供应商、生成方案、记录埋点
- 供应商（外部）：被联系的一方（一期不做系统内闭环）
- 微信平台（外部）：登录 code、用户标识

---

## 2. 领域命令（Commands）

> 命令是“用户/系统想要发生什么”。

- `LoginWithWeChat(code)`
- `CreatePlanRequest(input)`（提交需求，触发生成）
- `GeneratePlans(planRequestId)`（系统编排，产出 3 套方案）
- `SelectPlan(planId)`（在对比页选择进入详情）
- `ConfirmPlan(planId)`（确认方案）
- `ViewPlan(planId)`（查看详情）
- `ListPlans(userId, filters)`（我的方案列表）
- `ContactSupplier(planId, supplierId, channel)`（记录联系行为）
- `SharePlan(planId, channel)`（分享行为，一期可选）

---

## 3. 领域事件（Domain Events）

> 事件是“已经发生了什么”。一期建议至少把事件做成埋点/审计日志（哪怕不做 MQ）。

### 账号与会话
- `WeChatLoginSucceeded(userId, sessionId)`
- `WeChatLoginFailed(reason)`

### 方案生成闭环
- `PlanRequestCreated(planRequestId, userId)`
- `PlanGenerationStarted(planRequestId)`
- `PlanGenerated(planId, planType, userId)`
- `PlanGenerationFailed(planRequestId, errorCode)`

### 方案使用闭环
- `PlanViewed(planId, userId)`
- `PlanCompared(planIds[], userId)`
- `PlanConfirmed(planId, userId)`
- `SupplierContacted(planId, supplierId, channel, userId)`
- `PlanShared(planId, channel, userId)`（可选）

---

## 4. 业务策略/规则（Policies）

- **生成策略**：一次需求必须生成 3 套（budget/standard/premium）；若供应商不足，则降级为模板生成并提示“可用供应商不足”。
- **状态机**：`draft` → `confirmed`（允许）；`confirmed` → `draft`（一期不允许回退；二期如需提供“取消确认”再加）。
- **数据快照**：方案中供应商信息以“快照”存储，避免后续供应商数据变更导致历史方案不可复现。
- **幂等**：`CreatePlanRequest` 必须可防重复提交（同一 session 在短时间重复点击，服务端去重）。

---

## 5. 读模型（Read Models / Queries）

> 为避免“写模型被查询拖垮”，建议一期就明确读模型，哪怕实现上先复用同表。

- “我的方案列表”：按 `create_time` 倒序分页（卡片字段：方案名、人均、天数、状态、创建时间）
- “方案详情”：行程、预算明细、供应商快照、确认状态
- “供应商搜索（只读）”：按城市、品类、价格区间、评分排序（一期可静态/后台录入）

---

## 6. 聚合（Aggregates）与一致性边界（Tactical）

### 聚合A：`Plan`（聚合根）
- 标识：`plan_id`
- 关键属性：`user_id`、`plan_type`、`status`、`inputs_snapshot`、`itinerary`、`budget_breakdown`、`supplier_snapshots[]`
- 不变式（Invariants）：
  - `plan_type` 必须属于 `{budget, standard, premium}`
  - `status=confirmed` 时必须有 `confirmed_time`
  - `supplier_snapshots` 至少 1 个（否则标记为“资源不足降级方案”）

### 聚合B：`PlanRequest`（聚合根，生成编排输入）
- 标识：`plan_request_id`
- 关键属性：`user_id`、`people_count`、`budget_range`、`date_range`、`departure_city`（出发城市）、`destination`（目的地）、`preferences`
- 不变式：输入校验（人数/预算/日期）通过才可进入生成

### 聚合C：`Supplier`（聚合根，一期只读）
- 标识：`supplier_id`
- 属性：名称、品类、城市、价格区间、评分、联系方式、标签

### 聚合D：`SupplierContactLog`（聚合根或事件流）
- 标识：`contact_id`
- 属性：`plan_id`、`supplier_id`、`channel`、`contact_time`、`user_id`

---

## 7. 一期限界上下文（Bounded Contexts）

> 一期建议最小拆分 3 个 BC；实现可先单体，但边界要在代码结构与接口上体现，便于教学。

### 7.1 BC-1: Identity & Session Context（身份与会话）

**职责**：微信登录、session 管理、用户标识映射（不管理复杂权限）

**聚合（Aggregates）**：
- `User`（聚合根）
  - 标识：`user_id`
  - 关键属性：`wechat_openid`、`nickname`、`avatar_url`、`role`、`status`
  - 不变式：`wechat_openid` 必须唯一；`role` 一期固定为 "HR"

- `Session`（逻辑聚合，实际存储在 Redis）
  - 标识：`session_token`（JWT）
  - 关键属性：`user_id`、`expires_at`
  - 不变式：过期后自动失效（24小时）

**命令（Commands）**：
- `LoginWithWeChat(code, nickname, avatarUrl)`：微信登录，创建或更新用户
- `RefreshSession(token)`：刷新会话（一期未实现）
- `Logout(token)`：主动登出（一期未实现）
- `UpdateUserProfile(userId, nickname, avatarUrl)`：更新用户信息

**领域事件（Domain Events）**：
- ⚠️ **一期未实现**：`WeChatLoginSucceeded`、`WeChatLoginFailed`、`SessionCreated`、`SessionExpired`
- 实现状态：登录成功/失败目前仅通过 HTTP 响应体现，未记录领域事件

**值对象（Value Objects）**：
- `SessionToken`：JWT 格式的会话令牌
- `OpenID`：微信 OpenID（一期使用 SHA-256 哈希模拟）

**对外接口**：
- `POST /api/v1/auth/wechat/login`：登录接口
- `Authorization: Bearer <token>`：认证头（所有受保护接口）

---

### 7.2 BC-2: Planning Context（方案规划）

**职责**：需求输入、生成编排、方案生命周期（draft/confirmed）、方案展示所需数据快照

**聚合（Aggregates）**：
- `PlanRequest`（聚合根）
  - 标识：`plan_request_id`
  - 关键属性：`user_id`、`people_count`、`budget_min`、`budget_max`、`start_date`、`end_date`、`departure_city`、`preferences_json`、`status`
  - 状态机：`GENERATING` → `COMPLETED` / `FAILED`
  - 不变式：`budget_max` >= `budget_min`；`end_date` >= `start_date`；`people_count` > 0

- `Plan`（聚合根）
  - 标识：`plan_id`
  - 关键属性：`plan_request_id`、`user_id`、`plan_type`（budget/standard/premium）、`status`、`plan_name`、`departure_city`（出发城市）、`destination`（目的地）、`itinerary_json`、`budget_breakdown_json`、`supplier_snapshots`
  - 状态机：`DRAFT`（默认） → `CONFIRMED`（不可回退）
  - 不变式：`plan_type` ∈ {budget, standard, premium}；`status=CONFIRMED` 时必须有 `confirmed_time`

- `SupplierContactLog`（聚合根）
  - 标识：`contact_id`
  - 关键属性：`plan_id`、`supplier_id`、`user_id`、`channel`（PHONE/WECHAT/EMAIL）、`notes`、`contact_time`
  - 不变式：`channel` 必须合法；`plan_id` 必须存在

**命令（Commands）**：
- `CreatePlanRequest(input)`：提交需求，触发生成（发送 MQ）
- `GeneratePlans(planRequestId)`：（AI 服务内部）编排生成 3 套方案
- `ListPlans(userId, page, pageSize)`：查询我的方案列表
- `GetPlanDetail(userId, planId)`：查看方案详情
- `ConfirmPlan(userId, planId)`：确认方案（幂等）
- `LogSupplierContact(userId, planId, supplierId, channel)`：记录联系供应商

**领域事件（Domain Events）**：
- ✅ **已实现**：
  - `PlanRequestCreated(plan_request_id, user_id)`：提交需求后立即记录
  - `PlanGenerated(plan_id, user_id)`：AI 回调生成方案后记录（每套方案独立事件）
  - `PlanConfirmed(plan_id, user_id)`：用户确认方案后记录
  - `SupplierContacted(plan_id, supplier_id, channel, user_id)`：联系供应商后记录

- ⚠️ **未实现**：`PlanGenerationStarted`、`PlanGenerationFailed`、`PlanViewed`、`PlanCompared`、`PlanShared`

**值对象（Value Objects）**：
- `BudgetRange(min, max)`：预算区间
- `DateRange(start, end)`：日期区间
- `Preferences(activityTypes[], accommodationLevel, diningStyle[], specialRequirements)`：偏好设置
- `Itinerary(days[])`：行程安排（JSON 结构）
- `BudgetBreakdown(categories[])`：预算明细（JSON 结构）
- `SupplierSnapshot[]`：供应商快照（避免外部数据变更影响历史方案）

**对外接口**：
- `POST /api/v1/plans/generate`：生成方案
- `GET /api/v1/plans?page=1&pageSize=10`：查询我的方案
- `GET /api/v1/plans/{planId}`：查看详情
- `POST /api/v1/plans/{planId}/confirm`：确认方案
- `POST /api/v1/plans/{planId}/contact-supplier`：记录联系供应商

---

### 7.3 BC-3: Supplier Catalog Context（供应商目录）

**职责**：供应商数据维护与查询（一期只读/后台录入），提供给 Planning 的匹配与展示

**聚合（Aggregates）**：
- `Supplier`（聚合根，一期只读）
  - 标识：`supplier_id`
  - 关键属性：`name`、`category`（accommodation/dining/activity/transportation）、`city`、`price_min`、`price_max`、`rating`、`contact_phone`、`contact_wechat`、`tags_json`、`coordinates`（经纬度）
  - 不变式：`price_max` >= `price_min`；`category` 必须合法；`rating` ∈ [0, 5]

**命令（Commands）**：
- `SearchSuppliers(city, category, priceRange, sortBy)`：搜索供应商（支持筛选与排序）
- `GetSupplierDetail(supplierId)`：查看供应商详情
- ⚠️ **未实现**：`CreateSupplier`、`UpdateSupplier`（一期后台录入，无 API）

**领域事件（Domain Events）**：
- ⚠️ **一期无事件**：供应商数据变更不记录领域事件（只读场景）

**值对象（Value Objects）**：
- `GeoLocation(lat, lng, address)`：地理位置
- `PriceRange(min, max)`：价格区间
- `ContactInfo(phone, wechat, email)`：联系方式

**对外接口**：
- `GET /api/v1/suppliers?city=Beijing&category=accommodation`：搜索供应商
- `GET /api/v1/suppliers/{supplierId}`：查看供应商详情

---

### 7.4 横切关注点：Analytics & Tracking（分析与追踪）

**职责**：统一记录领域事件用于埋点分析、业务报表、审计日志

**实现方式**：
- 通过 `domain_events` 表集中存储所有领域事件
- 事件字段：`event_id`、`event_type`、`aggregate_type`、`aggregate_id`、`user_id`、`payload`（JSON）、`occurred_at`、`processed`（是否已消费）

**事件消费场景**（二期扩展）：
- 北极星指标计算：统计 `PlanConfirmed` 事件的周度数量
- 转化漏斗分析：`PlanConfirmed` → `SupplierContacted` 转化率
- 慢查询监控：分析 `PlanGenerationStarted` 到 `PlanGenerated` 的耗时分布

---

## 8. 上下文关系（Context Map）

```
┌──────────────────────┐
│  Identity & Session  │
│  （身份与会话）       │
└──────────┬───────────┘
           │ provides userId
           ▼
┌──────────────────────┐       ┌──────────────────────┐
│      Planning        │──────▶│  Supplier Catalog    │
│     （方案规划）      │ query │   （供应商目录）      │
└──────────┬───────────┘       └──────────────────────┘
           │ emits events
           ▼
┌──────────────────────┐
│  Analytics/Tracking  │
│   （横切关注点）      │
└──────────────────────┘
```

**关系说明**：
- **Planning → Identity（认证依赖 / ACL）**：Planning 必须通过 `userId` 确认身份，所有方案操作需鉴权
- **Planning → Supplier Catalog（查询依赖 / Customer-Supplier）**：Planning 读取供应商目录用于匹配与快照存储
- **Planning → Analytics（事件发布 / Open-Host Service）**：Planning 发布领域事件到 `domain_events` 表，供后续分析消费

---

## 9. 领域事件详细清单（实际实现版本）

> 基于 `DomainEventPO` 与实际业务代码的事件记录逻辑整理。

| 事件类型 | 聚合根 | 触发时机 | Payload 字段 | 后续动作 | 实现状态 |
|---------|--------|---------|-------------|---------|---------|
| `PlanRequestCreated` | PlanRequest | 用户提交生成需求后 | `{plan_request_id}` | 1. 写入 `domain_events` 表<br>2. 发送 RabbitMQ 消息到 AI 服务 | ✅ 已实现 |
| `PlanGenerated` | Plan | AI 服务回调生成单套方案后 | `{plan_id}` | 1. 写入 `domain_events` 表<br>2. 小程序可刷新对比页 | ✅ 已实现 |
| `PlanConfirmed` | Plan | 用户点击"确认此方案"后 | `{plan_id}` | 1. 写入 `domain_events` 表<br>2. 纳入北极星指标统计 | ✅ 已实现 |
| `SupplierContacted` | SupplierContactLog | 用户联系供应商后 | `{plan_id, supplier_id, channel}` | 1. 写入 `domain_events` 表<br>2. 转化漏斗分析数据源 | ✅ 已实现 |
| `WeChatLoginSucceeded` | User | 微信登录成功后 | `{user_id, openid}` | - | ⚠️ 未实现 |
| `PlanGenerationStarted` | PlanRequest | MQ 消息发送成功后 | `{plan_request_id}` | - | ⚠️ 未实现 |
| `PlanGenerationFailed` | PlanRequest | AI 服务生成失败后 | `{plan_request_id, error_code}` | - | ⚠️ 未实现 |
| `PlanViewed` | Plan | 用户打开方案详情页 | `{plan_id}` | - | ⚠️ 未实现 |

### 9.1 事件 Payload 结构示例

**PlanRequestCreated**
```json
{
  "plan_request_id": "plan_req_01JHTXXXXXXX"
}
```

**PlanGenerated**
```json
{
  "plan_id": "plan_01JHTXXXXXXX"
}
```

**PlanConfirmed**
```json
{
  "plan_id": "plan_01JHTXXXXXXX"
}
```

**SupplierContacted**
```json
{
  "plan_id": "plan_01JHTXXXXXXX",
  "supplier_id": "supp_01JHTXXXXXXX",
  "channel": "PHONE"
}
```

### 9.2 事件消费模式（一期 vs 二期）

**一期（当前实现）**：
- 所有事件落库到 `domain_events` 表
- `processed` 字段预留（默认 `false`），暂未实现消费逻辑
- 事件主要用于审计日志与手动数据分析

**二期（演进方向）**：
- 引入 EventBus 或 Kafka 实现异步消费
- 北极星指标实时计算（Flink / ClickHouse）
- 事件溯源（Event Sourcing）重建聚合状态

---

## 10. 业务流程泳道图（Swimlane Diagrams）

### 10.1 方案生成完整流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        方案生成端到端流程（含事件）                        │
└─────────────────────────────────────────────────────────────────────────┘

小程序                Java 业务服务          RabbitMQ         Python AI 服务
  │                        │                     │                  │
  │  POST /plans/generate  │                     │                  │
  ├───────────────────────▶│                     │                  │
  │                        │ 1. Insert PlanRequest (GENERATING)     │
  │                        │    生成 plan_request_id                 │
  │                        │                     │                  │
  │                        │ 2. Record Event:    │                  │
  │                        │    PlanRequestCreated                  │
  │                        │                     │                  │
  │                        │ 3. Publish MQ       │                  │
  │                        ├────────────────────▶│                  │
  │◀───────────────────────┤ 4. Return           │                  │
  │  {plan_request_id,     │    {plan_request_id,│                  │
  │   status: "generating"}│     status}         │                  │
  │                        │                     │                  │
  │                        │                     │  Consume MQ      │
  │                        │                     ├─────────────────▶│
  │                        │                     │                  │ 5. LangGraph Workflow
  │                        │                     │                  │    - parse_requirements
  │                        │                     │                  │    - match_suppliers
  │                        │                     │                  │    - generate_three_plans
  │                        │                     │                  │
  │                        │  6. POST /internal/plans/batch        │
  │                        │◀──────────────────────────────────────┤
  │                        │  {plan_request_id,                     │
  │                        │   plans: [3套方案]}                    │
  │                        │                     │                  │
  │                        │ 7. Insert 3 Plans   │                  │
  │                        │ 8. Record Event:    │                  │
  │                        │    PlanGenerated x3 │                  │
  │                        │ 9. Update PlanRequest                  │
  │                        │    status=COMPLETED │                  │
  │                        ├────────────────────▶│                  │
  │                        │  Return 200 OK      │                  │
  │                        │                     │                  │
  │  10. 轮询/刷新对比页    │                     │                  │
  ├───────────────────────▶│                     │                  │
  │  GET /plans?           │                     │                  │
  │   plan_request_id=xxx  │                     │                  │
  │◀───────────────────────┤                     │                  │
  │  返回 3 套方案         │                     │                  │
```

**关键点**：
- 步骤 2：`PlanRequestCreated` 事件记录到 `domain_events` 表
- 步骤 3：异步解耦，Java 服务立即返回
- 步骤 8：每套方案独立记录 `PlanGenerated` 事件（共 3 个事件）
- 步骤 10：前端轮询或主动刷新获取生成结果

---

### 10.2 确认方案与联系供应商流程

```
小程序                Java 业务服务          domain_events 表
  │                        │                     │
  │  POST /plans/{id}/confirm                   │
  ├───────────────────────▶│                     │
  │                        │ 1. Check ownership  │
  │                        │    (userId 校验)     │
  │                        │ 2. Idempotency:     │
  │                        │    if status=CONFIRMED, return OK
  │                        │ 3. Update status    │
  │                        │    = CONFIRMED      │
  │                        │ 4. Record Event:    │
  │                        │    PlanConfirmed    │
  │                        ├────────────────────▶│
  │◀───────────────────────┤                     │
  │  200 OK                │                     │
  │                        │                     │
  │  用户点击"联系供应商"   │                     │
  │  POST /plans/{planId}/contact-supplier       │
  ├───────────────────────▶│                     │
  │  {supplier_id,         │                     │
  │   channel: "PHONE"}    │                     │
  │                        │ 5. Insert           │
  │                        │    SupplierContactLog
  │                        │ 6. Record Event:    │
  │                        │    SupplierContacted│
  │                        ├────────────────────▶│
  │◀───────────────────────┤                     │
  │  200 OK                │                     │
```

**关键点**：
- 幂等性：重复确认同一方案不会报错，直接返回成功
- 事件解耦：`PlanConfirmed` 和 `SupplierContacted` 事件为后续分析提供数据源
- 北极星指标：可通过统计 `PlanConfirmed` 事件的周度数量计算

