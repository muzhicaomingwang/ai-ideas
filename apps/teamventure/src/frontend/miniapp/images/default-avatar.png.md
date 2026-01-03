# 默认头像文件

## 文件说明

`default-avatar.png` 是用户未选择头像时的默认头像图片。

## 要求

- 文件名：`default-avatar.png`
- 尺寸：200x200 像素（或更高分辨率，如 400x400）
- 格式：PNG（支持透明背景）
- 大小：建议小于 50KB

## 设计建议

可以使用以下设计：
1. 简单的用户图标剪影（灰色或浅色）
2. 品牌 Logo 的简化版本
3. 字母 "U"（User）或中文"默"字

## 快速生成方法

### 方法1：使用在线工具
访问 https://ui-avatars.com/api/?name=TeamVenture&size=200&background=e8e8e8&color=999

### 方法2：使用设计工具
- Figma / Sketch：绘制圆形，添加用户图标
- Photoshop：创建 200x200 画布，添加图标

### 方法3：临时方案
在小程序中，如果该文件不存在，可以显示一个 emoji 或纯色圆形作为备选。

## 注意事项

- 确保文件位于 `images/` 目录下
- 路径在代码中引用为：`/images/default-avatar.png`
