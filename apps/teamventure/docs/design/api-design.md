# TeamVenture 一期（小程序）接口设计（语言无关）

> 目标：给 Python(FastAPI) 与 Java(Spring Boot) 两种实现提供同一套契约（contract-first）。
>
> 约定：ID 为字符串（前缀 + 全局唯一），例如 `user_...`、`plan_req_...`、`plan_...`、`sup_...`。

---

## 1) 通用约定

### 1.1 响应包络
```json
{ "success": true, "data": { } }
```

错误：
```json
{ "success": false, "error": { "code": "INVALID_ARGUMENT", "message": "..." } }
```

### 1.2 认证
- 小程序端：`wx.login` 获取 `code`
- 服务端：换取 `session_token`
- 后续请求：`Authorization: Bearer <session_token>`

---

## 2) Identity & Session

### 2.1 微信登录
`POST /v1/auth/wechat/login`

Request:
```json
{ "code": "wx_code_xxx" }
```

Response:
```json
{
  "success": true,
  "data": {
    "user_id": "user_01JHXXXXXXX",
    "session_token": "sess_01JHXXXXXXX",
    "expires_in_seconds": 86400
  }
}
```

---

## 3) Planning（方案）

### 3.1 创建需求并生成方案（一步到位）
`POST /v1/plans/generate`

Request:
```json
{
  "people_count": 50,
  "budget_min": 35000,
  "budget_max": 50000,
  "start_date": "2026-01-10",
  "end_date": "2026-01-11",
  "departure_city": "北京",
  "preferences": {
    "activity_types": ["team_building", "outdoor"],
    "accommodation_level": "standard",
    "dining_style": ["local"],
    "special_requirements": "无"
  }
}
```

Response:
```json
{
  "success": true,
  "data": {
    "plan_request_id": "plan_req_01JHXXXXXXX",
    "plans": [
      {
        "plan_id": "plan_01JHXXXXXXX0",
        "plan_type": "budget",
        "plan_name": "经济实惠·怀柔山野团建",
        "summary": "人均¥700，2个精选活动，农家乐住宿",
        "budget_total": 35000,
        "budget_per_person": 700
      }
    ],
    "generation_time_ms": 45000
  }
}
```

### 3.2 方案列表（我的方案）
`GET /v1/plans?page=1&page_size=10`

### 3.3 方案详情
`GET /v1/plans/{plan_id}`

### 3.4 确认方案
`POST /v1/plans/{plan_id}/confirm`

Request:
```json
{ "confirm": true }
```

### 3.5 记录联系供应商
`POST /v1/plans/{plan_id}/supplier-contacts`

Request:
```json
{
  "supplier_id": "sup_01JHXXXXXXX",
  "channel": "PHONE"
}
```

---

## 4) Supplier Catalog（供应商）

### 4.1 搜索供应商（一期简化）
`GET /v1/suppliers/search?city=北京&category=accommodation`

### 4.2 供应商详情
`GET /v1/suppliers/{supplier_id}`

---

## 5) 错误码建议（一期最小集）

- `UNAUTHENTICATED`：未登录/过期
- `INVALID_ARGUMENT`：参数校验失败
- `BUDGET_TOO_LOW`：预算不足（可返回 suggestion）
- `GENERATION_TIMEOUT`：生成超时
- `UPSTREAM_LLM_ERROR`：LLM 异常
- `NOT_FOUND`：资源不存在

