# Notion 文档增强 - 使用示例

## 示例 1: 创建技术文档

### 用户请求

```
帮我在 Notion 创建一个 API 文档，页面地址是：
https://www.notion.so/api-docs-xxx

标题：用户认证 API 文档

内容包括：
1. 概述
2. 接口列表
3. 请求示例
4. 错误码
```

### Claude 执行流程

```javascript
// 1. 导航到页面
await mcp__plugin_playwright_playwright__browser_navigate({
  url: "https://www.notion.so/api-docs-xxx"
});

// 2. 等待加载
await mcp__plugin_playwright_playwright__browser_wait_for({ time: 3 });

// 3. 获取页面结构
await mcp__plugin_playwright_playwright__browser_snapshot();

// 4. 修改标题
await mcp__plugin_playwright_playwright__browser_click({
  element: "页面标题",
  ref: "标题ref"
});
await mcp__plugin_playwright_playwright__browser_type({
  element: "标题输入框",
  ref: "输入框ref",
  text: "用户认证 API 文档"
});
await mcp__plugin_playwright_playwright__browser_press_key({ key: "Enter" });

// 5. 粘贴内容
await mcp__plugin_playwright_playwright__browser_run_code({
  code: `async (page) => {
    const content = \`## 一、概述

用户认证 API 提供安全的身份验证服务，支持多种认证方式。

## 二、接口列表

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 登录 | POST | /auth/login | 用户登录获取 token |
| 登出 | POST | /auth/logout | 用户登出 |
| 刷新 | POST | /auth/refresh | 刷新 token |
| 验证 | GET | /auth/verify | 验证 token 有效性 |

## 三、请求示例

### 登录接口

**请求:**
\\\`\\\`\\\`json
POST /auth/login
{
  "username": "user@example.com",
  "password": "password123"
}
\\\`\\\`\\\`

**响应:**
\\\`\\\`\\\`json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 3600
}
\\\`\\\`\\\`

## 四、错误码

| 错误码 | 说明 |
|--------|------|
| 401 | 未授权 |
| 403 | 禁止访问 |
| 429 | 请求过于频繁 |
\`;

    await page.evaluate((text) => navigator.clipboard.writeText(text), content);
    await page.waitForTimeout(500);
    await page.keyboard.press('Meta+v');
    return 'done';
  }`
});

// 6. 截图确认
await mcp__plugin_playwright_playwright__browser_take_screenshot({
  filename: "api-docs-result.png",
  fullPage: true
});
```

---

## 示例 2: 创建会议纪要

### 用户请求

```
帮我创建今天的周会纪要：
https://www.notion.so/meeting-xxx

参会人：张三、李四、王五
讨论了：Q1 目标、资源分配、技术选型
待办事项：
- 张三负责完成需求文档
- 李四负责技术方案
```

### 生成的内容

```markdown
## 周会纪要 - 2026-01-05

### 会议信息
- 日期：2026-01-05
- 参会人：张三、李四、王五
- 主持人：[待填写]

### 讨论要点

#### Q1 目标
- [会议讨论内容]

#### 资源分配
- [会议讨论内容]

#### 技术选型
- [会议讨论内容]

### 行动项

| 任务 | 负责人 | 截止日期 | 状态 |
|------|--------|----------|------|
| 完成需求文档 | 张三 | [待定] | 待开始 |
| 完成技术方案 | 李四 | [待定] | 待开始 |

### 下次会议
- 时间：[待定]
- 议题：[待定]
```

---

## 示例 3: 批量格式化现有内容

### 用户请求

```
这个 Notion 页面有些乱，帮我整理一下格式：
https://www.notion.so/messy-page-xxx

把内容按以下结构重新组织：
1. 项目概述
2. 技术架构
3. 开发计划
4. 风险评估
```

### 执行策略

1. 先获取页面当前内容（通过 snapshot 了解结构）
2. 全选现有内容（`Meta+a`）
3. 删除旧内容（`Backspace`）
4. 粘贴新的格式化内容

```javascript
// 清理旧内容
await mcp__plugin_playwright_playwright__browser_click({
  element: "内容区域",
  ref: "content-ref"
});
await mcp__plugin_playwright_playwright__browser_press_key({ key: "Meta+a" });
await mcp__plugin_playwright_playwright__browser_press_key({ key: "Backspace" });

