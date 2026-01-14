// 清除所有Storage缓存并重置为正确配置
// 在微信开发者工具控制台运行此脚本

console.log('===== 开始清除Storage =====')

// 1. 查看当前Storage内容
console.log('当前apiBaseUrl:', wx.getStorageSync('apiBaseUrl'))
console.log('当前apiEnv:', wx.getStorageSync('apiEnv'))

// 2. 清除所有与API相关的Storage
wx.removeStorageSync('apiBaseUrl')
wx.removeStorageSync('apiEnv')
wx.removeStorageSync('SESSION_TOKEN')
wx.removeStorageSync('USER_INFO')

console.log('✅ Storage已清除')

// 3. 强制设置为local环境
wx.setStorageSync('apiEnv', 'local')
wx.setStorageSync('apiBaseUrl', 'http://localhost:8080/api/v1')

console.log('✅ 已设置为local环境')
console.log('新的apiBaseUrl:', wx.getStorageSync('apiBaseUrl'))

// 4. 重新导入配置验证
const config = require('./config.js')
console.log('配置验证 - API_BASE_URL:', config.API_BASE_URL)
console.log('配置验证 - CURRENT_ENV:', config.CURRENT_ENV)

console.log('===== 完成！请点击"编译"重新编译 =====')
