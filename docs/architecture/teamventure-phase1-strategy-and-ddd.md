# TeamVenture 一期（小程序）战略设计 + DDD 战术设计

> 面向教学：先用最小可行的 BC/聚合跑通闭环，再逐步演进为多服务/更细粒度。
>
> 参考：`docs/event-storming/teamventure-phase1-event-storming.md`

---

## 1) 战略设计（Strategic Design）

### 1.1 一句话定位（Strategy）
- **TeamVenture 小程序一期**：让 HR 在 10–15 分钟内生成 3 套可对比的团建方案，并能完成“确认方案 + 联系供应商”的行动闭环。

### 1.2 北极星与护栏指标
- 北极星：`Weekly Confirmed Plans`（每周确认方案数）
- 护栏：生成耗时 P95、失败率、投诉/纠错率、供应商联系转化率

### 1.3 一期 Bounded Context（BC）定义

**BC-1：Identity & Session**
- 目标：最低成本完成“可信身份 + 会话”
- 输入/输出：WeChat code → userId + session token

**BC-2：Planning**
- 目标：跑通“需求→生成→对比→确认→联系”的主闭环
- 关键资产：PlanRequest、Plan、SupplierSnapshot

**BC-3：Supplier Catalog**
- 目标：提供可查询的供应商目录与基础匹配素材（一期可人工录入）
- 关键资产：Supplier

### 1.4 Context Map（关系）
- Planning 依赖 Identity（认证）
- Planning 依赖 Supplier Catalog（查询/匹配）
- Analytics 作为横切能力，先落在 Planning/Identity 的事件日志与埋点

---

## 2) 战术设计（Tactical Design）

> 重点：聚合边界 + 不变式 + 用例（应用服务）+ 事件。

### 2.1 聚合与实体/值对象

#### 聚合：PlanRequest（聚合根）
- 作用：承载一次“用户需求输入”的事实快照与校验结果
- 值对象建议：
  - `BudgetRange(min, max)`
  - `DateRange(start, end)`
  - `Preferences(activityTypes[], accommodationLevel, diningStyle[], specialRequirements)`

#### 聚合：Plan（聚合根）
- 作用：承载一套可执行方案（行程/预算/供应商），并管理状态流转
- 关键状态：
  - `draft`：生成成功但未确认
  - `confirmed`：用户确认（用于北极星）
  - `cancelled`：一期可不实现（预留）
- 值对象建议：
  - `Itinerary(days[])`
  - `BudgetBreakdown(categories[])`
  - `SupplierSnapshot[]`（供应商快照，避免跨表 join）

#### 聚合：Supplier（聚合根，一期只读）
- 作用：供应商目录与匹配素材
- 值对象建议：
  - `GeoLocation(lat, lng, address)`
  - `PriceRange(min, max)`

#### 聚合/事件流：SupplierContactLog
- 作用：记录供应商联系行为（支持转化漏斗与运营）

### 2.2 领域事件（建议最小集）
- `PlanRequestCreated`
- `PlanGenerationStarted`
- `PlanGenerated`
- `PlanGenerationFailed`
- `PlanConfirmed`
- `SupplierContacted`

### 2.3 应用服务（Use Cases）

**Planning 应用服务**
- `CreatePlanRequestUseCase`
- `GeneratePlansUseCase`（编排：匹配→生成→校验→落库）
- `ListPlansUseCase`
- `GetPlanDetailUseCase`
- `ConfirmPlanUseCase`
- `LogSupplierContactUseCase`

**Identity 应用服务**
- `LoginWithWeChatUseCase`

**Supplier Catalog 应用服务**
- `SearchSuppliersUseCase`（一期可只支持按 city/category）
- `GetSupplierUseCase`

---

## 3) 架构落地建议（Python / Java 共用思路）

### 3.1 分层建议（Ports & Adapters）
- `domain/`：聚合、值对象、领域事件、仓储接口
- `application/`：用例、DTO、事务边界、编排
- `interfaces/`：HTTP 控制器、鉴权、参数校验、错误映射
- `infrastructure/`：PostgreSQL、缓存、外部 LLM、供应商数据源

### 3.2 数据与一致性（一期约束）
- 不做跨聚合强一致事务；PlanRequest 与 Plan 可在同一事务内写入，但保持接口幂等
- 不依赖外键与 join 做核心读路径：Plan 持有 supplier snapshots，列表与详情直接读 plan