// 粘贴新内容
await mcp__plugin_playwright_playwright__browser_run_code({
  code: `async (page) => {
    const newContent = \`## 一、项目概述
[从原内容提取]

## 二、技术架构
[从原内容提取]

## 三、开发计划
[从原内容提取]

## 四、风险评估
[从原内容提取]
\`;
    await page.evaluate((text) => navigator.clipboard.writeText(text), newContent);
    await page.waitForTimeout(500);
    await page.keyboard.press('Meta+v');
  }`
});
```

---

## 示例 4: 创建产品需求文档

### 用户请求

```
帮我创建一个 PRD 模板，标题是"AI 聊天机器人需求文档"
```

### 生成的 PRD 模板

```markdown
## 产品需求文档

### 基本信息
- 产品名称：AI 聊天机器人
- 版本：v1.0
- 作者：[作者]
- 日期：2026-01-05
- 状态：草稿

### 一、背景与目标

#### 1.1 背景
[描述产品背景和市场机会]

#### 1.2 目标
- 业务目标：
- 用户目标：
- 成功指标：

### 二、用户分析

#### 2.1 目标用户
| 用户类型 | 特征 | 需求 |
|---------|------|------|
| 类型A | | |
| 类型B | | |

#### 2.2 用户场景
1. 场景一：
2. 场景二：

### 三、功能需求

#### 3.1 核心功能
| 功能 | 优先级 | 描述 |
|------|--------|------|
| 功能1 | P0 | |
| 功能2 | P1 | |

#### 3.2 功能详情

##### 功能1：[名称]
- 描述：
- 输入：
- 输出：
- 验收标准：

### 四、非功能需求

- 性能要求：
- 安全要求：
- 兼容性：

### 五、里程碑

| 阶段 | 时间 | 交付物 |
|------|------|--------|
| 需求评审 | | PRD |
| 设计完成 | | 设计稿 |
| 开发完成 | | 代码 |
| 测试完成 | | 测试报告 |
| 上线 | | |

### 六、附录

- 相关文档：
- 参考资料：
```

---

## 示例 5: 使用表格整理数据

### 用户请求

```
把这些数据整理成表格放到 Notion：

项目A - 进行中 - 张三 - 60%
项目B - 已完成 - 李四 - 100%
项目C - 待开始 - 王五 - 0%
```

### 生成的表格

```markdown
## 项目进度一览

| 项目 | 状态 | 负责人 | 进度 |
|------|------|--------|------|
| 项目A | 进行中 | 张三 | 60% |
| 项目B | 已完成 | 李四 | 100% |
| 项目C | 待开始 | 王五 | 0% |
```

---

## 常见问题示例

### Q1: 内容粘贴后格式不对

**问题**: Markdown 没有被正确转换

**解决**: 确保在空行粘贴，而不是在已有文本块中

```javascript
// 先创建新行
await mcp__plugin_playwright_playwright__browser_press_key({ key: "Enter" });
// 再粘贴
await mcp__plugin_playwright_playwright__browser_press_key({ key: "Meta+v" });
```

### Q2: 页面一直加载

**问题**: 页面未完全加载就开始操作

**解决**: 增加等待时间或等待特定元素

```javascript
await mcp__plugin_playwright_playwright__browser_wait_for({ time: 5 });
// 或
await mcp__plugin_playwright_playwright__browser_wait_for({
  text: "开始输入以编辑文本"
});
```

### Q3: 找不到元素

**问题**: snapshot 返回的 ref 不可用

**解决**: 重新获取 snapshot，页面状态可能已变化

```javascript
// 每次操作前重新获取
await mcp__plugin_playwright_playwright__browser_snapshot();
```
