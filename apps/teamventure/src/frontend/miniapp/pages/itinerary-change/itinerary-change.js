// pages/itinerary-change/itinerary-change.js
import { get, put } from '../../utils/request.js'
import { API_ENDPOINTS } from '../../utils/config.js'
import { itineraryToMarkdown, validateItineraryMarkdown } from '../../utils/itinerary-markdown.js'

Page({
  data: {
    planId: '',
    baseVersion: 1,
    latestVersion: 1,
    initialMarkdown: '',
    markdown: ''
  },

  saveTimer: null,

  onLoad(options) {
    const planId = options.planId || ''
    this.setData({ planId })

    const eventChannel = this.getOpenerEventChannel?.()
    if (eventChannel && eventChannel.on) {
      eventChannel.on('init', (payload) => {
        const itinerary = payload?.itinerary
        const itineraryVersion = Number(payload?.itinerary_version || 1)
        const md = itineraryToMarkdown(itinerary, itineraryVersion)
        this.setData({
          baseVersion: itineraryVersion,
          latestVersion: itineraryVersion,
          initialMarkdown: md,
          markdown: md
        })
        this.tryRestoreDraft()
      })
    }

    // fallback: 如果未通过 eventChannel 注入，则自行拉取
    setTimeout(() => {
      if (!this.data.markdown && this.data.planId) {
        this.fetchLatest()
      }
    }, 0)
  },

  onUnload() {
    this.flushDraft()
  },

  draftKey() {
    return `itineraryChangeDraft:${this.data.planId || ''}`
  },

  saveDraft() {
    if (!this.data.planId) return
    const payload = {
      markdown: this.data.markdown,
      baseVersion: this.data.baseVersion,
      savedAt: Date.now()
    }
    wx.setStorageSync(this.draftKey(), payload)
  },

  flushDraft() {
    if (this.saveTimer) {
      clearTimeout(this.saveTimer)
      this.saveTimer = null
    }
    this.saveDraft()
  },

  clearDraft() {
    if (!this.data.planId) return
    wx.removeStorageSync(this.draftKey())
  },

  tryRestoreDraft() {
    if (!this.data.planId) return
    const draft = wx.getStorageSync(this.draftKey())
    if (!draft || !draft.markdown) return

    const draftMarkdown = String(draft.markdown || '')
    if (!draftMarkdown.trim()) return
    if (draftMarkdown === this.data.markdown) return

    wx.showModal({
      title: '发现未提交草稿',
      content: '检测到本地存在未提交的行程草稿，是否恢复？',
      confirmText: '恢复',
      cancelText: '忽略',
      success: (res) => {
        if (!res.confirm) return
        this.setData({
          markdown: draftMarkdown,
          baseVersion: Number(draft.baseVersion || this.data.baseVersion || 1)
        })
      }
    })
  },

  async fetchLatest() {
    try {
      wx.showLoading({ title: '加载中...', mask: true })
      const endpoint = API_ENDPOINTS.PLAN_DETAIL.replace(':id', this.data.planId)
      const plan = await get(endpoint, {}, { showLoading: false })
      wx.hideLoading()

      const itineraryVersion = Number(plan?.itinerary_version || 1)
      const md = itineraryToMarkdown(plan?.itinerary, itineraryVersion)
      this.setData({
        baseVersion: itineraryVersion,
        latestVersion: itineraryVersion,
        initialMarkdown: md,
        markdown: md
      })
      this.tryRestoreDraft()
    } catch (e) {
      wx.hideLoading()
      wx.showModal({ title: '加载失败', content: e?.message || '请稍后重试', showCancel: false })
    }
  },

  onMarkdownInput(e) {
    this.setData({ markdown: e.detail.value })
    if (this.saveTimer) clearTimeout(this.saveTimer)
    this.saveTimer = setTimeout(() => {
      this.saveTimer = null
      this.saveDraft()
    }, 500)
  },

  handleRestoreAndBack() {
    this.setData({ markdown: this.data.initialMarkdown })
    this.clearDraft()
    wx.navigateBack()
  },

  handleValidate() {
    const result = validateItineraryMarkdown(this.data.markdown)
    const content = result.valid
      ? `✅ 校验通过\n天数：${result.stats.days}\n行项目：${result.stats.items}`
      : `❌ 校验失败\n${result.errors.join('\n')}`

    wx.showModal({
      title: '校验结果',
      content,
      showCancel: false,
      confirmText: '确认'
    })
  },

  async handleSubmit() {
    const result = validateItineraryMarkdown(this.data.markdown)
    if (!result.valid) {
      wx.showModal({
        title: '格式不合规',
        content: result.errors.join('\n'),
        showCancel: false
      })
      return
    }

    try {
      wx.showLoading({ title: '提交中...', mask: true })

      const endpoint = API_ENDPOINTS.PLAN_UPDATE_ITINERARY.replace(':id', this.data.planId)
      const resp = await put(
        endpoint,
        {
          itinerary: result.itinerary,
          base_version: this.data.baseVersion
        },
        { showLoading: false, showError: false }
      )

      wx.hideLoading()
      this.clearDraft()

      const eventChannel = this.getOpenerEventChannel?.()
      eventChannel?.emit?.('itineraryUpdated', {
        itinerary: resp?.itinerary || result.itinerary,
        itinerary_version: resp?.itinerary_version || (this.data.baseVersion + 1)
      })

      wx.navigateBack()
    } catch (e) {
      wx.hideLoading()

      // CAS 冲突：刷新为新版本后继续编辑
      if (e?.code === 'CAS_CONFLICT' && e?.data?.itinerary) {
        this.flushDraft()
        const latestVersion = Number(e.data.itinerary_version || 1)
        const md = itineraryToMarkdown(e.data.itinerary, latestVersion)
        this.setData({
          latestVersion,
          initialMarkdown: md,
          markdown: md,
          baseVersion: latestVersion
        })

        wx.showModal({
          title: '文档已更新',
          content: '检测到行程在你编辑过程中已发生变化，已刷新到最新版本，请继续修改后再提交。',
          showCancel: false
        })
        return
      }

      wx.showModal({
        title: '提交失败',
        content: e?.message || '请稍后重试',
        showCancel: false
      })
    }
  }
})
