// pages/login/login.js
import { post } from '../../utils/request.js'
import { API_ENDPOINTS, STORAGE_KEYS } from '../../utils/config.js'

const app = getApp()

Page({
  data: {
    isLogin: false,
    agreed: true // 默认同意协议
  },

  onLoad(options) {
    console.log('登录页加载', options)

    // 检查是否已登录
    const isLogin = app.globalData.isLogin
    this.setData({ isLogin })

    // 如果已登录，显示继续使用按钮
    if (isLogin) {
      console.log('用户已登录')
    }
  },

  onShow() {
    // 每次显示页面时检查登录状态
    const isLogin = app.globalData.isLogin
    this.setData({ isLogin })
  },

  /**
   * 获取用户信息
   */
  handleGetUserInfo(e) {
    console.log('获取用户信息', e)

    if (!this.data.agreed) {
      wx.showToast({
        title: '请先同意用户协议和隐私政策',
        icon: 'none'
      })
      return
    }

    const { userInfo, errMsg } = e.detail

    if (errMsg === 'getUserInfo:ok' && userInfo) {
      // 用户同意授权
      this.loginWithUserInfo(userInfo)
    } else {
      // 用户拒绝授权
      wx.showToast({
        title: '需要授权才能使用',
        icon: 'none'
      })
    }
  },

  /**
   * 使用用户信息登录
   */
  async loginWithUserInfo(userInfo) {
    try {
      wx.showLoading({ title: '登录中...', mask: true })

      // 1. 获取微信登录凭证
      const loginRes = await this.wxLogin()
      console.log('微信登录成功', loginRes)

      // 2. 调用后端登录接口
      const loginData = await this.backendLogin({
        code: loginRes.code,
        userInfo: userInfo
      })

      // 3. 保存登录信息
      wx.setStorageSync(STORAGE_KEYS.SESSION_TOKEN, loginData.sessionToken)
      wx.setStorageSync(STORAGE_KEYS.USER_INFO, loginData.userInfo)

      // 4. 更新全局状态
      app.login(loginData.userInfo)

      wx.hideLoading()

      // 5. 登录成功提示
      wx.showToast({
        title: '登录成功',
        icon: 'success',
        duration: 1500
      })

      // 6. 跳转到首页
      setTimeout(() => {
        wx.switchTab({
          url: '/pages/index/index'
        })
      }, 1500)

    } catch (error) {
      wx.hideLoading()
      console.error('登录失败', error)
      wx.showModal({
        title: '登录失败',
        content: error.message || '网络错误，请稍后重试',
        showCancel: false
      })
    }
  },

  /**
   * 微信登录
   */
  wxLogin() {
    return new Promise((resolve, reject) => {
      wx.login({
        success: (res) => {
          if (res.code) {
            resolve(res)
          } else {
            reject(new Error('获取登录凭证失败'))
          }
        },
        fail: (error) => {
          reject(error)
        }
      })
    })
  },

  /**
   * 后端登录
   */
  async backendLogin(data) {
    try {
      const result = await post(API_ENDPOINTS.USER_LOGIN, data, {
        showLoading: false
      })
      return result
    } catch (error) {
      throw error
    }
  },

  /**
   * 继续使用（已登录）
   */
  handleContinue() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  },

  /**
   * 协议勾选变化
   */
  handleAgreementChange(e) {
    const values = e.detail.value
    this.setData({
      agreed: values.includes('agree')
    })
  },

  /**
   * 查看协议
   */
  handleShowAgreement(e) {
    const type = e.currentTarget.dataset.type
    const title = type === 'user' ? '用户协议' : '隐私政策'

    // TODO: 跳转到协议页面或使用 web-view 显示
    wx.showModal({
      title: title,
      content: '此处应显示完整的协议内容',
      showCancel: false
    })
  }
})
