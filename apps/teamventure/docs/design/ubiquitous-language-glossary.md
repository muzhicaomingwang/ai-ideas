# TeamVenture 领域统一语言词汇表 (Ubiquitous Language Glossary)

**创建日期**: 2026-01-06
**版本**: v1.0
**目的**: 确保全链路字段命名一致性，消除"翻译损耗"

---

## 1. 核心原则

> DDD 核心原则：团队使用统一的术语，从业务讨论、代码命名到文档表述保持一致，避免"翻译损耗"。

**命名规范**:
- **数据库字段**: `snake_case` (例: `departure_city`)
- **Java 字段**: `snake_case` (与数据库保持一致，MyBatis-Plus 自动映射)
- **API 字段**: `snake_case` (例: `departure_city`)
- **前端 JS 变量**: `camelCase` (例: `departureLocation`)，需显式注释映射关系

---

## 2. 核心实体字段定义

### 2.1 用户与会话 (Identity Domain)

| 中文术语 | 英文术语 | 数据库字段 | Java字段 | API字段 | 前端字段 | 说明 |
|---------|---------|-----------|----------|--------|---------|------|
| 用户ID | User ID | `user_id` | `userId` | `user_id` | `userId` | 前缀 `user_`，ULID格式 |
| 微信OpenID | WeChat OpenID | `wechat_openid` | `wechatOpenid` | `openid` | - | 不暴露给前端 |
| 昵称 | Nickname | `nickname` | `nickname` | `nickname` | `nickname` | |
| 头像URL | Avatar URL | `avatar_url` | `avatarUrl` | `avatar` | `avatarUrl` | API简化为avatar |
| 会话令牌 | Session Token | `session_token` | `sessionToken` | `sessionToken` | `token` | JWT格式 |

### 2.2 方案请求 (Plan Request)

| 中文术语 | 英文术语 | 数据库字段 | Java字段 | API字段 | 前端字段 | 说明 |
|---------|---------|-----------|----------|--------|---------|------|
| 方案请求ID | Plan Request ID | `plan_request_id` | `planRequestId` | `plan_request_id` | `planRequestId` | 前缀 `plan_req_` |
| 参与人数 | People Count | `people_count` | `peopleCount` | `people_count` | `peopleCount` | 正整数 |
| 最低预算 | Budget Min | `budget_min` | `budgetMin` | `budget_min` | `budgetMin` | 单位：元 |
| 最高预算 | Budget Max | `budget_max` | `budgetMax` | `budget_max` | `budgetMax` | 单位：元 |
| 开始日期 | Start Date | `start_date` | `startDate` | `start_date` | `startDate` | YYYY-MM-DD |
| 结束日期 | End Date | `end_date` | `endDate` | `end_date` | `endDate` | YYYY-MM-DD |
| **出发城市** | **Departure City** | `departure_city` | `departureCity` | `departure_city` | `departureLocation` | ⚠️ 前端字段名不同，需映射 |
| **目的地** | **Destination** | `destination` | `destination` | `destination` | `destination` | 团建活动举办地点 |
| 偏好设置 | Preferences | `preferences` | `preferencesJson` | `preferences` | `preferences` | JSON对象 |
| 请求状态 | Status | `status` | `status` | `status` | `status` | CREATING/GENERATING/COMPLETED/FAILED |

### 2.3 方案 (Plan)

