# TeamVenture 后端 API 一步一步功能测试计划（全覆盖）

目标：在前端完成前，对后端 API 做“可重复、可回归、可定位”的全覆盖功能测试；发现问题可快速复现与修复。  
适用范围：本机/测试环境（含 Docker Compose），Java 业务服务 + Python AI 服务 + MQ + Redis + MySQL + Nginx 网关。

相关材料：
- 交接说明：`apps/teamVenture/docs/qa/backend-api-functional-test-handoff.md:1`
- 全覆盖用例矩阵：`apps/teamVenture/docs/qa/backend-api-testcases-full.md:1`
- Bug 记录模板：`apps/teamVenture/docs/qa/buglist.md:1`
- Postman/Newman 使用：`apps/teamVenture/docs/qa/postman/README.md:1`
- 可执行脚本：`apps/teamVenture/docs/qa/scripts/README.md:1`

---

## 子域划分（按“出问题能快速修”组织）

1. **Gateway & Routing（网关与路由）**：Nginx 是否能正确转发 `/api/v1/*`、`/ai/*`、`/actuator/health`  
2. **Auth & Session（鉴权与会话）**：登录、token 透传、未登录/过期行为、错误码一致性  
3. **Suppliers（供应商）**：查询/过滤/详情、数据种子与 NOT_FOUND 行为  
4. **Plans API（方案业务 API）**：生成请求、列表、详情、确认幂等、联系记录  
5. **Async Pipeline（异步链路）**：Java→MQ→Python→Java 回写→落库→查询可见  
6. **Internal Callback（内部回写安全）**：`/internal/plans/batch` 的密钥校验与数据一致性  
7. **Observability（可观测性）**：日志/队列/容器状态检查，问题快速定位  

每个子域都有：
- **前置检查**（确保测的不是环境问题）
- **执行步骤**（一步一步）
- **期望结果**（判定 PASS/FAIL）
- **失败处理**（立刻该找谁/看哪类证据）

---

## 0. 测试前准备（一次性）

### 0.1 Host 与 Base URL
1) 在 QA 机器 `/etc/hosts` 添加（需管理员权限）：
```text
127.0.0.1 api.teamVenture.com
```
2) 统一 base URL（本计划默认）：
```text
http://api.teamVenture.com
```

### 0.2 环境变量（真实大模型调用）
1) 确认 `apps/teamVenture/src/.env.local` 已配置 `OPENAI_API_KEY`（不要把 key 写进 bug 里）
2) 说明：`docker-compose.yml` 已通过 `env_file` 注入 `.env.local` 给 Java/Python 服务（避免手动 export）

### 0.3 启动与基本健康
1) 启动服务（在项目根目录执行，**请明确选择环境**）：

推荐使用 `--env-file` 显式指定环境文件（避免误用默认配置）：

- 本地（默认，用 `.env.local`，也包含 `OPENAI_API_KEY`）：
```bash
docker compose --env-file apps/teamVenture/src/.env.local -f apps/teamVenture/src/docker-compose.yml up -d
```
- dev：
```bash
docker compose --env-file apps/teamVenture/src/.env.dev -f apps/teamVenture/src/docker-compose.yml up -d
```
- beta：
```bash
docker compose --env-file apps/teamVenture/src/.env.beta -f apps/teamVenture/src/docker-compose.yml up -d
```
- prod（仅用于验证时，谨慎执行）：
```bash
docker compose --env-file apps/teamVenture/src/.env.prod -f apps/teamVenture/src/docker-compose.yml up -d
```

> 说明：`apps/teamVenture/src/docker-compose.yml` 内部也配置了 `env_file: ./.env.local` 给 Java/Python 服务；  
> 但为了让 compose 自身的 `${VAR}` 替换也使用同一套环境变量，仍建议 QA 启动时显式指定 `--env-file`。

2) 启动服务（如果你仍想用默认方式，也可以，但请确保当前目录/环境变量正确）：
```bash
docker compose -f apps/teamVenture/src/docker-compose.yml up -d
```
3) 查看容器状态（必须全部 Running/Healthy）：
```bash
docker ps --filter name=teamventure- --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```
4) 如有异常，先不要开始 API 测试，转到“第 7 节 可观测性/排查”。

