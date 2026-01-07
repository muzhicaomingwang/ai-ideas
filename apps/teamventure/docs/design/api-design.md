# TeamVenture API 设计文档

**版本**: v1.5（Phase 1 - 小程序端）
**创建日期**: 2026-01-04
**更新日期**: 2026-01-06
**变更记录**:
- v1.5 (2026-01-06): 查询方案列表API新增status筛选参数，支持Tab状态过滤
- v1.4 (2026-01-06): 明确字段语义 - departure_city(出发城市)与destination(目的地)
- v1.3 (2026-01-06): 新增方案删除API(3.6)、归档API(3.7)
- v1.2 (2026-01-05): 添加出发地/目的地字段
- v1.0 (2026-01-04): 初始版本
**目标**: 为 Python(FastAPI) 与 Java(Spring Boot) 两种实现提供统一契约（Contract-First）
**ID约定**: 使用ULID（前缀 + 26位字符），例如 `user_01ke3abc123`、`plan_req_01ke3...`、`plan_01ke3...`

---

## 目录

1. [通用约定](#1-通用约定)
2. [认证流程](#2-认证流程)
3. [Planning API（方案管理）](#3-planning-api方案管理)
4. [Supplier API（供应商）](#4-supplier-api供应商)
5. [错误码清单](#5-错误码清单)
6. [分页约定](#6-分页约定)

---

## 1. 通用约定

### 1.1 统一响应格式

**成功响应**:
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

**错误响应**:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "budget_min 不能大于 budget_max"
  }
}
```

### 1.2 HTTP 状态码约定

| HTTP状态码 | 含义 | 示例场景 |
|----------|------|---------|
| 200 | 成功 | 所有成功的请求 |
| 400 | 参数错误 | 参数验证失败 |
| 401 | 未认证 | Token缺失或过期 |
| 403 | 无权限 | 跨用户访问 |
| 404 | 资源不存在 | 方案ID不存在 |
| 500 | 服务器错误 | 内部异常 |

### 1.3 请求头约定

**必需头**（除登录接口外）:
```
Authorization: Bearer <session_token>
Content-Type: application/json
```

**可选头**:
```
X-Request-ID: <client_generated_id>  # 请求追踪ID
```

### 1.4 字段命名约定

- **JSON字段**: 使用 `snake_case` (例如: `people_count`, `budget_min`)
- **URL路径**: 使用 `kebab-case` (例如: `/supplier-contacts`)
- **枚举值**: 使用 `UPPER_SNAKE_CASE` (例如: `CONFIRMED`, `PHONE`)

---

## 2. 认证流程

### 2.1 微信登录流程详解

**流程图**:
```
小程序                 后端                 微信服务器
  │                     │                      │
  │──wx.login()─────────┤                      │
  │                     │                      │
  │◄─code───────────────┤                      │
  │                     │                      │
  │──POST /auth/login───┤                      │
  │   {code}            │                      │
  │                     │──jscode2session──────┤
  │                     │   (code→openid)      │
  │                     │                      │
  │                     │◄─openid──────────────┤
  │                     │                      │
  │                     │──生成JWT Token────────┤
  │                     │  存储到Redis         │
  │                     │                      │
  │◄─sessionToken + ────┤                      │
  │   userInfo          │                      │
```

### 2.2 微信登录 API

#### Endpoint
```
POST /api/v1/auth/wechat/login
```

#### 请求参数

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| code | String | ✅ | 微信登录code（调用wx.login获取） |
| nickname | String | ❌ | 用户昵称（可选，新用户需提供） |
| avatarUrl | String | ❌ | 头像URL（可选） |

#### 请求示例

**curl命令**:
```bash
curl -X POST http://localhost/api/v1/auth/wechat/login \
  -H "Content-Type: application/json" \
  -d '{
    "code": "081vXS0w3qE5Rq2bCe2w3lv...",
    "nickname": "张三",
    "avatarUrl": "https://thirdwx.qlogo.cn/..."
  }'
```

**JSON请求**:
```json
{
  "code": "081vXS0w3qE5Rq2bCe2w3lv...",
  "nickname": "张三",
  "avatarUrl": "https://thirdwx.qlogo.cn/..."
}
```

#### 成功响应

**HTTP 200**:
```json
{
  "success": true,
  "data": {
    "sessionToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "userInfo": {
      "user_id": "user_01ke3abc123",
      "nickname": "张三",
      "avatar": "https://thirdwx.qlogo.cn/...",
      "phone": "",
      "company": "",
      "role": "user"
    }
  },
  "error": null
}
```

#### 错误响应

**HTTP 400 - 参数错误**:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "code 不能为空"
  }
}
```

**HTTP 401 - 微信验证失败**:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "UNAUTHENTICATED",
    "message": "微信登录code无效或已过期"
  }
}
```

---

## 3. Planning API（方案管理）

### 3.1 生成方案 API

#### Endpoint
```
POST /api/v1/plans/generate
```

#### 请求参数

| 字段 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| people_count | Integer | ✅ | 参与人数 | 50 |
| budget_min | Number | ✅ | 最低预算（元） | 10000 |
| budget_max | Number | ✅ | 最高预算（元） | 15000 |
| start_date | String | ✅ | 开始日期（YYYY-MM-DD） | "2026-02-01" |
| end_date | String | ✅ | 结束日期（YYYY-MM-DD） | "2026-02-03" |
| departure_city | String | ✅ | 出发城市（团队从哪里出发，如公司所在地） | "上海市" |
| destination | String | ❌ | 目的地（团建活动举办地点，可选，留空由AI推荐） | "杭州千岛湖" |
| preferences | Object | ❌ | 偏好设置（JSON对象） | 见下方 |

> **字段语义说明**：
> - `departure_city`：出发城市，表示团队从哪里出发，通常是公司所在地（如：上海市）
> - `destination`：目的地，表示团建活动举办地点（如：杭州千岛湖）
> - 前端显示格式："{departure_city} → {destination}"，例如：上海市 → 杭州千岛湖

**preferences对象结构**:
```json
{
  "activity_types": ["team_building", "leisure"],   // 活动类型（数组）
  "accommodation_level": "standard",                 // 住宿标准（single）
  "dining_style": ["bbq", "hotpot"],                // 餐饮偏好（数组）
  "special_requirements": "有老人，需要无障碍设施"    // 特殊需求（文本）
}
```

#### 请求示例

**curl命令**:
```bash
curl -X POST http://localhost/api/v1/plans/generate \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "people_count": 50,
    "budget_min": 10000,
    "budget_max": 15000,
    "start_date": "2026-02-01",
    "end_date": "2026-02-03",
    "departure_city": "上海市",
    "destination": "杭州千岛湖",
    "preferences": {
      "activity_types": ["team_building", "leisure"],
      "accommodation_level": "standard",
      "dining_style": ["bbq", "hotpot"],
      "special_requirements": "有老人，需要无障碍设施"
    }
  }'