| 中文术语 | 英文术语 | 数据库字段 | Java字段 | API字段 | 前端字段 | 说明 |
|---------|---------|-----------|----------|--------|---------|------|
| 方案ID | Plan ID | `plan_id` | `planId` | `plan_id` | `planId` | 前缀 `plan_` |
| **方案名称** | **Plan Name** | `plan_name` | `planName` | `plan_name` | `planName` | ✅ 统一使用 plan_name |
| 方案类型 | Plan Type | `plan_type` | `planType` | `plan_type` | `planType` | budget/standard/premium |
| 方案摘要 | Summary | `summary` | `summary` | `summary` | `summary` | |
| 亮点 | Highlights | `highlights` | `highlights` | `highlights` | `highlights` | JSON数组 |
| 行程安排 | Itinerary | `itinerary` | `itinerary` | `itinerary` | `itinerary` | JSON对象 |
| 预算明细 | Budget Breakdown | `budget_breakdown` | `budgetBreakdown` | `budget_breakdown` | `budgetBreakdown` | JSON对象 |
| **供应商快照** | **Supplier Snapshots** | `supplier_snapshots` | `supplierSnapshots` | `supplier_snapshots` | `supplierSnapshots` | ✅ 统一使用复数形式 |
| 总预算 | Budget Total | `budget_total` | `budgetTotal` | `budget_total` | `budgetTotal` | 冗余字段 |
| 人均预算 | Budget Per Person | `budget_per_person` | `budgetPerPerson` | `budget_per_person` | `budgetPerPerson` | 冗余字段 |
| 天数 | Duration Days | `duration_days` | `durationDays` | `duration_days` | `durationDays` | |
| **出发城市** | **Departure City** | `departure_city` | `departureCity` | `departure_city` | `departureCity` | 从请求继承 |
| **目的地** | **Destination** | `destination` | `destination` | `destination` | `destination` | 从请求继承 |
| 方案状态 | Status | `status` | `status` | `status` | `status` | draft/confirmed |
| 确认时间 | Confirmed Time | `confirmed_time` | `confirmedTime` | `confirmed_time` | `confirmedTime` | |

### 2.4 供应商 (Supplier)

| 中文术语 | 英文术语 | 数据库字段 | Java字段 | API字段 | 前端字段 | 说明 |
|---------|---------|-----------|----------|--------|---------|------|
| 供应商ID | Supplier ID | `supplier_id` | `supplierId` | `supplier_id` | `supplierId` | 前缀 `sup_` |
| 供应商名称 | Name | `name` | `name` | `name` | `name` | |
| 品类 | Category | `category` | `category` | `category` | `category` | accommodation/dining/activity/transportation |
| 城市 | City | `city` | `city` | `city` | `city` | |
| 联系电话 | Contact Phone | `contact_phone` | `contactPhone` | `contact_phone` | `contactPhone` | |
| 联系微信 | Contact WeChat | `contact_wechat` | `contactWechat` | `contact_wechat` | `contactWechat` | |
| 价格区间(低) | Price Min | `price_min` | `priceMin` | `price_min` | `priceMin` | |
| 价格区间(高) | Price Max | `price_max` | `priceMax` | `price_max` | `priceMax` | |
| 评分 | Rating | `rating` | `rating` | `rating` | `rating` | 0-5 |

---

## 3. 关键字段语义详解

### 3.1 出发城市与目的地

| 字段 | 中文名 | 语义说明 | 示例值 | 使用场景 |
|------|--------|----------|--------|----------|
| `departure_city` | 出发城市 | 团队从哪里出发，通常是公司所在城市 | 上海市 | 行程规划起点、交通费用计算 |
| `destination` | 目的地 | 团建活动举办地点，团队前往的地方 | 杭州千岛湖 | 活动安排、供应商匹配、住宿费用计算 |

**前端显示格式**: `{departure_city} → {destination}`
**示例**: 上海市 → 杭州千岛湖

**前端字段映射**:
```javascript
// pages/index/index.js
formData.departureLocation  →  API: departure_city  // 出发城市
formData.destination        →  API: destination     // 目的地
```

### 3.2 方案类型 (Plan Type)

| 类型值 | 中文名 | 定位说明 | 预算占比 |
|--------|--------|----------|----------|
| `budget` | 经济型 | 最低预算方案，满足基本需求 | ≈ budget_min |
| `standard` | 平衡型 | 性价比方案，推荐选择 | ≈ (budget_min + budget_max) / 2 |
| `premium` | 品质型 | 最高预算方案，追求体验 | ≈ budget_max |

### 3.3 方案状态 (Plan Status)

| 状态值 | 中文名 | 说明 | 后续动作 |
|--------|--------|------|----------|
| `generating` | 生成中 | AI正在生成方案 | 等待完成 |
| `failed` | 生成失败 | AI生成过程出错 | 重新生成 |
| `draft` | 制定完成 | 方案已生成，待用户通晒 | 可通晒、可删除 |
| `reviewing` | 通晒中 | 方案已提交通晒，团队审阅中 | 可确认、可撤回 |
| `confirmed` | 已确认 | 用户已采纳此方案 | 纳入北极星指标、可归档 |
| `archived` | 已归档 | 方案已归档，不再展示 | 可恢复 |

