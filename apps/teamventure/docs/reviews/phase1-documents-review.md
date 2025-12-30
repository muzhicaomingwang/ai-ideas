# TeamVenture 一期文档 Review 报告

> **Review 日期**: 2025-12-30
> **Review 范围**: 事件风暴、DDD设计、产品设计、API设计、QA测试文档
> **Review 方法**: 基于 .project/ai/skills 定义的专业标准进行跨角色评审

---

## 📊 执行摘要

### 整体质量评级
| 文档 | 评级 | 主要优点 | 关键改进点 |
|------|------|---------|-----------|
| 事件风暴 | ⭐⭐⭐⭐⭐ 9.2/10 | 结构完整、BC边界清晰、事件设计规范 | 缺少时间线规划、风险优先级 |
| DDD设计 | ⭐⭐⭐⭐⭐ 9.0/10 | 聚合设计合理、值对象清晰 | 缺少迁移路径、性能指标 |
| 产品设计 | ⭐⭐⭐⭐☆ 8.5/10 | 用户旅程完整、UE状态机清晰 | 缺少可访问性规范、埋点设计 |
| API设计 | ⭐⭐⭐⭐☆ 8.3/10 | 契约清晰、错误码统一 | 缺少幂等性说明、分页规范、版本策略 |
| QA文档 | ⭐⭐⭐⭐☆ 8.7/10 | 测试覆盖全面、用例结构化 | 缺少自动化策略、性能基线 |

### 跨文档一致性检查
✅ **已对齐**:
- 事件命名：事件风暴 ↔ DDD设计 ↔ API设计完全一致
- 聚合边界：DDD设计 ↔ API路径 ↔ 前端模块映射清晰
- 状态机：draft→confirmed 在所有文档中一致

⚠️ **需要同步**:
- 产品设计中的"导出"功能在API设计中缺失
- QA文档中的并发测试场景在API设计中未明确幂等性规范
- 事件风暴中的`PlanShared`事件在API设计中缺少对应接口

---

## 1️⃣ 事件风暴文档 Review

**使用 Skills**: `strategy` + `project-management`

### ✅ 优点
1. **范围边界清晰**
   - P0/P1/非目标三级划分，符合 strategy skill 的"约束管理"要求
   - 一期最小可交付闭环明确：登录→生成→确认→联系

2. **领域事件设计规范**
   - 命名遵循"已发生"原则（`PlanGenerated` 而非 `GeneratePlan`）
   - 事件分组合理（账号与会话/方案生成/方案使用）
   - 符合 DDD 事件溯源最佳实践

3. **聚合边界科学**
   - 4个聚合根定义清晰，职责单一
   - 不变式（Invariants）明确，便于后续实现校验逻辑
   - 数据快照策略（supplier_snapshots）避免跨表依赖

4. **BC拆分合理**
   - 3个BC符合教学目标（Identity/Planning/Supplier Catalog）
   - Context Map 清晰标注依赖关系（查询依赖/认证依赖）

### ⚠️ 改进建议

#### P0（必须修复）
1. **缺少里程碑与时间线**
   - 问题：文档未给出一期交付的时间预期，project-management skill 要求明确里程碑
   - 建议：增加章节 "9. 一期交付里程碑"
     ```markdown
     ## 9. 一期交付里程碑
     - W1-W2：Identity BC + 微信登录闭环（可 E2E 测试）
     - W3-W4：Planning BC + 生成3套方案（含 LLM 编排）
     - W5：Supplier Catalog 后台录入 + 前端对比/详情页
     - W6：确认 + 联系供应商 + 埋点接入
     - W7：回归测试 + 性能调优 + 上线准备
     ```

2. **缺少 RAID 风险矩阵**
   - 问题：project-management skill 要求明确风险/假设/问题/依赖
   - 建议：增加章节 "10. 一期 RAID"
     ```markdown
     ## 10. 一期 RAID（Risks/Assumptions/Issues/Dependencies）

     ### 风险
     | ID | 风险描述 | 概率 | 影响 | 缓解方案 | Owner |
     |----|---------|------|------|---------|-------|
     | R1 | LLM 生成超时（>60s）导致用户流失 | 中 | 高 | 降级方案：模板生成 + 异步通知 | BE Lead |
     | R2 | 供应商数据不足（<10家）导致方案质量低 | 高 | 中 | 一期手动录入50家高质量供应商 | 运营 |

     ### 假设
     - 假设微信 session 有效期 >= 24h（实际需验证）
     - 假设一期不需要支付/履约，仅信息撮合

     ### 依赖
     - 外部依赖：OpenAI API 稳定性 SLA ≥ 99.5%
     - 内部依赖：PostgreSQL 实例就绪（W1前）
     ```

