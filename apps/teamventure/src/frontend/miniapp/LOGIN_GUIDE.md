# 微信小程序登录功能使用指南

## 功能概述

TeamVenture 小程序现已支持微信登录和用户头像功能，采用微信官方最新推荐的登录方式。

## 登录流程

### 前端流程

1. **点击"微信一键登录"按钮**
   - 调用 `wx.login()` 获取临时登录凭证 `code`
   - 显示用户信息填写表单

2. **填写用户信息**
   - 选择头像：使用 `<button open-type="chooseAvatar">` 让用户选择微信头像
   - 输入昵称：使用 `<input type="nickname">` 让用户输入昵称

3. **完成登录**
   - 将 `code`、`nickname`、`avatarUrl` 发送到后端
   - 后端返回 `sessionToken` 和 `userInfo`
   - 保存到本地存储并更新全局状态
   - 跳转到首页

### 后端需要实现的接口

#### 登录接口

**接口地址**: `POST /api/user/login`

**请求参数**:
```json
{
  "code": "微信临时登录凭证",
  "nickname": "用户昵称",
  "avatarUrl": "用户头像临时URL（可选）"
}
```

**后端处理流程**:

1. 使用 `code` 向微信服务器换取 `openid` 和 `session_key`
   ```
   GET https://api.weixin.qq.com/sns/jscode2session?
       appid=YOUR_APPID&
       secret=YOUR_SECRET&
       js_code=CODE&
       grant_type=authorization_code
   ```

2. 根据 `openid` 查询或创建用户
   - 如果是新用户：创建用户记录，保存昵称和头像
   - 如果是老用户：更新昵称和头像（如果有变化）

3. 生成自定义登录态 `sessionToken`
   - 可以使用 JWT 或其他方式
   - 建议设置过期时间（如 7 天）

4. 返回登录信息

**响应示例**:
```json
{
  "sessionToken": "your-custom-session-token",
  "userInfo": {
    "user_id": "user_123456",
    "nickname": "用户昵称",
    "avatar": "https://your-server.com/avatars/user_123456.jpg",
    "openid": "wx_openid_xxx" // 可选，前端不需要
  }
}
```

## 微信配置要求

### 1. 小程序设置

在微信公众平台（https://mp.weixin.qq.com/）完成以下配置：

#### 基础设置
- 进入【开发】→【开发管理】→【开发设置】
- 获取 `AppID` 和 `AppSecret`
- 配置服务器域名（request 合法域名、uploadFile 合法域名）

#### 用户隐私保护指引
- 进入【设置】→【基本设置】→【服务内容声明】
- 填写【用户信息】相关说明
- 说明收集和使用用户昵称、头像的目的

### 2. 后端环境变量配置

```bash
# 微信小程序配置
WECHAT_APPID=wx1234567890abcdef
WECHAT_SECRET=your_app_secret_here

# 会话密钥（用于生成 sessionToken）
SESSION_SECRET=your_session_secret_here
```

### 3. 头像文件处理

小程序选择头像后，`avatarUrl` 是微信临时文件路径，需要后端：

**选项1：保存到自己的服务器**
```javascript
// 前端上传头像
const uploadRes = await wx.uploadFile({
  url: 'https://your-server.com/api/upload/avatar',
  filePath: avatarUrl,
  name: 'file'
})
```

**选项2：直接使用微信 CDN**
- 下载用户选择的头像到服务器
- 重新上传到自己的存储服务（OSS、COS 等）
- 保存永久链接到数据库

## 测试流程

### 1. 本地测试（开发者工具）

1. 打开微信开发者工具
2. 进入【登录页面】
3. 点击"微信一键登录"
4. 选择头像（开发工具会模拟选择）
5. 输入昵称
6. 点击"完成登录"

**注意**: 开发者工具中的 `code` 可能无法在微信服务器换取真实的 `openid`，建议后端在开发环境提供 mock 数据。

### 2. 真机测试

1. 将小程序上传到微信平台（体验版）
2. 使用手机微信扫码打开
3. 完成登录流程
4. 验证头像和昵称是否正确显示

## 安全注意事项

1. **AppSecret 保密**
   - 切勿将 `AppSecret` 暴露在前端代码中
   - 所有与微信服务器的交互必须在后端完成

2. **Code 单次有效**
   - `wx.login()` 获取的 `code` 只能使用一次
   - 5 分钟内未使用会过期

3. **SessionToken 管理**
   - 建议使用 JWT 并设置合理的过期时间
   - 需要刷新机制避免频繁登录

4. **用户隐私**
   - 用户头像和昵称属于个人信息
   - 需要在隐私政策中明确说明用途
   - 遵守《个人信息保护法》

## 常见问题

### Q1: 开发者工具中登录失败？
**A**: 检查以下几点：
- 是否配置了正确的 AppID
- 是否勾选了"不校验合法域名"
- 后端是否提供了开发环境的 mock 接口

### Q2: 真机测试时无法获取头像？
**A**:
- 确保小程序已配置【用户信息】相关的隐私协议
- 检查是否勾选了用户协议复选框

### Q3: 登录后刷新小程序需要重新登录？
**A**:
- 检查是否正确使用 `wx.setStorageSync` 保存了 `sessionToken`
- 确认 `app.js` 中的 `checkLoginStatus()` 逻辑正确

### Q4: 如何退出登录？
**A**: 调用以下代码：
```javascript
wx.removeStorageSync('sessionToken')
wx.removeStorageSync('userInfo')
app.logout()
wx.reLaunch({
  url: '/pages/login/login'
})
```

## 后续优化建议

1. **手机号登录**
   - 使用 `<button open-type="getPhoneNumber">` 获取手机号
   - 实现手机号绑定和验证码登录

2. **自动登录**
   - 检查 `sessionToken` 是否有效
   - 有效则自动登录，无效则跳转登录页

3. **用户信息更新**
   - 允许用户在个人中心修改头像和昵称
   - 提供信息编辑页面

4. **多端登录**
   - 实现账号在多个设备间的同步
   - 检测异地登录并提示用户

## 参考文档

- [微信小程序登录](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/login.html)
- [获取头像昵称](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/userProfile.html)
- [小程序隐私保护](https://developers.weixin.qq.com/miniprogram/dev/framework/user-privacy/)