```

**JSON请求**:
```json
{
  "people_count": 50,
  "budget_min": 10000,
  "budget_max": 15000,
  "start_date": "2026-02-01",
  "end_date": "2026-02-03",
  "departure_city": "上海市",
  "destination": "杭州千岛湖",
  "preferences": {
    "activity_types": ["team_building", "leisure"],
    "accommodation_level": "standard",
    "dining_style": ["bbq", "hotpot"],
    "special_requirements": "有老人，需要无障碍设施"
  }
}
```

#### 成功响应

**HTTP 200**:
```json
{
  "success": true,
  "data": {
    "plan_request_id": "plan_req_01ke3cnw4t5dvp8jhjvfdafq1v",
    "status": "generating"
  },
  "error": null
}
```

**说明**: 方案生成为异步操作，立即返回`plan_request_id`，实际生成由Python AI服务处理，完成后通过回调接口写入plans表。

#### 错误响应

**HTTP 400 - 参数验证失败**:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "budget_max 不能小于 budget_min"
  }
}
```

**HTTP 401 - Token无效**:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "UNAUTHENTICATED",
    "message": "登录已过期，请重新登录"
  }
}
```

### 3.2 查询方案列表 API

#### Endpoint
```
GET /api/v1/plans?page=1&pageSize=10&status=draft
```

#### 请求参数

| 字段 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | Integer | ❌ | 1 | 页码（从1开始） |
| pageSize | Integer | ❌ | 10 | 每页大小（最大100） |
| status | String | ❌ | - | 状态筛选：`draft`/`confirmed`/`generating`/`failed`，不传则返回全部 |

#### 状态值说明

| 状态值 | Tab展示名 | 说明 |
|--------|-----------|------|
| `draft` | 制定完成 | 方案已生成，待用户确认（默认Tab） |
| `confirmed` | 已确认 | 用户已采纳此方案 |
| `generating` | 生成中 | AI正在生成方案 |
| `failed` | - | 生成失败（混在"全部"中显示） |

#### 排序规则

- **有status参数**: 按 `create_time DESC` 排序
- **无status参数（全部）**: `confirmed` 置顶，然后按 `create_time DESC` 排序

#### 请求示例

**筛选"制定完成"的方案**:
```bash
curl -X GET "http://localhost/api/v1/plans?page=1&pageSize=10&status=draft" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**查询全部方案（已确认置顶）**:
```bash
curl -X GET "http://localhost/api/v1/plans?page=1&pageSize=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### 成功响应

**HTTP 200**:
```json
{
  "success": true,
  "data": {
    "records": [
      {
        "plan_id": "plan_01ke3d123",
        "plan_request_id": "plan_req_01ke3cnw",
        "plan_type": "standard",
        "plan_name": "千岛湖团建3日游方案A",
        "summary": "经典团建+休闲娱乐，性价比之选",
        "budget_total": 12000,
        "budget_per_person": 240,
        "duration_days": 3,
        "departure_city": "上海市",
        "destination": "杭州千岛湖",
        "status": "generated",
        "create_time": "2026-01-04T15:30:00",
        "confirmed_time": null
      }
    ],
    "total": 15,
    "size": 10,
    "current": 1,
    "pages": 2
  },
  "error": null
}
```

> **字段说明**：
> - `departure_city`：出发城市（团队从哪里出发）
> - `destination`：目的地（团建活动举办地点）
> - 前端显示格式：上海市 → 杭州千岛湖

**说明**: 使用MyBatis Plus分页对象，仅返回当前用户的方案。

### 3.3 查询方案详情 API

#### Endpoint
```
GET /api/v1/plans/{planId}
```

#### 请求参数

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| planId | String | ✅ | 方案ID（路径参数） |

#### 请求示例

**curl命令**:
```bash
curl -X GET "http://localhost/api/v1/plans/plan_01ke3d123" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### 成功响应