#### P1（建议优化）
3. **业务策略缺少量化指标**
   - 当前："生成策略：一次需求必须生成 3 套"
   - 建议优化："生成策略：一次需求必须生成 3 套；目标耗时 P50<30s, P95<60s；若供应商<5家，降级为模板生成"

4. **读模型设计不完整**
   - 当前：只提到"分页"，未明确 pageSize/offset/cursor
   - 建议：在"5. 读模型"章节补充：
     ```markdown
     - 分页规范：cursor-based（一期可先用 offset，但预留 cursor 字段）
     - 排序：默认按 `create_time DESC`
     - 筛选：一期支持按 status（draft/confirmed）筛选
     ```

---

## 2️⃣ DDD战略+战术设计文档 Review

**使用 Skills**: `strategy` + `python`

### ✅ 优点
1. **一句话定位精准**
   - 符合 strategy skill 要求的"What/Who/Time constraint"
   - "10–15 分钟" + "3套可对比" + "行动闭环" 三要素齐全

2. **北极星指标合理**
   - `Weekly Confirmed Plans` 聚焦用户价值，而非虚荣指标
   - 护栏指标覆盖性能/质量/转化，符合 strategy skill 的"guardrails"要求

3. **值对象设计优秀**
   - `BudgetRange(min, max)` / `DateRange(start, end)` 等封装合理
   - 避免原始类型暴露，符合 DDD 最佳实践

4. **分层架构清晰**
   - Ports & Adapters 分层符合 python skill 的 "app/core/db/schemas" 推荐结构
   - 明确"不做跨聚合强一致事务"，避免分布式事务陷阱

### ⚠️ 改进建议

#### P0（必须修复）
1. **缺少数据库迁移策略**
   - 问题：python skill 要求"prefer explicit migrations (Alembic)"，文档未提及
   - 建议：增加章节 "3.3 数据迁移与版本管理"
     ```markdown
     ### 3.3 数据迁移与版本管理
     - 工具：Alembic（Python）/ Flyway（Java）
     - 命名：`V{YYYYMMDD}_{sequence}_{description}.sql`
     - 回滚：每个 up 迁移必须有对应 down 脚本（一期可先不实现，但留接口）
     - 数据快照：Plan 表的 `supplier_snapshots` 字段为 JSONB，避免 JOIN 依赖
     ```

2. **缺少性能指标与可观测性**
   - 问题：python skill 要求"Metrics for latency, error rate, DB timings"
   - 建议：在 "2.3 应用服务" 后增加章节 "2.4 可观测性要求"
     ```markdown
     ### 2.4 可观测性要求（一期最小集）
     - **日志**：结构化日志（JSON），包含 `request_id` / `user_id` / `action`
     - **指标**：
       - `http_request_duration_seconds`（P50/P95/P99）
       - `llm_generation_duration_seconds`
       - `db_query_duration_seconds`
       - `plan_generation_success_rate`
     - **追踪**：一期可先不做分布式追踪，二期接入 Jaeger/OpenTelemetry
     ```

#### P1（建议优化）
3. **聚合间通信未明确**
   - 当前："Planning 依赖 Supplier Catalog（查询/匹配）"
   - 建议明确：是同步 RPC 还是异步事件？
     ```markdown
     ### 2.5 跨BC通信模式（一期）
     - Planning → Supplier Catalog：**同步查询**（直接调用 SearchSuppliersUseCase）
     - Planning → Identity：**依赖注入**（从 HTTP header 提取 userId，由中间件完成）
     - Planning → Analytics：**异步事件**（通过日志/埋点上报，二期可改为 MQ）
     ```

4. **缺少测试策略**
   - python skill 要求"Unit tests for business logic + API tests for endpoints"
   - 建议：增加章节 "3.4 测试分层"
     ```markdown
     ### 3.4 测试分层（Python/Java 通用）
     - **单元测试**：聚合/值对象/领域逻辑（不依赖 DB/网络）
     - **集成测试**：应用服务 + 仓储（使用 TestContainers 启动真实 PostgreSQL）
     - **契约测试**：API 接口 schema 验证（Pact/OpenAPI validator）
     - **E2E测试**：核心用户旅程（登录→生成→确认），占比 <10%
     ```

---

