// pages/login/login.js
import { post, put, get, uploadFile } from '../../utils/request.js'
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
      avatarUrl
    })
  },

  /**
   * 昵称输入（实时更新，包括微信自动填充）
   */
  onNicknameInput(e) {
    const nickname = e.detail.value
    console.log('昵称输入:', nickname)
    this.setData({
      nickname
    })
  },

  /**
   * 昵称失焦
   */
  onNicknameBlur(e) {
    const nickname = e.detail.value
    console.log('昵称失焦:', nickname)
    // 确保失焦时也更新（兼容处理）
    if (nickname !== this.data.nickname) {
      this.setData({
        nickname
      })
    }
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
        avatarUrl: '' // 头像走 OSS 上传后再绑定
      })

      // 保存登录信息
      wx.setStorageSync(STORAGE_KEYS.SESSION_TOKEN, loginData.sessionToken || loginData.token)
      wx.setStorageSync(STORAGE_KEYS.USER_INFO, loginData.userInfo)

      // 更新全局状态
      app.login(loginData.userInfo)

      // 如果选择了头像，登录后上传并绑定
      if (avatarUrl) {
        try {
          const uploadRes = await uploadFile('/media/upload?category=avatar', avatarUrl, {
            showLoading: false
          })
          const payload = uploadRes?.data || uploadRes
          if (uploadRes?.success && payload?.key) {
            await put('/users/me/avatar', { avatarKey: payload.key }, { showLoading: false, showError: false })
            const me = await get('/users/me', {}, { showLoading: false, showError: false })
            wx.setStorageSync(STORAGE_KEYS.USER_INFO, me)
            app.login(me)
          }
        } catch (e) {
          console.warn('头像上传/绑定失败，已忽略:', e)
        }
      }

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
    const result = await post(API_ENDPOINTS.USER_LOGIN, data, {
      showLoading: false
    })
    return result
  },

  /**
   * 继续使用（已登录）- 验证 token 有效性
   * Continue: 用户已登录时点击"继续使用"按钮
   *
   * 术语对照（ubiquitous-language-glossary.md Section 4.4）:
   *   - 继续使用 = Continue = handleContinue
   *   - Token验证 = Token Verification via GET /users/me
   *
   * 流程:
   *   1. 调用 GET /users/me 验证token有效性
   *   2. 验证成功 → 跳转首页
   *   3. 验证失败 → 触发重新登录流程（handleReLogin）
   *
   * 参考: api-design.md Section 2.3
   */
  async handleContinue() {
    try {
      wx.showLoading({ title: '验证中...', mask: true })
      await get('/users/me', {}, { showLoading: false, showError: false })
      wx.hideLoading()
      wx.switchTab({ url: '/pages/home/home' })
    } catch (error) {
      wx.hideLoading()
      console.error('Token 验证失败', error)
      this.handleReLogin()
    }
  },

  /**
   * 切换账号（清除登录状态）
   * Switch Account: 用户主动切换账号或token验证失败时触发
   *
   * 术语对照（ubiquitous-language-glossary.md Section 4.4）:
   *   - 切换账号 = Switch Account = handleReLogin
   *   - 登录状态 = Login Status = isLogin
   *   - 用户信息 = User Info = userInfo
   *
   * 清理内容:
   *   - Storage: SESSION_TOKEN, USER_INFO
   *   - Global State: app.globalData.isLogin, app.globalData.userInfo
   *   - Page State: this.data.isLogin, this.data.showUserForm
   */
  handleReLogin() {
    wx.removeStorageSync(STORAGE_KEYS.SESSION_TOKEN)
    wx.removeStorageSync(STORAGE_KEYS.USER_INFO)
    app.globalData.isLogin = false
    app.globalData.userInfo = null
    this.setData({ isLogin: false, showUserForm: false })
    wx.showToast({ title: '请重新登录', icon: 'none' })
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
      title,
      content: '此处应显示完整的协议内容',
      showCancel: false
    })
  },

  /**
   * 游客模式入口
   */
  handleGuestMode() {
    // 设置游客模式标记
    app.globalData.isGuestMode = true
    app.globalData.isLogin = false

    wx.showToast({
      title: '游客模式',
      icon: 'none',
      duration: 1500
    })

    // 跳转到首页，部分功能受限
    setTimeout(() => {
      wx.switchTab({
        url: '/pages/index/index'
      })
    }, 800)
  }
})
