# TeamVenture 领域统一语言词汇表 (Ubiquitous Language Glossary)

**创建日期**: 2026-01-06
**版本**: v1.3
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
| 头像占位符 | Avatar Placeholder | - | - | - | `avatarPlaceholder` | 未上传头像时显示emoji 👤 |
| 会话令牌 | Session Token | `session_token` | `sessionToken` | `sessionToken` | `token` | JWT格式 |
| 登录状态 | Login Status | - | - | - | `isLogin` | Boolean，全局状态 |
| 用户信息 | User Info | - | `UserInfo` | `userInfo` | `userInfo` | 聚合对象（userId+nickname+avatar等） |

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
| **目的地城市** | **Destination City** | `destination_city` | `destinationCity` | `destination_city` | - | 目的地所属行政城市（用于季节/价格配置） |
| 偏好设置 | Preferences | `preferences` | `preferencesJson` | `preferences` | `preferences` | JSON对象 |
| 请求状态 | Status | `status` | `status` | `status` | `status` | CREATING/GENERATING/COMPLETED/FAILED |

#### 2.2.1 偏好设置字段 (Preferences)

| 中文术语 | API字段（统一） | 常见误用/旧字段 | 说明 |
|---------|----------------|----------------|------|
| 活动类型 | `activity_types` | `activityTypes` | 数组，多选 |
| 住宿标准 | `accommodation_level` | `accommodation` | 单选：budget/standard/premium |
| 特殊需求 | `special_requirements` | - | 字符串（可为空） |

### 2.3 方案 (Plan)

| 中文术语 | 英文术语 | 数据库字段 | Java字段 | API字段 | 前端字段 | 说明 |
|---------|---------|-----------|----------|--------|---------|------|
| 方案ID | Plan ID | `plan_id` | `planId` | `plan_id` | `planId` | 前缀 `plan_` |
| **方案名称** | **Plan Name** | `plan_name` | `planName` | `plan_name` | `planName` | ✅ 统一使用 plan_name |
| 方案类型 | Plan Type | `plan_type` | `planType` | `plan_type` | `planType` | budget/standard/premium |
| 方案摘要 | Summary | `summary` | `summary` | `summary` | `summary` | |
| 亮点 | Highlights | `highlights` | `highlights` | `highlights` | `highlights` | JSON数组 |
| 行程安排 | Itinerary | `itinerary` | `itinerary` | `itinerary` | `itinerary` | JSON对象 |
| 预算明细（非MVP） | Budget Breakdown | `budget_breakdown` | `budgetBreakdown` | `budget_breakdown` | - | DB 保留字段，MVP 不对外输出 |
| **供应商快照（非MVP）** | **Supplier Snapshots** | `supplier_snapshots` | `supplierSnapshots` | `supplier_snapshots` | - | DB 保留字段，MVP 不对外输出 |
| 总预算 | Budget Total | `budget_total` | `budgetTotal` | `budget_total` | `budgetTotal` | 冗余字段 |
| 人均预算 | Budget Per Person | `budget_per_person` | `budgetPerPerson` | `budget_per_person` | `budgetPerPerson` | 冗余字段 |
| 天数 | Duration Days | `duration_days` | `durationDays` | `duration_days` | `durationDays` | |
| **出发城市** | **Departure City** | `departure_city` | `departureCity` | `departure_city` | `departureCity` | 从请求继承 |
| **目的地** | **Destination** | `destination` | `destination` | `destination` | `destination` | 从请求继承 |
| **目的地城市** | **Destination City** | `destination_city` | `destinationCity` | `destination_city` | - | 从请求继承/可由地图补全 |
| **评价数** | **Review Count** | `review_count` | `reviewCount` | `review_count` | - | 通晒后反馈收集 |
| **平均分** | **Average Score** | `average_score` | `averageScore` | `average_score` | - | 通晒后反馈收集（0-5，可为空） |
| 方案状态 | Status | `status` | `status` | `status` | `status` | draft/confirmed |
| 确认时间 | Confirmed Time | `confirmed_time` | `confirmedTime` | `confirmed_time` | `confirmedTime` | |
| 创建时间 | Created At | `create_time` | `createTime` | `created_at` | `created_at` | API 统一 `created_at`（前端列表使用） |