## 3️⃣ 小程序产品设计文档 Review

**使用 Skills**: `ux` + `ui` + `ue` + `wechat-minware`

### ✅ 优点
1. **用户旅程完整**
   - Journey A/B 覆盖主流程与辅助流程，符合 ux skill 的"happy path + edge cases"要求
   - Step 1 → Step 2 → 生成 → 对比 → 详情 → 确认的流程清晰

2. **交互状态机设计规范**
   - Empty/Error/Loading 状态齐全，符合 ui/ue skill 的"states must-have"要求
   - 状态转换（draft→confirmed）明确标注不可回退

3. **小程序工程提示实用**
   - `setData` 合并更新建议符合 wechat-minware skill 的性能优化要求
   - 封装 `request` 统一注入 token 符合最佳实践

4. **体验验收标准可测试**
   - Given/When/Then 格式符合 ux skill 的 acceptance criteria 模板
   - 每个验收点都可转化为测试用例

### ⚠️ 改进建议

#### P0（必须修复）
1. **缺少可访问性规范**
   - 问题：ui skill 要求"Accessibility checklist (WCAG basics)"，文档几乎未提及
   - 建议：增加章节 "6) 可访问性要求"
     ```markdown
     ## 6) 可访问性要求（WCAG 2.1 AA基线）

     ### 颜色与对比度
     - 文字与背景对比度 ≥ 4.5:1（普通文字）/ ≥ 3:1（大字号≥18pt）
     - 不依赖颜色传递唯一信息（如"绿色=已确认"需配合图标/文字）

     ### 动态文字支持
     - 支持微信系统字号调节（小程序 `page-meta` 设置 `page-style`）
     - 关键信息不用固定像素，使用 `rpx` 或相对单位

     ### 语义化标签
     - 按钮用 `<button>`，不用 `<view>` + `bindtap`
     - 图片添加 `aria-label`（虽然小程序支持有限，但建议预留）
     ```

2. **缺少埋点设计**
   - 问题：文档提到"记录联系行为"，但未系统化定义埋点规范
   - 建议：增加章节 "7) 埋点与分析"
     ```markdown
     ## 7) 埋点与分析（一期最小集）

     | 事件名 | 触发时机 | 关键参数 | 用途 |
     |--------|---------|---------|------|
     | `page_view` | 页面 onShow | `page_name`, `user_id` | 漏斗分析 |
     | `generate_plan_click` | 点击"生成方案" | `people_count`, `budget_range` | 转化率 |
     | `plan_generated` | 对比页展示 | `plan_request_id`, `duration_ms` | 性能监控 |
     | `plan_viewed` | 进入详情 | `plan_id`, `plan_type` | 用户偏好分析 |
     | `plan_confirmed` | 确认方案 | `plan_id` | 北极星指标 |
     | `supplier_contacted` | 点击联系供应商 | `plan_id`, `supplier_id`, `channel` | 转化漏斗 |
     ```

#### P1（建议优化）
3. **缺少空状态与错误文案**
   - 当前："Empty：首次进入默认值 + 引导文案"（未给出具体文案）
   - 建议：补充具体 copy
     ```markdown
     ### 3.1 生成方案页（Empty State）
     - 标题："快速生成专属团建方案"
     - 描述："3 分钟填写需求，AI 为你匹配最优资源"
     - CTA："开始填写"

     ### 3.4 对比页（Error State）
     - 生成失败：
       - 标题："生成失败，请稍后重试"
       - 描述："当前访问人数较多，请稍等片刻"
       - CTA："重新生成"（保留已填写内容）
     ```

4. **loading 状态缺少骨架屏设计**
   - 当前：只提到"进度 + 文案反馈"
   - 建议：wechat-minware skill 推荐使用骨架屏提升体验
     ```markdown
     ### 3.3 生成中页（Loading UX优化）
     - 方案A（推荐）：骨架屏 + 进度条（"正在匹配供应商 60%"）
     - 方案B：Lottie动画 + 文案轮播（"为你寻找性价比最高的住宿..."）
     - 超时策略：60s后显示"生成时间较长，稍后在'我的方案'查看"
     ```

---

## 4️⃣ API设计文档 Review

**使用 Skills**: `python` + `pg-doc-schema-review`

### ✅ 优点
1. **契约优先设计**
   - "contract-first" 理念符合 python skill 推荐
   - Request/Response JSON schema 清晰，便于前后端并行开发

