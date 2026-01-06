# 字段一致性验证报告

**创建日期**: 2026-01-06
**目的**: 确保 departure_city 和 destination 字段在全链路中语义一致

---

## 字段语义定义

| 字段名 | 中文名 | 语义说明 | 示例值 |
|--------|--------|----------|--------|
| `departure_city` | 出发城市 | 团队从哪里出发，通常是公司所在城市 | 上海市 |
| `destination` | 目的地 | 团建活动举办地点，团队前往的地方 | 杭州千岛湖 |

**前端显示格式**: `{departure_city} → {destination}`
**示例**: 上海市 → 杭州千岛湖

---

## 全链路验证清单

### 1. 数据库层

| 检查项 | 文件位置 | 状态 | 说明 |
|--------|----------|------|------|
| plan_requests.departure_city | V1.0.6 COMMENT | ✅ | 出发城市（团队从哪里出发，如公司所在地：上海市） |
| plan_requests.destination | V1.0.6 COMMENT | ✅ | 目的地（团建活动举办地点，如：杭州千岛湖） |
| plans.departure_city | V1.0.6 COMMENT | ✅ | 出发城市（团队从哪里出发，如公司所在地：上海市） |
| plans.destination | V1.0.6 COMMENT | ✅ | 目的地（团建活动举办地点，如：杭州千岛湖） |

**迁移脚本**: `database/schema/V1.0.6__clarify_location_field_comments.sql`

### 2. Java 后端层

| 检查项 | 文件位置 | 状态 | 说明 |
|--------|----------|------|------|
| PlanRequestPO.departure_city | infrastructure/persistence/po/PlanRequestPO.java | ✅ | JavaDoc注释已添加 |
| PlanRequestPO.destination | infrastructure/persistence/po/PlanRequestPO.java | ✅ | JavaDoc注释已添加 |
| PlanPO.departure_city | infrastructure/persistence/po/PlanPO.java | ✅ | JavaDoc注释已添加 |
| PlanPO.destination | infrastructure/persistence/po/PlanPO.java | ✅ | JavaDoc注释已添加 |
| GenerateRequest.departure_city | adapter/web/plans/PlanController.java | ✅ | JavaDoc注释已添加 |
| GenerateRequest.destination | adapter/web/plans/PlanController.java | ✅ | JavaDoc注释已添加 |
| PlanService 字段使用 | app/service/PlanService.java | ✅ | 正确区分两个字段 |

### 3. Python AI 服务层

| 检查项 | 文件位置 | 状态 | 说明 |
|--------|----------|------|------|
| 模块文档注释 | services/plan_generation.py | ✅ | 模块级文档说明字段语义 |
| _normalize_generated_plans | services/plan_generation.py | ✅ | 正确传递并使用两个字段 |
| _generate_three_plans_stub | services/plan_generation.py | ✅ | 正确区分出发城市和目的地 |
| generate_three_plans | services/plan_generation.py | ✅ | 正确使用 destination 进行季节适配和预算校验 |
| LLM Prompt | services/plan_generation.py | ✅ | 明确说明出发城市和目的地 |

### 4. 前端小程序层

| 检查项 | 文件位置 | 状态 | 说明 |
|--------|----------|------|------|
| 页面级文档注释 | pages/index/index.js | ✅ | 说明字段映射关系 |
| formData.departureLocation | pages/index/index.js | ✅ | 注释说明映射到 departure_city |
| formData.destination | pages/index/index.js | ✅ | 注释说明为目的地 |
| 请求构建注释 | pages/index/index.js | ✅ | 详细说明字段含义 |
| 表单标签 | pages/index/index.wxml | ✅ | "出发地点" / "目的地" |
| 列表显示格式 | pages/myplans/myplans.wxml | ✅ | "{departure_city} → {destination}" |

### 5. API 文档层

| 检查项 | 文件位置 | 状态 | 说明 |
|--------|----------|------|------|
| 请求参数说明 | docs/design/api-design.md | ✅ | 详细说明字段语义 |
| 请求示例 | docs/design/api-design.md | ✅ | 示例使用中文值 |
| 响应示例 | docs/design/api-design.md | ✅ | 包含两个字段及说明 |
| 版本记录 | docs/design/api-design.md | ✅ | v1.4 记录本次变更 |

---

## 数据流向验证

```
用户输入表单
    ├── departureLocation: "上海市"    (出发城市)
    └── destination: "杭州千岛湖"       (目的地)
           │
           ▼
前端 API 请求
    ├── departure_city: "上海市"       (出发城市)
    └── destination: "杭州千岛湖"       (目的地)
           │
           ▼
Java PlanController (GenerateRequest)
    ├── departure_city: "上海市"       (出发城市)
    └── destination: "杭州千岛湖"       (目的地)
           │
           ▼
Java PlanService → RabbitMQ 消息
    ├── departure_city: "上海市"       (出发城市)
    └── destination: "杭州千岛湖"       (目的地)
           │
           ▼
Python AI Service (plan_generation.py)
    ├── departure_city: "上海市"       (出发城市)
    └── destination: "杭州千岛湖"       (目的地，用于季节适配/预算校验)
           │
           ▼
生成的方案数据
    ├── departure_city: "上海市"       (出发城市)
    └── destination: "杭州千岛湖"       (目的地)
           │
           ▼
Java 回调 → 存储到 plans 表
    ├── departure_city: "上海市"       (出发城市)
    └── destination: "杭州千岛湖"       (目的地)
           │
           ▼
前端列表/详情展示
    └── 显示: "上海市 → 杭州千岛湖"
```

---

## 修改文件清单

1. **数据库迁移**: `src/database/schema/V1.0.6__clarify_location_field_comments.sql`
2. **Java PO**:
   - `src/backend/java-business-service/.../PlanRequestPO.java`
   - `src/backend/java-business-service/.../PlanPO.java`
3. **Java Controller**: `src/backend/java-business-service/.../PlanController.java`
4. **Python AI**: `src/backend/python-ai-service/src/services/plan_generation.py`
5. **前端 JS**: `src/frontend/miniapp/pages/index/index.js`
6. **API 文档**: `docs/design/api-design.md`

---

## 验证结论

✅ **全链路字段语义一致**

- 数据库层：COMMENT 清晰说明字段含义
- 后端层：JavaDoc/Python docstring 注释完整
- 前端层：代码注释和表单标签一致
- 文档层：API 文档详细说明字段语义

**关键改进**:
1. 消除了 Python AI 服务中将 `departure_city` 误用为活动目的地的问题
2. 添加了从数据库到前端的完整字段注释链
3. 统一了显示格式："{出发城市} → {目的地}"