### 0.4 导入 Postman（推荐执行方式）
1) 导入 Collection：
`apps/teamVenture/docs/qa/postman/teamventure.postman_collection.json`
2) 导入 Environment：
`apps/teamVenture/docs/qa/postman/teamventure.postman_environment.json`
3) 选择环境后再开始执行步骤。

---

## 1. 子域：Gateway & Routing（网关与路由）

### 1.1 网关默认页（连通性）
步骤：
1) 浏览器访问：`http://api.teamVenture.com/`
期望：
- 返回 JSON：`{"message":"TeamVenture API Gateway",...}`
失败处理：
- 若 404/无法访问：检查 `/etc/hosts`、Nginx 容器、端口 80 是否被占用

### 1.2 Java 健康检查（经网关）
步骤：
1) `GET http://api.teamVenture.com/actuator/health`
期望：
- HTTP 200；body 含 `status`（通常 `UP`）
失败处理：
- 看 Nginx 日志、Java 日志（第 7 节）

### 1.3 Python 健康检查（经网关）
步骤：
1) `GET http://api.teamVenture.com/ai/health`
期望：
- HTTP 200；body 含 `status: healthy`
失败处理：
- 看 Python 日志；看 Python 容器是否 Running

---

## 2. 子域：Auth & Session（鉴权与会话）

### 2.1 登录成功（拿 token）
步骤（Postman）：
1) 运行 `Auth/Auth - WeChat Login`
期望：
- `success=true`
- `data.session_token` 非空，写入环境变量 `sessionToken`
失败处理：
- 记录请求/响应；看 Java 日志；若 500 记为 BUG（模块 auth）

### 2.2 未登录访问受保护接口
步骤：
1) 去掉 `Authorization` 调用：`GET /api/v1/plans?page=1&pageSize=10`
期望：
- HTTP 400；`error.code=UNAUTHENTICATED`
失败处理：
- 若返回 200 或 500：记 BUG（安全/鉴权）

### 2.3 鉴权格式错误
步骤：
1) Header `Authorization: {{sessionToken}}`（不带 `Bearer `）调用任一受保护接口
期望：
- HTTP 400；`UNAUTHENTICATED`
失败处理：
- 若放行：记 BUG（安全/鉴权）

### 2.4 获取当前用户信息（Token验证）
**术语对照**: `获取当前用户信息 API` = `Get Current User` = `GET /users/me`
**参考文档**: api-design.md Section 2.3, ubiquitous-language-glossary.md Section 2.1

步骤（Postman）：
1) 运行 `Auth/Users - Get Me`（使用有效token）
期望：
- HTTP 200；`success=true`
- `data.user_id` 非空（前缀 `user_`）
- `data.nickname` 与登录时的昵称一致
- `data.avatar` 为完整URL或空字符串
失败处理：
- 若 401：检查 token 是否有效（可能已过期）
- 若 500：记 BUG（模块 users）

**用途场景**:
- 登录页"继续使用"按钮点击时验证token有效性
- 前端页面初始化时验证登录状态
- 获取最新用户信息（如昵称、头像变更）

### 2.5 Token刷新（自动续期）
**术语对照**: `刷新Token API` = `Token Refresh` = `POST /auth/wechat/refresh`
**参考文档**: api-design.md Section 2.4, ubiquitous-language-glossary.md Section 4.4

步骤（Postman）：
1) 运行 `Auth/Auth - Refresh Token`（使用有效token）
期望：
- HTTP 200；`success=true`
- 如果token剩余有效期 > 12小时：`data=null`（无需刷新）
- 如果token剩余有效期 < 12小时：返回新的 `sessionToken` 和 `userInfo`
失败处理：
- 若 401：token已失效，需重新登录
- 若 500：记 BUG（模块 auth）