2. **响应包络统一**
   - `{ success, data, error }` 格式一致，符合最佳实践
   - 错误码与 message 分离，便于国际化

3. **认证方案清晰**
   - 微信 code 换 session token 流程标准
   - Bearer token 认证符合行业规范

4. **错误码设计合理**
   - `UNAUTHENTICATED` / `INVALID_ARGUMENT` 等符合 gRPC/HTTP 标准错误码

### ⚠️ 改进建议

#### P0（必须修复）
1. **缺少幂等性规范**
   - 问题：python skill 要求"Idempotency and retry rules"，文档未明确
   - 建议：在 "1) 通用约定" 增加 "1.3 幂等性"
     ```markdown
     ### 1.3 幂等性要求
     - **POST /v1/plans/generate**：
       - 客户端传 `idempotency_key`（UUID）
       - 服务端 60s 内相同 key 返回缓存结果（避免重复生成）
     - **POST /v1/plans/{plan_id}/confirm**：
       - 重复确认返回成功（状态不变）
     - **POST /v1/plans/{plan_id}/supplier-contacts**：
       - 可重复调用（记录多次联系行为）
     ```

2. **缺少分页规范**
   - 当前："GET /v1/plans?page=1&page_size=10"
   - 问题：未明确响应格式、最大page_size、是否支持 cursor
   - 建议：补充响应示例
     ```markdown
     ### 3.2 方案列表（我的方案）
     `GET /v1/plans?page=1&page_size=10&status=confirmed`

     Response:
     ```json
     {
       "success": true,
       "data": {
         "items": [ /* plan 列表 */ ],
         "pagination": {
           "page": 1,
           "page_size": 10,
           "total_count": 23,
           "total_pages": 3
         }
       }
     }
     ```

     **约束**：
     - `page` ≥ 1（默认1）
     - `page_size` ∈ [1, 50]（默认10，超过50报错）
     - 一期使用 offset 分页；二期可改为 cursor-based
     ```

3. **缺少数据库 schema 说明**
   - 问题：pg-doc-schema-review skill 要求"明确表结构与索引"
   - 建议：增加附录 "6) 核心表结构"
     ```markdown
     ## 6) 核心表结构（PostgreSQL）

     ### plans 表
     | 字段 | 类型 | 约束 | 索引 | 说明 |
     |-----|------|------|------|------|
     | plan_id | VARCHAR(32) | PK | ✅ | 主键，前缀 `plan_` |
     | user_id | VARCHAR(32) | NOT NULL | ✅ | 用户ID，联合索引 |
     | plan_type | VARCHAR(20) | NOT NULL CHECK | - | budget/standard/premium |
     | status | VARCHAR(20) | NOT NULL | ✅ | draft/confirmed |
     | inputs_snapshot | JSONB | NOT NULL | - | 用户输入快照 |
     | itinerary | JSONB | NOT NULL | - | 行程数据 |
     | budget_breakdown | JSONB | NOT NULL | - | 预算明细 |
     | supplier_snapshots | JSONB | NOT NULL | - | 供应商快照数组 |
     | create_time | TIMESTAMPTZ | NOT NULL DEFAULT now() | ✅ | 创建时间 |
     | update_time | TIMESTAMPTZ | NOT NULL DEFAULT now() | - | 更新时间 |

     **索引设计**：
     - `idx_plans_user_id_create_time`：支持"我的方案"列表查询（user_id + create_time DESC）
     - `idx_plans_status`：支持按状态筛选（可选）
     ```

#### P1（建议优化）
4. **缺少 API 版本演进策略**
   - 当前：所有接口为 `/v1/`
   - 建议：补充版本策略
     ```markdown
     ### 1.4 API 版本策略
     - 当前版本：`v1`
     - 兼容性承诺：v1 接口向后兼容，只增不减（Additive changes only）
     - 破坏性变更：发布 v2 并保持 v1 存活至少 6 个月
     - 弃用通知：响应头 `X-API-Deprecation-Warning: "This endpoint will be deprecated on 2026-06-01"`
     ```

5. **错误响应缺少 `details` 字段示例**
   - 当前：只有 code + message
   - 建议：补充 details 用于字段级错误
     ```json
     {
       "success": false,
       "error": {
         "code": "INVALID_ARGUMENT",
         "message": "输入参数校验失败",
         "details": [
           { "field": "budget_min", "issue": "must be > 0" },
           { "field": "budget_max", "issue": "must be >= budget_min" }
         ]
       }
     }
     ```

---

## 5️⃣ QA文档 Review