**HTTP 200**:
```json
{
  "success": true,
  "data": {
    "plan_id": "plan_01ke3d123",
    "plan_type": "standard",
    "plan_name": "北京团建3日游方案A",
    "summary": "经典团建+休闲娱乐，性价比之选",
    "highlights": [
      "怀柔拓展训练基地",
      "烧烤晚会",
      "慕田峪长城徒步"
    ],
    "itinerary": {
      "day1": {
        "date": "2026-02-01",
        "morning": "上午抵达酒店，团队破冰活动",
        "afternoon": "下午团建拓展训练",
        "evening": "晚上烧烤晚会"
      },
      "day2": {
        "date": "2026-02-02",
        "morning": "慕田峪长城徒步",
        "afternoon": "怀柔水库休闲",
        "evening": "篝火晚会"
      },
      "day3": {
        "date": "2026-02-03",
        "morning": "农家乐体验",
        "afternoon": "返程"
      }
    },
    "budget_breakdown": {
      "accommodation": 6000,
      "dining": 4500,
      "activities": 3000,
      "transportation": 2000,
      "other": 1500,
      "total": 17000
    },
    "supplier_snapshots": [
      {
        "supplier_id": "sup_hotel_001",
        "name": "北京怀柔会议酒店",
        "category": "accommodation",
        "contact": "010-12345678",
        "address": "北京市怀柔区雁栖镇",
        "price": 300,
        "unit": "间/晚"
      }
    ],
    "budget_total": 12000,
    "budget_per_person": 240,
    "duration_days": 3,
    "status": "generated",
    "create_time": "2026-01-04T15:30:00",
    "confirmed_time": null
  },
  "error": null
}
```

