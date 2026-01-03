# 清除缓存指南

## 问题说明

如果看到 `Failed to load image https://via.placeholder.com/100` 错误，说明之前的登录数据还缓存在本地存储中。

## 解决方法

### 方法1：在开发者工具中清除缓存

1. **打开微信开发者工具**
2. **点击菜单栏** → 工具 → 清除缓存
3. **选择"清除全部缓存"**
4. **刷新页面**（点击工具栏的刷新按钮或按 Ctrl+R / Cmd+R）

### 方法2：在代码中添加清除缓存逻辑

在 `app.js` 的 `onLaunch` 中添加以下代码（临时调试用）：

```javascript
onLaunch(options) {
  console.log('TeamVenture 小程序启动', options)

  // 🧪 临时代码：清除旧的缓存数据（调试用）
  wx.clearStorageSync()
  console.log('已清除所有缓存')

  // 检查登录状态
  this.checkLoginStatus()

  // 获取系统信息
  this.getSystemInfo()
}
```

**注意**：这会清除所有数据，包括登录信息。调试完成后请移除此代码。

### 方法3：手动清除特定的存储项

在控制台执行以下代码：

```javascript
wx.removeStorageSync('sessionToken')
wx.removeStorageSync('token')
wx.removeStorageSync('userInfo')
console.log('已清除登录信息')
```

或者在页面中添加一个"清除缓存"按钮：

```xml
<!-- 在任意页面添加 -->
<button bindtap="handleClearCache">清除缓存</button>
```

```javascript
// 在页面 JS 中添加
handleClearCache() {
  wx.clearStorageSync()
  wx.showToast({
    title: '缓存已清除',
    icon: 'success'
  })
  setTimeout(() => {
    wx.reLaunch({
      url: '/pages/login/login'
    })
  }, 1500)
}
```

### 方法4：退出登录后重新登录

1. 进入"我的"页面
2. 点击"退出登录"
3. 重新登录

## 验证修复

清除缓存后：

1. 重新启动小程序
2. 进入登录页面
3. 完成登录流程
4. **不应该再看到** `via.placeholder.com` 的错误

## 检查是否成功

打开控制台，应该看到：
```
[MOCK] 返回登录信息: {user_id: "mock_user_001", nickname: "您输入的昵称", avatar: "您选择的头像URL或空字符串"}
```

## 永久解决方案

为了避免旧数据问题，可以在 `app.js` 中添加版本检查：

```javascript
onLaunch(options) {
  console.log('TeamVenture 小程序启动', options)

  // 检查版本，如果版本不匹配则清除旧数据
  const APP_VERSION = '1.0.0'
  const storedVersion = wx.getStorageSync('appVersion')

  if (storedVersion !== APP_VERSION) {
    console.log('版本更新，清除旧数据')
    wx.clearStorageSync()
    wx.setStorageSync('appVersion', APP_VERSION)
  }

  this.checkLoginStatus()
  this.getSystemInfo()
}
```
