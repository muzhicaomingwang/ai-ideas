# TeamVenture DDD 一致性修订计划

> **版本**: v1.0
> **创建日期**: 2026-01-07
> **状态**: 待执行
> **方法论**: 先审计、后制定计划、再执行修订

---

## 1. 审计概述

### 1.1 审计范围

| 类别 | 审计文件 |
|------|----------|
| **前端代码** | `src/frontend/miniapp/utils/config.js` |
| **后端代码** | `src/backend/java-business-service/.../PlanController.java` |
| **API设计文档** | `docs/design/api-design.md` (v1.5) |
| **领域语言词汇表** | `docs/design/ubiquitous-language-glossary.md` (v1.0) |
| **事件风暴文档** | `docs/design/event-storming.md` |
| **测试文档** | `docs/qa/checklist-and-testcases.md` (v1.4) |

### 1.2 权威来源确定

**API 设计文档 (`api-design.md` v1.5)** 作为权威来源，原因：
1. 版本号最高，明确标注了最新状态机流转
2. 与实际后端代码实现一致
3. 包含完整的 6 状态定义和转换规则

---

## 2. 不一致性矩阵

### 2.1 方案状态（Plan Status）定义不一致

| 源文件 | 定义的状态 | 状态数 | 一致性 |
|--------|-----------|--------|--------|
| **api-design.md (v1.5)** | generating, failed, draft, reviewing, confirmed, archived | 6 | ✅ 权威来源 |
| **前端 config.js** | generating, failed, draft, reviewing, confirmed, archived, **cancelled** | 7 | ⚠️ 多出 `cancelled` |
| **checklist-and-testcases.md** | generating, draft, reviewing, confirmed, archived | 5 | ⚠️ 缺 `failed` |
| **event-storming.md** | draft, confirmed | 2 | ❌ 严重过时 |
| **ubiquitous-language-glossary.md** | draft, confirmed | 2 | ❌ 严重过时 |

### 2.2 状态机流转不一致

| 源文件 | 定义的流转 | 一致性 |
|--------|-----------|--------|
| **api-design.md** | `generating → failed \| draft → reviewing ↔ draft → confirmed → archived` | ✅ 权威 |
| **event-storming.md** | `draft → confirmed (不可回退)` | ❌ 缺少 reviewing/archived，缺少回退 |
| **glossary** | 无明确流转定义 | ❌ 需补充 |

### 2.3 领域术语不一致

| 术语 | 词汇表定义 | 实际使用 | 问题 |
|------|-----------|---------|------|
| `generating` | ❌ 未定义 | 前端/后端均使用 | 需添加 |
| `failed` | ❌ 未定义 | 前端/后端均使用 | 需添加 |
| `reviewing` | ❌ 未定义 | "通晒中"状态 | 需添加 |
| `archived` | ❌ 未定义 | "已归档"状态 | 需添加 |
| `cancelled` | ❌ 未定义 | 仅前端定义 | **需决策** |

---

## 3. 修订决策

### 3.1 关于 `cancelled` 状态的决策

**问题**: 前端 `config.js` 定义了 `cancelled` 状态，但后端和所有文档均未定义。

**决策**: ❌ **移除前端的 `cancelled` 状态**

**理由**:
1. 后端 API 未实现 `cancelled` 状态和相关端点
2. 产品需求中未提及"取消方案"功能
3. 当前业务流程不需要此状态（用户可通过"归档"达到类似效果）
4. 保持前后端一致性

**如未来需要**:
- 应先更新 PRD，再更新 API 设计，最后实现

### 3.2 权威状态机定义（基于 api-design.md v1.5）

```
                    ┌──────────────────────────────────────────────────────────┐
                    │                                                          │
                    ▼                                                          │
[generating] ──┬──► [failed]                                                   │
               │                                                               │
               └──► [draft] ◄───► [reviewing] ───► [confirmed] ───► [archived]│
                         │              │                                      │
                         │              │ (revert-review)                      │
                         │              ▼                                      │
                         └──────────────┘                                      │
```