#### 错误响应

**HTTP 404 - 方案不存在**:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "NOT_FOUND",
    "message": "plan not found"
  }
}
```

**HTTP 403 - 无权访问**:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "not owner"
  }
}
```

### 3.4 确认方案 API（v1.4 更新）

#### Endpoint
```
POST /api/v1/plans/{planId}/confirm
```

#### 请求参数

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| planId | String | ✅ | 方案ID（路径参数） |

**说明**:
- 请求体为空，幂等操作（重复调用不报错）
- **状态约束**：只有 `reviewing`（通晒中）状态的方案才能确认

#### 请求示例

**curl命令**:
```bash
curl -X POST "http://localhost/api/v1/plans/plan_01ke3d123/confirm" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json"
```

#### 成功响应

**HTTP 200**:
```json
{
  "success": true,
  "data": null,
  "error": null
}
```

#### 错误响应

| 场景 | HTTP状态码 | 错误码 | 错误消息 |
|------|----------|--------|---------|
| 方案不存在 | 404 | NOT_FOUND | plan not found |
| 非本人方案 | 403 | UNAUTHORIZED | not owner |
| 方案已删除 | 404 | NOT_FOUND | plan not found |
| 状态不正确 | 400 | INVALID_STATUS | 只有通晒中状态的方案才能确认 |
| 未登录 | 401 | UNAUTHENTICATED | missing bearer token |

**说明**: 确认后会记录领域事件`PlanConfirmed`，用于北极星指标统计。

### 3.5 记录供应商联系 API

#### Endpoint
```
POST /api/v1/plans/{planId}/supplier-contacts
```

#### 请求参数

| 字段 | 类型 | 必需 | 说明 | 枚举值 |
|------|------|------|------|-------|
| supplier_id | String | ✅ | 供应商ID | - |
| channel | String | ✅ | 联系渠道 | `PHONE`, `WECHAT`, `EMAIL` |
| notes | String | ❌ | 备注信息 | - |

#### 请求示例

**curl命令**:
```bash
curl -X POST "http://localhost/api/v1/plans/plan_01ke3d123/supplier-contacts" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "supplier_id": "sup_hotel_001",
    "channel": "PHONE",
    "notes": "致电酒店预订部，确认50人会议室和住宿"
  }'
```

**JSON请求**:
```json
{
  "supplier_id": "sup_hotel_001",
  "channel": "PHONE",
  "notes": "致电酒店预订部，确认50人会议室和住宿"
}
```

#### 成功响应

**HTTP 200**:
```json
{
  "success": true,
  "data": null,
  "error": null
}
```

**说明**: 记录后会生成领域事件`SupplierContacted`，用于转化漏斗分析。

### 3.6 删除方案 API（v1.3 新增）

#### Endpoint
```
DELETE /api/v1/plans/{planId}
```

#### 功能说明

- 支持删除已生成的方案（plans 表）和生成中/失败的请求（plan_requests 表）
- 使用软删除机制，设置 `deleted_at` 时间戳
- 幂等设计：重复删除同一方案返回成功
- 权限验证：只能删除自己的方案

#### 请求示例

**curl命令**:
```bash
curl -X DELETE "http://localhost/api/v1/plans/plan_01ke3d123" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### 成功响应

**HTTP 200**:
```json
{
  "success": true,
  "data": null,
  "error": null
}
```

#### 错误响应

| 场景 | HTTP状态码 | 错误码 | 错误消息 |
|------|----------|--------|---------|
| 方案不存在 | 404 | NOT_FOUND | plan not found |
| 非本人方案 | 403 | UNAUTHORIZED | not owner |
| 未登录 | 401 | UNAUTHENTICATED | missing bearer token |

**说明**: 删除后会生成领域事件 `PlanDeleted` 或 `PlanRequestDeleted`。

### 3.7 归档方案 API（v1.3 新增，v1.4 更新）

#### Endpoint
```
POST /api/v1/plans/{planId}/archive
```

#### 功能说明

- **状态约束**：只有 `confirmed`（已确认）状态的方案才能归档
- 归档后状态变为 `archived`，使用 `archived_at` 时间戳标记归档时间
- 归档后的方案不在列表中显示，但可通过详情 API 查看
- 幂等设计：重复归档同一方案返回成功
- 权限验证：只能归档自己的方案

#### 请求示例

**curl命令**:
```bash
curl -X POST "http://localhost/api/v1/plans/plan_01ke3d123/archive" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### 成功响应

