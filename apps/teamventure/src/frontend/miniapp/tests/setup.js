/**
 * Jest测试环境全局配置
 *
 * 功能:
 *   - Mock微信小程序全局对象（wx, getApp等）
 *   - 设置测试用全局变量
 */

// Mock wx全局对象
global.wx = {
  // 网络请求
  request: jest.fn(),
  uploadFile: jest.fn(),

  // 本地存储
  getStorageSync: jest.fn(),
  setStorageSync: jest.fn(),
  removeStorageSync: jest.fn(),
  getStorage: jest.fn(),
  setStorage: jest.fn(),
  removeStorage: jest.fn(),
  clearStorage: jest.fn(),

  // 界面交互
  showLoading: jest.fn(),
  hideLoading: jest.fn(),
  showToast: jest.fn(),
  showModal: jest.fn(),
  showActionSheet: jest.fn(),

  // 页面导航
  navigateTo: jest.fn(),
  redirectTo: jest.fn(),
  switchTab: jest.fn(),
  reLaunch: jest.fn(),
  navigateBack: jest.fn(),

  // 用户信息
  login: jest.fn(),
  getUserInfo: jest.fn(),
  getUserProfile: jest.fn(),

  // 系统信息
  getSystemInfoSync: jest.fn(() => ({
    statusBarHeight: 20,
    windowWidth: 375,
    windowHeight: 667,
    pixelRatio: 2
  }))
}

// Mock getApp
global.getApp = jest.fn(() => ({
  globalData: {
    isLogin: false,
    userInfo: null,
    isGuestMode: false
  },
  login: jest.fn(),
  logout: jest.fn()
}))

// Mock getCurrentPages
global.getCurrentPages = jest.fn(() => [])

// Mock Page (注册函数)
global.Page = jest.fn()

// Mock Component (注册函数)
global.Component = jest.fn()

// Mock App (注册函数)
global.App = jest.fn()

// 注意: beforeEach应该在测试文件中使用，不在setup.js中
// 每个测试文件需要在beforeEach中调用以下代码:
//
// beforeEach(() => {
//   jest.clearAllMocks()
//   global.wx.getStorageSync.mockReturnValue(null)
//   global.getApp.mockReturnValue({
//     globalData: { isLogin: false, userInfo: null, isGuestMode: false },
//     login: jest.fn(),
//     logout: jest.fn()
//   })
// })
