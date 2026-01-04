# TeamVenture 后端 API 功能测试用例（全覆盖）

覆盖对象（当前版本代码）：
- Java（业务）：`/api/v1/auth/wechat/*`、`/api/v1/plans/*`、`/api/v1/suppliers/*`、`/internal/plans/batch`
- Python（AI）：`/health`、`/`、`/api/v1/plans/generate`（HTTP 调试）；以及 MQ 消费链路
- Nginx：`/api/v1/*`、`/actuator/health`、`/ai/*`

配套交接说明：`apps/teamVenture/docs/qa/backend-api-functional-test-handoff.md:1`

---

## 0. 统一约定（所有接口）

### 0.1 响应包裹（Java）
Java 接口统一返回：
```json
{ "success": true, "data": <any> }
```
或失败：
```json
{ "success": false, "error": { "code": "XXX", "message": "..." } }
```

### 0.2 鉴权（除登录外）
- Header：`Authorization: Bearer <session_token>`
- 缺失/格式不对：应返回 HTTP `400`，`error.code=UNAUTHENTICATED`

### 0.3 必备测试数据
- 初始化 DB（含供应商种子数据）：`apps/teamVenture/src/database/schema/V1.0.0__init.sql`、`apps/teamVenture/src/database/schema/V1.0.1__seed_suppliers.sql`

---

## 1. 覆盖矩阵（接口列表）

| 模块 | 方法 | Path | 鉴权 | 备注 |
|---|---:|---|---|---|
| auth | POST | `/api/v1/auth/wechat/login` | 否 | 返回 `session_token` |
| plans | POST | `/api/v1/plans/generate` | 是 | 异步：入 MQ，等待 Python 回写 |
| plans | GET | `/api/v1/plans` | 是 | 列表分页 |
| plans | GET | `/api/v1/plans/{planId}` | 是 | 仅本人可见 |
| plans | POST | `/api/v1/plans/{planId}/confirm` | 是 | 幂等 |
| plans | POST | `/api/v1/plans/{planId}/supplier-contacts` | 是 | 写联系记录 |
| suppliers | GET | `/api/v1/suppliers` | 是 | 可选 city/category |
| suppliers | GET | `/api/v1/suppliers/{supplierId}` | 是 | 详情 |
| internal | POST | `/internal/plans/batch` | 内部密钥 | Python 回写入口 |
| ops | GET | `/actuator/health` | 否（当前） | 走网关转发 |
| ai-debug | GET | `/ai/health` | 否 | 走网关转发到 Python |
| ai-debug | POST | `/ai/api/v1/plans/generate` | 否 | Python HTTP 调试接口 |

---

## 2. 用例（逐接口全覆盖）

说明：
- “请求/响应”示例中请 QA 按环境替换域名与 token。
- 除非特别说明，默认走网关：`http://<gateway-host>`

### 2.1 Auth：微信登录（v1.2 更新）

**API 签名（v1.2）**：
```
POST /api/v1/auth/wechat/login
Content-Type: application/json

Request Body:
{
  "code": "string",        // 必填：微信登录 code
  "nickname": "string",    // 可选：用户昵称
  "avatarUrl": "string"    // 可选：用户头像 URL
}

Response (成功):
{
  "success": true,
  "data": {
    "sessionToken": "JWT_TOKEN_STRING",
    "userInfo": {
      "user_id": "user_xxx",
      "nickname": "用户昵称",
      "avatar": "https://thirdwx.qlogo.cn/...",
      "phone": "",
      "company": "",
      "role": "user"
    }
  }
}
```

---

#### 2.1.1 基础登录功能

**TC-AUTH-001 登录成功（提供完整信息）**
- API：`POST /api/v1/auth/wechat/login`
- Body：
```json
{
  "code": "qa-code-001",
  "nickname": "测试用户001",
  "avatarUrl": "https://thirdwx.qlogo.cn/mmopen/test001.jpg"
}
```
- 期望：
  - HTTP 200，`success=true`
  - `data.sessionToken` 非空（JWT格式）
  - `data.userInfo.user_id` 非空
  - `data.userInfo.nickname` 为 "测试用户001"
  - `data.userInfo.avatar` 为传入的 avatarUrl
  - `data.userInfo.role` 为 "user"
