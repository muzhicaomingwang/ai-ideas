# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 📌 维护规则（Meta Rules）

### 🔄 自动更新机制
**在 Code Review 时，将新发现的项目规则、约定、最佳实践更新到本文件，目的是让 AI 更懂这个项目。**

更新触发时机：
- 发现代码中有未文档化的重要约定
- 新增关键命令或工具链
- 架构发生重大变更
- 踩坑后总结的经验教训
- 团队达成的新共识

更新方式：
1. 在相应章节添加具体规则（保持结构化）
2. 如果是全新类别，在本文件末尾添加新章节
3. 提交 PR 时在描述中注明"更新 CLAUDE.md"
4. 定期（每月）review 并精简过时内容

⚠️ **注意**：避免重复 README 中的内容，优先记录"难以通过搜索发现的隐性知识"

---

## 仓库性质与核心原则

这是一个**AI产品创新知识库**，而非传统代码项目。核心内容是结构化的Markdown文档（PRD/BP/模板/课程），用于沉淀AI产品设计方法论。

### 核心原则（适用于所有产品与技术讨论）
详细应用指南见 `docs/architecture-analysis.md`

1. **结构化优先** - 输入/输出尽量结构化（便于渲染、评测、埋点、复盘）
2. **可验证** - 每个结论配"证据/数据/假设/验证计划"
3. **隐私与安全** - 对情绪/心理相关场景采用最小化数据与明确边界；危机内容优先安全兜底
4. **可落地** - 设计必须能转化为工程任务（API、数据结构、指标、实验计划、里程碑）

---

## 仓库架构（4层金字塔）

```
L1: 入口层
├── README.md - 导航枢纽 + 推荐阅读路径

L2: 想法层
├── ai-product-ideas.md - 6个AI产品想法池（toC/toProC/toB）

L3: 执行层
├── docs/prds/ - 完整产品需求文档
├── docs/business-plans/ - 商业计划书
└── apps/ - 进入开发阶段的应用（含文档+源代码）
    └── teamventure/ - AI团建策划助手（Phase 1 开发中）

L4: 基础设施层
├── templates/ - 可复用的BP模板（包含AI特有章节）
└── educational-products/ - 12周课程体系（面向非技术产品人员）
```

---

## TeamVenture 应用开发（`apps/teamventure/`）

### 技术栈
- **前端**: 微信小程序（原生框架 WXML/WXSS/JS）
- **后端（业务）**: Java 17 + SpringBoot 3.2 + COLA架构 + MyBatis-Plus
- **后端（AI）**: Python 3.11 + FastAPI + LangGraph + GPT-4
- **基础设施**: MySQL 8.0（主从）+ Redis 7.0 + RabbitMQ 3.12 + Nginx

### 常用命令

#### 使用 Makefile（推荐）
```bash
# 在 apps/teamventure/ 目录下运行

# 显示所有可用命令
make help

# 启动所有服务（local环境）
make up

# 启动所有服务（指定环境：dev/beta/prod）
make ENV=dev up

# 查看服务状态
make ps

# 查看所有服务日志
make logs

# 查看指定服务日志
make logs SERVICE=java-business-service
make logs-java          # Java服务
make logs-python        # Python AI服务
make logs-mysql         # MySQL
make logs-redis         # Redis
make logs-rabbitmq      # RabbitMQ

# 重启服务
make restart

# 停止服务
make down

# 完全重建并启动
make rebuild

# 进入容器
make exec-java          # Java容器
make exec-python        # Python容器
make exec-mysql         # MySQL（自动登录）
make exec-redis         # Redis（自动认证）

# 运行测试
make test               # 所有测试
make test-java          # Java单元测试
make test-python        # Python测试

# 健康检查
make health             # 检查所有服务健康状态

# 代码格式化
make format-java        # 使用spotless格式化Java代码
make format-python      # 使用black+isort格式化Python代码

# 数据库操作
make db-backup          # 备份数据库
make db-restore FILE=backup/xxx.sql  # 恢复数据库

# 清理
make clean              # 停止服务并清理容器、网络
make clean-volumes      # 清理数据卷（危险操作！）
make clean-images       # 清理构建的镜像
```

#### 手动启动（不使用Makefile）
```bash
# 1. 启动基础设施
cd apps/teamventure/src
docker compose -f docker-compose.yml --env-file .env.local up -d

# 2. 启动Java服务
cd backend/java-business-service
mvn spring-boot:run

# 3. 启动Python AI服务
cd backend/python-ai-service
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 4. 运行测试
# Java测试
cd backend/java-business-service
mvn test                    # 单元测试
mvn verify                  # 集成测试

# Python测试
cd backend/python-ai-service
poetry run pytest tests/unit/              # 单元测试
poetry run pytest tests/integration/       # 集成测试
poetry run pytest --cov=src tests/         # 测试覆盖率

# 5. 代码格式化
# Java
cd backend/java-business-service
mvn spotless:apply

# Python
cd backend/python-ai-service
poetry run black .
poetry run isort .
poetry run ruff check .
```

### 服务端口清单
| 服务 | 端口 | 访问地址 |
|------|------|---------|
| Java业务服务 | 8080 | http://localhost:8080 |
| Python AI服务 | 8000 | http://localhost:8000 |
| MySQL主库 | 3306 | localhost:3306 |
| MySQL从库 | 3307 | localhost:3307 |
| Redis | 6379 | localhost:6379 |
| RabbitMQ | 5672 | localhost:5672 |
| RabbitMQ管理界面 | 15672 | http://localhost:15672 (admin/admin123456) |

