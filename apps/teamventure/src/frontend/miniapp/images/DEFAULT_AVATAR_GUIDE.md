# 默认头像设置指南

## 问题说明

小程序中需要一个默认头像图片，当用户未选择头像时显示。

## 解决方案

### 方案1：使用 Emoji 占位符（当前方案）

如果头像 URL 为空，页面会显示 emoji "👤" 作为占位符。这是最简单的方案，无需准备图片文件。

### 方案2：准备默认头像图片

#### 1. 创建默认头像图片

**在线生成**：
访问以下网址，会自动下载一张默认头像图片：
```
https://ui-avatars.com/api/?name=U&size=200&background=e8e8e8&color=999999&format=png
```

或者使用文字作为头像：
```
https://ui-avatars.com/api/?name=TeamVenture&size=200&background=1890ff&color=ffffff&format=png
```

#### 2. 保存图片

将下载的图片重命名为 `default-avatar.png`，放到以下目录：
```
apps/teamventure/src/frontend/miniapp/images/default-avatar.png
```

#### 3. 更新代码

修改 `pages/login/login.wxml` 文件：
```xml
<!-- 原代码 -->
<image class="avatar" src="{{avatarUrl || '/images/default-avatar.png'}}" mode="aspectFill"></image>

<!-- 如果图片存在，这样就可以正常显示了 -->
```

### 方案3：使用 base64 图片（临时方案）

如果需要快速测试，可以使用 base64 编码的图片。

在 `app.wxss` 中添加：
```css
.default-avatar {
  background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAYAAACtWK6eAAAACXBIWXMAAAsTAAALEwEAmpwYAAADfElEQVR4nO3YQW7bMBRA0Z+6p+gRcpkcJUfIEXKaHqFATQMJkCVSokh9vgcMOrPw4g8gURoAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/qerruvrZ1VVN/f393+22+3her3+WZZl+X6/f1zX9eP5fP51u91+7/f73263W7vdbrvv+/7weDz+Pp/Pv8/n8+/z+fy73+8/Pz8/Px+Px8/X6/Xz+Xz+fL/fP9/v98/3+/3z/X7/fL/fP9/v9//r+/7zerxe//P9fr9+3u/3+/V4PF6P1+v1eq3r+vparb/X9Xq9XqvP57Nerw/n8/l4Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD4AAAAAAAAAAAAAAAAAAAAAAAAAAAAA4Bf6C6TgN4gkPE6kAAAAAElFTkSuQmCC');
  background-size: cover;
}
```

## 当前状态

- ✅ Mock 登录数据已修复，不再使用外部占位图片
- ✅ 页面使用 emoji 👤 作为默认头像
- ⏳ 可选：准备实际的默认头像图片文件

## 注意事项

1. **开发者工具设置**
   - 如果要使用网络图片，需要在开发者工具中勾选"不校验合法域名"
   - 或在微信公众平台配置 request 合法域名

2. **最佳实践**
   - 使用本地图片更可靠
   - 文件大小应控制在 50KB 以内
   - 建议尺寸：200x200 像素或更高

3. **测试**
   - 清除缓存后重新测试
   - 确保图片路径正确
