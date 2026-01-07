# TeamVenture 设计系统

## 设计工作流

**Obsidian + AI 直接生成代码**（简化版）

```
1. 编辑设计文档 (Obsidian Markdown)
   └── docs/design/miniapp-pages-obsidian.md

2. 将页面描述喂给 Claude
   └── "请根据 [[index]] 页面的描述生成 WXML/WXSS"

3. 在微信开发者工具验证
   └── 调整细节后更新设计文档
```

## 目录结构

```
design/
├── tokens/                    # Design Tokens（样式参考）
│   ├── index.json            # 索引文件
│   ├── colors.json           # 颜色系统
│   ├── typography.json       # 字体排版
│   ├── spacing.json          # 间距系统
│   ├── radius.json           # 圆角系统
│   ├── shadows.json          # 阴影系统
│   └── components.json       # 组件级变量
└── README.md

docs/design/
└── miniapp-pages-obsidian.md # 页面设计文档（Obsidian 格式）
```

## Design Tokens 使用

### 颜色

```wxss
/* 主色 */
color: #1890ff;           /* colors.primary.default */
background: #e6f7ff;      /* colors.primary.light */

/* 状态色 */
color: #52c41a;           /* colors.success.default */
color: #faad14;           /* colors.warning.default */
color: #f5222d;           /* colors.danger.default */

/* 中性色 */
color: #333;              /* colors.neutral.text */
color: #666;              /* colors.neutral.secondary */
color: #999;              /* colors.neutral.muted */
border-color: #e8e8e8;    /* colors.neutral.border */
background: #f5f5f5;      /* colors.neutral.background */
```

### 字号

```wxss
font-size: 24rpx;  /* typography.fontSize.xs - 标签、提示 */
font-size: 28rpx;  /* typography.fontSize.base - 正文 */
font-size: 32rpx;  /* typography.fontSize.md - 强调文本 */
font-size: 36rpx;  /* typography.fontSize.lg - 小标题 */
font-size: 40rpx;  /* typography.fontSize.xl - 大标题 */
```

### 间距

```wxss
/* 基于 8rpx 网格 */
padding: 8rpx;    /* spacing.scale.1 */
padding: 16rpx;   /* spacing.scale.2 */
padding: 24rpx;   /* spacing.scale.3 */
padding: 32rpx;   /* spacing.scale.4 - 容器默认 */
padding: 48rpx;   /* spacing.scale.6 */
```

### 圆角

```wxss
border-radius: 8rpx;   /* radius.base - 按钮 */
border-radius: 12rpx;  /* radius.md - 输入框 */
border-radius: 16rpx;  /* radius.lg - 卡片 */
border-radius: 40rpx;  /* radius.full - 胶囊按钮、Chip */
```

### 阴影

```wxss
box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);  /* shadows.base - 卡片 */
box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);  /* shadows.md - 悬浮卡片 */
```

## 组件样式对照表

| 组件 | 代码路径 | Token 参考 |
|------|----------|-----------|
| 按钮 | app.wxss `.btn-primary` | components.button |
| 输入框 | index.wxss `.text-input` | components.input |
| 卡片 | app.wxss `.card` | components.card |
| 标签 | app.wxss `.tag` | components.tag |
| 选择芯片 | index.wxss `.chip` | components.chip |
| 步进器 | stepper.wxss | components.stepper |
| 步骤条 | index.wxss `.steps` | components.steps |
| 单选项 | index.wxss `.radio-item` | components.radio |

## 更新日志

### v1.1.0 (2026-01-06)
- 简化设计工作流：Obsidian + AI 直接生成代码
- 移除 Figma/Stitch 相关配置
- 保留 Design Tokens 作为样式参考

### v1.0.0 (2026-01-05)
- 初始化 Design Tokens
- 从现有 WXSS 提取颜色、字体、间距、圆角、阴影