### 架构要点

#### COLA架构（Java业务服务）
- **写操作**: 4层架构（adapter → app → domain → infrastructure）
- **读操作**: 3层架构（adapter → app → infrastructure，跳过domain）
- **数据源路由**: 写操作强制主库，读操作优先从库
- **幂等性**: 所有写操作通过Redis实现幂等（key: `idempotency:${requestId}`）

#### LangGraph AI编排（Python AI服务）
- **4个Agent**: RequirementParser → SupplierMatcher → PlanGenerator → PlanReviewer
- **状态机**: 使用LangGraph StateGraph管理Agent流转
- **回调机制**: AI生成完成后通过HTTP回调Java服务（`POST /internal/plans/batch`）
- **消息队列**: 通过RabbitMQ接收plan_request事件（队列: `plan.generation.request`）

#### 数据库设计
- **主从复制**: 所有写操作写入主库，读操作从从库读取
- **分表策略**: `plans` 表按用户ID哈希分4个分表（`plans_0` ~ `plans_3`）
- **ULID**: 所有ID使用ULID格式（26字符，字典序可排序）
- **DDL位置**: `apps/teamventure/src/database/schema/`

### 重要文档位置
- **完整PRD**: `apps/teamventure/docs/requirements/prd.md`（1352行）
- **详细设计**: `apps/teamventure/docs/design/detailed-design.md`（1660行）
- **数据库设计**: `apps/teamventure/docs/design/database-design.md`（755行，含DDL）
- **API设计**: `apps/teamventure/docs/design/api-design.md`
- **测试文档**: `apps/teamventure/docs/qa/backend-api-step-by-step-test-plan.md`
- **测试脚本**: `apps/teamventure/docs/qa/scripts/run_backend_api_full_coverage.sh`
- **开发指南**: `apps/teamventure/src/README.md`（完整开发环境搭建步骤）

---

## 文档维护规范

### 命名规范
- PRD文件: `docs/prds/{产品代号}-{模块}-prd.md`
- BP文件: `docs/business-plans/{产品代号}-business-plan.md`
- 文件命名尽量稳定，避免破坏链接与目录锚点

### 版本管理
- PRD/BP重大变更按"版本号 + 日期 + 变更点"记录在文档头部
- 关键里程碑打Git标签（如 `ego-echo-bp-v2.0`）

### 一致性检查
修改核心概念（产品定位/时间承诺/目标用户）时，检查是否需要同步更新多个文档：
- 参考 `docs/architecture-analysis.md` 第3章了解需同步的字段清单
- 跨文档引用字段（如"15分钟""3套方案""¥99-299"）需全局一致

### Git提交规范（TeamVenture应用）
```
<type>(<scope>): <subject>

<body>

<footer>

类型（type）:
- feat: 新功能
- fix: 修复bug
- docs: 文档修改
- style: 代码格式调整（不影响逻辑）
- refactor: 重构（既不是新功能也不是bug修复）
- test: 添加测试
- chore: 构建配置或辅助工具变更

范围（scope）:
- auth: 认证模块
- plan: 方案生成模块
- supplier: 供应商模块
- db: 数据库
- config: 配置文件
- ai: AI服务

示例:
feat(plan): 实现方案生成核心流程

- 添加4个Agent（RequirementParser, SupplierMatcher, PlanGenerator, PlanReviewer）
- 实现LangGraph状态机编排
- 添加单元测试（覆盖率85%）

Closes #123
```

---

## 推荐阅读路径

### 快速了解（5分钟）
1. 阅读本 `CLAUDE.md`
2. 浏览想法池: `ai-product-ideas.md`

### 学习BP写作（15分钟）
1. 模板: `templates/business-plan-template.md`
2. 参考字段说明

### 深度学习样例（1小时）
1. 完整PRD: `docs/prds/ego-echo-workplace-recovery-prd.md`
2. 完整BP: `docs/business-plans/ego-echo-business-plan.md`

### 了解架构与风险（30分钟）
1. 架构分析: `docs/architecture-analysis.md`（1200+行）

### TeamVenture开发入门（30分钟）
1. 应用总览: `apps/teamventure/README.md`
2. 开发环境搭建: `apps/teamventure/src/README.md`
3. 详细设计: `apps/teamventure/docs/design/detailed-design.md`

---

## 特殊注意事项

### 敏感信息
- `.env.*` 文件包含数据库密码、API密钥等敏感信息，**绝不提交到Git**
- `.env.example` 和 `.env.local` 中的示例密码仅供本地开发，生产环境必须更换

### 跨文档一致性
修改以下关键字段时，需全局搜索并同步更新：
- 产品定位（如"AI团建策划助手"）
- 时间承诺（如"15分钟"）
- 核心指标（如"3套方案""¥99-299"）
- 技术栈版本号

### 数据库迁移
- 新增DDL脚本命名: `V{major}.{minor}.{patch}__{description}.sql`
- 生产环境执行DDL前必须经过Code Review
- 涉及大表（>100万行）的ALTER操作需制定降级预案

### AI成本控制（TeamVenture）
- 每次方案生成约调用GPT-4 4次（4个Agent）
- 单次成本约¥0.8-1.2（输入3000 tokens，输出2000 tokens）
- 生产环境需配置预算告警（Prometheus + Grafana）
