# 新工程目录结构提案

> **目的**: 为多应用开发提供清晰的隔离和组织方式
> **日期**: 2025-12-30
> **状态**: 📋 待评审

---

## 🎯 核心设计原则

1. **应用隔离**: 每个应用的所有资产（文档+代码）集中管理
2. **最小依赖**: 共享资源（如skills、scripts）保持在顶层
3. **开发友好**: AI能看到完整的应用上下文（需求→设计→代码）
4. **迁移平滑**: 现有结构可无缝迁移

---

## 📂 完整目录结构

```
ideas/
├── README.md                           # 仓库总入口（指向各应用）
├── ai-product-ideas.md                 # 产品创意索引
│
├── docs/                               # 共享文档（跨应用）
│   ├── finance/                        # CFO token追踪
│   ├── architecture-analysis.md        # 仓库级架构分析
│   └── learning-roadmap.md             # 学习路线图
│
├── .claude/                            # Claude Code 配置
│   └── skills/                         # 共享技能库
│       ├── CFO/
│       ├── strategy/
│       └── ...
│
├── scripts/                            # 共享脚本
│   ├── generate-daily-token-report.py
│   └── ...
│
└── apps/                               # 🆕 应用集合
    │
    ├── ego-echo/                       # 应用1：Ego-Echo
    │   ├── README.md                   # 应用入口（状态、Quick Start）
    │   │
    │   ├── docs/                       # 应用文档
    │   │   ├── requirements/
    │   │   │   ├── prd.md
    │   │   │   └── business-plan.md
    │   │   ├── design/
    │   │   │   ├── architecture.md
    │   │   │   ├── api-design.md
    │   │   │   └── ux-design.md
    │   │   └── qa/
    │   │       ├── checklist.md
    │   │       └── test-cases.md
    │   │
    │   └── src/                        # 应用代码（Monorepo）
    │       ├── backend/
    │       │   ├── python-ai-service/
    │       │   │   ├── pyproject.toml
    │       │   │   └── src/
    │       │   └── java-business-service/
    │       │       ├── pom.xml
    │       │       └── src/
    │       └── frontend/
    │           └── miniapp/
    │               └── src/
    │
    └── teamventure/                    # 应用2：TeamVenture（重点）
        ├── README.md                   # 🆕 应用状态仪表盘
        │
        ├── docs/                       # 📚 应用文档
        │   ├── requirements/           # 需求阶段
        │   │   ├── market-research.md
        │   │   ├── prd.md
        │   │   └── business-plan.md
        │   │
        │   ├── design/                 # 设计阶段
        │   │   ├── event-storming.md            # 事件风暴
        │   │   ├── strategy-and-ddd.md          # DDD战略+战术
        │   │   ├── miniapp-product-design.md    # UX/UI/UE设计
        │   │   ├── api-design.md                # 接口设计
        │   │   ├── detailed-design.md           # ⭐ 详细设计（主）
        │   │   └── database-design.md           # ⭐ 数据库设计
        │   │
        │   ├── qa/                     # 测试阶段
        │   │   ├── checklist.md
        │   │   └── test-cases.md
        │   │
        │   └── reviews/                # 评审记录
        │       └── phase1-documents-review.md
        │
        └── src/                        # 💻 应用代码（Monorepo）
            ├── README.md               # 开发环境 Quick Start
            ├── docker-compose.yml      # 本地开发环境
            │
            ├── backend/
            │   ├── python-ai-service/
            │   │   ├── pyproject.toml
            │   │   ├── poetry.lock
            │   │   └── src/
            │   │       ├── main.py
            │   │       ├── agents/
            │   │       ├── workflows/
            │   │       └── models/
            │   │
            │   └── java-business-service/
            │       ├── pom.xml
            │       └── src/
            │           └── main/
            │               └── java/
            │                   └── com/teamventure/
            │                       ├── adapter/       # COLA Adapter层
            │                       ├── app/           # COLA App层
            │                       ├── domain/        # COLA Domain层
            │                       └── infrastructure/ # COLA Infrastructure层
            │
            ├── frontend/
            │   └── miniapp/
            │       ├── app.json
            │       ├── pages/
            │       ├── components/
            │       └── utils/
            │
            ├── database/
            │   ├── schema/
            │   │   ├── V1.0.0__init.sql
            │   │   └── V1.0.1__seed_suppliers.sql
            │   └── migrations/
            │
            └── nginx/
                └── nginx.conf
```