### 2.4 供应商 (Supplier, 非MVP)

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
| `destination` | 目的地 | 团建活动举办地点（可视为“目的地聚合”的展示名） | 千岛湖洲际酒店 | 行程安排、POI推荐 |
| `destination_city` | 目的地城市 | 目的地所属行政城市（季节/价格配置维度） | 杭州 | 季节配置、住宿/交通参考价 |

**前端显示格式**: `{departure_city} → {destination}`
**示例**: 上海市 → 杭州千岛湖

**前端字段映射**:
```javascript
// pages/index/index.js
formData.departureLocation  →  API: departure_city  // 出发城市
formData.destination        →  API: destination     // 目的地
```

### 3.2 方案类型 (Plan Type)

| 类型值 | 中文名 | 核心价值主张 | 定位说明 | 预算占比 |
|--------|--------|-------------|----------|----------|
| `budget` | 经济型 | 极致性价比，确保核心体验 | 最低预算方案，满足基本需求 | ≈ budget_min |
| `standard` | 平衡型 | 平衡之选，兼顾舒适与趣味 | 性价比方案，推荐选择 | ≈ (budget_min + budget_max) / 2 |
| `premium` | 品质型 | 尊享体验，打造团队高光时刻 | 最高预算方案，追求体验 | ≈ budget_max |

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
| `destination_city` | ✅ | 数据库/Java/Python/API 全链路一致（可选字段） |
| `plan_name` | ✅ | 数据库/Java/Python/API 全链路一致（非 title） |
| `supplier_snapshots` | ✅ | DB/Java/Python 一致（MVP 不对外输出） |
| `budget_breakdown` | ✅ | DB/Java/Python 一致（MVP 不对外输出） |
| `review_count` | ✅ | DB/Java/API 一致（通晒反馈指标） |
| `average_score` | ✅ | DB/Java/API 一致（通晒反馈指标） |

### 4.2 ⚠️ 需注意的映射

| 前端字段 | API字段 | 说明 |
|----------|---------|------|
| `departureLocation` | `departure_city` | 前端变量名保留，UI文案统一为“出发城市” |
| `create_time` | `created_at` | DB字段为 `create_time`，API 列表统一输出 `created_at` |
| `accommodation` | `preferences.accommodation_level` | 旧字段名，需迁移/兼容 |

### 4.3 📋 跨团队术语映射

| 产品/业务术语 | 技术术语 | 数据库字段 | API字段 | 前端展示 |
|-------------|---------|-----------|---------|---------|
| 团建方案 | Plan | `plans` 表 | `plan` | "方案" |
| 方案类型（经济/平衡/品质） | PlanType | `plan_type` | `plan_type` | "经济型"/"平衡型"/"品质型" |
| **通晒方案** | **SubmitReview** | `status='reviewing'` | `PUT /plans/{id}/submit-review` | **"通晒此方案"** |
| 确认方案 | ConfirmPlan | `status='confirmed'` | `PUT /plans/{id}/confirm` | "确认此方案" |
| 供应商快照（非MVP） | SupplierSnapshot | `supplier_snapshots` | `supplier_snapshots` | - |
| 生成时间 | GenerationDuration | `generation_time_ms` | `generation_time_ms` | "已为您生成方案（耗时45秒）" |
| 出发城市 | DepartureCity | `departure_city` | `departure_city` | "出发城市" |
| 目的地 | Destination | `destination` | `destination` | "目的地" |
| 目的地城市 | DestinationCity | `destination_city` | `destination_city` | - |

---

## 4.4 UI组件与交互术语

