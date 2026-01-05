# TeamVenture Design Tokens

使用 Tokens Studio for Figma 实现代码与 Figma 设计的双向同步。

## 快速开始

### 1. 安装 Tokens Studio 插件

1. 打开 Figma 桌面应用
2. 进入 TeamVenture 设计文件
3. 右键 → Plugins → 搜索 **Tokens Studio for Figma**
4. 点击安装（免费版即可）

### 2. 导入 Design Tokens

1. 在 Figma 中运行 Tokens Studio 插件
2. 点击 **Settings** (齿轮图标)
3. 选择 **Sync providers** → **GitHub**
4. 配置连接：

```
Personal Access Token: <你的 GitHub Token>
Repository: qitmac001395/ideas
Branch: main
File Path: apps/teamventure/src/frontend/miniapp/design-tokens/tokens.json
```

或者使用**本地文件导入**：

1. 点击 **Import** 按钮
2. 选择 `tokens.json` 文件
3. 点击 **Import**

### 3. 应用 Tokens 到设计

1. 选择要应用颜色的元素（如按钮、文字）
2. 在 Tokens Studio 面板中点击对应的 Token
3. Token 会自动应用到选中的元素

## Token 结构

```
tokens.json
├── global/                 # 全局基础 Token
│   ├── colors/            # 颜色系统
│   │   ├── primary        # #1890ff 品牌蓝
│   │   ├── success        # #52c41a 成功绿
│   │   ├── danger         # #f5222d 危险红
│   │   ├── purple-start   # #667eea 登录页渐变
│   │   └── purple-end     # #764ba2 登录页渐变
│   ├── neutrals/          # 中性色
│   ├── typography/        # 字体排版
│   ├── spacing/           # 间距
│   ├── borderRadius/      # 圆角
│   └── shadows/           # 阴影
├── components/            # 组件级 Token
│   ├── button/            # 按钮
│   ├── card/              # 卡片
│   ├── input/             # 输入框
│   ├── navigation/        # 导航
│   └── status/            # 状态标签
└── pages/                 # 页面级 Token
    ├── login/             # 登录页
    └── form/              # 表单页
```

## 颜色预览

| Token | 值 | 预览 | 用途 |
|-------|----|----|------|
| `colors.primary` | #1890ff | 🔵 | 按钮、链接、选中态 |
| `colors.primary-dark` | #096dd9 | 🔵 | 按钮悬停 |
| `colors.success` | #52c41a | 🟢 | 完成状态 |
| `colors.danger` | #f5222d | 🔴 | 删除、错误 |
| `colors.warning` | #faad14 | 🟡 | 警告 |
| `colors.purple-start` | #667eea | 🟣 | 登录页渐变起始 |
| `colors.purple-end` | #764ba2 | 🟣 | 登录页渐变结束 |

## 同步工作流

### 代码 → Figma（推荐）

```
1. 开发者修改 tokens.json
2. 提交到 GitHub
3. 设计师在 Tokens Studio 中 Pull
4. 点击 Apply 应用到设计
```

### Figma → 代码

```
1. 设计师在 Tokens Studio 修改 Token
2. 点击 Push 同步到 GitHub
3. 开发者 Pull 获取更新
4. 运行 transform 脚本生成 WXSS
```

## 转换为 WXSS

运行以下命令将 tokens.json 转换为小程序可用的 WXSS 变量：

```bash
node design-tokens/transform.js
```

这将生成 `design-tokens/variables.wxss`，可在 `app.wxss` 中引入：

```css
@import './design-tokens/variables.wxss';
```

## 最佳实践

1. **Token 命名规范**
   - 使用小写字母和连字符
   - 语义化命名（如 `primary` 而非 `blue`）
   - 组件级 Token 引用全局 Token

2. **修改流程**
   - 优先修改代码中的 `tokens.json`
   - 通过 GitHub 同步保持版本控制
   - 避免直接在 Figma 中修改硬编码颜色

3. **版本管理**
   - Token 变更需要在 Git 中记录
   - 重大变更需通知设计和开发团队

## 常见问题

### Q: 为什么 Figma 中的颜色还是灰色？

A: 需要在 Tokens Studio 中选中元素后手动应用 Token。步骤：
1. 选中灰色元素
2. 在 Tokens Studio 面板找到对应 Token
3. 点击 Token 名称应用

### Q: 如何批量应用 Token？

A: 使用 Tokens Studio 的 "Apply to document" 功能：
1. Settings → Apply to document
2. 勾选要应用的 Token 集
3. 点击 Apply

### Q: 修改 Token 后代码没有更新？

A: 需要运行转换脚本：
```bash
cd design-tokens
node transform.js
```

## 相关链接

- [Tokens Studio 官方文档](https://docs.tokens.studio/)
- [Design Tokens 规范](https://design-tokens.github.io/community-group/format/)
- [Figma Variables 指南](https://help.figma.com/hc/en-us/articles/15339657135383)
