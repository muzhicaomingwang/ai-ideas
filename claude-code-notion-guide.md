# 如何使用 Claude Code 完善 Notion 文档

## 一、概述

Claude Code 是 Anthropic 官方的 CLI 工具，通过 **MCP (Model Context Protocol) 集成** 可以直接与 Notion 工作区交互。这使得你可以：

- 搜索和查找 Notion 页面/数据库
- 创建新页面和数据库行
- 查询数据库内容
- 创建任务

---

## 二、可用的 Notion 技能

| 技能名称 | 功能描述 | 调用方式 |
|---------|---------|---------|
| `notion-search` | 搜索工作区中的页面/数据库 | 自然语言描述搜索内容 |
| `notion-find` | 按标题关键词快速查找 | 提供标题关键词 |
| `notion-create-page` | 创建新页面 | 指定父页面和内容 |
| `notion-create-database-row` | 在数据库中新增行 | 提供数据库名和字段值 |
| `notion-create-task` | 创建任务 | 提供任务描述 |
| `notion-database-query` | 查询数据库内容 | 指定数据库名/ID |

---

## 三、配置步骤

### 1. 确保 MCP Server 已连接

Claude Code 需要连接到 Notion MCP Server。在 Claude Code 设置中添加：

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@anthropic/notion-mcp-server"],
      "env": {
        "NOTION_API_KEY": "your-notion-api-key"
      }
    }
  }
}
```

### 2. 获取 Notion API Key

1. 访问 [Notion Integrations](https://www.notion.so/my-integrations)
2. 点击 "New integration"
3. 命名你的集成（如 "Claude Code"）
4. 复制生成的 API Key

### 3. 授权页面访问

在 Notion 中，对需要访问的页面：
- 点击右上角 `...` → `Connections` → 添加你创建的集成

---

## 四、实用场景与示例

### 场景1：搜索文档

```
你：帮我在Notion中搜索"产品需求"相关的文档
Claude Code：[调用 notion-search] 找到以下结果...
```

### 场景2：创建会议纪要

```
你：在"团队周报"数据库中创建一条新记录，标题是"2026-01-05周会"
Claude Code：[调用 notion-create-database-row] 已创建...
```

### 场景3：批量整理文档

```
你：查询"任务追踪"数据库中所有状态为"进行中"的任务
Claude Code：[调用 notion-database-query] 返回结果列表...
```

### 场景4：基于本地文件创建Notion页面

```
你：把 docs/meeting-notes.md 的内容创建为一个新的Notion页面
Claude Code：[读取本地文件，调用 notion-create-page] 页面已创建...
```

---

## 五、最佳实践

1. **结构化内容**：Notion擅长处理结构化数据，准备好清晰的标题和层级结构
2. **使用数据库**：对于重复性内容（会议、任务、文档），优先使用数据库而非普通页面
3. **批量操作**：一次请求可以包含多个操作，Claude Code 会并行处理
4. **保持授权**：确保所有需要访问的页面都已对集成授权

---

## 六、常见问题

**Q: 为什么搜索不到某些页面？**
A: 确保页面已对你的 Notion 集成授权（Connections设置）

**Q: 能否编辑现有页面内容？**
A: 目前技能主要支持创建和查询，复杂编辑建议直接在Notion中操作

**Q: API调用有限制吗？**
A: Notion API 有频率限制（约3请求/秒），正常使用不会触发

---

## 七、参考资源

- [Claude Code 官方文档](https://docs.anthropic.com/claude-code)
- [Notion API 文档](https://developers.notion.com/)
- [Notion Skills for Claude](https://www.notion.so/notiondevs/Notion-Skills-for-Claude-28da4445d27180c7af1df7d8615723d0)
