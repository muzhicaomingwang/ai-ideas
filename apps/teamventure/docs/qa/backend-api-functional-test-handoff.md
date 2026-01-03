# TeamVenture 后端 API 功能测试交接（给 QA）

面向：在前端开发完成前，对已上线的后端 API 做功能验证与回归基线建立。  
覆盖：Java 业务服务（主）、Python AI 服务（异步生成）、Nginx 网关、RabbitMQ、Redis、MySQL。

---

## 1. 测试目标与范围（建议）

全覆盖用例清单（逐接口）：`apps/teamVenture/docs/qa/backend-api-testcases-full.md:1`

### P0（必须）
- 登录拿到 `session_token`（鉴权可用）
- 生成方案主链路可跑通：`生成请求 → MQ → Python 消费 → 回写 Java → 查询到 3 套方案`
- 方案列表/详情查询可用（权限隔离：只能看自己的）
- 方案确认接口幂等（重复确认不报错）
- 供应商查询/详情接口可用（鉴权必需）
- 供应商联系记录接口可用（写入成功）

### P1（建议）
- 参数校验边界（人数/预算/日期/城市）
- 错误码与 HTTP 状态码一致性（401/400/404/500）
- 依赖异常的行为（MQ/Redis/AI 不可用时）：是否可观测、返回是否可理解

---

## 2. 环境与入口（开发/测试默认）

### 2.0 Host 映射（本机 Nginx 测试）
如本机通过 Nginx 网关测试，建议在 `/etc/hosts` 配置：
- `127.0.0.1 api.teamVenture.com`

### 2.1 通过 Nginx 访问（推荐）
- 网关（Nginx）：`http://localhost:80`
- 推荐 base URL：`http://api.teamVenture.com`（配合 hosts 映射）
- Java 业务 API：`http://localhost/api/v1/*`（会转发到 `java-business-service:8080`）
- Java 健康检查：`http://localhost/actuator/health`
- Python AI（调试用途）：`http://localhost/ai/*`（会转发到 `python-ai-service:8000`）

### 2.2 直连服务（可选）
- Java：`http://localhost:8080`
- Python：`http://localhost:8000`
- RabbitMQ 管理台：`http://localhost:15672`（默认 `admin/admin123456`）
- Redis：`localhost:6379`（默认密码 `redis123456`）
- MySQL：`localhost:3306`（默认 `root/root123456`，库 `teamventure_main`）

> Docker Compose 文件：`apps/teamVenture/src/docker-compose.yml:1`  
> Nginx 配置：`apps/teamVenture/src/nginx/nginx.conf:1`

---

## 3. 鉴权与测试账号（当前实现说明）

### 3.1 登录
接口：`POST /api/v1/auth/wechat/login`  
请求体：
```json
{ "code": "any-string-for-test" }
```
响应体（成功时 `success=true`）包含：
- `data.user_id`
- `data.session_token`
- `data.expires_in_seconds`

### 3.2 业务接口鉴权头
除登录外，均要求：
- `Authorization: Bearer <session_token>`

> 当前 Java 登录实现是“伪 openid”（由 code hash 得到），适合 QA 自造 `code` 测试用（不依赖微信真接口）。

---

## 4. 可测 API 清单（当前版本）

以下均以网关形式举例（`http://localhost`）。

### 4.1 登录
- `POST /api/v1/auth/wechat/login`

### 4.2 方案
- `POST /api/v1/plans/generate`：发起方案生成（异步）
- `GET /api/v1/plans?page=1&pageSize=10`：我的方案列表
- `GET /api/v1/plans/{planId}`：方案详情（仅本人可见）
- `POST /api/v1/plans/{planId}/confirm`：确认方案（幂等）
- `POST /api/v1/plans/{planId}/supplier-contacts`：记录联系供应商

### 4.3 供应商
- `GET /api/v1/suppliers?city=...&category=...`：筛选/查询
- `GET /api/v1/suppliers/{supplierId}`：详情

