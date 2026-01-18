// pages/index/index.js
import { post } from '../../utils/request.js'
import { API_ENDPOINTS, STORAGE_KEYS } from '../../utils/config.js'

const app = getApp()

Page({
  data: {
    formData: {
      markdownContent: ''
    },
    isSubmitting: false,

    // 小红书导入
    xhsImportStatus: 'idle', // idle | parsing | error
    xhsLink: '',
    xhsParseProgress: 0,
    xhsParseError: '',
    xhsParseErrorCode: ''
  },

  progressTimer: null,

  onLoad() {
    // 检查登录状态
    if (!app.globalData.isLogin) {
      wx.redirectTo({ url: '/pages/login/login' })
      return
    }

    this.loadLastRequest()
  },

  onHide() {
    this.saveDraft()
  },

  onUnload() {
    if (this.progressTimer) {
      clearInterval(this.progressTimer)
      this.progressTimer = null
    }
  },

  loadLastRequest() {
    try {
      const lastRequest = wx.getStorageSync(STORAGE_KEYS.LATEST_REQUEST)
      if (lastRequest?.markdownContent) {
        this.setData({
          'formData.markdownContent': lastRequest.markdownContent
        })
      }
    } catch (error) {
      console.error('加载上次请求失败:', error)
    }
  },

  saveCurrentRequest() {
    try {
      wx.setStorageSync(STORAGE_KEYS.LATEST_REQUEST, {
        mode: 'markdown',
        markdownContent: this.data.formData.markdownContent
      })
    } catch (error) {
      console.error('保存请求数据失败:', error)
    }
  },

  saveDraft() {
    try {
      const markdown = (this.data.formData.markdownContent || '').trim()
      const link = (this.data.xhsLink || '').trim()
      if (!markdown && !link) return

      wx.setStorageSync(STORAGE_KEYS.DRAFT_REQUEST, {
        timestamp: Date.now(),
        xhsLink: link,
        markdownContent: markdown
      })
    } catch (error) {
      console.error('保存草稿失败:', error)
    }
  },

  handleXhsLinkInput(e) {
    this.setData({ xhsLink: e.detail.value })
  },

  handlePasteXhsLink() {
    wx.getClipboardData({
      success: (res) => {
        const text = (res.data || '').toString()
        this.setData({ xhsLink: text })
      }
    })
  },

  handleResetXhsImport() {
    if (this.progressTimer) {
      clearInterval(this.progressTimer)
      this.progressTimer = null
    }
    this.setData({
      xhsImportStatus: 'idle',
      xhsLink: '',
      xhsParseProgress: 0,
      xhsParseError: '',
      xhsParseErrorCode: ''
    })
  },

  buildXhsItineraryTemplate() {
    return `请将小红书分享文本补全为“按天行程”格式（建议包含 D1/D2 或 第1天/第2天，以便识别）：

标题：________（可选）
目的地：________（可选）
天数：__天__夜（可选）

D1 ________
- ________
- ________

D2 ________
- ________
- ________

（如有更多天数请继续 D3/D4...）

交通（可选）：高铁/航班/大巴/自驾 + 时间/车次
住宿（可选）：酒店/民宿 + 区域
预算（可选）：¥____/人
注意事项（可选）：防晒/预约/集合时间等`
  },

  handleCopyXhsItineraryTemplate() {
    wx.setClipboardData({
      data: this.buildXhsItineraryTemplate(),
      success: () => wx.showToast({ title: '已复制模板', icon: 'success' })
    })
  },

  handleFillXhsItineraryTemplate() {
    this.setData({
      xhsImportStatus: 'idle',
      xhsLink: this.buildXhsItineraryTemplate(),
      xhsParseProgress: 0,
      xhsParseError: '',
      xhsParseErrorCode: ''
    })
  },

  buildXhsPasteGuide() {
    return `URL 导入在部分情况下会被限制抓取正文（反爬/需要登录）。

建议用“分享口令全文”导入（成功率更高）：
1) 在小红书 App 打开笔记
2) 点击“分享”
3) 选择“复制链接/复制口令”
4) 把复制出来的整段文字完整粘贴到输入框
   - 为提高识别成功率，尽量包含按天行程：D1/D2… 或 第1天/第2天…
5) 点击“开始解析”

如果原文没有分天结构，可先用“补全模板”整理后再解析。`
  },

  handleCopyXhsPasteGuide() {
    wx.setClipboardData({
      data: this.buildXhsPasteGuide(),
      success: () => wx.showToast({ title: '已复制指南', icon: 'success' })
    })
  },

  async handleStartXhsParse() {
    const link = (this.data.xhsLink || '').trim()
    if (!link) return

    this.setData({
      xhsImportStatus: 'parsing',
      xhsParseProgress: 0,
      xhsParseError: '',
      xhsParseErrorCode: ''
    })

    if (this.progressTimer) clearInterval(this.progressTimer)
    this.progressTimer = setInterval(() => {
      const current = this.data.xhsParseProgress || 0
      if (current >= 90) return
      this.setData({ xhsParseProgress: current + 5 })
    }, 120)

    try {
      const result = await post(API_ENDPOINTS.XHS_PARSE, { link }, { showLoading: false, timeout: 45000 })

      if (this.progressTimer) {
        clearInterval(this.progressTimer)
        this.progressTimer = null
      }
      this.setData({ xhsParseProgress: 100 })

      const markdown = (result?.generatedMarkdown || result?.raw_content || '').toString()
      if (!markdown || markdown.trim().length === 0) {
        const err = new Error('未获取到可导入的内容，请重试')
        err.code = 'PARSE_FAILED'
        throw err
      }

      this.setData({
        xhsImportStatus: 'idle',
        'formData.markdownContent': markdown
      })
      this.saveCurrentRequest()
    } catch (error) {
      if (this.progressTimer) {
        clearInterval(this.progressTimer)
        this.progressTimer = null
      }

      this.setData({
        xhsImportStatus: 'error',
        xhsParseProgress: 0,
        xhsParseError: error?.message || '解析失败，请稍后重试',
        xhsParseErrorCode: error?.code || ''
      })
    }
  },

  validateMarkdown() {
    const markdown = (this.data.formData.markdownContent || '').trim()
    if (!markdown) {
      wx.showToast({ title: '请先导入生成Markdown', icon: 'none' })
      return false
    }
    if (markdown.length < 50) {
      wx.showToast({ title: '内容过少，请导入更完整的行程', icon: 'none' })
      return false
    }
    return true
  },

  async handleGenerate() {
    if (this.data.isSubmitting) return
    if (!this.validateMarkdown()) return

    this.setData({ isSubmitting: true })
    try {
      wx.showLoading({ title: '正在生成方案...', mask: true })

      const requestData = { markdown_content: this.data.formData.markdownContent }
      await post(API_ENDPOINTS.PLAN_GENERATE, requestData, { showLoading: false, timeout: 120000 })

      wx.hideLoading()
      this.saveCurrentRequest()

      wx.showModal({
        title: '提交成功',
        content: 'AI正在为您生成方案，预计需要1-2分钟。请在"我的方案"中查看结果。',
        showCancel: false,
        confirmText: '去查看',
        success: () => {
          wx.switchTab({ url: '/pages/myplans/myplans' })
        }
      })
    } catch (error) {
      wx.hideLoading()
      wx.showModal({
        title: '生成失败',
        content: error?.message || '请稍后重试',
        showCancel: true,
        confirmText: '重试',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) this.handleGenerate()
        }
      })
    } finally {
      this.setData({ isSubmitting: false })
    }
  }
})