---

## 🔄 迁移计划

### Phase 1: 创建新结构（不影响现有工作）

```bash
# 1. 创建apps/目录和teamventure应用结构
mkdir -p apps/teamventure/{docs/{requirements,design,qa,reviews},src/{backend/{python-ai-service,java-business-service},frontend/miniapp,database/{schema,migrations},nginx}}

# 2. 创建应用README
touch apps/teamventure/README.md
touch apps/teamventure/src/README.md
```

### Phase 2: 迁移文档（保留原文件作为符号链接）

```bash
# 迁移需求文档
mv docs/teamventure-market-research.md apps/teamventure/docs/requirements/market-research.md
mv docs/prds/teamventure-team-building-assistant-prd.md apps/teamventure/docs/requirements/prd.md
mv docs/business-plans/teamventure-business-plan.md apps/teamventure/docs/requirements/business-plan.md

# 迁移设计文档
mv docs/event-storming/teamventure-phase1-event-storming.md apps/teamventure/docs/design/event-storming.md
mv docs/architecture/teamventure-phase1-strategy-and-ddd.md apps/teamventure/docs/design/strategy-and-ddd.md
mv docs/design/teamventure-phase1-miniapp-product-design.md apps/teamventure/docs/design/miniapp-product-design.md
mv docs/design/teamventure-phase1-api-design.md apps/teamventure/docs/design/api-design.md

# 迁移详细设计文档
mv docs/detailed-design/teamventure-phase1-detailed-design.md apps/teamventure/docs/design/detailed-design.md
mv docs/detailed-design/teamventure-phase1-database-design.md apps/teamventure/docs/design/database-design.md

# 迁移QA文档
mv docs/qa/teamventure-phase1-qa-checklist-and-testcases.md apps/teamventure/docs/qa/checklist-and-testcases.md

# 迁移评审文档
mv docs/reviews/teamventure-phase1-documents-review.md apps/teamventure/docs/reviews/phase1-documents-review.md

# 创建反向链接（保持旧链接有效）
ln -s ../../apps/teamventure/docs/requirements/prd.md docs/prds/teamventure-team-building-assistant-prd.md
```

### Phase 3: 更新README和索引链接

```bash
# 更新顶层README.md，添加apps/目录说明
# 更新ai-product-ideas.md，链接指向apps/teamventure/README.md
```

### Phase 4: 初始化代码结构（开发启动时）

```bash
cd apps/teamventure/src

# 创建Python服务
cd backend/python-ai-service
poetry init
poetry add fastapi uvicorn langgraph openai redis pydantic

# 创建Java服务
cd ../java-business-service
mvn archetype:generate \
  -DgroupId=com.teamventure \
  -DartifactId=teamventure-business \
  -DarchetypeArtifactId=maven-archetype-quickstart

# 初始化数据库
cp ../../docs/design/database-design.md ../database/schema/README.md
# 从database-design.md提取DDL → V1.0.0__init.sql
```

---

## ✅ 优点分析

### 1. 开发体验优化
- ✅ **上下文完整性**: AI在apps/teamventure/内就能看到需求→设计→代码的完整链路
- ✅ **职责清晰**: 每个应用自包含，不会与其他应用混淆
- ✅ **快速定位**: 新开发者进入项目，直接cd apps/teamventure即可开始