### 4.4 内部回写（不建议 QA 直接测，除非做安全性验证）
- `POST /internal/plans/batch`
  - Header：`X-Internal-Secret: <secret>`
  - 说明：Python 消费完生成结果后回调该接口写入 plans，并把 plan_request 状态置为 `COMPLETED`。

---

## 5. 方案生成主链路（E2E）如何验证

### 5.1 发起生成
`POST /api/v1/plans/generate`，请求体字段（必填）：
- `people_count`（int）
- `budget_min`/`budget_max`（number）
- `start_date`/`end_date`（string）
- `departure_city`（string）
- `preferences`（object，可空）

响应示例：
```json
{
  "success": true,
  "data": { "plan_request_id": "plan_req_xxx", "status": "generating" }
}
```

### 5.2 观察进度（推荐手段）
- RabbitMQ 队列：`ai.gen.req.queue` 的 `messages`（积压）与 `consumers`（消费者数）
- Python 日志：出现 `Received plan generation message: <plan_request_id>`，以及 `workflow start`/`requirements parsed`/`suppliers matched`/`plans generated`
- Java 日志：启动正常即可；当前回写成功不一定有显式日志（可按需补充）

### 5.3 验证结果落库（功能层面）
`GET /api/v1/plans` 轮询 10~30 秒（取决于 LLM/网络），应出现 3 条 `plan_type` 不同的方案记录；取其中 `plan_id` 再调详情接口。

---

## 6. Python 大模型调用说明（QA 关注点）

### 6.1 模型与密钥来源
- 环境变量：
  - `OPENAI_API_KEY`
  - `OPENAI_MODEL`（默认 `gpt-4-0125-preview`）
  - `OPENAI_TEMPERATURE` / `OPENAI_MAX_TOKENS`
- 代码入口：
  - `apps/teamVenture/src/backend/python-ai-service/src/integrations/openai_client.py:1`
  - `apps/teamVenture/src/backend/python-ai-service/src/services/plan_generation.py:1`

### 6.2 无 key 的行为（避免环境不全导致整体不可测）
如果 `OPENAI_API_KEY` 为空，Python 会降级使用“确定性 stub”生成 3 套方案（仍可验证 MQ/回写/查询链路）。  
如果 QA 要验证真实大模型链路，请确保 `OPENAI_API_KEY` 已注入到 `python-ai-service` 容器环境变量。

建议：将 key 写入 `apps/teamVenture/src/.env.local`，并通过 compose `env_file` 注入（避免手动 export）。

---

## 7. 测试数据与初始化

- 数据库初始化脚本目录：`apps/teamVenture/src/database/schema`
  - `V1.0.0__init.sql`（建表）
  - `V1.0.1__seed_suppliers.sql`（供应商种子数据）

建议 QA 执行策略：
- 功能测试优先使用“固定 code → 固定 user_id”形成可复跑基线；
- 每轮回归加 `test_run_id` 到 notes/preferences 中，便于日志与数据检索；
- 如在共享环境，避免用真实手机号/真实个人信息。

---

## 8. 常见问题与排查清单（QA 自查）

- 生成后一直查不到 plans：
  - RabbitMQ 队列是否有积压（messages>0）？
  - Python 是否已启动且 `consumers=1`？
  - Python 日志是否有收到 message/是否报错？
  - Java 内部回写是否 401（`X-Internal-Secret` 不一致）？
- Redis 相关异常：
  - 鉴权失败/Token 失效：检查 `Authorization` 格式与 Redis 连接/密码
- MySQL 相关异常：
  - 供应商查询为空：检查是否执行了 seed 脚本

---

## 9. QA 反馈格式（建议）

请在缺陷中附带：
- 接口路径 + 请求/响应（脱敏）
- `plan_request_id` / `trace_id`（如果有）
- Java/Python 对应时间窗口的日志片段
- 环境（dev/staging/prod）与构建版本（镜像 tag 或 commit）
