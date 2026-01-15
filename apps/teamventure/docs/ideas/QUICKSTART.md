# 每日创意生成 - 快速开始指南

> 本指南帮助你快速启动和使用 TeamVenture 每日创意生成功能

## 🚀 功能概述

**每日创意生成**是一个自动化后台任务，每天上午10点自动生成5个 TeamVenture 功能改进创意，并：
- 保存为 Markdown 文件（`docs/ideas/YYYY/MM/YYYY-MM-DD.md`）
- 自动提交到 Git
- 同步到 Notion（可选）
- 推送到飞书文档（可选）

---

## 📋 前置条件

### 必需
- ✅ Docker 和 Docker Compose 已安装
- ✅ OpenAI API Key（用于调用 GPT-4）
- ✅ Git 仓库已初始化

### 可选
- 🔲 Notion 工作区和页面 ID（需启用 Notion MCP）
- 🔲 飞书应用凭证（需启用飞书 MCP）

---

## ⚙️ 配置步骤

### Step 1: 安装依赖

```bash
cd teamventure/src/backend/python-ai-service
poetry install
```

这会自动安装以下新增依赖：
- `apscheduler` - 定时任务框架
- `gitpython` - Git 操作库

### Step 2: 配置环境变量

编辑 `teamventure/src/.env.local`：

```bash
# ==================== 每日创意生成配置 ====================
DAILY_IDEA_ENABLED=true        # 启用创意生成
DAILY_IDEA_CRON_HOUR=10        # 每天10点
DAILY_IDEA_CRON_MINUTE=0       # 0分

# Notion 集成（可选）
NOTION_PAGE_ID=your-notion-page-id-here

# 飞书集成（可选）
FEISHU_DOC_TOKEN=your-feishu-doc-token
FEISHU_CHAT_ID=your-feishu-chat-id
```

**获取配置方法**：
- **Notion Page ID**: 在 Notion 页面 URL 中获取（格式：`https://notion.so/xxxxx`）
- **飞书 Doc Token**: 在飞书文档分享链接中获取
- **飞书 Chat ID**: 使用飞书 API 获取群聊 ID

### Step 3: 重新构建并启动服务

```bash
cd teamventure
make rebuild
```

这会：
1. 重新构建 Python AI 服务镜像（包含新增代码）
2. 启动所有服务（包括定时任务调度器）

### Step 4: 验证调度器启动

查看日志，确认调度器已启动：

```bash
make logs-python | grep "Scheduler started"
```

预期输出：
```
✅ Scheduler started
📅 每日创意生成任务: 每天 10:00
```

---

## 🧪 测试运行

### 手动触发（无需等待10点）

```bash
make generate-ideas
```

这会立即执行创意生成任务，输出类似：
```
🎯 开始生成 2026-01-15 的创意...
📚 收集上下文信息...
✅ 上下文收集完成: 6 项
🤖 调用 OpenAI API 生成创意...
✅ 创意生成成功: 5 个
   1. [P0/ux] 方案对比智能排序
   2. [P1/performance] 地图静态图片预加载
   3. [P1/feature] 新增密室逃脱活动类型
   4. [P2/architecture] 重构供应商匹配模块
   5. [P2/security] API 限流防护
✅ 文件保存成功: docs/ideas/2026/01/2026-01-15.md
✅ Git 提交成功
✅ 任务执行完成，耗时 45.23 秒
```

### 查看生成结果

```bash
# 查看今日创意
cat docs/ideas/2026/01/$(date +%Y-%m-%d).md

# 查看创意生成历史
make ideas-status
```

### 验证 Git 提交

```bash
git log --oneline -1
```

预期输出：
```
a1b2c3d auto: daily ideas generation 2026-01-15
```

---

## 📊 监控和调试

### 查看定时任务日志

```bash
# 实时查看 Python 服务日志
make logs-python

# 过滤创意生成相关日志
make logs-python | grep "daily_idea"
```

### 检查调度器状态

在 Python 服务日志中查找：
```
✅ 定时任务调度器已启动
📅 每日创意生成任务: 每天 10:00
📋 已注册任务数: 1
   - 每日创意生成 (ID: daily_idea_generation)
```

### 常见问题排查

