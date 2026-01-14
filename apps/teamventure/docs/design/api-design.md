# TeamVenture API 设计文档

**版本**: v1.6（Phase 1 - 小程序端）
**创建日期**: 2026-01-04
**更新日期**: 2026-01-14
**变更记录**:
- **v1.6 (2026-01-14)**: 新增Location API（地点选择）模块
  - 新增第4章：Location API（地点选择）
  - 4.1: 搜索地点建议API（suggest）
  - 4.2: 获取热门景点API（hot-spots）
  - 4.3: 逆地理编码API（reverse-geocode）
  - 4.4: 术语说明（LocationValue数据结构、POI类型枚举）
  - 调整章节编号：Supplier API改为第5章，错误码清单改为第6章
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
4. [Location API（地点选择）](#4-location-api地点选择)
5. [Supplier API（供应商）](#5-supplier-api供应商)
6. [错误码清单](#6-错误码清单)
7. [分页约定](#7-分页约定)

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

### 2.3 获取当前用户信息 API

#### Endpoint
```
GET /api/v1/users/me
```

#### 用途
- **Token验证**: 在用户"继续使用"时验证token有效性
- **数据刷新**: 获取最新的用户信息（如昵称、头像变更）
- **登录状态检查**: 前端页面初始化时验证登录状态

#### 请求头
```
Authorization: Bearer <session_token>
```

#### 成功响应

**HTTP 200**:
```json
{
  "success": true,
  "data": {
    "user_id": "user_01ke3abc123",
    "nickname": "张三",
    "avatar": "http://api.teamventure.com/avatars/users/user_01ke3abc123/avatars/obj_01ke3abc123.jpg",
    "phone": "138****8888",
    "company": "某科技公司",
    "role": "HR"
  },
  "error": null
}
```

#### 错误响应

**HTTP 401 - Token无效或已过期**:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "UNAUTHENTICATED",
    "message": "invalid token"
  }
}
```

**前端处理逻辑**（参考 pages/login/login.js:handleContinue）:
```javascript
async handleContinue() {
  try {
    wx.showLoading({ title: '验证中...', mask: true })
    await get('/users/me', {}, { showLoading: false, showError: false })
    wx.hideLoading()
    wx.switchTab({ url: '/pages/home/home' })
  } catch (error) {
    wx.hideLoading()
    console.error('Token 验证失败', error)
    this.handleReLogin()  // 清除登录状态，提示重新登录
  }
}
```

### 2.4 刷新Token API

#### Endpoint
```
POST /api/v1/users/refresh
```

#### 用途
- **自动刷新**: 当token剩余有效期 < 12小时时自动刷新
- **无感续期**: 用户无需重新登录即可获得新token
- **防止中断**: 避免用户在操作过程中突然掉线

#### 请求头
```
Authorization: Bearer <session_token>
```

#### 请求参数
无需请求体

#### 成功响应

**HTTP 200 - Token需要刷新**:
```json
{
  "success": true,
  "data": {
    "sessionToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",  // 新token
    "userInfo": {
      "user_id": "user_01ke3abc123",
      "nickname": "张三",
      "avatar": "http://api.teamventure.com/avatars/users/user_01ke3abc123/avatars/obj_01ke3abc123.jpg",
      "phone": "138****8888",
      "company": "某科技公司",
      "role": "HR"
    }
  },
  "error": null
}
```

**HTTP 200 - Token仍然有效，无需刷新**:
```json
{
  "success": true,
  "data": null,  // 注意：返回 null 表示无需刷新
  "error": null
}
```

#### 错误响应

**HTTP 401 - Token无效**:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "UNAUTHENTICATED",
    "message": "invalid token"
  }
}
```

**刷新策略**（参考 utils/request.js:refreshTokenIfNeeded）:
- **触发时机**: 每次API请求前检查（除登录和刷新接口本身）
- **阈值设置**: JWT剩余有效期 < 12小时
- **并发控制**: 使用Promise防止多个请求同时触发刷新
- **失败处理**: 刷新失败时清除登录状态，跳转登录页

```javascript
async function refreshTokenIfNeeded() {
  const sessionToken = wx.getStorageSync(STORAGE_KEYS.SESSION_TOKEN)
  if (!sessionToken) return false

  // 防止并发刷新
  if (tokenRefreshInProgress) {
    return tokenRefreshInProgress
  }

  tokenRefreshInProgress = new Promise((resolve) => {
    wx.request({
      url: `${API_BASE_URL}/users/refresh`,
      method: 'POST',
      header: { 'Authorization': `Bearer ${sessionToken}` },
      success: (res) => {
        if (res.statusCode === 200 && res.data?.data?.sessionToken) {
          // 更新token和用户信息
          wx.setStorageSync(STORAGE_KEYS.SESSION_TOKEN, res.data.data.sessionToken)
          wx.setStorageSync(STORAGE_KEYS.USER_INFO, res.data.data.userInfo)
          resolve(true)
        } else {
          resolve(true)  // data为null表示无需刷新
        }
      },
      fail: () => resolve(true),  // 网络错误不阻止后续请求
      complete: () => { tokenRefreshInProgress = null }
    })
  })

  return tokenRefreshInProgress
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
| destination_city | String | ❌ | 目的地所属行政城市（可选，用于季节/价格配置） | "杭州" |
| preferences | Object | ❌ | 偏好设置（JSON对象） | 见下方 |

> **字段语义说明**：
> - `departure_city`：出发城市，表示团队从哪里出发，通常是公司所在地（如：上海市）
> - `destination`：目的地，表示团建活动举办地点（如：杭州千岛湖）
> - `destination_city`：目的地所属行政城市（如：杭州），用于季节/价格配置维度
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
    "destination_city": "杭州",
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
  "destination_city": "杭州",
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

## 4. Location API（地点选择）⭐ v1.6新增

### 4.1 搜索地点建议 API

**用途**: 根据关键词搜索地点（POI），支持自动补全，用于LocationPicker组件

#### Endpoint
```
GET /api/v1/locations/suggest
```

#### 请求参数

| 字段 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| keyword | String | ✅ | 搜索关键词（至少2个字符） | "莫干山" |
| type | String | ✅ | 地点类型：`departure`（出发地）或 `destination`（目的地） | "destination" |
| province | String | ❌ | 省份名称（限定搜索范围） | "浙江省" |
| limit | Integer | ❌ | 返回数量限制（1-50），默认10 | 10 |

#### 请求示例

**curl命令**:
```bash
curl -X GET "http://localhost:8080/api/v1/locations/suggest?keyword=莫干山&type=destination&province=浙江省&limit=5" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**JavaScript (小程序)**:
```javascript
const { suggestions } = await get('/api/v1/locations/suggest', {
  keyword: '莫干山',
  type: 'destination',
  province: '浙江省',
  limit: 10
});
```

#### 成功响应

**HTTP 200**:
```json
{
  "success": true,
  "data": {
    "suggestions": [
      {
        "poi_id": "B000A7BD6C",
        "name": "莫干山风景名胜区",
        "short_name": "莫干山",
        "address": "浙江省湖州市德清县",
        "location": {
          "longitude": 119.912722,
          "latitude": 30.562778
        },
        "poi_type": "scenic",
        "tags": ["4A级景区", "避暑胜地"],
        "distance": 62000
      },
      {
        "poi_id": "B000A7BD6D",
        "name": "莫干山郡安里度假酒店",
        "short_name": "郡安里酒店",
        "address": "浙江省湖州市德清县莫干山镇",
        "location": {
          "longitude": 119.918888,
          "latitude": 30.565000
        },
        "poi_type": "hotel",
        "tags": ["高端酒店", "4.8分"],
        "distance": 63500
      }
    ]
  },
  "error": null
}
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| poi_id | String | 高德POI唯一标识 |
| name | String | POI全名（用于显示） |
| short_name | String | POI简称（用于标签） |
| address | String | 完整地址（省市区） |
| location.longitude | Number | 经度（GCJ-02坐标系） |
| location.latitude | Number | 纬度（GCJ-02坐标系） |
| poi_type | String | POI类型：`scenic`（景点）/`hotel`（酒店）/`activity`（活动场所）/`district`（行政区）/`landmark`（地标） |
| tags | Array<String> | 标签列表（用于展示特色） |
| distance | Number | 距离用户当前位置（米），需前端传location参数，未授权时为null |

#### 错误响应

**HTTP 400** - 参数错误:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "keyword长度至少为2个字符"
  }
}
```

**HTTP 500** - 服务器错误（降级处理）:
```json
{
  "success": false,
  "data": {
    "suggestions": []  // 返回空数组，前端显示"无搜索结果"
  },
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "搜索服务暂时不可用，请稍后重试"
  }
}
```

#### 实现策略

1. **查询静态表**：优先查询`hot_destinations`表（本地数据，<100ms）
2. **高德API补充**：结果不足时调用高德地图`/v3/place/text` API
3. **Redis缓存**：缓存搜索结果24小时（key: `location:suggest:{keyword}:{province}`）
4. **降级策略**：高德API失败时返回静态表数据

---

### 4.2 获取热门景点 API

**用途**: 获取指定省份或全国的热门景点，用于快捷标签

#### Endpoint
```
GET /api/v1/locations/hot-spots
```

#### 请求参数

| 字段 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| province | String | ❌ | 省份名称（为空则返回全国热门） | "浙江省" |
| limit | Integer | ❌ | 返回数量限制（1-20），默认8 | 8 |

#### 请求示例

**curl命令**:
```bash
curl -X GET "http://localhost:8080/api/v1/locations/hot-spots?province=浙江省&limit=8" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**JavaScript (小程序)**:
```javascript
const { hot_spots } = await get('/api/v1/locations/hot-spots', {
  province: '浙江省',
  limit: 8
});
```

#### 成功响应

**HTTP 200**:
```json
{
  "success": true,
  "data": {
    "hot_spots": [
      {
        "poi_id": "B000A7BD6C",
        "name": "莫干山风景名胜区",
        "short_name": "莫干山",
        "province": "浙江省",
        "city": "湖州市",
        "popularity": 95
      },
      {
        "poi_id": "B000A83Q9F",
        "name": "千岛湖风景区",
        "short_name": "千岛湖",
        "province": "浙江省",
        "city": "杭州市",
        "popularity": 100
      }
    ]
  },
  "error": null
}
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| poi_id | String | 高德POI ID |
| name | String | POI全名 |
| short_name | String | POI简称（用于标签显示） |
| province | String | 所属省份 |
| city | String | 所属城市 |
| popularity | Integer | 热度值（0-100，用于排序） |

#### 实现策略

1. **查询数据库**：查询`hot_destinations`表
2. **排序规则**：按`popularity`字段降序
3. **缓存策略**：结果缓存24小时（热门景点变化不频繁）

---

### 4.3 逆地理编码 API（可选）

**用途**: 将经纬度坐标转换为地址文本，用于"我的位置"功能

#### Endpoint
```
GET /api/v1/locations/reverse-geocode
```

#### 请求参数

| 字段 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| longitude | Number | ✅ | 经度（GCJ-02坐标系） | 119.912722 |
| latitude | Number | ✅ | 纬度（GCJ-02坐标系） | 30.562778 |

#### 请求示例

**curl命令**:
```bash
curl -X GET "http://localhost:8080/api/v1/locations/reverse-geocode?longitude=119.912722&latitude=30.562778" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**JavaScript (小程序)**:
```javascript
// 获取当前位置后调用
const position = await wx.getLocation({ type: 'gcj02' });
const geocode = await get('/api/v1/locations/reverse-geocode', {
  longitude: position.longitude,
  latitude: position.latitude
});
```

#### 成功响应

**HTTP 200**:
```json
{
  "success": true,
  "data": {
    "formatted_address": "浙江省湖州市德清县莫干山镇",
    "province": "浙江省",
    "province_code": "330000",
    "city": "湖州市",
    "city_code": "330500",
    "district": "德清县",
    "district_code": "330521"
  },
  "error": null
}
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| formatted_address | String | 完整格式化地址 |
| province | String | 省份名称 |
| province_code | String | 省份行政区划代码 |
| city | String | 城市名称 |
| city_code | String | 城市行政区划代码 |
| district | String | 区县名称 |
| district_code | String | 区县行政区划代码 |

#### 实现策略

1. **调用高德API**：使用高德地图`/v3/geocode/regeo` API
2. **缓存策略**：坐标→地址映射缓存24小时（经纬度精确到小数点后4位作为key）

---

### 4.4 术语说明（LocationPicker模块）

#### 核心概念定义

| 术语 | 英文 | 说明 |
|------|------|------|
| **地点** | Location | 泛指任何地理位置（城市/景点/地标/酒店） |
| **景点/POI** | Attraction/Point of Interest | 旅游目的地，包括风景区、主题公园、名胜古迹 |
| **出发地点** | Departure Location | 团建活动的出发位置（细化到景点/地标维度） |
| **目的地点** | Destination Location | 团建活动的目标位置（细化到景点/地标维度） |
| **搜索建议** | Suggestion | 基于关键词返回的候选地点列表项 |
| **热门景点** | Hot Spot | 高热度的推荐目的地 |

#### LocationValue 标准数据结构

前端LocationPicker组件使用的统一数据格式：

```typescript
interface LocationValue {
  name: string;              // 地点名称
  address: string;           // 完整地址
  location?: {               // 经纬度（可选）
    longitude: number;       // 经度（GCJ-02）
    latitude: number;        // 纬度（GCJ-02）
  };
  poi_id?: string;          // 高德POI ID（可选）
  poi_type?: string;        // POI类型（可选）
}
```

#### POI类型枚举

| 类型值 | 中文名 | 说明 |
|--------|--------|------|
| `scenic` | 景点 | 风景区、名胜古迹、主题公园 |
| `hotel` | 酒店 | 住宿场所（度假村、民宿、酒店） |
| `activity` | 活动场所 | 团建活动场地（拓展基地、会议中心） |
| `district` | 行政区 | 区县级行政区划 |
| `landmark` | 地标 | 地标性建筑、广场、车站 |
| `current` | 当前位置 | 用户当前所在位置 |
| `map_selected` | 地图选点 | 用户通过地图手动选择的位置 |

#### 与现有API的关系

**扩展现有字段**：
```json
// 现有：PLAN_GENERATE 接口
{
  "departure_city": "上海市",              // 现有字段（兼容）
  "destination": "千岛湖",                  // 现有字段（兼容）
  "destination_city": "杭州市",            // 现有字段（可选）

  // 新增可选字段（LocationPicker提供）
  "departure_location": {                  // 出发地精确坐标（可选）
    "longitude": 121.473701,
    "latitude": 31.230416
  },
  "destination_location": {                // 目的地精确坐标（可选）
    "longitude": 119.030122,
    "latitude": 29.605768
  }
}
```

**向后兼容保证**：
- 前端可只传`departure_city`和`destination`文本字段（旧版）
- 前端也可传完整的LocationValue（新版），后端从中提取`name`和`location`
- 后端接收到`destination_location`字段时，可用于距离计算、路线规划优化

---

## 5. Supplier API（供应商）

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

## 6. 错误码清单

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

## 7. 分页约定

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
