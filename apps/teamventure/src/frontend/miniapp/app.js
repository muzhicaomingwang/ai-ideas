// app.js
App({
  onLaunch(options) {
    console.log('TeamVenture 小程序启动', options)

    // 版本检查，清除旧数据
    const APP_VERSION = '1.0.2' // 更新版本号（修复URIError）
    const storedVersion = wx.getStorageSync('appVersion')

    if (storedVersion !== APP_VERSION) {
      console.log('检测到版本更新，清除旧数据...')
      wx.clearStorageSync()
      wx.setStorageSync('appVersion', APP_VERSION)
      console.log('旧数据已清除')
    }

    // 【紧急修复】清理可能错误的apiBaseUrl（包含weapp://或格式错误的URL）
    try {
      const apiBaseUrl = wx.getStorageSync('apiBaseUrl')
      if (apiBaseUrl && (
        apiBaseUrl.includes('weapp:') ||
        apiBaseUrl.includes('http:/127.0.0.1') ||  // 格式错误
        !apiBaseUrl.startsWith('http://') && !apiBaseUrl.startsWith('https://')
      )) {
        console.warn('[修复] 检测到错误的apiBaseUrl:', apiBaseUrl)
        wx.removeStorageSync('apiBaseUrl')
        console.log('[修复] 已清理，将使用默认配置')
      }
    } catch (e) {
      console.error('[修复] Storage清理失败:', e)
    }

    // 开发者工具默认走统一网关（apps/nginx）：http://api.teamventure.com/api/v1
    // - 仅在 devtools 且用户未手动设置 apiBaseUrl 时生效
    try {
      const existingBaseUrl = wx.getStorageSync('apiBaseUrl')
      const platform = wx.getSystemInfoSync?.()?.platform
      if (!existingBaseUrl && platform === 'devtools') {
        wx.setStorageSync('apiBaseUrl', 'http://api.teamventure.com/api/v1')
      }
    } catch (e) {
      // ignore
    }

    // 检查登录状态
    this.checkLoginStatus()

    // 获取系统信息
    this.getSystemInfo()
  },

  onShow(options) {
    console.log('TeamVenture 小程序显示', options)
  },

  onHide() {
    console.log('TeamVenture 小程序隐藏')
  },

  onError(error) {
    console.error('TeamVenture 小程序错误', error)
  },

  // 检查登录状态
  checkLoginStatus() {
    const sessionToken = wx.getStorageSync('sessionToken') || wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')

    if (sessionToken && userInfo) {
      this.globalData.isLogin = true
      this.globalData.userInfo = userInfo
      console.log('已登录用户:', userInfo)
    } else {
      this.globalData.isLogin = false
      console.log('用户未登录')
    }
  },

  // 获取系统信息
  getSystemInfo() {
    wx.getSystemInfo({
      success: (res) => {
        this.globalData.systemInfo = res
        console.log('系统信息:', res)
      },
      fail: (error) => {
        console.error('获取系统信息失败:', error)
      }
    })
  },

  // 登录
  login(userInfo) {
    this.globalData.isLogin = true
    this.globalData.userInfo = userInfo
    wx.setStorageSync('userInfo', userInfo)
  },

  // 退出登录
  logout() {
    this.globalData.isLogin = false
    this.globalData.userInfo = null
    wx.removeStorageSync('sessionToken')
    wx.removeStorageSync('token')
    wx.removeStorageSync('userInfo')
  },

  // 全局数据
  globalData: {
    isLogin: false,
    userInfo: null,
    systemInfo: null
  }
})