- 验证数据库：
  - `users` 表中存在该用户记录
  - `nickname` 字段为 "测试用户001"
  - `avatar_url` 字段为传入的 URL
  - `wechat_openid` 非空（基于 code 生成的伪 openid）
- 验证 Redis：
  - 存在 session key：`session:{user_id}`
  - session 数据包含 token 信息

**TC-AUTH-002 登录成功（仅提供 code）**
- Body：`{"code":"qa-code-002"}`
- 期望：
  - HTTP 200，`success=true`
  - `data.userInfo.nickname` 为默认值 "微信用户"
  - `data.userInfo.avatar` 为空字符串 `""`
- 验证数据库：
  - `users` 表中 `nickname` 为 "微信用户"
  - `avatar_url` 为空字符串

**TC-AUTH-003 登录成功（提供 nickname，不提供 avatarUrl）**
- Body：
```json
{
  "code": "qa-code-003",
  "nickname": "只有昵称的用户"
}
```
- 期望：
  - HTTP 200，`success=true`
  - `data.userInfo.nickname` 为 "只有昵称的用户"
  - `data.userInfo.avatar` 为空字符串 `""`

**TC-AUTH-004 登录成功（提供 avatarUrl，不提供 nickname）**
- Body：
```json
{
  "code": "qa-code-004",
  "avatarUrl": "https://thirdwx.qlogo.cn/mmopen/test004.jpg"
}
```
- 期望：
  - HTTP 200，`success=true`
  - `data.userInfo.nickname` 为默认值 "微信用户"
  - `data.userInfo.avatar` 为传入的 URL

---

#### 2.1.2 重复登录与信息更新

**TC-AUTH-010 重复登录（同一 openid，不同信息）**
- 步骤：
  1. 第一次登录：`{"code":"qa-code-010","nickname":"旧昵称","avatarUrl":"https://old.jpg"}`
  2. 第二次登录（模拟同一微信用户）：`{"code":"qa-code-010-repeat","nickname":"新昵称","avatarUrl":"https://new.jpg"}`
- 期望：
  - 两次登录的 `data.userInfo.user_id` 相同（因为 openid 相同）
  - 第二次登录返回的 `nickname` 为 "新昵称"
  - 第二次登录返回的 `avatar` 为 "https://new.jpg"
  - 两次 `sessionToken` 不同（每次登录生成新 token）
  - 两次 token 均可用于后续 API 调用
- 验证数据库：
  - `users` 表中该用户的 `nickname` 已更新为 "新昵称"
  - `avatar_url` 已更新为 "https://new.jpg"
  - 仅有一条用户记录（不会重复创建）

**TC-AUTH-011 重复登录（不提供新信息）**
- 步骤：
  1. 第一次登录：`{"code":"qa-code-011","nickname":"原始昵称","avatarUrl":"https://original.jpg"}`
  2. 第二次登录：`{"code":"qa-code-011-repeat"}`（仅提供 code）
- 期望：
  - 第二次登录返回的信息保持不变：
    - `nickname` 仍为 "原始昵称"
    - `avatar` 仍为 "https://original.jpg"
  - 数据库中用户信息未被覆盖为默认值

---

#### 2.1.3 边界情况与数据验证

**TC-AUTH-020 nickname 包含前后空格**
- Body：`{"code":"qa-code-020","nickname":"  有空格的昵称  "}`
- 期望：
  - `data.userInfo.nickname` 为 "有空格的昵称"（已 trim）
- 验证数据库：
  - `nickname` 字段无前后空格