| 中文术语 | 英文术语 | 组件名 | 事件处理 | 说明 |
|---------|---------|--------|----------|------|
| 自定义导航栏 | Custom Navigation Bar | `custom-navbar` | - | 替代系统默认导航栏，支持自定义右侧内容 |
| 状态栏占位 | Status Bar Placeholder | `status-bar` | - | 适配不同机型的状态栏高度 |
| 用户状态显示 | User Status Display | `navbar-user` | `handleUserAvatar` | 导航栏右上角显示登录状态 |
| 用户信息胶囊 | User Info Capsule | `user-info-mini` | - | 已登录时显示头像+昵称的胶囊组件 |
| 登录入口按钮 | Login Entry Button | `login-btn-mini` | - | 未登录时显示的"登录"按钮 |
| 切换账号 | Switch Account | `relogin-entry` | `handleReLogin` | 登录页清除当前登录状态的入口 |
| 继续使用 | Continue | `btn-continue` | `handleContinue` | 已登录时验证token后进入主功能 |
| Token刷新 | Token Refresh | - | `refreshTokenIfNeeded` | 自动检测token即将过期并刷新 |

---

## 5. 领域事件命名

| 事件类型 | 聚合根 | 触发时机 | Payload字段 |
|---------|--------|---------|-------------|
| `PlanRequestCreated` | PlanRequest | 用户提交生成需求后 | `{plan_request_id}` |
| `PlanGenerationRequested` | PlanRequest | 用户请求生成（更明确） | `{plan_request_id}` |
| `PlanGenerated` | Plan | AI服务回调生成方案后 | `{plan_id}` |
| `PlanGenerationSucceeded` | Plan | 生成成功（更明确） | `{plan_id}` |
| `PlanSubmittedForReview` | Plan | 用户通晒方案后 | `{plan_id}` |
| `PlanConfirmed` | Plan | 用户确认方案后 | `{plan_id}` |
| `PlanAdoptionConfirmed` | Plan | 用户采纳确认（更明确） | `{plan_id}` |
| `SupplierContacted`（非MVP） | SupplierContactLog | 用户联系供应商后 | `{plan_id, supplier_id, channel}` |

---

## 6. 反模式与禁用术语

| ❌ 禁用术语 | ✅ 应使用 | 原因 |
|-----------|---------|------|
| "订单" | Plan（方案） | 一期不涉及支付/履约 |
| "预订" | Confirm（确认） | 确认≠预订 |
| "出发地" | departure_city（出发城市） | 统一术语 |
| "title" | plan_name（方案名称） | 代码已统一使用 plan_name |
| "suppliers" (单数形式) | supplier_snapshots（供应商快照） | 非MVP：如保留该字段，也应强调是快照而非引用 |

---

## 7. 前端UI状态管理

### 7.1 全局状态 (app.globalData)

| 状态字段 | 类型 | 初始值 | 说明 |
|---------|------|--------|------|
| `isLogin` | Boolean | `false` | 用户是否已登录 |
| `userInfo` | Object/null | `null` | 用户信息（userId, nickname, avatar等） |
| `isGuestMode` | Boolean | `false` | 是否游客模式 |

### 7.2 本地存储 (Storage Keys)

| 存储键 | 值类型 | 说明 |
|--------|--------|------|
| `STORAGE_KEYS.SESSION_TOKEN` | String | JWT会话令牌 |
| `STORAGE_KEYS.USER_INFO` | Object | 用户信息JSON |

### 7.3 页面导航与路由

| 页面路径 | 页面名称 | 导航栏类型 | 说明 |
|---------|---------|-----------|------|
| `/pages/login/login` | 登录页 | 系统默认 | 微信登录入口 |
| `/pages/home/home` | 首页 | 自定义 | 发现页，显示热门目的地和推荐方案 |
| `/pages/index/index` | 生成方案页 | 系统默认 | AI方案生成主流程 |
| `/pages/myplans/myplans` | 我的方案 | 系统默认 | 历史方案列表 |

---

## 8. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-01-06 | 初始版本，整合全链路字段定义 |
| v1.1 | 2026-01-07 | 补充"通晒"工作流：Section 4.3 添加"通晒方案"术语映射，Section 5 添加 `PlanSubmittedForReview` 领域事件 |
| v1.2 | 2026-01-08 | 补充UI组件术语：添加Section 4.4（自定义导航栏、用户状态显示等），添加Section 7（前端状态管理、路由） |
| v1.3 | 2026-01-09 | 强化出发城市/目的地/目的地城市区分；补充通晒反馈指标；补充更明确的领域事件命名；PlanType补充价值主张 |