**HTTP 200**:
```json
{
  "success": true,
  "data": null,
  "error": null
}
```

#### 错误响应

| 场景 | HTTP状态码 | 错误码 | 错误消息 |
|------|----------|--------|---------|
| 方案不存在 | 404 | NOT_FOUND | plan not found |
| 非本人方案 | 403 | UNAUTHORIZED | not owner |
| 方案已删除 | 404 | NOT_FOUND | plan not found |
| 状态不正确 | 400 | INVALID_STATUS | 只有已确认状态的方案才能归档 |
| 未登录 | 401 | UNAUTHENTICATED | missing bearer token |

**说明**: 归档后会生成领域事件 `PlanArchived`。

### 3.8 提交通晒 API（v1.4 新增）

#### Endpoint
```
POST /api/v1/plans/{planId}/submit-review
```

#### 功能说明

- **状态转换**：将方案从 `draft`（制定完成）状态提交到 `reviewing`（通晒中）状态
- 记录 `review_started_at` 时间戳标记进入通晒的时间
- 权限验证：只能操作自己的方案
- 状态约束：只有 `draft` 状态的方案才能提交通晒

#### 请求示例

**curl命令**:
```bash
curl -X POST "http://localhost/api/v1/plans/plan_01ke3d123/submit-review" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### 成功响应

**HTTP 200**:
```json
{
  "success": true,
  "data": null,
  "error": null
}
```

#### 错误响应

| 场景 | HTTP状态码 | 错误码 | 错误消息 |
|------|----------|--------|---------|
| 方案不存在 | 404 | NOT_FOUND | plan not found |
| 非本人方案 | 403 | UNAUTHORIZED | not owner |
| 方案已删除 | 404 | NOT_FOUND | plan not found |
| 状态不正确 | 400 | INVALID_STATUS | 只有制定完成状态的方案才能提交通晒 |
| 未登录 | 401 | UNAUTHENTICATED | missing bearer token |

**说明**: 提交通晒后会生成领域事件 `PlanSubmittedForReview`。

### 3.9 回退通晒 API（v1.4 新增）

#### Endpoint
```
POST /api/v1/plans/{planId}/revert-review
```

#### 功能说明

- **状态转换**：将方案从 `confirmed`（已确认）状态回退到 `reviewing`（通晒中）状态
- 清除 `confirmed_time` 时间戳
- 允许用户重新修改已确认的方案
- 权限验证：只能操作自己的方案
- 状态约束：只有 `confirmed` 状态的方案才能回退

#### 请求示例

**curl命令**:
```bash
curl -X POST "http://localhost/api/v1/plans/plan_01ke3d123/revert-review" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### 成功响应

**HTTP 200**:
```json
{
  "success": true,
  "data": null,
  "error": null
}
```

#### 错误响应

| 场景 | HTTP状态码 | 错误码 | 错误消息 |
|------|----------|--------|---------|
| 方案不存在 | 404 | NOT_FOUND | plan not found |
| 非本人方案 | 403 | UNAUTHORIZED | not owner |
| 方案已删除 | 404 | NOT_FOUND | plan not found |
| 状态不正确 | 400 | INVALID_STATUS | 只有已确认状态的方案才能回退通晒 |
| 未登录 | 401 | UNAUTHENTICATED | missing bearer token |

**说明**: 回退通晒后会生成领域事件 `PlanRevertedToReview`。

---

## 方案状态机（v1.4 更新）