**测试场景**:
```bash
# 场景1：使用刚登录的token（有效期7天，不应刷新）
TOKEN="eyJhbGciOiJIUzI1NiJ9..."  # 刚登录获得的token
curl -X POST http://api.teamventure.com/api/v1/auth/wechat/refresh \
  -H "Authorization: Bearer $TOKEN"
# 期望: {"success":true,"data":null}

# 场景2：使用即将过期的token（剩余 < 12小时，应刷新）
# 需要等待token接近过期，或修改 AuthService.REFRESH_THRESHOLD_SECONDS 为更小值测试
```

**并发控制验证**:
- 前端实现了并发控制（request.js:tokenRefreshInProgress）
- 测试方法：同时发起多个需要token的请求，观察是否只触发一次刷新

### 2.6 Token过期后访问
步骤：
1) 使用已过期的token（或伪造的token）调用 `GET /users/me`
期望：
- HTTP 401；`error.code=UNAUTHENTICATED`
- `error.message` 包含 "invalid token"
失败处理：
- 若返回 200：严重安全漏洞，立即记录并通知开发

---

## 3. 子域：Suppliers（供应商）

### 3.1 查询供应商（基础）
步骤（Postman）：
1) 运行 `Suppliers/Suppliers - Search`
期望：
- `success=true`
- `data` 为数组；若执行过 seed，通常非空
- 首条 supplierId 写入环境变量 `supplierId`
失败处理：
- 若为空：确认是否已执行 `V1.0.1__seed_suppliers.sql`
- 若报错：记 BUG（模块 suppliers）

### 3.2 供应商详情（存在）
步骤（Postman）：
1) 运行 `Suppliers/Suppliers - Detail`
期望：
- `success=true`
失败处理：
- 若 NOT_FOUND：可能 seed 异常或 supplierId 字段名不一致；记录响应并提 BUG/修复映射

### 3.3 供应商详情（不存在）
步骤：
1) `GET /api/v1/suppliers/not_exist_id`
期望：
- HTTP 400；`error.code=NOT_FOUND`
失败处理：
- 若 500：记 BUG（错误处理不当）

---

## 4. 子域：Plans API（方案业务 API）

### 4.1 生成方案（异步入口）
步骤（Postman）：
1) 运行 `Plans/Plans - Generate (Async)`
期望：
- `success=true`
- 返回 `data.plan_request_id` 并写入环境变量 `planRequestId`
- 自动跳转到轮询请求（见 4.2）
失败处理：
- 若 401/UNAUTHENTICATED：回到 2.1 检查 token
- 若 500：记 BUG（plans.generate）

### 4.2 轮询直到生成 3 条方案（关键步骤）
步骤（Postman）：
1) 自动运行 `Plans/Plans - Wait Until 3 Plans Ready`（最多轮询 30 次，1s/次）
期望：
- 最终列表 records ≥ 3
- 自动写入 `planId`（取第一条）
失败处理（按优先级排查）：
1) 看 MQ 队列是否积压（第 7.2）
2) 看 Python 是否收到 message（第 7.1）
3) 看 Java 内部回写是否失败（Python 日志会打印 callback 失败）
4) 若长时间无结果：记 BUG（异步链路）

### 4.3 方案列表（有数据）
步骤（Postman）：
1) 运行 `Plans/Plans - List`
期望：
- `success=true` 且 records 非空
失败处理：
- 若空：按 4.2 的“失败处理”定位

### 4.4 方案详情（本人）
步骤（Postman）：
1) 运行 `Plans/Plans - Detail`
期望：
- `success=true`
失败处理：
- NOT_FOUND：planId 未正确写入环境变量；或落库失败

### 4.5 确认方案（幂等）
步骤（Postman）：
1) 运行 `Plans/Plans - Confirm (Idempotent)` 两次
期望：
- 两次都 `success=true`
失败处理：
- 第二次失败：记 BUG（幂等性）

### 4.6 记录联系供应商
步骤（Postman）：
1) 运行 `Plan Supplier Contacts/Plans - Record Supplier Contact`
期望：
- `success=true`
失败处理：
- 若返回 200 但实际不写入：需要补 DB 校验或补接口校验（记录为 BUG）

---

## 5. 子域：Async Pipeline（异步链路专项验证）

本子域的目标是把“问题定位到哪个服务/组件”，便于开发及时修复。