**使用 Skills**: `qa`

### ✅ 优点
1. **测试范围清晰**
   - P0 必测旅程 + 非功能测试，符合 qa skill 的"risk-based test design"
   - 覆盖功能/性能/兼容性三大维度

2. **Checklist 结构化**
   - 2.1~2.7 按模块组织，便于分工执行
   - 每个检查点可直接转化为测试用例

3. **测试用例表规范**
   - 包含 ID/模块/前置/步骤/期望，符合 qa skill 的 test case 模板
   - TC-PLAN-002（budget边界）等负向用例设计合理

4. **安全测试覆盖**
   - TC-SEC-001 检查未登录保护，体现安全意识

### ⚠️ 改进建议

#### P0（必须修复）
1. **缺少自动化策略**
   - 问题：qa skill 要求"Automation strategy (what to automate, where to stop)"
   - 建议：增加章节 "4) 自动化测试策略"
     ```markdown
     ## 4) 自动化测试策略

     ### 测试金字塔（一期目标）
     - **单元测试**（60%）：聚合/值对象/业务逻辑（BE团队负责）
     - **API契约测试**（30%）：核心接口（登录/生成/确认/列表）
       - 工具：Postman/pytest + JSON Schema validator
       - 覆盖：正向流程 + 主要错误码 + 幂等性验证
     - **E2E UI测试**（10%）：核心用户旅程（生成→确认）
       - 工具：微信小程序自动化SDK（miniprogram-automator）
       - 覆盖：2条主路径（预计20分钟执行时间）

     ### 一期不做自动化的部分
     - 兼容性测试（手动在3种机型/系统组合测试）
     - 弱网测试（使用 Charles/Proxyman 手动模拟）
     - 可访问性测试（手动检查对比度/字号）
     ```

2. **缺少性能基线**
   - 当前："生成耗时与超时兜底"（未给出具体指标）
   - 建议：增加章节 "5) 性能验收基线"
     ```markdown
     ## 5) 性能验收基线（一期）

     | 指标 | P50 | P95 | P99 | 超时阈值 |
     |------|-----|-----|-----|---------|
     | 生成方案耗时 | ≤ 30s | ≤ 50s | ≤ 60s | 60s（前端提示超时） |
     | 方案详情加载 | ≤ 500ms | ≤ 1s | ≤ 2s | 5s |
     | 我的方案列表 | ≤ 300ms | ≤ 800ms | ≤ 1.5s | 3s |

     **测试条件**：
     - 并发：10个并发用户（一期预期流量）
     - 网络：4G网络（下行10Mbps，延迟50ms）
     - 数据：后端已有100条方案记录

     **不通过处理**：
     - P95 超标：优化查询/缓存后重测
     - P99 超标但 P95达标：可接受（记录为已知问题）
     ```

#### P1（建议优化）
3. **边界测试用例不完整**
   - 当前：TC-PLAN-002 只覆盖 budget 边界
   - 建议：补充日期/人数边界测试用例
     ```markdown
     | TC-PLAN-004 | 生成 | 日期区间非法（end<start） | 已登录 | 输入 start=2026-01-15, end=2026-01-10 → 生成 | 前端或接口返回错误 |
     | TC-PLAN-005 | 生成 | 人数边界（0人） | 已登录 | 输入 people_count=0 → 生成 | 前端禁用按钮或接口返回 `INVALID_ARGUMENT` |
     | TC-PLAN-006 | 生成 | 人数边界（501人） | 已登录 | 输入 people_count=501 → 生成 | 接口返回 `INVALID_ARGUMENT: "人数范围 1-500"` |
     ```

4. **缺少回归测试策略**
   - qa skill 要求"Regression suite definition"
   - 建议：补充回归套件定义
     ```markdown
     ### 2.8 回归测试套件（每次发版前执行）
     - **冒烟测试**（5分钟）：
       - 登录成功
       - 生成方案成功（1套）
       - 查看详情成功
     - **核心回归**（30分钟）：
       - 所有 TC-* 用例中标记为 P0 的用例
       - 历史缺陷回归（回归所有已修复的 bug）
     - **执行频率**：
       - 每次合并到 main 分支：冒烟测试
       - 每周五上线前：核心回归
     ```

---

## 🔗 跨文档一致性检查

