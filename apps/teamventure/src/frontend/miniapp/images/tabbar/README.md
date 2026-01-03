# TabBar 图标说明

## 图标要求

根据微信小程序规范，TabBar 图标需要满足以下要求：

- 图片格式：PNG（建议使用 PNG 格式，支持透明背景）
- 图片尺寸：建议 81px × 81px
- 文件大小：不超过 40kb
- 颜色要求：
  - 未选中图标：建议使用灰色（#999999）
  - 选中图标：建议使用品牌色（#1890ff）

## 需要准备的图标文件

请准备以下 8 个图标文件：

### 1. 首页
- `home.png` - 未选中状态（灰色）
- `home-active.png` - 选中状态（蓝色）

### 2. 生成方案
- `generate.png` - 未选中状态（灰色）
- `generate-active.png` - 选中状态（蓝色）

### 3. 我的方案
- `plans.png` - 未选中状态（灰色）
- `plans-active.png` - 选中状态（蓝色）

### 4. 我的
- `profile.png` - 未选中状态（灰色）
- `profile-active.png` - 选中状态（蓝色）

## 图标设计建议

### 首页图标
- 可以使用：房子、首页、Home 等图标
- 风格：简洁、线性

### 生成方案图标
- 可以使用：魔法棒、星星、加号、创建等图标
- 风格：突出"生成"、"创建"的概念

### 我的方案图标
- 可以使用：列表、文档、文件夹等图标
- 风格：突出"列表"、"记录"的概念

### 我的图标
- 可以使用：用户、个人、头像等图标
- 风格：突出"个人"的概念

## 图标资源推荐

可以从以下网站获取免费图标：

1. **Iconfont（阿里巴巴矢量图标库）**
   - https://www.iconfont.cn/
   - 可下载 PNG 格式，支持自定义颜色和尺寸

2. **IconPark（字节跳动图标库）**
   - https://iconpark.oceanengine.com/
   - 提供多种风格的图标

3. **Remix Icon**
   - https://remixicon.com/
   - 开源图标库，风格统一

## 配置方法

准备好图标后，需要在 `app.json` 的 `tabBar.list` 中添加图标配置：

```json
{
  "tabBar": {
    "list": [
      {
        "pagePath": "pages/home/home",
        "text": "首页",
        "iconPath": "images/tabbar/home.png",
        "selectedIconPath": "images/tabbar/home-active.png"
      },
      {
        "pagePath": "pages/index/index",
        "text": "生成方案",
        "iconPath": "images/tabbar/generate.png",
        "selectedIconPath": "images/tabbar/generate-active.png"
      },
      {
        "pagePath": "pages/myplans/myplans",
        "text": "我的方案",
        "iconPath": "images/tabbar/plans.png",
        "selectedIconPath": "images/tabbar/plans-active.png"
      },
      {
        "pagePath": "pages/profile/profile",
        "text": "我的",
        "iconPath": "images/tabbar/profile.png",
        "selectedIconPath": "images/tabbar/profile-active.png"
      }
    ]
  }
}
```

## 注意事项

1. 所有 TabBar 项要么都配置图标，要么都不配置
2. 如果配置了图标但文件不存在，小程序会显示空白
3. 建议先准备好所有图标文件后再一次性配置
4. 图标路径是相对于小程序根目录的相对路径