### 5.1 MQ 入队验证（Java → RabbitMQ）
步骤：
1) 触发一次 `POST /api/v1/plans/generate`（见 4.1）
2) 立即查看队列：
```bash
docker exec teamventure-rabbitmq rabbitmqctl list_queues name messages consumers | sed -n '1,60p'
```
期望：
- `ai.gen.req.queue` 的 `consumers` 为 1
- `messages` 短暂上升后回到 0
失败处理：
- consumers=0：Python MQ consumer 未启动（看 Python 日志）
- messages 持续上升：Python 消费/处理能力问题或异常退出

### 5.2 Python 消费与生成（RabbitMQ → Python workflow）
步骤：
1) 查看 Python 日志：
```bash
docker logs --tail=200 teamventure-python
```
期望日志关键字：
- `Received plan generation message: <plan_request_id>`
- `workflow start` / `requirements parsed` / `suppliers matched` / `plans generated`
失败处理：
- 没收到 message：MQ 连接/队列绑定问题
- workflow 报错：记录异常堆栈，直接提 BUG（模块 ai-service/mq）

### 5.3 回写 Java（Python → /internal/plans/batch）
步骤：
1) 在 Python 日志中观察 callback 是否报错（关键字 `Java callback failed`）
2) 如怀疑密钥问题，核对：
   - Java：`TEAMVENTURE_AI_SERVICE_CALLBACK_SECRET`
   - Python：`JAVA_INTERNAL_SECRET`
期望：
- Python 不应出现 callback 4xx/5xx
失败处理：
- 401/UNAUTHORIZED：内部密钥不一致（属于配置问题，优先修）

### 5.4 落库可见（Java 回写 → GET plans）
步骤：
1) `GET /api/v1/plans` 应出现 3 条 plans
2) `GET /api/v1/plans/{planId}` 可查到详情
失败处理：
- 若 Python 已生成但 Java 查不到：优先查 Java 回写/DB 插入异常

---

## 6. 子域：Internal Callback（内部回写安全）

仅在隔离环境执行，避免误触生产数据。

### 6.1 密钥错误应拒绝
步骤：
1) `POST /internal/plans/batch`，Header：`X-Internal-Secret: wrong`
期望：
- `success=false`，`error.code=UNAUTHORIZED`
失败处理：
- 若被放行：严重安全缺陷（S0-blocker）

---

## 7. 子域：Observability（可观测性与快速定位）

### 7.1 一键看关键容器日志（出现问题优先收集）
```bash
docker logs --tail=200 teamventure-nginx
docker logs --tail=200 teamventure-java
docker logs --tail=200 teamventure-python
```

### 7.2 一键看 MQ 队列积压与消费者
```bash
docker exec teamventure-rabbitmq rabbitmqctl list_queues name messages consumers | sed -n '1,60p'
```

### 7.3 一键确认服务仍在运行
```bash
docker ps --filter name=teamventure- --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

---

## 8. 缺陷记录与修复闭环（强制执行）

### 8.1 记录位置
- 缺陷清单：`apps/teamVenture/docs/qa/buglist.md:1`

### 8.2 每条缺陷最少附带信息（否则不进入修复）
- Env（本机/测试/预发）
- API path + 请求/响应（脱敏）
- `plan_request_id`（如涉及生成）
- 对应时间窗口的 `teamventure-java` / `teamventure-python` / `teamventure-nginx` 日志片段

### 8.3 建议的修复优先级（便于及时修）
- **P0/S0**：鉴权绕过、内部回写密钥失效、生成链路完全不可用、数据越权
- **P1/S1**：生成不稳定、错误码不一致导致前端无法处理、幂等失败
- **P2/S2**：参数校验缺失、非关键字段映射问题

---

## 9. 退出准则（全覆盖完成的判定）

满足以下全部条件：
1) 覆盖矩阵中的所有接口至少跑过一次 happy path
2) 所有“鉴权负向用例”均通过（至少 UNAUTHENTICATED 生效）
3) 生成链路至少连续跑通 3 次（避免偶发）：
   - 入队→消费→生成→回写→列表可见 3 条
4) `buglist.md` 中 P0/S0 缺陷为 0；P1 缺陷有明确修复计划或已修复验证
