// pages/home/home.js
import { STORAGE_KEYS } from '../../utils/config.js'

const app = getApp()

Page({
  data: {
    isLogin: false,
    userInfo: null,
    statusBarHeight: 20 // 默认状态栏高度，会在 onLoad 时动态获取
  },

  onLoad() {
    // 获取系统状态栏高度
    const systemInfo = wx.getSystemInfoSync()
    this.setData({
      statusBarHeight: systemInfo.statusBarHeight || 20
    })

    // 加载用户登录状态
    this.loadUserInfo()
  },

  onShow() {
    // 每次显示时刷新用户信息
    this.loadUserInfo()
  },

  /**
   * 加载用户信息
   * Load User Info: 从全局状态和本地存储加载用户登录状态
   *
   * 术语对照（ubiquitous-language-glossary.md Section 2.1, 7.1, 7.2）:
   *   - 登录状态 = Login Status = isLogin
   *   - 用户信息 = User Info = userInfo
   *   - 会话令牌 = Session Token = STORAGE_KEYS.SESSION_TOKEN
   *
   * 数据来源优先级:
   *   1. app.globalData (运行时状态)
   *   2. wx.getStorageSync (持久化存储)
   */
  loadUserInfo() {
    const isLogin = app.globalData.isLogin
    const userInfo = wx.getStorageSync(STORAGE_KEYS.USER_INFO) || app.globalData.userInfo

    this.setData({
      isLogin,
      userInfo
    })
  },

  /**
   * 点击导航栏用户头像/登录按钮
   * User Avatar Click: 导航栏右上角用户状态显示区域的点击处理
   *
   * 术语对照（ubiquitous-language-glossary.md Section 4.4）:
   *   - 用户状态显示 = User Status Display = navbar-user
   *   - 用户信息胶囊 = User Info Capsule = user-info-mini
   *   - 登录入口按钮 = Login Entry Button = login-btn-mini
   *
   * 交互行为:
   *   - 已登录: 弹出ActionSheet（个人中心/退出登录）
   *   - 未登录: 跳转登录页
   *
   * 参考: miniapp-ux-ui-specification.md Section 4.6 "自定义导航栏设计"
   */
  handleUserAvatar() {
    if (this.data.isLogin) {
      // 已登录：显示菜单或跳转个人中心
      wx.showActionSheet({
        itemList: ['个人中心', '退出登录'],
        success: (res) => {
          if (res.tapIndex === 0) {
            // 跳转个人中心（待开发）
            wx.showToast({
              title: '功能开发中',
              icon: 'none'
            })
          } else if (res.tapIndex === 1) {
            // 退出登录
            this.handleLogout()
          }
        }
      })
    } else {
      // 未登录：跳转登录页
      wx.navigateTo({
        url: '/pages/login/login'
      })
    }
  },

  /**
   * 退出登录
   * Logout: 用户主动退出登录，清除会话状态
   *
   * 术语对照（ubiquitous-language-glossary.md Section 7.1, 7.2）:
   *   - 会话令牌 = Session Token = STORAGE_KEYS.SESSION_TOKEN
   *   - 用户信息 = User Info = STORAGE_KEYS.USER_INFO
   *   - 登录状态 = Login Status = isLogin
   *
   * 清理范围: 同 handleReLogin (pages/login/login.js)
   */
  handleLogout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync(STORAGE_KEYS.SESSION_TOKEN)
          wx.removeStorageSync(STORAGE_KEYS.USER_INFO)
          app.globalData.isLogin = false
          app.globalData.userInfo = null
          this.setData({ isLogin: false, userInfo: null })
          wx.showToast({
            title: '已退出登录',
            icon: 'success'
          })
        }
      }
    })
  },

  // 快捷操作
  handleGoGenerate() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  },

  handleGoMyPlans() {
    wx.switchTab({
      url: '/pages/myplans/myplans'
    })
  }
})
