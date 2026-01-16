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

### 📊 任务进度报告
**执行多步骤任务时，必须给出当前预估进度百分比。**

报告格式：
- **每30分钟报告一次**当前进度（如 `[进度: 30%]`）
- 进度应基于已完成步骤占总步骤的比例
- 遇到阻塞或需要调整计划时，及时更新进度预估

示例：
```
[进度: 0%] 开始分析需求...
[进度: 20%] 完成代码结构分析
[进度: 50%] 核心功能实现完成
[进度: 80%] 测试通过，开始收尾
[进度: 100%] 任务完成
```

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

### 🚨 服务运行规范（重要规则）

**【必须遵守】只使用Docker容器化服务**：
- ✅ **唯一运行方式**: 通过 `docker compose` 启动所有服务
- ❌ **禁止本地Maven服务**: 不要通过 `mvn spring-boot:run` 启动Java服务
- ❌ **禁止多节点混跑**: 禁止同时运行Docker版(8080)和本地Maven版(8082)
- **原因**:
  - 避免代码不同步（Docker镜像 vs 本地代码可能不一致）
  - 避免端口冲突和配置混乱
  - 确保环境一致性（依赖版本、环境变量）
  - 统一监控和日志收集

**端口映射架构**（单节点配置）：
```
外部访问              Docker网络              容器内部
─────────────────────────────────────────────────────
localhost:8080  →  [端口映射]  →  java-business-service:8082
localhost:8000  →  [端口映射]  →  python-ai-service:8000
localhost:9090  →  [端口映射]  →  prometheus:9090
localhost:3306  →  [端口映射]  →  mysql-master:3306
```

**Nginx反向代理配置**：
- Nginx通过Docker内部网络访问服务（如 `java-business-service:8082`）
- 外部通过域名 `api.teamventure.com` 访问（Nginx监听80/443端口）
- 禁止前端直连端口（如 `localhost:8080`）

**配置同步要求**：
修改服务端口时，必须同步更新以下配置：
1. `backend/java-business-service/src/main/resources/application.yml` - 容器内端口(8082)
2. `src/nginx/nginx.conf` - Nginx upstream端口(8082)
3. `src/docker-compose.yml` - 端口映射 + Python回调URL
4. `.env.local` - `JAVA_SERVICE_PORT`宿主机端口映射(8080)

### 🔄 代码修改后的同步规范

**【关键】修改代码后必须重新构建Docker镜像**：
- ❌ **错误做法**: 直接修改代码 → `docker compose restart` → 代码不生效（镜像仍是旧版本）
- ✅ **正确做法**: 修改代码 → `docker compose build` → `docker compose up -d` → 代码生效
- **原因**: Docker镜像在构建时打包代码，重启容器不会更新镜像内的代码

**快速验证代码是否同步**：
```bash
# 检查镜像构建时间
docker images src-java-business-service --format "table {{.CreatedAt}}"

# 检查本地代码最后修改时间
ls -lt backend/java-business-service/src/main/resources/application.yml | head -1

# 如果镜像构建时间早于代码修改时间，说明代码不同步，需要重新构建
```

### 常用命令

