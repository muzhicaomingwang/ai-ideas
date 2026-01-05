# Notion 文档增强 - 技术参考

## Playwright MCP 工具完整参考

### browser_navigate

导航到指定 URL。

```javascript
await mcp__plugin_playwright_playwright__browser_navigate({
  url: "https://www.notion.so/page-id"
});
```

### browser_snapshot

获取页面可访问性快照，用于定位元素。

```javascript
await mcp__plugin_playwright_playwright__browser_snapshot();
// 返回 YAML 格式的页面结构，包含 ref 值用于后续操作
```

### browser_click

点击页面元素。

```javascript
await mcp__plugin_playwright_playwright__browser_click({
  element: "元素描述",  // 人类可读描述
  ref: "e123",          // 从 snapshot 获取的 ref 值
  doubleClick: false,   // 可选：双击
  button: "left"        // 可选：left/right/middle
});
```

### browser_type

在元素中输入文本。

```javascript
await mcp__plugin_playwright_playwright__browser_type({
  element: "输入框描述",
  ref: "e456",
  text: "要输入的文本",
  slowly: false,  // 可选：逐字符输入
  submit: false   // 可选：输入后按 Enter
});
```

### browser_press_key

按下键盘按键。

```javascript
await mcp__plugin_playwright_playwright__browser_press_key({
  key: "Enter"  // 支持: Enter, Escape, Tab, Backspace, Delete,
                // ArrowUp/Down/Left/Right, Meta+a, Meta+v, Meta+z 等
});
```

### browser_wait_for

等待条件满足。

```javascript
// 等待指定时间（秒）
await mcp__plugin_playwright_playwright__browser_wait_for({
  time: 3
});

// 等待文本出现
await mcp__plugin_playwright_playwright__browser_wait_for({
  text: "保存成功"
});

// 等待文本消失
await mcp__plugin_playwright_playwright__browser_wait_for({
  textGone: "加载中..."
});
```

### browser_run_code

执行自定义 Playwright 代码。

```javascript
await mcp__plugin_playwright_playwright__browser_run_code({
  code: `async (page) => {
    // 可以访问完整的 Playwright API
    await page.waitForSelector('.selector');
    await page.evaluate(() => {
      // 在页面上下文中执行 JavaScript
    });
    return 'result';
  }`
});
```

### browser_take_screenshot

截取页面截图。

```javascript
await mcp__plugin_playwright_playwright__browser_take_screenshot({
  filename: "screenshot.png",  // 文件名
  fullPage: true,              // 是否截取完整页面
  type: "png"                  // png 或 jpeg
});
```

### browser_close

关闭浏览器页面。

```javascript
await mcp__plugin_playwright_playwright__browser_close();
```

---

## Notion 页面结构

### 典型页面元素

```yaml
# 页面主要结构
- navigation "侧边栏"        # 左侧导航
- banner                     # 顶部工具栏
- main                       # 主内容区
  - textbox "开始输入..."    # 可编辑内容区
    - heading "标题"         # 页面标题 (level=1)
    - generic               # 内容块
    - table                 # 表格
```

### 常见元素 ref 模式

| 元素类型 | 识别方式 |
|---------|---------|
| 页面标题 | `heading [level=1]` |
| 内容区域 | `textbox "开始输入以编辑文本"` |
| 侧边栏页面 | `treeitem "页面名称"` |
| 按钮 | `button "按钮文字"` |
| 链接 | `link "链接文字"` |
| 表格 | `table` → `row` → `cell` |

---

## Notion Markdown 转换规则

### 支持的语法

| Markdown 语法 | Notion 块类型 |
|--------------|--------------|
| `# 标题` | Heading 1 |
| `## 标题` | Heading 2 |
| `### 标题` | Heading 3 |
| `- 项目` | Bulleted list |
| `1. 项目` | Numbered list |
| `[ ] 任务` | To-do |
| `[x] 完成` | To-do (checked) |
| `> 引用` | Quote |
| `---` | Divider |
| `` `代码` `` | Inline code |
| ```` ```代码块``` ```` | Code block |
| `**粗体**` | Bold |
| `*斜体*` | Italic |
| `~~删除线~~` | Strikethrough |
| `[文字](url)` | Link |
| `![图片](url)` | Image (外部链接) |