#### 1. 调度器未启动
**症状**：日志中没有"Scheduler started"
**原因**：`DAILY_IDEA_ENABLED=false`
**解决**：检查 `.env.local` 配置

#### 2. OpenAI API 调用失败
**症状**：日志显示"OpenAI API error"
**原因**：API Key 无效或限流
**解决**：检查 `OPENAI_API_KEY` 配置，查看 OpenAI 账户余额

#### 3. Git 提交失败
**症状**：日志显示"Git 操作失败"
**原因**：容器内没有 Git 权限或配置
**解决**：
- 检查 Docker volumes 挂载（`../.git:/workspace/.git:rw`）
- 检查 Git 用户配置（`GIT_AUTHOR_NAME` 等）

#### 4. 创意重复
**症状**：生成的创意与历史相似
**原因**：历史创意扫描失败或 Prompt 未生效
**解决**：检查 `docs/ideas/` 目录结构，手动调整 Prompt

---

## 🔧 高级配置

### 自定义执行时间

修改 `.env.local`：
```bash
DAILY_IDEA_CRON_HOUR=14        # 改为每天下午2点
DAILY_IDEA_CRON_MINUTE=30      # 30分
```

重启服务：
```bash
make restart
```

### 禁用自动生成

```bash
DAILY_IDEA_ENABLED=false
```

### 仅启用本地存储（跳过 Notion/飞书）

```bash
NOTION_PAGE_ID=           # 留空
FEISHU_DOC_TOKEN=         # 留空
FEISHU_CHAT_ID=           # 留空
```

---

## 📝 手动编辑创意

生成的创意文件是标准 Markdown 格式，可以手动编辑：

1. 打开文件：`docs/ideas/2026/01/YYYY-MM-DD.md`
2. 编辑内容（修改描述、优先级等）
3. Git 提交更改

**注意**：手动编辑后，建议在 commit message 中注明"人工调整"以区分自动生成。

---

## 🔗 集成配置

### Notion 集成

1. **启用 Notion MCP**（如果未启用）：
   ```bash
   claude mcp auth plugin:notion
   ```

2. **创建 Notion 父页面**：
   - 在 Notion 中创建一个新页面作为创意归档的父页面
   - 复制页面 ID（从 URL 中获取）

3. **配置环境变量**：
   ```bash
   NOTION_PAGE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

4. **重启服务**：
   ```bash
   make restart
   ```

### 飞书集成

1. **启用飞书 MCP**（如果未启用）：
   ```bash
   claude mcp auth plugin:feishu
   ```

2. **创建飞书文档和群聊**：
   - 创建一个飞书文档用于归档创意
   - 创建或选择一个飞书群聊用于通知

3. **获取 Token 和 ID**：
   ```bash
   # 获取文档 token
   # 从飞书文档 URL 中提取（格式：https://xxx.feishu.cn/docx/xxxxx）

   # 获取群聊 ID
   # 使用飞书 API: mcp__feishu__im_v1_chat_list
   ```

4. **配置环境变量**：
   ```bash
   FEISHU_DOC_TOKEN=doccnxxxxxxxxxxxxx
   FEISHU_CHAT_ID=oc_xxxxxxxxxxxxx
   ```

5. **重启服务**：
   ```bash
   make restart
   ```

---

## 📈 后续优化建议

### Phase 1（已完成）
- ✅ 基础定时任务
- ✅ 本地 Markdown 存储
- ✅ Git 自动提交
- ✅ Notion/飞书同步框架

### Phase 2（可选增强）
- 🔲 添加创意评分系统（团队投票）
- 🔲 自动创建 GitHub Issue（高优先级创意）
- 🔲 实现创意实现进度跟踪
- 🔲 生成周报/月报汇总

### Phase 3（高级功能）
- 🔲 多模型对比（GPT-4 vs Claude vs Gemini）
- 🔲 创意实现助手（自动生成代码框架）
- 🔲 竞品动态监控
- 🔲 集成 JIRA/Linear 项目管理工具

---

## 🆘 获取帮助

遇到问题？请检查：

1. **日志文件**：`make logs-python`
2. **配置文件**：`src/.env.local`
3. **测试用例**：`make test-python`
4. **计划文档**：参考本仓库的实现计划

---

*最后更新时间: 2026-01-15*