**TC-AUTH-021 nickname 为空字符串**
- Body：`{"code":"qa-code-021","nickname":""}`
- 期望：
  - `data.userInfo.nickname` 为默认值 "微信用户"

**TC-AUTH-022 nickname 仅包含空格**
- Body：`{"code":"qa-code-022","nickname":"   "}`
- 期望：
  - trim 后为空，使用默认值 "微信用户"

**TC-AUTH-023 nickname 包含特殊字符**
- Body：`{"code":"qa-code-023","nickname":"昵称@#$%^&*()"}`
- 期望：
  - 按原样存储和返回（或按产品需求过滤，记录实际行为）

**TC-AUTH-024 nickname 超长（>64字符）**
- Body：包含65+字符的昵称
- 期望：
  - 按数据库schema限制（VARCHAR(64)），应截断或返回错误
  - 记录实际行为：成功则截断，失败则返回 400

**TC-AUTH-025 avatarUrl 为空字符串**
- Body：`{"code":"qa-code-025","avatarUrl":""}`
- 期望：
  - `data.userInfo.avatar` 为空字符串 `""`
  - 前端应显示占位符

**TC-AUTH-026 avatarUrl 格式非法（非URL）**
- Body：`{"code":"qa-code-026","avatarUrl":"not-a-url"}`
- 期望：
  - 按产品需求决定：直接存储或验证URL格式
  - 记录实际行为

**TC-AUTH-027 avatarUrl 超长（>255字符）**
- Body：包含256+字符的URL
- 期望：
  - 按数据库schema限制（VARCHAR(255)），应截断或返回错误

---

#### 2.1.4 错误场景

**TC-AUTH-030 缺少 code**
- Body：`{}`
- 期望：HTTP `400`，`error.code=VALIDATION_ERROR` 或类似，消息包含 "code不能为空"

**TC-AUTH-031 code 为空字符串**
- Body：`{"code":""}`
- 期望：HTTP `400`（Jakarta validation），`error.code` 为 `VALIDATION_ERROR`

**TC-AUTH-032 code 为 null**
- Body：`{"code":null}`
- 期望：HTTP `400`

**TC-AUTH-033 微信 API 返回无效 code**
- Body：`{"code":"INVALID_WX_CODE"}`
- 期望：
  - HTTP 200 但 `success=false`，`error.code=INVALID_WX_CODE` 或类似
  - 或 HTTP 401
  - 不应返回 500

**TC-AUTH-034 请求体格式错误（非 JSON）**
- Body：`not-json`
- Header：`Content-Type: application/json`
- 期望：HTTP `400`

---

#### 2.1.5 会话与鉴权验证

**TC-AUTH-040 登录后使用 token 访问受保护接口**
- 步骤：
  1. 登录获取 `sessionToken`
  2. 使用该 token 调用 `GET /api/v1/plans`
- 期望：
  - 第2步成功返回，不返回 `UNAUTHENTICATED`

**TC-AUTH-041 token 格式验证**
- 期望：
  - 返回的 `sessionToken` 符合 JWT 格式（三段式，base64 编码）
  - 可被解析，payload 包含 `user_id`

**TC-AUTH-042 session 过期**
- 步骤：
  1. 登录获取 token
  2. 手动从 Redis 删除该 session
  3. 使用该 token 访问受保护接口
- 期望：
  - 第3步返回 HTTP `400` 或 `401`，`error.code=UNAUTHENTICATED`

---

#### 2.1.6 并发与压力测试

**TC-AUTH-050 并发登录（同一用户）**
- 10个并发请求，相同 code（模拟同一 openid）
- 期望：
  - 所有请求返回成功
  - 数据库中仅有一条用户记录
  - 无死锁或重复插入错误

**TC-AUTH-051 并发登录（不同用户）**
- 100个并发请求，不同 code
- 期望：
  - 所有请求返回成功
  - 数据库中有100条用户记录
  - 平均响应时间 < 500ms

---

#### 2.1.7 性能基准