### 表格转换

```markdown
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| A1  | B1  | C1  |
| A2  | B2  | C2  |
```

转换为 Notion 原生表格，支持：
- 表头行
- 任意列数
- 单元格内文本格式

---

## 常见操作脚本

### 完整页面创建流程

```javascript
async function createNotionPage(pageUrl, title, content) {
  // 1. 导航
  await mcp__plugin_playwright_playwright__browser_navigate({ url: pageUrl });

  // 2. 等待加载
  await mcp__plugin_playwright_playwright__browser_wait_for({ time: 3 });

  // 3. 获取页面结构
  const snapshot = await mcp__plugin_playwright_playwright__browser_snapshot();

  // 4. 找到并点击标题（从 snapshot 中查找 heading level=1 的 ref）
  await mcp__plugin_playwright_playwright__browser_click({
    element: "页面标题",
    ref: "从snapshot获取"
  });

  // 5. 修改标题
  await mcp__plugin_playwright_playwright__browser_type({
    element: "标题输入框",
    ref: "从snapshot获取",
    text: title
  });
  await mcp__plugin_playwright_playwright__browser_press_key({ key: "Enter" });

  // 6. 移动到内容区域
  await mcp__plugin_playwright_playwright__browser_press_key({ key: "ArrowDown" });

  // 7. 粘贴内容
  await mcp__plugin_playwright_playwright__browser_run_code({
    code: `async (page) => {
      await page.evaluate((text) => navigator.clipboard.writeText(text), '${content}');
      await page.waitForTimeout(500);
      await page.keyboard.press('Meta+v');
      return 'pasted';
    }`
  });

  // 8. 截图验证
  await mcp__plugin_playwright_playwright__browser_take_screenshot({
    filename: "result.png",
    fullPage: true
  });

  // 9. 关闭
  await mcp__plugin_playwright_playwright__browser_close();
}
```

### 删除指定文本块

```javascript
async function deleteTextBlock(textContent) {
  // 点击目标文本
  await mcp__plugin_playwright_playwright__browser_click({
    element: `文本 "${textContent}"`,
    ref: "从snapshot获取"
  });

  // 全选块内容
  await mcp__plugin_playwright_playwright__browser_press_key({ key: "Meta+a" });

  // 删除
  await mcp__plugin_playwright_playwright__browser_press_key({ key: "Backspace" });

  // 删除空块
  await mcp__plugin_playwright_playwright__browser_press_key({ key: "Backspace" });
}
```

---

## 错误处理

### 常见错误及解决方案

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `Element not found` | ref 值过期 | 重新获取 snapshot |
| `Page timeout` | 网络慢或页面未加载 | 增加等待时间 |
| `Unauthorized (401)` | 未登录 | 在浏览器中登录 Notion |
| `Cross-Origin error` | 安全限制 | 使用 run_code 执行 |
| `Clipboard blocked` | 权限不足 | 使用 page.evaluate |

### 重试机制

```javascript
async function withRetry(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await mcp__plugin_playwright_playwright__browser_wait_for({ time: 2 });
    }
  }
}
```

---

## 性能优化

### 最佳实践

1. **最小化 snapshot 调用** - 每次 snapshot 都会重新分析页面
2. **批量操作** - 使用 `browser_run_code` 合并多个操作
3. **合理等待** - 使用 `wait_for` 代替固定延时
4. **及时关闭** - 操作完成后立即关闭浏览器

### 性能对比

| 操作方式 | 耗时 | 推荐场景 |
|---------|------|---------|
| 单独调用多个工具 | ~5s/操作 | 简单操作 |
| `browser_run_code` 批量 | ~1s/批次 | 复杂操作 |
| Notion API (如果可用) | ~0.5s/请求 | 大规模操作 |