### 检查项 1：事件命名一致性
| 事件名 | 事件风暴 | DDD设计 | API设计 | 产品设计 | 状态 |
|--------|---------|---------|---------|---------|------|
| `PlanRequestCreated` | ✅ | ✅ | ✅（/generate触发） | ✅（Step 2提交） | ✅ 一致 |
| `PlanGenerated` | ✅ | ✅ | ✅（/generate响应） | ✅（进入对比页） | ✅ 一致 |
| `PlanConfirmed` | ✅ | ✅ | ✅（/confirm接口） | ✅（状态变更） | ✅ 一致 |
| `SupplierContacted` | ✅ | ✅ | ✅（/supplier-contacts） | ✅（拨号/复制） | ✅ 一致 |
| `PlanShared` | ✅（可选） | ❌ 缺失 | ❌ 缺失 | ✅（分享按钮） | ⚠️ 需同步 |

**建议**：
- 如果一期确认实现分享功能，需补充：
  - DDD设计：增加 `SharePlanUseCase`
  - API设计：增加 `POST /v1/plans/{plan_id}/share`

### 检查项 2：状态机一致性
| 状态流转 | 事件风暴 | DDD设计 | API设计 | 产品设计 | 状态 |
|---------|---------|---------|---------|---------|------|
| draft → confirmed | ✅ | ✅ | ✅ | ✅ | ✅ 一致 |
| confirmed → draft（回退） | ❌ 不允许 | ❌ 不允许 | - 未明确 | ❌ 不允许 | ⚠️ API需明确 |
| 重复确认（幂等） | - | - | - 未明确 | - | ⚠️ 需补充 |

**建议**：
- API设计文档在 "3.4 确认方案" 补充：
  ```markdown
  ### 3.4 确认方案
  `POST /v1/plans/{plan_id}/confirm`

  **幂等性**：重复确认返回成功，状态不变
  **错误情况**：
  - 若 plan_id 不存在：返回 `NOT_FOUND`
  - 若 plan 已 cancelled：返回 `INVALID_STATE: "已取消的方案无法确认"`
  ```

### 检查项 3：供应商数据结构一致性
| 字段 | 事件风暴 | DDD设计 | API设计 | 产品设计 | 状态 |
|-----|---------|---------|---------|---------|------|
| supplier_id | ✅ | ✅ | ✅ | - | ✅ 一致 |
| 快照存储 | ✅（snapshots） | ✅（SupplierSnapshot） | ❌ 响应未体现 | - | ⚠️ 需补充 |

**建议**：
- API设计文档在 "3.3 方案详情" 补充 supplier_snapshots 字段结构：
  ```json
  {
    "plan_id": "plan_xxx",
    "suppliers": [
      {
        "supplier_id": "sup_xxx",
        "name": "怀柔山水农家院",
        "category": "accommodation",
        "price_range": { "min": 200, "max": 500 },
        "rating": 4.5,
        "contact": { "phone": "138xxxx", "wechat": "xxx" },
        "tags": ["山景", "团建专供"],
        "snapshot_time": "2026-01-01T10:00:00Z"
      }
    ]
  }
  ```

---

## 📋 总结与行动项

### 核心优势
1. ✅ **领域建模成熟**：事件风暴 + DDD 设计严谨，聚合边界清晰
2. ✅ **前后端契约清晰**：API 设计 contract-first，便于并行开发
3. ✅ **用户体验完整**：产品设计覆盖主流程与边界情况
4. ✅ **测试覆盖全面**：QA 文档涵盖功能/性能/安全多维度

### 关键改进（按优先级）

#### 🔴 P0（必须在开发前修复）
1. **事件风暴**：补充里程碑时间线 + RAID 风险矩阵
2. **DDD设计**：补充数据库迁移策略 + 可观测性指标
3. **产品设计**：补充可访问性规范 + 埋点设计
4. **API设计**：补充幂等性规范 + 分页规范 + 数据库 schema
5. **QA文档**：补充自动化策略 + 性能基线

#### 🟡 P1（建议在一期完成前优化）
6. 跨文档同步：`PlanShared` 事件与接口
7. API设计：补充版本演进策略 + 错误 details 字段
8. QA文档：补充边界测试用例 + 回归测试策略

### 下一步建议
1. **Week 1**：各 owner 根据 P0 改进项更新文档（预计 2-3 天）
2. **Week 2**：开发团队 review 更新后文档，确认无歧义后开始编码
3. **持续**：每周五同步会议检查文档与实现的一致性，发现偏差及时更新

---

**Review 完成时间**: 2025-12-30
**预计文档更新工作量**: 3-5 人日
**建议复审时间**: 文档更新完成后 2 个工作日内

