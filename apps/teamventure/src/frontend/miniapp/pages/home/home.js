// pages/home/home.js
import { STORAGE_KEYS } from '../../utils/config.js'

const app = getApp()

Page({
  data: {
    isLogin: false,
    userInfo: null,
    statusBarHeight: 20, // 默认状态栏高度，会在 onLoad 时动态获取
    hotDestinations: [
      { id: 1, name: '北京怀柔', emoji: '🏔️', tag: '山水田园' },
      { id: 2, name: '杭州千岛湖', emoji: '🏞️', tag: '湖光山色' },
      { id: 3, name: '上海崇明', emoji: '🌳', tag: '生态休闲' },
      { id: 4, name: '苏州周庄', emoji: '🏘️', tag: '古镇风情' },
      { id: 5, name: '南京紫金山', emoji: '⛰️', tag: '历史文化' },
      { id: 6, name: '青岛崂山', emoji: '🌊', tag: '海滨风光' }
    ],
    recommendedPlans: [
      {
        id: 1,
        name: '怀柔山水两日游',
        pricePerPerson: 800,
        duration: '2天1夜',
        destination: '北京怀柔',
        tags: ['户外拓展', '团队协作']
      },
      {
        id: 2,
        name: '千岛湖休闲三日游',
        pricePerPerson: 1200,
        duration: '3天2夜',
        destination: '杭州千岛湖',
        tags: ['休闲度假', '美食体验']
      },
      {
        id: 3,
        name: '崇明生态一日游',
        pricePerPerson: 300,
        duration: '1天',
        destination: '上海崇明',
        tags: ['亲近自然', '农家乐']
      }
    ],
    activityTypes: [
      { value: 'outdoor', label: '户外拓展', emoji: '🏃' },
      { value: 'leisure', label: '休闲度假', emoji: '🏖️' },
      { value: 'culture', label: '文化体验', emoji: '🎭' },
      { value: 'food', label: '美食之旅', emoji: '🍜' },
      { value: 'sports', label: '运动竞技', emoji: '⚽' },
      { value: 'adventure', label: '探险挑战', emoji: '🧗' }
    ]
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
  },

  // 查看更多目的地
  handleViewMoreDestinations() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    })
  },

  // 选择目的地
  handleSelectDestination(e) {
    const destination = e.currentTarget.dataset.destination
    // 跳转到生成方案页面，并预填目的地
    wx.switchTab({
      url: '/pages/index/index'
    })
    // 注意：TabBar 页面无法通过 URL 传参，需要使用全局变量或缓存
    wx.setStorageSync('prefilledDestination', destination)
  },

  // 查看更多推荐方案
  handleViewMorePlans() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    })
  },

  // 查看方案模板
  handleViewPlanTemplate(e) {
    const planId = e.currentTarget.dataset.planId
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    })
  },

  // 选择活动类型
  handleSelectActivityType(e) {
    const type = e.currentTarget.dataset.type
    // 跳转到生成方案页面，并预填活动类型
    wx.switchTab({
      url: '/pages/index/index'
    })
    wx.setStorageSync('prefilledActivityType', type)
  }
})