```
                    ┌─────────────────────────────────┐
                    │                                 │
                    ▼                                 │
┌──────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐
│generating│───▶│   draft   │───▶│ reviewing │───▶│ confirmed │───▶ archived
└──────────┘    └───────────┘    └───────────┘    └───────────┘
     │                              submit-         confirm       archive
     │                              review
     ▼
  ┌──────┐
  │failed│
  └──────┘
```

**状态说明**:
| 状态 | 中文名 | 说明 |
|------|--------|------|
| generating | 生成中 | AI正在生成方案 |
| failed | 生成失败 | AI生成失败或超时 |
| draft | 制定完成 | AI生成完成，待用户提交通晒 |
| reviewing | 通晒中 | 候选方案在通晒中，可修改 |
| confirmed | 已确认 | 用户确认选用此方案 |
| archived | 已归档 | 方案已归档，不在主列表显示 |

**状态转换**:
- `draft → reviewing`：提交通晒（POST /plans/:id/submit-review）
- `reviewing → confirmed`：确认方案（POST /plans/:id/confirm）
- `confirmed → reviewing`：回退通晒（POST /plans/:id/revert-review）
- `confirmed → archived`：归档方案（POST /plans/:id/archive）

---

## 4. Supplier API（供应商）

### 4.1 搜索供应商 API

#### Endpoint
```
GET /api/v1/suppliers/search?city=Beijing&category=accommodation
```

#### 请求参数

| 字段 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| city | String | ❌ | 城市过滤 | "Beijing" |
| category | String | ❌ | 类别过滤 | "accommodation", "activity", "catering" |

#### 请求示例

**curl命令**:
```bash
curl -X GET "http://localhost/api/v1/suppliers/search?city=Beijing&category=accommodation" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### 成功响应

**HTTP 200**:
```json
{
  "success": true,
  "data": [
    {
      "supplier_id": "sup_hotel_001",
      "name": "北京怀柔会议酒店",
      "category": "accommodation",
      "city": "Beijing",
      "address": "北京市怀柔区雁栖镇",
      "contact": "010-12345678",
      "rating": 4.5,
      "price_range": "300-500",
      "capacity": 200,
      "facilities": ["会议室", "KTV", "烧烤场地"],
      "description": "适合50-200人团建活动"
    }
  ],
  "error": null
}
```

**说明**: 仅返回`status=active`的供应商，按评分倒序排列。

### 4.2 供应商详情 API

#### Endpoint
```
GET /api/v1/suppliers/{supplierId}
```

#### 请求参数

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| supplierId | String | ✅ | 供应商ID（路径参数） |

#### 请求示例

**curl命令**:
```bash
curl -X GET "http://localhost/api/v1/suppliers/sup_hotel_001" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### 成功响应

**HTTP 200**:
```json
{
  "success": true,
  "data": {
    "supplier_id": "sup_hotel_001",
    "name": "北京怀柔会议酒店",
    "category": "accommodation",
    "city": "Beijing",
    "address": "北京市怀柔区雁栖镇",
    "contact": "010-12345678",
    "wechat": "hotel_wx_123",
    "email": "hotel@example.com",
    "rating": 4.5,
    "price_range": "300-500",
    "capacity": 200,
    "facilities": ["会议室", "KTV", "烧烤场地", "无障碍设施"],
    "description": "适合50-200人团建活动，提供会议室、住宿、餐饮一站式服务",
    "images": [
      "https://example.com/hotel_01.jpg",
      "https://example.com/hotel_02.jpg"
    ],
    "location": {
      "latitude": 40.3167,
      "longitude": 116.6333
    }
  },
  "error": null
}
```

#### 错误响应