**TC-AUTH-060 登录性能基准**
- 单用户登录（提供完整信息）
- 期望：
  - P50 响应时间 < 200ms
  - P95 响应时间 < 500ms
  - P99 响应时间 < 1000ms

**TC-AUTH-061 Redis 连接池正常**
- 批量登录100次
- 期望：
  - Redis 连接池无泄漏
  - 查看 Druid actuator 端点，空闲连接正常回收

---

### 2.2 Plans：发起生成（异步链路核心）

**TC-PLAN-GEN-001 生成请求成功（happy path）**
- API：`POST /api/v1/plans/generate`
- Header：`Authorization: Bearer <token>`
- Body（示例）：
```json
{
  "people_count": 50,
  "budget_min": 25000,
  "budget_max": 35000,
  "start_date": "2026-01-10",
  "end_date": "2026-01-11",
  "departure_city": "北京",
  "preferences": { "theme": "户外" }
}
```
- 期望：
  - 立即返回：`success=true`，`data.plan_request_id` 非空，`data.status="generating"`
  - 观测：RabbitMQ `ai.gen.req.queue` 短暂 messages 增加后归零；Python 日志出现该 `plan_request_id`
  - 最终：`GET /api/v1/plans` 能查询到 3 条计划（通常 10~60s，取决于 LLM/网络/资源）

**TC-PLAN-GEN-002 鉴权缺失**
- Header 不带 `Authorization`
- 期望：HTTP `400`，`error.code=UNAUTHENTICATED`

**TC-PLAN-GEN-003 鉴权格式错误**
- Header：`Authorization: <token>`
- 期望：HTTP `400`，`error.code=UNAUTHENTICATED`

**TC-PLAN-GEN-010 people_count 边界**
- 0 / 1 / 500 / 501
- 期望：按后端实际校验记录缺陷或补需求；至少不应 500 崩溃

**TC-PLAN-GEN-011 budget_min/budget_max 边界**
- min=0、max<min、极大值（例如 1e12）
- 期望：不应 500 崩溃；若返回成功但生成异常，应在 Python/回写日志可观测

**TC-PLAN-GEN-012 日期边界**
- end<start、跨月、格式非法（`2026/01/10`）
- 期望：不应 500 崩溃（如目前未校验则记录缺陷）

**TC-PLAN-GEN-020 preferences 为空/缺失**
- `preferences` 缺失或 `{}` 或 `null`
- 期望：生成请求仍成功

**TC-PLAN-GEN-030 异步链路可观测性**
- 记录并关联：
  - Java 返回的 `plan_request_id`
  - MQ message 内 `trace_id`（可从 Python 回写 payload 观察）
  - Python 日志的 workflow 进度（parse/match/generate）
- 期望：三者能串起来定位问题

---

### 2.3 Plans：列表

**TC-PLAN-LIST-001 列表成功（空）**
- 新用户刚登录，未生成方案
- API：`GET /api/v1/plans?page=1&pageSize=10`
- 期望：`success=true`，返回分页结构（MyBatis-Plus Page），records 为空

**TC-PLAN-LIST-002 列表成功（有数据）**
- 先跑一次 `generate` 并等待回写
- 期望：records 至少 3 条；按 `create_time` 倒序

**TC-PLAN-LIST-003 分页参数边界**
- page=0、page=-1、pageSize=0、pageSize=1000
- 期望：不应 500 崩溃；记录实际行为（必要时提缺陷/补需求）

**TC-PLAN-LIST-010 鉴权缺失/错误**
- 同 2.2 的鉴权用例

---

### 2.4 Plans：详情

**TC-PLAN-DETAIL-001 详情成功**
- 前置：列表取一个 `plan_id`
- API：`GET /api/v1/plans/{planId}`
- 期望：`success=true`，data.plan_id 匹配

**TC-PLAN-DETAIL-002 planId 不存在**
- planId 随便填
- 期望：HTTP `400`（BizException），`error.code=NOT_FOUND`

