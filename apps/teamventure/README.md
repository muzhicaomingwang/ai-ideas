# TeamVenture - AI团建策划助手

> **定位**: toProC AI SaaS - 替代传统团建第三方服务，成本降低50%+
>
> **状态**: 🟡 Phase 1 开发中 | Week 0 - 文档就绪，准备启动开发
>
> **版本**: v0.1.0-alpha

---

## 📚 学习资源

![从零开始学习AI编程](./docs/images/从零开始学习AI编程.png)

---

## 🎯 产品概述

### 核心价值主张
帮助企业HR/行政人员在15分钟内生成3套完整团建方案（预算+行程+供应商），无需支付传统第三方机构¥1000-2000/人的高昂费用。

### 一句话描述
**"AI驱动的团建策划助手，让HR从焦头烂额的协调者变为手握多套方案的决策者"**

### 目标用户
- 🎯 **主要用户**: 50-200人中小企业的HR/行政人员
- 📊 **典型场景**: 组织2天1夜、50人规模、预算¥600/人的团建活动
- 💰 **支付意愿**: 愿为确定性和效率支付¥99-299的服务费

---

## 📂 项目结构

```
teamventure/
├── README.md                   # 本文件（应用总览）
│
├── docs/                       # 📚 完整文档集
│   ├── requirements/           # 需求文档
│   │   ├── market-research.md          # 市场调研
│   │   ├── prd.md                      # 产品需求文档（1352行）
│   │   └── business-plan.md            # 商业计划（10000+字）
│   │
│   ├── design/                 # 设计文档
│   │   ├── event-storming.md           # 事件风暴+领域语言
│   │   ├── strategy-and-ddd.md         # DDD战略+战术设计
│   │   ├── miniapp-product-design.md   # 小程序UX/UI/UE设计
│   │   ├── api-design.md               # API接口设计
│   │   ├── detailed-design.md          # ⭐ 详细设计（1660行）
│   │   └── database-design.md          # ⭐ 数据库设计+DDL（755行）
│   │
│   ├── qa/                     # 测试文档
│   │   └── checklist-and-testcases.md  # 测试用例+Checklist
│   │
│   └── reviews/                # 评审记录
│       └── phase1-documents-review.md  # Phase 1文档评审报告
│
└── src/                        # 💻 源代码（Monorepo）
    ├── README.md               # 开发环境Quick Start
    ├── docker-compose.yml      # 本地开发环境（待创建）
    │
    ├── backend/
    │   ├── python-ai-service/          # AI服务（FastAPI + LangGraph）
    │   └── java-business-service/      # 业务服务（SpringBoot + COLA）
    │
    ├── frontend/
    │   └── miniapp/                    # 微信小程序
    │
    ├── database/
    │   ├── schema/                     # DDL脚本
    │   └── migrations/                 # 数据迁移脚本
    │
    └── nginx/                          # API网关配置
```

---

## 🚀 快速开始

### 1. 了解产品（5分钟）

**必读文档**：
1. [产品需求文档 (PRD)](./docs/requirements/prd.md) - 理解用户需求和产品设计
2. [详细设计](./docs/design/detailed-design.md) - 理解技术架构和开发规范

**可选文档**：
- [市场调研](./docs/requirements/market-research.md) - 市场背景和竞争分析
- [商业计划](./docs/requirements/business-plan.md) - 商业模式和财务预测

### 2. 理解架构（10分钟）

**技术栈速览**：
```
前端: 微信小程序（原生框架）
后端: Java 17 + SpringBoot 3.2（业务） + Python 3.11 + FastAPI（AI）
数据库: MySQL 8.0（主从）+ Redis 7.0
消息队列: RabbitMQ 3.12
AI框架: LangGraph 0.0.40 + GPT-4
```

**架构图**：
```
┌──────────────────┐
│   微信小程序      │
└────────┬─────────┘
         │ HTTPS
         ▼
┌──────────────────┐
│   Nginx Gateway  │
└────┬────────┬────┘
     │        │
     ▼        ▼
┌─────────┐ ┌──────────┐
│  Java   │ │  Python  │
│ Service │◄──RabbitMQ──►│ AI Service│
└────┬────┘ └─────┬────┘
     │            │
     ▼            ▼
┌──────────────────────┐
│ MySQL + Redis + MQ   │
└──────────────────────┘
```

### 3. 开始开发

👉 **详细开发环境配置请查看**: [src/README.md](./src/README.md)

```bash
# 进入代码目录
cd apps/teamventure/src

# 启动本地开发环境（Docker）
docker-compose up -d

# 启动Java服务
cd backend/java-business-service
mvn spring-boot:run

# 启动Python AI服务
cd backend/python-ai-service
poetry run uvicorn src.main:app --reload
```

---

## 📊 开发状态

### Phase 1 里程碑（2026 Q1）

| Week | 目标 | 状态 | 交付物 |
|------|------|------|--------|
| **Week 0** | 文档完成 | ✅ **已完成** | PRD、详细设计、数据库设计 |
| **Week 1** | 基础设施 | 🟡 进行中 | Docker环境、MySQL主从、RabbitMQ |
| **Week 2** | Java框架 | ⏳ 未开始 | SpringBoot、COLA架构、微信登录 |
| **Week 3** | Python AI | ⏳ 未开始 | FastAPI、LangGraph、GPT-4集成 |
| **Week 4** | 核心功能 | ⏳ 未开始 | 方案生成E2E流程 |
| **Week 5** | 小程序 | ⏳ 未开始 | 4个核心页面 |
| **Week 6** | 测试 | ⏳ 未开始 | 测试用例通过 |
| **Week 7** | 上线 | ⏳ 未开始 | 灰度→全量发布 |