**状态说明**:
| 状态 | 中文名 | 说明 |
|------|--------|------|
| `generating` | 生成中 | AI 正在生成方案 |
| `failed` | 生成失败 | AI 生成过程出错 |
| `draft` | 制定完成 | 方案草稿已生成，可编辑 |
| `reviewing` | 通晒中 | 已提交给团队成员审阅 |
| `confirmed` | 已确认 | 方案已最终确认 |
| `archived` | 已归档 | 方案已归档（历史记录） |

**转换动作**:
| 转换 | 动作端点 | 说明 |
|------|---------|------|
| `generating → draft` | (内部回调) | AI 生成成功 |
| `generating → failed` | (内部回调) | AI 生成失败 |
| `draft → reviewing` | `POST /plans/:id/submit-review` | 提交通晒 |
| `reviewing → draft` | `POST /plans/:id/revert-review` | 撤回通晒 |
| `reviewing → confirmed` | `POST /plans/:id/confirm` | 确认方案 |
| `confirmed → archived` | `POST /plans/:id/archive` | 归档方案 |

---

## 4. 修订任务清单

### 4.1 前端代码修订

| 文件 | 修订内容 | 优先级 |
|------|---------|--------|
| `utils/config.js` | 移除 `PLAN_STATUS.CANCELLED` 和 `PLAN_STATUS_NAMES[cancelled]` | P0 |

### 4.2 领域语言词汇表修订

| 文件 | 修订内容 | 优先级 |
|------|---------|--------|
| `docs/design/ubiquitous-language-glossary.md` | 更新"方案状态"章节，添加全部 6 个状态定义 | P0 |
| `docs/design/ubiquitous-language-glossary.md` | 添加状态转换动作术语（submit-review, revert-review, archive） | P0 |

### 4.3 事件风暴文档修订

| 文件 | 修订内容 | 优先级 |
|------|---------|--------|
| `docs/design/event-storming.md` | 更新状态机图示，补充 generating/failed/reviewing/archived 状态 | P0 |
| `docs/design/event-storming.md` | 补充状态转换事件（PlanSubmittedForReview, PlanReviewReverted, PlanArchived） | P1 |

### 4.4 测试文档修订

| 文件 | 修订内容 | 优先级 |
|------|---------|--------|
| `docs/qa/checklist-and-testcases.md` | 在状态流转测试中明确添加 `failed` 状态的测试用例 | P1 |
| `docs/qa/checklist-and-testcases.md` | 确认状态名称与权威定义一致 | P1 |

---

## 5. 执行顺序

按照依赖关系，建议执行顺序：

1. **Step 1**: 修订前端 `config.js`（移除 cancelled）
2. **Step 2**: 修订领域语言词汇表（建立一致的术语定义）
3. **Step 3**: 修订事件风暴文档（状态机与权威来源对齐）
4. **Step 4**: 修订测试文档（确保测试覆盖所有状态）

---

## 6. 验收标准

修订完成后，应满足：

- [ ] 所有文档中的方案状态定义一致（6 个状态）
- [ ] 所有文档中的状态流转图一致
- [ ] 前端代码与后端 API 状态定义一致
- [ ] 领域术语在所有文档中使用一致
- [ ] 测试用例覆盖所有状态和转换

---

## 7. 附录：文件位置速查

```
apps/teamventure/
├── docs/
│   ├── design/
│   │   ├── api-design.md                      # ✅ 权威来源
│   │   ├── ubiquitous-language-glossary.md    # ❌ 需修订
│   │   ├── event-storming.md                  # ❌ 需修订
│   │   └── ddd-revision-plan.md               # 本文件
│   └── qa/
│       └── checklist-and-testcases.md         # ⚠️ 需补充
└── src/
    └── frontend/
        └── miniapp/
            └── utils/
                └── config.js                  # ⚠️ 需修订
```