#### 使用 Makefile（推荐）
```bash
# 在 apps/teamventure/ 目录下运行

# 显示所有可用命令
make help

# 启动所有服务（local环境）
make up

# 【代码修改后】重新构建并启动
make rebuild

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

# Token优化（减少AI调用成本）
make mock-on            # 启用Mock模式（开发测试，完全不消耗token）
make mock-off           # 关闭Mock模式（使用真实AI）
make cache-clear        # 清空AI响应缓存
make cache-stats        # 查看缓存统计
make token-stats        # 查看Token使用统计
make test-optimization  # 测试Token优化功能

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

### 前端配置规范（TeamVenture 小程序）
- **API 地址配置**: `src/frontend/miniapp/utils/config.js:38`
  - ✅ **正确**: `local: 'http://api.teamventure.com/api/v1'`（通过 Nginx 网关）
  - ❌ **错误**: `local: 'http://localhost:8080/api/v1'`（直连 Java 绕过网关）
- **本地域名绑定**: 需在 `/etc/hosts` 添加 `127.0.0.1 api.teamventure.com`
- **原因**: 小程序必须通过 Nginx 网关访问（统一 CORS、日志、限流）

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

**Token消耗（优化后）**：
- **优化前**: 输入~2500 tokens + 输出~2000 tokens = 单次¥1.0
- **优化后**: 输入~1000 tokens + 输出~2000 tokens = 单次¥0.4（节省60%）

**开发测试优化方案**：
1. **Mock模式**（推荐）：完全不调用OpenAI，token消耗为0
   ```bash
   make mock-on && make restart  # 启用Mock模式
   make mock-off && make restart # 关闭Mock模式
   ```

2. **缓存机制**（自动）：相同输入24小时内复用结果
   ```bash
   make cache-stats      # 查看缓存统计
   make cache-clear      # 清空缓存
   make token-stats      # 查看token使用量
   ```

3. **成本估算**：
   - 开发阶段（Mock模式）: ¥0/月
   - 集成测试（缓存24h，100次/天）: ~¥40/月
   - 生产环境（缓存1h，1000次/天）: ~¥480/月

**配置位置**：
- 环境变量: `src/backend/python-ai-service/.env.local`
- 完整文档: `src/backend/python-ai-service/docs/AI_TOKEN_OPTIMIZATION.md`

**监控告警**：
- 生产环境需配置预算告警（Prometheus + Grafana）
- 单日超过1000次调用时发送告警

---

## 每日播客生成规范（daily-podcast-ai）

### 标准配置（v2.0）
**生效日期**: 2026-01-16
**路径**: `apps/daily-podcast-ai/`

#### 语音参数配置
位置：`config/voice.yaml`

```yaml
hosts:
  host_a:
    name: "植萌"
    voice_id: "SKlxpKXGwoM0E8XpnxNs"  # 克隆声音
    voice_settings:
      stability: 0.0      # Creative - 最大情绪波动
      style: 0.8          # 高风格强度，激情饱满
      speed: 1.2          # 最快语速
      similarity_boost: 0.75
      use_speaker_boost: true

  host_b:
    name: "小雅"
    voice_id: "cgSgspJ2msm6clMCkdW9"  # Jessica - 活泼女声
    voice_settings:
      stability: 0.5      # Natural - 中等稳定性
      style: 0.6          # 中高风格强度
      speed: 1.1          # 稍快语速
      similarity_boost: 0.75
      use_speaker_boost: true
```

#### 重要参数说明
- **stability 仅支持**: 0.0 (Creative), 0.5 (Natural), 1.0 (Robust)
- **style 范围**: 0.0-1.0，越高越有表现力
- **speed 范围**: 0.7-1.2，越高越快
- **similarity_boost**: 保持 0.75 即可

#### 快速执行（推荐）
```bash
# 在 apps/daily-podcast-ai/ 目录下
./scripts/generate_podcast_v2.sh            # 生成今天
./scripts/generate_podcast_v2.sh 2026-01-17 # 指定日期
```

#### 手动执行
```bash
# 清理旧文件（避免缓存）
rm -rf output/{date}/dailytechnews/audio

# 生成播客
python scripts/daily_generate.py \
    --date {date} \
    --from-cache \
    --max-articles 10
```

#### 常见问题排查
1. **小雅声音不是女声**
   - 检查 `config/voice.yaml` 中 `host_b.voice_id` 是否为女声ID
   - 验证：`ls output/{date}/dailytechnews/audio/*小雅*` 应该有文件
   - 代码位置：`src/generators/tts_generator.py:327-342`（voice_map映射）

2. **植萌激情度不够**
   - 确认 `host_a.voice_settings.stability = 0.0`
   - 确认 `host_a.voice_settings.style >= 0.8`

3. **TTS报错 "invalid_ttd_stability"**
   - stability 只能是 0.0/0.5/1.0，不能是其他值
