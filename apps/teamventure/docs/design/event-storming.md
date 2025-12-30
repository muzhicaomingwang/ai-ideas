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
| **行程** | Itinerary | 按天拆分的活动安排与时间表 | Day1: 09:00 出发 → 12:00 午餐... | 以"天"为单位组织 |
| **预算明细** | Budget Breakdown | 按类目拆分的费用构成 | 交通¥5000、住宿¥15000... | 分类：交通/住宿/餐饮/活动/其他 |
| **数据快照** | Snapshot | 方案生成时对外部数据（如供应商信息）的副本存储 | 供应商当时的价格、联系方式 | 避免历史方案因外部数据变更失效 |

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
| 方案类型（经济/平衡/品质） | PlanType | `plan_type` | `plan_type: budget/standard/premium` | "经济型"/"平衡型"/"品质型" |
| 确认方案 | ConfirmPlan | `status='confirmed'` | `POST /plans/{id}/confirm` | "确认此方案" |
| 供应商快照 | SupplierSnapshot | `supplier_snapshots` (JSONB) | `suppliers[]` | "供应商信息" |
| 生成时间 | GenerationDuration | `generation_time_ms` | `generation_time_ms` | "已为您生成方案（耗时 45 秒）" |

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
- 关键属性：`user_id`、`people_count`、`budget_range`、`date_range`、`departure_location`、`preferences`
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

1) **Identity & Session Context（身份与会话）**
- 职责：微信登录、session 管理、用户标识映射（不管理复杂权限）

2) **Planning Context（方案规划）**
- 职责：需求输入、生成编排、方案生命周期（draft/confirmed）、方案展示所需数据快照

3) **Supplier Catalog Context（供应商目录）**
- 职责：供应商数据维护与查询（一期可只读/后台录入），提供给 Planning 的匹配与展示

> Analytics/Tracking 属于横切能力：一期先作为“埋点事件规范 + 服务端日志”，二期可独立成 BC。

---

## 8. 上下文关系（Context Map）

- Planning → Supplier Catalog：**查询依赖**（Planning 读取供应商目录用于匹配与展示）
- Planning → Identity：**认证依赖**（必须拿到 userId 才能生成/保存方案）
- Planning → Analytics（横切）：记录关键事件与指标

