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

## 1. 参与者（Actors）

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