### 当前待办

**Week 1 任务清单**：
- [ ] 配置docker-compose.yml（MySQL主从+Redis+RabbitMQ）
- [ ] 执行数据库初始化脚本（V1.0.0__init.sql）
- [ ] 验证MySQL主从复制状态
- [ ] 配置Java项目骨架（pom.xml + COLA目录结构）
- [ ] 配置Python项目骨架（pyproject.toml + 目录结构）

---

## 🎯 核心功能清单

### Phase 1 MVP功能（7周）

| 功能模块 | 优先级 | 状态 | 说明 |
|---------|-------|------|------|
| 微信登录 | P0 | ⏳ | 用户身份认证 |
| 方案生成（AI） | P0 | ⏳ | 4个Agent协作生成3套方案 |
| 方案列表 | P0 | ⏳ | 查看历史方案 |
| 方案详情 | P0 | ⏳ | 查看方案完整信息 |
| 确认方案 | P0 | ⏳ | 标记已采纳方案 |
| 联系供应商 | P1 | ⏳ | 记录联系日志 |
| 供应商目录 | P1 | ⏳ | 查看供应商库 |

### Phase 2 增强功能（规划中）

- 方案对比（并排查看3套方案）
- 自定义预算分配
- 供应商评价系统
- 团队协作（多人共同决策）

---

## 📈 关键指标

### 产品指标
- **方案生成时长**: < 5分钟（目标）
- **方案采纳率**: > 40%（目标）
- **供应商联系率**: > 60%（目标）

### 技术指标
- **API响应时间**: P95 < 500ms
- **AI生成成功率**: > 95%
- **系统可用性**: > 99.5%

### 商业指标
- **付费转化率**: 20%（免费试用→付费）
- **CAC**: ¥600/用户
- **LTV**: ¥17,940/用户（3年）
- **LTV/CAC**: 29.9x

---

## 📚 文档导航

### 需求阶段
1. [市场调研](./docs/requirements/market-research.md) - 市场规模、竞品分析、用户痛点
2. [产品需求文档 (PRD)](./docs/requirements/prd.md) - JTBD、用户画像、功能设计
3. [商业计划](./docs/requirements/business-plan.md) - 商业模式、GTM策略、融资计划

### 设计阶段
4. [事件风暴](./docs/design/event-storming.md) - 领域事件、聚合根、领域语言
5. [DDD战略+战术设计](./docs/design/strategy-and-ddd.md) - 限界上下文、实体、值对象
6. [小程序产品设计](./docs/design/miniapp-product-design.md) - UX/UI/UE设计
7. [API接口设计](./docs/design/api-design.md) - RESTful API规范
8. **[详细设计](./docs/design/detailed-design.md)** ⭐ - 架构、服务、代码规范
9. **[数据库设计](./docs/design/database-design.md)** ⭐ - DDL、索引、分表策略

### 测试阶段
10. [测试用例+Checklist](./docs/qa/checklist-and-testcases.md) - 测试清单

### 评审记录
11. [Phase 1文档评审](./docs/reviews/phase1-documents-review.md) - 文档质量评审

---

## 🛠️ 技术栈详情

### 后端（Java）
- **框架**: SpringBoot 3.2+、SpringMVC、MyBatis 3.5+
- **架构**: COLA 4层（写操作）+ 3层（读操作）
- **数据库**: MySQL 8.0（InnoDB、主从复制）
- **缓存**: Redis 7.0（Session、幂等性）
- **消息队列**: RabbitMQ 3.12（异步通信）

### 后端（Python AI）
- **框架**: FastAPI 0.109+
- **AI编排**: LangGraph 0.0.40+
- **LLM**: OpenAI GPT-4（gpt-4-0125-preview）
- **依赖**: Pydantic、httpx、redis-py

### 前端（小程序）
- **框架**: 微信小程序原生（WXML/WXSS/JavaScript）
- **基础库**: 最新稳定版
- **网络**: wx.request封装

### 基础设施
- **网关**: Nginx 1.24+（反向代理、负载均衡）
- **容器**: Docker + Docker Compose（本地开发）
- **监控**: 待定（考虑Prometheus + Grafana）

---

## 🤝 团队协作

### 开发规范
- **代码提交**: 遵循Git Commit规范（feat/fix/docs/test）
- **分支策略**: main（稳定）、develop（开发）、feature/*（特性）
- **Code Review**: 所有PR必须经过Review
- **测试覆盖率**: 核心业务逻辑 > 80%

### 沟通机制
- **每日站会**: 同步进度、识别阻塞
- **每周Review**: 评审代码和设计
- **里程碑演示**: 每周五演示可工作的软件

---

## 📞 联系方式

### 问题反馈
- **设计问题**: 在团队周会提出，记录到Issues
- **实现问题**: 先查阅文档，再咨询技术Leader
- **Bug报告**: 提交GitHub Issues，使用模板

### 相关链接
- **GitHub仓库**: [ideas/apps/teamventure](../../)
- **产品原型**: 待补充
- **API文档**: 待补充（OpenAPI）

---

## 📜 版本历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v0.1.0-alpha | 2025-12-30 | 初始应用结构，文档迁移到apps/目录 | Claude + Team |

---

**最后更新**: 2025-12-30
**应用状态**: 🟡 Phase 1 开发准备中
**下个里程碑**: Week 1 - 基础设施搭建（预计2026-01-06）