**TC-PLAN-DETAIL-003 越权访问**
- 用户 A 生成一条 plan，用户 B 用自己的 token 查 A 的 planId
- 期望：HTTP `400`，`error.code=UNAUTHORIZED`

---

### 2.5 Plans：确认（幂等）

**TC-PLAN-CONFIRM-001 确认成功**
- API：`POST /api/v1/plans/{planId}/confirm`
- 期望：`success=true`

**TC-PLAN-CONFIRM-002 重复确认幂等**
- 连续调用两次 confirm
- 期望：都返回 `success=true`；第二次不应报错（当前实现：已 confirmed 直接 return）

**TC-PLAN-CONFIRM-003 planId 不存在**
- 期望：`NOT_FOUND`

**TC-PLAN-CONFIRM-004 越权确认**
- 期望：`UNAUTHORIZED`

---

### 2.6 Plans：记录联系供应商

**TC-PLAN-CONTACT-001 记录成功**
- API：`POST /api/v1/plans/{planId}/supplier-contacts`
- Body：`{"supplier_id":"sup_xxx","channel":"PHONE","notes":"qa-run-001"}`
- 期望：`success=true`

**TC-PLAN-CONTACT-002 缺少必填字段**
- Body 缺 `supplier_id` / `channel`
- 期望：HTTP `400`

**TC-PLAN-CONTACT-003 channel 非法枚举**
- `channel="UNKNOWN"`
- 期望：当前实现未做枚举校验，按实际记录（建议作为缺陷或需求确认）

**TC-PLAN-CONTACT-010 planId 不存在/越权**
- 期望：当前实现未校验 plan 是否存在/归属（只写 contactLog），按实际记录并提缺陷（数据一致性/安全）

---

### 2.7 Suppliers：查询与详情

**TC-SUP-001 查询成功**
- API：`GET /api/v1/suppliers`
- 期望：`success=true`，列表非空（需 seed）

**TC-SUP-002 带 city/category 过滤**
- `GET /api/v1/suppliers?city=北京&category=...`
- 期望：返回按条件过滤（按实际实现记录）

**TC-SUP-003 详情成功**
- 从列表取 `supplierId` 调 `GET /api/v1/suppliers/{supplierId}`
- 期望：`success=true`

**TC-SUP-004 supplierId 不存在**
- 期望：当前实现可能返回 null 或报错（取决于 service），按实际记录并提缺陷/补需求

**TC-SUP-010 鉴权缺失**
- 期望：`UNAUTHENTICATED`

---

### 2.8 Internal：回写接口（安全性与数据一致性）

**TC-INTERNAL-001 密钥错误**
- API：`POST /internal/plans/batch`
- Header：`X-Internal-Secret: wrong`
- 期望：HTTP `200` 但 `success=false`，`error.code=UNAUTHORIZED`

**TC-INTERNAL-002 回写成功（可选：仅用于验证落库）**
- Header：正确 `X-Internal-Secret`
- Body（最小可用）：
```json
{
  "plan_request_id": "plan_req_xxx",
  "user_id": "user_xxx",
  "plans": [ { "plan_id":"plan_xxx", "plan_type":"standard" } ],
  "trace_id": "trace_xxx"
}
```
- 期望：plans 写入 DB；plan_request 状态更新为 COMPLETED

> 注意：该接口为内部通道，建议 QA 仅在隔离环境执行，避免污染真实数据。

---

### 2.9 Ops / AI Debug（可用性冒烟）

**TC-OPS-001 Java 健康检查**
- `GET /actuator/health`
- 期望：200 且 `status` 为 `UP`（按 actuator 输出）

**TC-AI-001 Python 健康检查（经网关）**
- `GET /ai/health`
- 期望：200 且 `{"status":"healthy",...}`

**TC-AI-002 Python HTTP 调试接口**
- `POST /ai/api/v1/plans/generate`
- 期望：200，返回 “note: 生产环境请使用MQ方式”（仅用于证明服务可用）