### 2. 多应用扩展性
- ✅ **水平扩展**: 新增应用（如ego-echo）不影响现有应用
- ✅ **独立部署**: 每个应用可以独立git submodule或docker compose部署
- ✅ **权限隔离**: 未来多团队协作时，可按应用分配访问权限

### 3. 文档与代码同步
- ✅ **版本一致**: 设计文档和代码在同一目录，git history关联紧密
- ✅ **减少过时风险**: 修改代码时更容易发现需要同步更新的文档
- ✅ **Review友好**: PR Review时能同时看到设计文档和代码实现

### 4. Monorepo优势保持
- ✅ **共享资源**: .claude/skills、scripts/等依然全局共享
- ✅ **统一构建**: 可以在顶层定义统一的CI/CD pipeline
- ✅ **原子提交**: 跨服务的功能变更可以在一个commit完成

---

## ⚠️ 需要注意的挑战

### 1. 链接维护成本
- ❌ **问题**: 现有README/ai-product-ideas.md中大量链接需要更新
- ✅ **解决方案**:
  - 使用符号链接保持旧路径有效
  - 统一使用相对路径（避免绝对路径）
  - 脚本自动检查并更新broken links

### 2. 共享资源管理
- ❌ **问题**: 如果多个应用共用某些设计模式或组件库，放哪里？
- ✅ **解决方案**:
  - 创建 `libs/` 目录存放共享代码库
  - 使用npm/maven的workspace功能实现跨应用依赖

### 3. 搜索/导航复杂度
- ❌ **问题**: 文档层级加深，搜索路径变长
- ✅ **解决方案**:
  - 每个应用的README.md提供清晰的文档导航
  - 使用 `rg` 或 `fzf` 等工具快速搜索
  - 顶层README维护"快速跳转"清单

---

## 🎯 对比：旧结构 vs 新结构

| 维度 | 旧结构（现状） | 新结构（apps/） | 评分 |
|------|--------------|----------------|------|
| **AI上下文完整性** | 文档分散在多个docs子目录 | 应用内所有资产集中 | 🟢 更好 |
| **多应用扩展** | 所有应用混在一起 | 清晰隔离 | 🟢 更好 |
| **开发启动速度** | 需要阅读多处README | 一个应用README即可 | 🟢 更好 |
| **链接维护** | 短路径 | 需要更新链接 | 🟡 稍差 |
| **学习曲线** | 平铺结构易理解 | 需要理解两层结构 | 🟡 稍差 |
| **CI/CD配置** | 简单 | 需要per-app配置 | 🟡 稍差 |

**综合评分**: 🟢 **新结构更优**（6个维度中4个更好）

---

## 📋 决策建议

### 立即执行（Week 0）
- [ ] 创建apps/目录结构
- [ ] 迁移TeamVenture所有文档到apps/teamventure/docs/
- [ ] 创建apps/teamventure/README.md（状态仪表盘）
- [ ] 更新顶层README.md，添加apps/说明

### 开发启动时（Week 1）
- [ ] 在apps/teamventure/src/下初始化代码目录
- [ ] 配置docker-compose.yml
- [ ] 创建src/README.md（开发环境Quick Start）

### 后续优化（Week 2+）
- [ ] 如果启动ego-echo开发，重复相同结构
- [ ] 编写scripts/check-links.py自动检查broken links
- [ ] 考虑是否需要libs/共享库目录

---

## 🚀 下一步行动

如果你同意这个结构，我可以立即执行：

1. **创建apps/teamventure/完整目录结构**
2. **迁移所有现有TeamVenture文档**
3. **生成apps/teamventure/README.md（应用仪表盘）**
4. **更新顶层README.md和ai-product-ideas.md链接**
5. **创建迁移完成后的验证checklist**

预计耗时：15分钟（纯文件操作，无代码修改）

---

**最后更新**: 2025-12-30
**提案状态**: 📋 待用户确认
**建议决策**: ✅ 推荐采纳新结构
