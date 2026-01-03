// pages/login/login.js
import { post } from '../../utils/request.js'
import { API_ENDPOINTS, STORAGE_KEYS } from '../../utils/config.js'

const app = getApp()

Page({
  data: {
    isLogin: false,
    agreed: true, // 默认同意协议
    showUserForm: false, // 是否显示用户信息表单
    avatarUrl: '', // 用户头像
    nickname: '', // 用户昵称
    loginCode: '' // 微信登录 code
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
   * 微信一键登录
   */
  async handleWechatLogin() {
    if (!this.data.agreed) {
      wx.showToast({
        title: '请先同意用户协议和隐私政策',
        icon: 'none'
      })
      return
    }

    try {
      wx.showLoading({ title: '登录中...', mask: true })

      // 1. 获取微信登录凭证
      const loginRes = await this.wxLogin()
      console.log('微信登录成功，code:', loginRes.code)

      wx.hideLoading()

      // 2. 保存 code，显示用户信息填写表单
      this.setData({
        loginCode: loginRes.code,
        showUserForm: true
      })

    } catch (error) {
      wx.hideLoading()
      console.error('微信登录失败', error)
      wx.showModal({
        title: '登录失败',
        content: '获取微信登录凭证失败，请重试',
        showCancel: false
      })
    }
  },

  /**
   * 选择头像
   */
  onChooseAvatar(e) {
    const { avatarUrl } = e.detail
    console.log('选择头像:', avatarUrl)
    this.setData({
      avatarUrl: avatarUrl
    })
  },

  /**
   * 昵称输入
   */
  onNicknameBlur(e) {
    const nickname = e.detail.value
    console.log('输入昵称:', nickname)
    this.setData({
      nickname: nickname
    })
  },

  /**
   * 完成登录
   */
  async handleCompleteLogin() {
    const { avatarUrl, nickname, loginCode } = this.data

    // 验证
    if (!nickname || nickname.trim() === '') {
      wx.showToast({
        title: '请输入昵称',
        icon: 'none'
      })
      return
    }

    try {
      wx.showLoading({ title: '登录中...', mask: true })

      // 调用后端登录接口
      const loginData = await this.backendLogin({
        code: loginCode,
        nickname: nickname.trim(),
        avatarUrl: avatarUrl
      })

      // 保存登录信息
      wx.setStorageSync(STORAGE_KEYS.SESSION_TOKEN, loginData.sessionToken || loginData.token)
      wx.setStorageSync(STORAGE_KEYS.USER_INFO, loginData.userInfo)

      // 更新全局状态
      app.login(loginData.userInfo)

      wx.hideLoading()

      // 登录成功提示
      wx.showToast({
        title: '登录成功',
        icon: 'success',
        duration: 1500
      })

      // 跳转到首页
      setTimeout(() => {
        wx.switchTab({
          url: '/pages/home/home'
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
      url: '/pages/home/home'
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