**状态流转图**:
```
generating → failed (生成出错)
generating → draft (生成完成)
draft → reviewing (通晒此方案)
reviewing → draft (撤回通晒)
reviewing → confirmed (确认此方案)
confirmed → archived (归档)
```

### 3.4 请求状态 (Request Status)

| 状态值 | 中文名 | 说明 |
|--------|--------|------|
| `CREATING` | 创建中 | 请求刚创建 |
| `GENERATING` | 生成中 | AI正在生成方案 |
| `COMPLETED` | 已完成 | 3套方案已生成 |
| `FAILED` | 失败 | 生成过程出错 |

---

## 4. 命名一致性检查清单

### 4.1 ✅ 已统一的字段

| 字段 | 状态 | 说明 |
|------|------|------|
| `departure_city` | ✅ | 数据库/Java/Python/API 全链路一致 |
| `destination` | ✅ | 数据库/Java/Python/API 全链路一致 |
| `plan_name` | ✅ | 数据库/Java/Python/API 全链路一致（非 title） |
| `supplier_snapshots` | ✅ | 数据库/Java/Python/API 全链路一致 |
| `budget_breakdown` | ✅ | 数据库/Java/Python/API 全链路一致 |

### 4.2 ⚠️ 需注意的映射

| 前端字段 | API字段 | 说明 |
|----------|---------|------|
| `departureLocation` | `departure_city` | 前端使用更通用的"出发地点"，API使用精确的"出发城市" |

### 4.3 📋 跨团队术语映射

| 产品/业务术语 | 技术术语 | 数据库字段 | API字段 | 前端展示 |
|-------------|---------|-----------|---------|---------|
| 团建方案 | Plan | `plans` 表 | `plan` | "方案" |
| 方案类型（经济/平衡/品质） | PlanType | `plan_type` | `plan_type` | "经济型"/"平衡型"/"品质型" |
| **通晒方案** | **SubmitReview** | `status='reviewing'` | `PUT /plans/{id}/submit-review` | **"通晒此方案"** |
| 确认方案 | ConfirmPlan | `status='confirmed'` | `PUT /plans/{id}/confirm` | "确认此方案" |
| 供应商快照 | SupplierSnapshot | `supplier_snapshots` | `supplier_snapshots` | "供应商信息" |
| 生成时间 | GenerationDuration | `generation_time_ms` | `generation_time_ms` | "已为您生成方案（耗时45秒）" |
| 出发城市 | DepartureCity | `departure_city` | `departure_city` | "出发地点" |
| 目的地 | Destination | `destination` | `destination` | "目的地" |

---

## 5. 领域事件命名

| 事件类型 | 聚合根 | 触发时机 | Payload字段 |
|---------|--------|---------|-------------|
| `PlanRequestCreated` | PlanRequest | 用户提交生成需求后 | `{plan_request_id}` |
| `PlanGenerated` | Plan | AI服务回调生成方案后 | `{plan_id}` |
| `PlanSubmittedForReview` | Plan | 用户通晒方案后 | `{plan_id}` |
| `PlanConfirmed` | Plan | 用户确认方案后 | `{plan_id}` |
| `SupplierContacted` | SupplierContactLog | 用户联系供应商后 | `{plan_id, supplier_id, channel}` |

---

## 6. 反模式与禁用术语

| ❌ 禁用术语 | ✅ 应使用 | 原因 |
|-----------|---------|------|
| "订单" | Plan（方案） | 一期不涉及支付/履约 |
| "预订" | Confirm（确认） | 确认≠预订 |
| "出发地" | departure_city（出发城市） | 统一术语 |
| "title" | plan_name（方案名称） | 代码已统一使用 plan_name |
| "suppliers" (单数形式) | supplier_snapshots（供应商快照） | 强调是快照而非引用 |

---

## 7. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-01-06 | 初始版本，整合全链路字段定义 |
| v1.1 | 2026-01-07 | 补充"通晒"工作流：Section 4.3 添加"通晒方案"术语映射，Section 5 添加 `PlanSubmittedForReview` 领域事件 |
