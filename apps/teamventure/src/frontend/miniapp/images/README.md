# 图片资源说明

请准备以下图片资源并放入此目录。

## 📋 必需图片列表

### 1. Logo

**文件名**: `logo.png`

**规格**:
- 尺寸: 160px × 160px (@2x: 320px × 320px)
- 格式: PNG（透明背景）
- 用途: 登录页顶部 Logo

**设计建议**:
- 使用品牌主色（蓝色 #1890ff）
- 简洁、现代的图标设计
- 可以是文字 + 图标组合

---

### 2. TabBar 图标 - 生成方案

**未选中态**: `tab-generate.png`
**选中态**: `tab-generate-active.png`

**规格**:
- 尺寸: 48px × 48px (@2x: 96px × 96px, @3x: 144px × 144px)
- 格式: PNG（透明背景）
- 颜色:
  - 未选中: #666666
  - 选中: #1890ff

**图标建议**:
- 使用"加号"或"创建"相关图标
- 线性图标风格
- 2px 线宽

---

### 3. TabBar 图标 - 我的方案

**未选中态**: `tab-myplans.png`
**选中态**: `tab-myplans-active.png`

**规格**:
- 尺寸: 48px × 48px (@2x: 96px × 96px, @3x: 144px × 144px)
- 格式: PNG（透明背景）
- 颜色:
  - 未选中: #666666
  - 选中: #1890ff

**图标建议**:
- 使用"文件夹"或"列表"相关图标
- 线性图标风格
- 2px 线宽

---

## 🎨 图标来源推荐

### 1. 在线图标库

- [iconfont](https://www.iconfont.cn/) - 阿里巴巴图标库
- [iconpark](https://iconpark.oceanengine.com/) - 字节跳动图标库
- [Remix Icon](https://remixicon.com/) - 开源图标库

### 2. 设计工具

- Figma（在线设计工具）
- Sketch（Mac）
- Adobe Illustrator

---

## 🛠️ 快速生成工具

### 使用 Figma 生成

1. 在 Figma 创建 48×48 画布
2. 绘制图标（线宽 2px）
3. 导出为 PNG（@2x, @3x）

### 使用 AI 工具

使用 ChatGPT 或 Midjourney 生成简单图标。

---

## 📐 图片规格对照表

| 文件名 | 基准尺寸 | @2x | @3x | 用途 |
|--------|---------|-----|-----|------|
| logo.png | 160×160 | 320×320 | 480×480 | 登录页 Logo |
| tab-generate.png | 48×48 | 96×96 | 144×144 | TabBar 图标（未选中） |
| tab-generate-active.png | 48×48 | 96×96 | 144×144 | TabBar 图标（选中） |
| tab-myplans.png | 48×48 | 96×96 | 144×144 | TabBar 图标（未选中） |
| tab-myplans-active.png | 48×48 | 96×96 | 144×144 | TabBar 图标（选中） |

---

## 🚀 临时解决方案

### 方案 1: 使用占位图

创建纯色占位图：

```html
<!-- 使用在线工具生成 -->
https://via.placeholder.com/160/1890ff/ffffff?text=TV
```

### 方案 2: 使用 Emoji

暂时使用 Emoji 代替图标（不推荐）：

```javascript
// app.json
"tabBar": {
  "list": [
    {
      "pagePath": "pages/index/index",
      "text": "生成方案"
      // 暂时不配置 iconPath
    }
  ]
}
```

### 方案 3: 使用微信官方图标

使用微信小程序内置图标组件：

```html
<icon type="search" size="48" color="#1890ff"/>
```

---

## ✅ 检查清单

- [ ] logo.png（160×160）
- [ ] tab-generate.png（48×48）
- [ ] tab-generate-active.png（48×48）
- [ ] tab-myplans.png（48×48）
- [ ] tab-myplans-active.png（48×48）

---

## 📞 需要帮助？

如果需要设计图标，可以：
1. 联系设计师
2. 使用在线图标生成工具
3. 参考其他小程序的图标设计

---

**更新日期**: 2026-01-02