**HTTP 404 - 供应商不存在**:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "NOT_FOUND",
    "message": "supplier not found"
  }
}
```

---

## 5. 错误码清单

### 5.1 认证相关错误

| 错误码 | HTTP状态 | 说明 | 前端处理 |
|-------|---------|------|---------|
| **UNAUTHENTICATED** | 401 | 未登录或Token过期 | 跳转登录页 |
| **UNAUTHORIZED** | 403 | 无权访问（如跨用户访问方案） | 提示无权限 |

### 5.2 参数验证错误

| 错误码 | HTTP状态 | 说明 | 示例场景 |
|-------|---------|------|---------|
| **INVALID_ARGUMENT** | 400 | 参数验证失败 | budget_min > budget_max |
| **NOT_FOUND** | 404 | 资源不存在 | 方案ID不存在 |

### 5.3 业务逻辑错误

| 错误码 | HTTP状态 | 说明 | 建议 |
|-------|---------|------|------|
| **BUDGET_TOO_LOW** | 400 | 预算不足以生成方案 | 提示最低预算金额 |
| **GENERATION_FAILED** | 500 | 方案生成失败 | 提示稍后重试 |
| **GENERATION_TIMEOUT** | 500 | 方案生成超时（>2分钟） | 提示稍后查看 |

### 5.4 系统错误

| 错误码 | HTTP状态 | 说明 | 处理方式 |
|-------|---------|------|---------|
| **INTERNAL_ERROR** | 500 | 服务器内部错误 | 提示稍后重试 |
| **NETWORK_ERROR** | - | 网络连接失败（前端） | 检查网络连接 |
| **TIMEOUT** | - | 请求超时（前端） | 提示重试 |

### 5.5 错误响应示例

**参数验证失败**:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "people_count 必须大于0"
  }
}
```

**未登录**:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "UNAUTHENTICATED",
    "message": "登录已过期，请重新登录"
  }
}
```

**无权访问**:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "not owner"
  }
}
```

**资源不存在**:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "NOT_FOUND",
    "message": "plan not found"
  }
}
```

**内部错误**:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Internal server error"
  }
}
```

---

## 6. 分页约定

### 6.1 分页参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | Integer | 1 | 页码（从1开始） |
| pageSize | Integer | 10 | 每页大小 |

**限制**: `pageSize` 最大值为 100。

### 6.2 分页响应格式

使用MyBatis Plus的Page对象：

```json
{
  "success": true,
  "data": {
    "records": [ ... ],      // 当前页数据
    "total": 100,           // 总记录数
    "size": 10,             // 每页大小
    "current": 1,           // 当前页码
    "pages": 10             // 总页数
  }
}
```

### 6.3 分页示例

**请求第2页**:
```bash
curl -X GET "http://localhost/api/v1/plans?page=2&pageSize=10" \
  -H "Authorization: Bearer ..."
```

**响应**:
```json
{
  "success": true,
  "data": {
    "records": [
      { "plan_id": "plan_11", ... },
      { "plan_id": "plan_12", ... },
      ...
    ],
    "total": 25,
    "size": 10,
    "current": 2,
    "pages": 3
  }
}
```

---

## 附录

### A. 完整端点清单

**认证接口** (1个):
- `POST /api/v1/auth/wechat/login`

**方案接口** (5个):
- `POST /api/v1/plans/generate`
- `GET /api/v1/plans?page=1&pageSize=10`
- `GET /api/v1/plans/{planId}`
- `POST /api/v1/plans/{planId}/confirm`
- `POST /api/v1/plans/{planId}/supplier-contacts`

**供应商接口** (2个):
- `GET /api/v1/suppliers/search?city=Beijing&category=accommodation`
- `GET /api/v1/suppliers/{supplierId}`

**内部接口** (1个，仅AI服务可调用):
- `POST /internal/plans/batch`

### B. 测试建议

1. **使用Postman Collection**: 导入API测试集合，快速验证所有接口
2. **Mock数据模式**: 前端可开启Mock模式独立开发
3. **集成测试**: 使用`docs/qa/scripts/run_backend_api_full_coverage.sh`执行完整测试
4. **错误场景测试**: 覆盖所有错误码，验证错误处理逻辑

### C. API版本管理

- **当前版本**: v1（`/api/v1/...`）
- **版本策略**: URL路径版本号
- **兼容性**: 非破坏性变更在同一版本内升级

---

**文档版本**: v1.0
**最后更新**: 2026-01-04
**维护者**: TeamVenture开发团队

