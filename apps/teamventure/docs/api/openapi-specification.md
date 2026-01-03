# TeamVenture API 规范文档

**版本:** 1.0.0
**协议:** OpenAPI 3.0.3
**基础 URL:** `http://api.teamventure.com`
**更新时间:** 2026-01-01

---

## 目录

- [1. API 概述](#1-api-概述)
- [2. 认证方式](#2-认证方式)
- [3. 通用响应格式](#3-通用响应格式)
- [4. Java 业务服务接口](#4-java-业务服务接口)
  - [4.1 认证模块](#41-认证模块)
  - [4.2 方案管理模块](#42-方案管理模块)
  - [4.3 供应商管理模块](#43-供应商管理模块)
  - [4.4 内部回调接口](#44-内部回调接口)
- [5. Python AI 服务接口](#5-python-ai-服务接口)
  - [5.1 基础接口](#51-基础接口)
  - [5.2 方案生成接口](#52-方案生成接口)
  - [5.3 流式输出接口（规划中）](#53-流式输出接口规划中)
- [6. 数据模型](#6-数据模型)
- [7. 错误码说明](#7-错误码说明)
- [8. 完整流程示例](#8-完整流程示例)

---

## 1. API 概述

### 1.1 服务架构

TeamVenture 采用微服务架构，包含以下服务：

| 服务名称 | 技术栈 | 端口 | 职责 |
|---------|--------|------|------|
| Java Business Service | Spring Boot 3.2.1 | 8080 | 业务逻辑、数据持久化 |
| Python AI Service | FastAPI 0.109+ | 8000 | AI 方案生成、LLM 集成 |
| Nginx | OpenResty | 80/443 | 反向代理、负载均衡 |

### 1.2 协议规范

- **传输协议:** HTTP/1.1, HTTPS
- **内容类型:** application/json (UTF-8)
- **日期格式:** ISO 8601 (YYYY-MM-DD)
- **时间戳格式:** ISO 8601 (YYYY-MM-DDTHH:mm:ss+08:00)
- **字符编码:** UTF-8

### 1.3 API 版本控制

当前版本: `v1`
版本策略: URL 路径版本化 (`/api/v1/...`)

---

## 2. 认证方式

### 2.1 微信小程序登录

使用微信授权码换取会话令牌。

**认证流程:**

```mermaid
sequenceDiagram
    participant 小程序
    participant API
    participant 微信服务器

    小程序->>微信服务器: wx.login()
    微信服务器->>小程序: code
    小程序->>API: POST /api/v1/auth/wechat/login
    API->>微信服务器: jscode2session
    微信服务器->>API: openid, session_key
    API->>API: 生成 JWT token
    API->>小程序: session_token
```

### 2.2 Token 使用

所有需要认证的接口，在 HTTP 请求头中携带：

```
Authorization: Bearer {session_token}
```

### 2.3 Token 过期

- **有效期:** 7 天
- **刷新策略:** 客户端需在 token 过期前重新登录

---

## 3. 通用响应格式

### 3.1 成功响应

```json
{
  "success": true,
  "data": <响应数据>,
  "error": null
}
```

### 3.2 失败响应

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述信息"
  }
}
```

### 3.3 分页响应

```json
{
  "success": true,
  "data": {
    "records": [...],
    "total": 100,
    "size": 10,
    "current": 1,
    "pages": 10
  },
  "error": null
}
```

---

## 4. Java 业务服务接口

### 4.1 认证模块

#### 4.1.1 微信登录

**接口信息:**

```yaml
operationId: wechatLogin
tags: [Authentication]
summary: 微信授权码登录
description: 使用微信小程序授权码换取会话令牌
```

**请求:**

```http
POST /api/v1/auth/wechat/login
Content-Type: application/json
```

```json
{
  "code": "061xYz0w3JCWJp20JJ2w32q0On2xYz0c"
}
```

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 是 | 微信授权码，通过 wx.login() 获取 |

**响应示例:**

```json
{
  "success": true,
  "data": {
    "user_id": "user_01kdtfvysdar6dpcd0pkww4srq",
    "session_token": "eyJhbGciOiJIUzI1NiJ9...",
    "expires_in_seconds": 604800
  },
  "error": null
}
```

**响应字段:**

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | string | 用户唯一标识 |
| session_token | string | JWT 会话令牌 |
| expires_in_seconds | integer | 过期时间（秒） |

**错误码:**

| 错误码 | HTTP 状态码 | 说明 |
|--------|-------------|------|
| INVALID_CODE | 400 | 微信授权码无效 |
| WECHAT_API_ERROR | 500 | 微信接口调用失败 |

---

### 4.2 方案管理模块

#### 4.2.1 生成团建方案

**接口信息:**

```yaml
operationId: generatePlan
tags: [Plans]
summary: 创建方案生成请求
description: 提交团建需求，异步生成 3 套方案（经济型/标准型/高端型）
security:
  - BearerAuth: []
```

**请求:**

```http
POST /api/v1/plans/generate
Authorization: Bearer {token}
Content-Type: application/json
```

```json
{
  "people_count": 50,
  "budget_min": 25000,
  "budget_max": 35000,
  "start_date": "2026-01-10",
  "end_date": "2026-01-11",
  "departure_city": "北京",
  "preferences": {
    "活动类型": "户外拓展",
    "住宿要求": "民宿",
    "餐饮偏好": "团餐"
  }
}
```

**请求参数:**

| 参数 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| people_count | integer | 是 | > 0 | 参与人数 |
| budget_min | number | 是 | > 0 | 最低预算（元） |
| budget_max | number | 是 | >= budget_min | 最高预算（元） |
| start_date | string | 是 | ISO 8601 | 开始日期 |
| end_date | string | 是 | >= start_date | 结束日期 |
| departure_city | string | 是 | 非空 | 出发城市 |
| preferences | object | 否 | - | 个性化偏好 |

**响应示例:**

```json
{
  "success": true,
  "data": {
    "plan_request_id": "plan_req_01kdthds2ykj530hexcjyearxg",
    "status": "generating"
  },
  "error": null
}
```

**处理流程:**

1. 创建 `plan_requests` 记录（状态：GENERATING）
2. 发布消息到 RabbitMQ Exchange: `plan.generation.topic`
3. Python AI 服务异步处理（约 15-20 秒）
4. 生成结果通过内部接口写入数据库
5. 客户端轮询 `GET /api/v1/plans` 获取结果

**错误码:**

| 错误码 | HTTP 状态码 | 说明 |
|--------|-------------|------|
| INVALID_DATE_RANGE | 400 | 日期范围无效 |
| INVALID_BUDGET_RANGE | 400 | 预算范围无效 |
| UNAUTHORIZED | 401 | 未登录或 token 过期 |

---

#### 4.2.2 获取方案列表

**接口信息:**

```yaml
operationId: listPlans
tags: [Plans]
summary: 获取用户方案列表
description: 分页查询当前用户的所有团建方案
security:
  - BearerAuth: []
```

**请求:**

```http
GET /api/v1/plans?page=1&pageSize=10
Authorization: Bearer {token}
```

**请求参数:**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | integer | 否 | 1 | 页码（从 1 开始） |
| pageSize | integer | 否 | 10 | 每页数量（最大 100） |

**响应示例:**

```json
{
  "success": true,
  "data": {
    "records": [
      {
        "planId": "plan_01kdthebe39nnh3brm0sqmmt4j",
        "planRequestId": "plan_req_01kdthds2ykj530hexcjyearxg",
        "userId": "user_01kdtfvysdar6dpcd0pkww4srq",
        "planType": "budget",
        "planName": "经济型团队建设方案",
        "summary": "适合预算有限的团队，提供基本的住宿和活动选择。",
        "budgetTotal": 25000.00,
        "budgetPerPerson": 500.00,
        "durationDays": 2,
        "departureCity": "北京",
        "status": "draft",
        "confirmedTime": null
      },
      {
        "planId": "plan_01kdthebe3zj4w3f8ppygzxt5y",
        "planType": "standard",
        "planName": "标准型团队建设方案",
        "budgetTotal": 30000.00,
        "budgetPerPerson": 600.00,
        "status": "draft"
      },
      {
        "planId": "plan_01kdthebe3rrkn1kf5wc0cv29y",
        "planType": "premium",
        "planName": "高端型团队建设方案",
        "budgetTotal": 35000.00,
        "budgetPerPerson": 700.00,
        "status": "confirmed",
        "confirmedTime": "2026-01-01T12:30:00+08:00"
      }
    ],
    "total": 3,
    "size": 10,
    "current": 1,
    "pages": 1
  },
  "error": null
}
```

**方案状态:**

| 状态 | 说明 |
|------|------|
| draft | 草稿（待确认） |
| confirmed | 已确认 |

---

#### 4.2.3 获取方案详情

**接口信息:**

```yaml
operationId: getPlanDetail
tags: [Plans]
summary: 获取方案详细信息
description: 查询单个方案的完整信息，包括行程、预算明细等
security:
  - BearerAuth: []
```

**请求:**

```http
GET /api/v1/plans/{planId}
Authorization: Bearer {token}
```

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| planId | string | 方案ID |

**响应示例:**

```json
{
  "success": true,
  "data": {
    "planId": "plan_01kdthebe39nnh3brm0sqmmt4j",
    "planRequestId": "plan_req_01kdthds2ykj530hexcjyearxg",
    "userId": "user_01kdtfvysdar6dpcd0pkww4srq",
    "planType": "budget",
    "planName": "经济型团队建设计划",
    "summary": "两天一夜的经济型团队建设活动，包含住宿、活动与餐饮。",
    "highlights": [
      "经济实惠的住宿",
      "趣味团队活动",
      "丰富的团体晚餐"
    ],
    "itinerary": {
      "days": [
        {
          "day": 1,
          "items": [
            {
              "time_start": "09:00",
              "time_end": "12:00",
              "activity": "团队破冰活动"
            },
            {
              "time_start": "12:00",
              "time_end": "13:00",
              "activity": "团体午餐"
            },
            {
              "time_start": "14:00",
              "time_end": "17:00",
              "activity": "团队协作游戏"
            },
            {
              "time_start": "18:00",
              "time_end": "20:00",
              "activity": "晚餐与自由交流"
            }
          ]
        },
        {
          "day": 2,
          "items": [
            {
              "time_start": "09:00",
              "time_end": "11:00",
              "activity": "晨间团队建设活动"
            },
            {
              "time_start": "11:30",
              "time_end": "13:00",
              "activity": "午餐与活动总结"
            }
          ]
        }
      ]
    },
    "budgetBreakdown": {
      "total": 25000,
      "per_person": 500,
      "categories": [
        {
          "category": "住宿",
          "subtotal": 10000
        },
        {
          "category": "活动",
          "subtotal": 8000
        },
        {
          "category": "餐饮",
          "subtotal": 7000
        }
      ]
    },
    "supplierSnapshots": [
      {
        "supplier_id": "sup_acc_002",
        "name": "密云水库度假村",
        "type": "accommodation",
        "price_range": "低"
      },
      {
        "supplier_id": "sup_demo_activity",
        "name": "北京·示例活动教练",
        "type": "activity",
        "price_range": "低"
      },
      {
        "supplier_id": "sup_demo_dining",
        "name": "北京·示例餐饮",
        "type": "dining",
        "price_range": "低"
      }
    ],
    "budgetTotal": 25000.00,
    "budgetPerPerson": 500.00,
    "durationDays": 2,
    "departureCity": "北京",
    "status": "draft",
    "confirmedTime": null
  },
  "error": null
}
```

**权限验证:**

- 仅方案所有者（userId 匹配）可查看详情
- 否则返回 403 FORBIDDEN

---

#### 4.2.4 确认方案

**接口信息:**

```yaml
operationId: confirmPlan
tags: [Plans]
summary: 确认选择方案
description: 用户选定某个方案后，标记为已确认状态
security:
  - BearerAuth: []
```

**请求:**

```http
POST /api/v1/plans/{planId}/confirm
Authorization: Bearer {token}
Content-Type: application/json
```

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| planId | string | 方案ID |

**请求体:** 无（空 JSON 或省略）

**响应示例:**

```json
{
  "success": true,
  "data": null,
  "error": null
}
```

**业务逻辑:**

1. 验证方案归属权
2. 更新 `status` 为 `confirmed`
3. 记录 `confirmed_time` 为当前时间
4. 发布 `PlanConfirmed` 领域事件

**幂等性:** 多次确认同一方案，保持 `confirmed` 状态不变

**错误码:**

| 错误码 | HTTP 状态码 | 说明 |
|--------|-------------|------|
| PLAN_NOT_FOUND | 404 | 方案不存在 |
| FORBIDDEN | 403 | 无权操作此方案 |

---

#### 4.2.5 记录供应商联系

**接口信息:**

```yaml
operationId: recordSupplierContact
tags: [Plans]
summary: 记录用户联系供应商行为
description: 当用户通过电话/微信/邮件联系供应商时，记录此行为用于数据分析
security:
  - BearerAuth: []
```

**请求:**

```http
POST /api/v1/plans/{planId}/supplier-contacts
Authorization: Bearer {token}
Content-Type: application/json
```

```json
{
  "supplier_id": "sup_acc_002",
  "channel": "WECHAT",
  "notes": "已添加供应商微信，咨询具体价格和档期"
}
```

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| planId | string | 方案ID |

**请求参数:**

| 参数 | 类型 | 必填 | 枚举值 | 说明 |
|------|------|------|--------|------|
| supplier_id | string | 是 | - | 供应商ID |
| channel | string | 是 | PHONE / WECHAT / EMAIL | 联系渠道 |
| notes | string | 否 | - | 备注信息 |

**响应示例:**

```json
{
  "success": true,
  "data": null,
  "error": null
}
```

**业务逻辑:**

1. 创建 `supplier_contact_logs` 记录
2. 发布 `SupplierContacted` 领域事件

---

### 4.3 供应商管理模块

#### 4.3.1 搜索供应商

**接口信息:**

```yaml
operationId: searchSuppliers
tags: [Suppliers]
summary: 搜索供应商
description: 根据城市、类别筛选供应商，按评分降序排列
security:
  - BearerAuth: []
```

**请求:**

```http
GET /api/v1/suppliers?city=北京&category=accommodation
Authorization: Bearer {token}
```

**请求参数:**

| 参数 | 类型 | 必填 | 枚举值 | 说明 |
|------|------|------|--------|------|
| city | string | 否 | - | 城市筛选 |
| category | string | 否 | accommodation / dining / activity / transportation | 类别筛选 |

**响应示例:**

```json
{
  "success": true,
  "data": [
    {
      "supplierId": "sup_acc_002",
      "name": "密云水库度假村",
      "category": "accommodation",
      "city": "北京",
      "district": "密云区",
      "address": "密云区水库路188号",
      "contactPhone": "13800138002",
      "contactWechat": "miyun_resort",
      "contactPerson": "李经理",
      "priceMin": 300.00,
      "priceMax": 800.00,
      "priceUnit": "per_room",
      "rating": 4.8,
      "reviewCount": 256,
      "tags": ["水景", "会议室", "KTV", "垂钓"],
      "capacityMin": 30,
      "capacityMax": 150,
      "status": "active",
      "verified": true
    },
    {
      "supplierId": "sup_acc_001",
      "name": "怀柔山水农家院",
      "category": "accommodation",
      "rating": 4.5,
      "reviewCount": 128,
      "status": "active"
    }
  ],
  "error": null
}
```

**排序规则:** 按 `rating` 降序

**筛选规则:** 仅返回 `status = 'active'` 的供应商

---

#### 4.3.2 获取供应商详情

**接口信息:**

```yaml
operationId: getSupplierDetail
tags: [Suppliers]
summary: 获取供应商详细信息
description: 查询单个供应商的完整信息
security:
  - BearerAuth: []
```

**请求:**

```http
GET /api/v1/suppliers/{supplierId}
Authorization: Bearer {token}
```

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| supplierId | string | 供应商ID |

**响应示例:**

```json
{
  "success": true,
  "data": {
    "supplierId": "sup_acc_002",
    "name": "密云水库度假村",
    "category": "accommodation",
    "city": "北京",
    "district": "密云区",
    "address": "密云区水库路188号",
    "coordinates": {
      "latitude": 40.38,
      "longitude": 116.85
    },
    "contactPhone": "13800138002",
    "contactWechat": "miyun_resort",
    "contactPerson": "李经理",
    "priceMin": 300.00,
    "priceMax": 800.00,
    "priceUnit": "per_room",
    "rating": 4.8,
    "reviewCount": 256,
    "tags": ["水景", "会议室", "KTV", "垂钓"],
    "capacityMin": 30,
    "capacityMax": 150,
    "status": "active",
    "verified": true
  },
  "error": null
}
```

---

### 4.4 内部回调接口

#### 4.4.1 批量创建方案（Python AI 回调）

**接口信息:**

```yaml
operationId: batchCreatePlans
tags: [Internal]
summary: 批量创建方案（内部接口）
description: 接收 Python AI 服务生成的方案数据并写入数据库
security:
  - InternalSecretAuth: []
```

**重要:** 此接口仅供内部服务调用，不对外暴露

**请求:**

```http
POST /internal/plans/batch
X-Internal-Secret: {配置的密钥}
Content-Type: application/json
```

```json
{
  "plan_request_id": "plan_req_01kdthds2ykj530hexcjyearxg",
  "user_id": "user_01kdtfvysdar6dpcd0pkww4srq",
  "plans": [
    {
      "plan_id": "plan_01kdthebe39nnh3brm0sqmmt4j",
      "plan_type": "budget",
      "plan_name": "经济型团队建设计划",
      "summary": "两天一夜的经济型团队建设活动",
      "highlights": ["经济实惠", "趣味活动"],
      "itinerary": { "days": [...] },
      "budget_breakdown": { "total": 25000, "per_person": 500, "categories": [...] },
      "supplier_snapshots": [...],
      "budget_total": 25000.00,
      "budget_per_person": 500.00,
      "duration_days": 2,
      "departure_city": "北京",
      "status": "draft"
    },
    {
      "plan_type": "standard",
      "plan_name": "标准型团队建设计划",
      "budget_total": 30000.00,
      "budget_per_person": 600.00,
      "status": "draft"
    },
    {
      "plan_type": "premium",
      "plan_name": "高端型团队建设计划",
      "budget_total": 35000.00,
      "budget_per_person": 700.00,
      "status": "draft"
    }
  ],
  "trace_id": "trace_qa_001"
}
```

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| plan_request_id | string | 是 | 方案请求ID |
| user_id | string | 是 | 用户ID |
| plans | array | 是 | 方案列表（通常 3 个） |
| trace_id | string | 否 | 追踪ID |

**plans 数组元素:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| plan_id | string | 否 | 方案ID（服务端生成） |
| plan_type | string | 是 | budget / standard / premium |
| plan_name | string | 是 | 方案名称 |
| summary | string | 是 | 方案概要 |
| highlights | array | 是 | 亮点列表 |
| itinerary | object | 是 | 行程安排 |
| budget_breakdown | object | 是 | 预算明细 |
| supplier_snapshots | array | 是 | 供应商快照 |
| budget_total | number | 是 | 总预算 |
| budget_per_person | number | 是 | 人均预算 |
| duration_days | integer | 是 | 天数 |
| departure_city | string | 是 | 出发城市 |
| status | string | 是 | 固定为 "draft" |

**响应示例:**

```json
{
  "success": true,
  "data": null,
  "error": null
}
```

**安全验证:**

- 验证请求头 `X-Internal-Secret` 与配置项 `teamventure.ai-service.callback-secret` 匹配
- 验证失败返回:
  ```json
  {
    "success": false,
    "data": null,
    "error": {
      "code": "UNAUTHORIZED",
      "message": "invalid internal secret"
    }
  }
  ```

**业务逻辑:**

1. 验证 `plan_request_id` 存在
2. 批量插入 `plans` 表
3. 更新 `plan_requests.status` 为 `COMPLETED`
4. 记录 `generation_completed_at` 时间戳
5. 为每个 plan 发布 `PlanGenerated` 领域事件

---

## 5. Python AI 服务接口

### 5.1 基础接口

#### 5.1.1 根路径

**接口信息:**

```yaml
operationId: root
tags: [Basic]
summary: 服务欢迎页面
```

**请求:**

```http
GET /
```

**响应示例:**

```json
{
  "message": "Welcome to TeamVenture AI Service",
  "docs": "/docs",
  "health": "/health"
}
```

---

#### 5.1.2 健康检查

**接口信息:**

```yaml
operationId: healthCheck
tags: [Basic]
summary: 服务健康检查
description: 检查 Python AI 服务是否正常运行
```

**请求:**

```http
GET /health
```

**响应示例:**

```json
{
  "status": "healthy",
  "service": "teamventure-ai-service",
  "version": "1.0.0"
}
```

**HTTP 状态码:** 200 OK

---

#### 5.1.3 Prometheus 监控指标

**接口信息:**

```yaml
operationId: metrics
tags: [Monitoring]
summary: Prometheus 格式监控指标
description: 导出服务运行指标供 Prometheus 采集
```

**请求:**

```http
GET /metrics
```

**响应格式:** text/plain (Prometheus Exposition Format)

**示例指标:**

```
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 123456.0

# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/health"} 1000.0
```

---

### 5.2 方案生成接口

#### 5.2.1 HTTP 方式生成方案（调试用）

**接口信息:**

```yaml
operationId: generatePlanHTTP
tags: [Plans, Debug]
summary: HTTP 触发方案生成（调试接口）
description: 提供 HTTP 方式触发方案生成，主要用于调试和测试，生产环境使用 MQ 方式
deprecated: false
```

**⚠️ 注意:** 此接口仅作为调试/备用接口，生产环境主要通过 RabbitMQ 消费方式处理

**请求:**

```http
POST /api/v1/plans/generate
Content-Type: application/json
```

```json
{
  "plan_request_id": "plan_req_01kdthds2ykj530hexcjyearxg"
}
```

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| plan_request_id | string | 是 | 方案请求ID（从 Java 服务获取） |

**响应示例:**

```json
{
  "message": "Plan generation request received",
  "request_id": "plan_req_01kdthds2ykj530hexcjyearxg",
  "note": "生产环境请使用MQ方式"
}
```

**处理流程:**

此接口会触发与 MQ 消费相同的处理流程：

1. 查询 Java 服务获取完整请求参数
2. 执行 LangGraph Workflow
3. 回调 Java 服务写入结果

---

### 5.3 流式输出接口（规划中）

#### 5.3.1 流式方案生成（SSE）

**接口信息:**

```yaml
operationId: generatePlanStream
tags: [Plans, Streaming]
summary: 流式生成方案（规划中）
description: 使用 Server-Sent Events (SSE) 实时推送方案生成进度和内容
security:
  - BearerAuth: []
x-streaming: true
x-status: planned
```

**设计方案:**

**请求:**

```http
GET /api/v1/plans/generate-stream?plan_request_id=plan_req_xxx
Authorization: Bearer {token}
Accept: text/event-stream
```

**响应格式:** Server-Sent Events (SSE)

**事件流示例:**

```
event: progress
data: {"stage": "parsing", "message": "正在解析需求...", "progress": 10}

event: progress
data: {"stage": "matching", "message": "正在匹配供应商...", "progress": 30}

event: supplier
data: {"supplier_id": "sup_acc_002", "name": "密云水库度假村", "category": "accommodation"}

event: progress
data: {"stage": "generating", "message": "正在生成方案（经济型）...", "progress": 50}

event: plan_chunk
data: {"plan_type": "budget", "chunk": "## 经济型团队建设方案\n\n"}

event: plan_chunk
data: {"plan_type": "budget", "chunk": "### 第一天\n- 09:00-12:00 团队破冰活动\n"}

event: progress
data: {"stage": "generating", "message": "正在生成方案（标准型）...", "progress": 70}

event: plan_chunk
data: {"plan_type": "standard", "chunk": "## 标准型团队建设方案\n\n"}

event: progress
data: {"stage": "generating", "message": "正在生成方案（高端型）...", "progress": 90}

event: plan_chunk
data: {"plan_type": "premium", "chunk": "## 高端型团队建设方案\n\n"}

event: complete
data: {"message": "方案生成完成", "plan_count": 3, "progress": 100}
```

**事件类型说明:**

| 事件类型 | 说明 | 数据格式 |
|---------|------|----------|
| progress | 进度更新 | `{"stage": string, "message": string, "progress": number}` |
| supplier | 匹配到供应商 | `{"supplier_id": string, "name": string, "category": string}` |
| plan_chunk | 方案内容片段 | `{"plan_type": string, "chunk": string}` |
| complete | 生成完成 | `{"message": string, "plan_count": number, "progress": 100}` |
| error | 错误信息 | `{"error": string, "code": string}` |

**客户端示例（JavaScript）:**

```javascript
const eventSource = new EventSource(
  '/api/v1/plans/generate-stream?plan_request_id=plan_req_xxx',
  {
    headers: {
      'Authorization': 'Bearer ' + token
    }
  }
);

eventSource.addEventListener('progress', (e) => {
  const data = JSON.parse(e.data);
  console.log(`进度: ${data.progress}% - ${data.message}`);
});

eventSource.addEventListener('plan_chunk', (e) => {
  const data = JSON.parse(e.data);
  appendToDisplay(data.plan_type, data.chunk);
});

eventSource.addEventListener('complete', (e) => {
  console.log('生成完成');
  eventSource.close();
});

eventSource.addEventListener('error', (e) => {
  const data = JSON.parse(e.data);
  console.error('错误:', data.error);
  eventSource.close();
});
```

**技术实现:**

- 使用 FastAPI 的 `StreamingResponse`
- 集成 OpenAI Client 的 `stream=True` 模式
- LangGraph Workflow 改造为流式输出

**实现优先级:** 中（根据前端需求确定）

---

#### 5.3.2 Chat 对话接口（规划中）

**接口信息:**

```yaml
operationId: chatWithAI
tags: [Chat, Streaming]
summary: AI 对话接口（规划中）
description: 与 AI 助手进行对话，优化团建方案需求
x-streaming: true
x-status: planned
```

**设计方案:**

**请求:**

```http
POST /api/v1/chat
Authorization: Bearer {token}
Content-Type: application/json
Accept: text/event-stream
```

```json
{
  "message": "我想组织一次 50 人的团建活动，预算 3 万左右",
  "session_id": "chat_session_xxx",
  "context": {
    "previous_plans": ["plan_01", "plan_02"]
  }
}
```

**响应格式:** Server-Sent Events (SSE)

**事件流示例:**

```
event: message_start
data: {"message_id": "msg_001"}

event: content_chunk
data: {"delta": "好的"}

event: content_chunk
data: {"delta": "，我"}

event: content_chunk
data: {"delta": "帮您"}

event: content_chunk
data: {"delta": "规划"}

event: content_chunk
data: {"delta": "一下"}

event: content_chunk
data: {"delta": "。"}

event: content_chunk
data: {"delta": "请问"}

event: content_chunk
data: {"delta": "："}

event: content_chunk
data: {"delta": "\n1. "}

event: content_chunk
data: {"delta": "活动"}

event: content_chunk
data: {"delta": "日期"}

event: content_chunk
data: {"delta": "是"}

event: content_chunk
data: {"delta": "什么"}

event: content_chunk
data: {"delta": "时候"}

event: content_chunk
data: {"delta": "？\n"}

event: content_chunk
data: {"delta": "2. "}

event: content_chunk
data: {"delta": "出发"}

event: content_chunk
data: {"delta": "城市"}

event: content_chunk
data: {"delta": "在哪"}

event: content_chunk
data: {"delta": "里？\n"}

event: message_end
data: {"message_id": "msg_001", "finish_reason": "stop"}
```

**应用场景:**

1. 需求澄清：用户描述模糊时，AI 主动提问
2. 方案对比：解释不同方案的优缺点
3. 个性化推荐：根据对话历史调整推荐

**实现优先级:** 低（V2 功能）

---

## 6. 数据模型

### 6.1 User（用户）

```json
{
  "user_id": "string (ULID)",
  "openid": "string (微信 OpenID)",
  "nickname": "string | null",
  "avatar_url": "string | null",
  "phone": "string | null",
  "create_time": "timestamp",
  "update_time": "timestamp"
}
```

### 6.2 PlanRequest（方案请求）

```json
{
  "plan_request_id": "string (ULID)",
  "user_id": "string",
  "people_count": "integer",
  "budget_min": "decimal(10,2)",
  "budget_max": "decimal(10,2)",
  "start_date": "string (YYYY-MM-DD)",
  "end_date": "string (YYYY-MM-DD)",
  "departure_city": "string",
  "preferences": "object (JSON)",
  "status": "enum (GENERATING | COMPLETED | FAILED)",
  "generation_started_at": "timestamp",
  "generation_completed_at": "timestamp | null"
}
```

### 6.3 Plan（方案）

```json
{
  "plan_id": "string (ULID)",
  "plan_request_id": "string",
  "user_id": "string",
  "plan_type": "enum (budget | standard | premium)",
  "plan_name": "string",
  "summary": "string",
  "highlights": "array of string",
  "itinerary": {
    "days": [
      {
        "day": "integer",
        "items": [
          {
            "time_start": "string (HH:mm)",
            "time_end": "string (HH:mm)",
            "activity": "string"
          }
        ]
      }
    ]
  },
  "budget_breakdown": {
    "total": "number",
    "per_person": "number",
    "categories": [
      {
        "category": "string",
        "subtotal": "number"
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
  "budget_total": "decimal(10,2)",
  "budget_per_person": "decimal(10,2)",
  "duration_days": "integer",
  "departure_city": "string",
  "status": "enum (draft | confirmed)",
  "confirmed_time": "timestamp | null",
  "confirmed_by": "string | null",
  "view_count": "integer (default 0)",
  "share_count": "integer (default 0)",
  "create_time": "timestamp",
  "update_time": "timestamp"
}
```

### 6.4 Supplier（供应商）

```json
{
  "supplier_id": "string",
  "name": "string",
  "category": "enum (accommodation | dining | activity | transportation)",
  "city": "string",
  "district": "string",
  "address": "string",
  "coordinates": {
    "latitude": "number",
    "longitude": "number"
  },
  "contact_phone": "string",
  "contact_wechat": "string",
  "contact_person": "string",
  "price_min": "decimal(10,2)",
  "price_max": "decimal(10,2)",
  "price_unit": "enum (per_person | per_room | per_day | per_vehicle)",
  "rating": "decimal(2,1)",
  "review_count": "integer",
  "tags": "array of string",
  "capacity_min": "integer",
  "capacity_max": "integer",
  "status": "enum (active | inactive)",
  "verified": "boolean"
}
```

### 6.5 SupplierContactLog（供应商联系记录）

```json
{
  "contact_id": "string (ULID)",
  "plan_id": "string",
  "supplier_id": "string",
  "user_id": "string",
  "channel": "enum (PHONE | WECHAT | EMAIL)",
  "notes": "string | null",
  "contacted_at": "timestamp"
}
```

---

## 7. 错误码说明

### 7.1 通用错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|-------------|------|
| INTERNAL_ERROR | 500 | 服务内部错误 |
| BAD_REQUEST | 400 | 请求参数错误 |
| UNAUTHORIZED | 401 | 未登录或 token 无效 |
| FORBIDDEN | 403 | 无权访问资源 |
| NOT_FOUND | 404 | 资源不存在 |

### 7.2 业务错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|-------------|------|
| INVALID_CODE | 400 | 微信授权码无效 |
| WECHAT_API_ERROR | 500 | 微信 API 调用失败 |
| INVALID_DATE_RANGE | 400 | 日期范围无效 |
| INVALID_BUDGET_RANGE | 400 | 预算范围无效 |
| PLAN_NOT_FOUND | 404 | 方案不存在 |
| SUPPLIER_NOT_FOUND | 404 | 供应商不存在 |
| PLAN_REQUEST_NOT_FOUND | 404 | 方案请求不存在 |

---

## 8. 完整流程示例

### 8.1 方案生成完整流程

```mermaid
sequenceDiagram
    participant 小程序
    participant Nginx
    participant Java
    participant RabbitMQ
    participant Python
    participant OpenAI

    Note over 小程序,OpenAI: 1. 用户登录
    小程序->>Nginx: POST /api/v1/auth/wechat/login
    Nginx->>Java: 转发
    Java->>小程序: 返回 session_token

    Note over 小程序,OpenAI: 2. 提交方案需求
    小程序->>Nginx: POST /api/v1/plans/generate
    Nginx->>Java: 转发
    Java->>Java: 创建 PlanRequest (GENERATING)
    Java->>RabbitMQ: 发布消息
    Java->>小程序: 返回 plan_request_id

    Note over 小程序,OpenAI: 3. 异步生成方案
    RabbitMQ->>Python: 消费消息
    Python->>Python: 解析需求
    Python->>Python: 匹配供应商
    Python->>OpenAI: 调用 GPT-4 生成方案
    OpenAI->>Python: 返回 3 套方案
    Python->>Java: POST /internal/plans/batch
    Java->>Java: 写入 plans 表
    Java->>Java: 更新 PlanRequest (COMPLETED)

    Note over 小程序,OpenAI: 4. 轮询获取结果
    小程序->>Nginx: GET /api/v1/plans
    Nginx->>Java: 转发
    Java->>小程序: 返回方案列表（3 套）

    Note over 小程序,OpenAI: 5. 查看详情并确认
    小程序->>Nginx: GET /api/v1/plans/{planId}
    Nginx->>Java: 转发
    Java->>小程序: 返回方案详情
    小程序->>Nginx: POST /api/v1/plans/{planId}/confirm
    Nginx->>Java: 转发
    Java->>Java: 更新状态为 confirmed
    Java->>小程序: 确认成功
```

### 8.2 cURL 示例

#### 8.2.1 登录

```bash
curl -X POST http://api.teamventure.com/api/v1/auth/wechat/login \
  -H "Content-Type: application/json" \
  -d '{"code":"061xYz0w3JCWJp20JJ2w32q0On2xYz0c"}'
```

#### 8.2.2 生成方案

```bash
curl -X POST http://api.teamventure.com/api/v1/plans/generate \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "people_count": 50,
    "budget_min": 25000,
    "budget_max": 35000,
    "start_date": "2026-01-10",
    "end_date": "2026-01-11",
    "departure_city": "北京",
    "preferences": {
      "活动类型": "户外拓展"
    }
  }'
```

#### 8.2.3 查询方案列表

```bash
curl -X GET "http://api.teamventure.com/api/v1/plans?page=1&pageSize=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9..."
```

#### 8.2.4 确认方案

```bash
curl -X POST http://api.teamventure.com/api/v1/plans/plan_01kdthebe39nnh3brm0sqmmt4j/confirm \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json"
```

---

## 附录

### A. OpenAPI 3.0 YAML 规范

完整的 OpenAPI 3.0 YAML 文件可通过以下方式生成：

- **Java:** 使用 SpringDoc 自动生成（需配置依赖）
- **Python:** FastAPI 自动生成 OpenAPI JSON: `http://localhost:8000/openapi.json`

### B. API 更新日志

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0.0 | 2026-01-01 | 初始版本，包含所有核心接口 |

### C. 联系方式

- **API 问题反馈:** 提交 GitHub Issue
- **技术支持:** 查阅项目文档

---

**文档结束**
