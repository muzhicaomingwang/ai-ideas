// pages/index/index.js
import { post, uploadFile } from '../../utils/request.js'
import { API_ENDPOINTS, STORAGE_KEYS } from '../../utils/config.js'
import { filterItineraryMarkdownLines, validateItineraryMarkdown } from '../../utils/itinerary-markdown.js'

const app = getApp()

const API_ENDPOINTS_LOCAL = {
  MARKDOWN_CONVERT: '/markdown/convert',
  MARKDOWN_OPTIMIZE: '/markdown/optimize'
}

const OPENAI_MODEL = 'gpt-5.2'

Page({
  data: {
    formData: {
      parsedContent: '',
      markdownContent: ''
    },
    planNameDialog: {
      visible: false,
      value: ''
    },
    logoPickerDialog: {
      visible: false,
      images: [],
      selectedIndex: 0
    },
    pendingSave: null, // { markdown, logoUrl }
    pendingLogoUrl: '',
    isSubmitting: false,
    isConverting: false,

    // 小红书导入
    xhsImportStatus: 'idle', // idle | parsing | error
    xhsLink: '',
    xhsImages: [],
    xhsParseProgress: 0,
    xhsParseError: '',
    xhsParseErrorCode: ''
  },

  progressTimer: null,

  sanitizeItineraryText(text) {
    const s = (text || '').toString().replace(/\r/g, '')
    if (!s) return ''
    const lines = s.split('\n')
    const out = []
    for (const line of lines) {
      const raw = (line || '').toString()
      const trimmed = raw.trim()

      // Strip concrete dates in day headings: "## Day 1（2023-10-01）" -> "## Day 1"
      const m = trimmed.match(/^(##\s*Day\s*\d+)\s*（[^）]*）\s*$/)
      if (m) {
        out.push(m[1])
        continue
      }

      // Drop placeholder-time rows like: "- - | 北戴河/阿那亚 |  |"
      if (trimmed.startsWith('- ')) {
        const body = trimmed.slice(2)
        const parts = body.split('|')
        if (parts.length >= 2) {
          const time = (parts[0] || '').trim()
          const normalized = time
            .replace(/[—–－‐‑‒―−~〜～﹣]/g, '-')
            .replace(/\s+/g, '')
          if (normalized && normalized.replace(/-/g, '') === '') {
            continue
          }
        }
      }

      out.push(raw)
    }

    return out.join('\n').replace(/\n{3,}/g, '\n\n').trim()
  },

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

  noop() {},

  isLikelyImageUrl(url) {
    const u = String(url || '').trim()
    if (!u) return false
    if (!/^https?:\/\//i.test(u)) return false
    if (/\.(png|jpe?g|webp|gif)(\?|#|$)/i.test(u)) return true
    // 小红书图片CDN常见域名（有些链接不带扩展名）
    if (/xiaohongshu\.com/i.test(u)) return true
    if (/xhscdn\.com/i.test(u)) return true
    if (/xhs(?:img|link)?\.com/i.test(u)) return true
    if (/ci\.xiaohongshu\.com/i.test(u)) return true
    return false
  },

  extractImageUrlsFromText(textLike) {
    const text = String(textLike || '')
    if (!text) return []

    const urls = []
    const push = (u) => {
      const s = String(u || '').trim()
      if (!s) return
      // strip surrounding <>
      const cleaned = s.replace(/^<|>$/g, '').trim()
      if (!cleaned) return
      if (!this.isLikelyImageUrl(cleaned)) return
      urls.push(cleaned)
    }

    // Markdown images: ![alt](url "title")
    const mdImg = /!\[[^\]]*]\(([^)\s]+)(?:\s+["'][^"']*["'])?\)/g
    let m
    while ((m = mdImg.exec(text))) {
      push(m[1])
    }

    // HTML images: <img src="...">
    const htmlImg = /<img[^>]+src=["']([^"']+)["'][^>]*>/gi
    while ((m = htmlImg.exec(text))) {
      push(m[1])
    }

    // Plain URLs
    const plain = /https?:\/\/[^\s<>"')]+/g
    while ((m = plain.exec(text))) {
      push(m[0])
    }

    // de-dup + cap to avoid huge dialogs
    const seen = new Set()
    const out = []
    for (const u of urls) {
      if (seen.has(u)) continue
      seen.add(u)
      out.push(u)
      if (out.length >= 12) break
    }
    return out
  },

  getLogoCandidates(sourceText) {
    const fromSource = this.extractImageUrlsFromText(sourceText)
    const fromParsed = this.extractImageUrlsFromText(this.data.formData?.parsedContent || '')
    const fromXhs = Array.isArray(this.data.xhsImages)
      ? this.data.xhsImages.filter(u => this.isLikelyImageUrl(u))
      : []
    const merged = []
    const seen = new Set()
    for (const u of [...fromSource, ...fromParsed, ...fromXhs]) {
      const s = String(u || '').trim()
      if (!s || seen.has(s)) continue
      seen.add(s)
      merged.push(s)
      if (merged.length >= 12) break
    }
    return merged
  },

  openLogoPicker(markdown, images) {
    this.setData({
      pendingSave: { markdown, logoUrl: '' },
      logoPickerDialog: {
        visible: true,
        images,
        selectedIndex: 0
      }
    })
  },

  closeLogoPicker() {
    this.setData({
      logoPickerDialog: { ...this.data.logoPickerDialog, visible: false, images: [] },
      pendingSave: null
    })
  },

  handleLogoPickSelect(e) {
    const idx = Number(e.currentTarget.dataset.index)
    if (Number.isNaN(idx)) return
    this.setData({ 'logoPickerDialog.selectedIndex': idx })
  },

  handleLogoPickSkip() {
    const pending = this.data.pendingSave
    if (!pending) return
    const markdown = pending.markdown
    this.closeLogoPicker()
    this.setData({ pendingLogoUrl: '' })
    this.handleSaveWithLogo(markdown, '')
  },

  handleLogoPickConfirm() {
    const pending = this.data.pendingSave
    const dlg = this.data.logoPickerDialog
    if (!pending) return
    const images = Array.isArray(dlg?.images) ? dlg.images : []
    const idx = Number(dlg?.selectedIndex || 0)
    const selected = images[idx] || images[0] || ''
    const markdown = pending.markdown
    this.closeLogoPicker()
    this.setData({ pendingLogoUrl: selected })
    this.handleSaveWithLogo(markdown, selected)
  },

  handleSaveWithLogo(markdownContent, logoUrl) {
    // 进入“输入方案名称”阶段，logoUrl（可为空）暂存，提交时一起保存
    this.setData({
      pendingLogoUrl: logoUrl || '',
      planNameDialog: {
        visible: true,
        value: this.suggestPlanName()
      }
    })
  },

  downloadToTempFile(url) {
    const u = String(url || '').trim()
    if (!u) return Promise.reject(new Error('缺少图片链接'))
    return new Promise((resolve, reject) => {
      wx.downloadFile({
        url: u,
        timeout: 20000,
        success: (res) => {
          if (res.statusCode === 200 && res.tempFilePath) {
            resolve(res.tempFilePath)
          } else {
            reject(new Error('图片下载失败'))
          }
        },
        fail: () => reject(new Error('图片下载失败'))
      })
    })
  },

  async uploadLogoFromUrl(url) {
    const tempPath = await this.downloadToTempFile(url)
    const resp = await uploadFile('/media/upload?category=itinerary&scope=plan_logo', tempPath, { showLoading: false })
    if (!resp?.success || !resp?.data?.bucket || !resp?.data?.key) {
      throw new Error('Logo 上传失败')
    }
    return `minio://${resp.data.bucket}/${resp.data.key}`
  },

  loadLastRequest() {
    try {
      const lastRequest = wx.getStorageSync(STORAGE_KEYS.LATEST_REQUEST)
      if (lastRequest?.markdownContent || lastRequest?.parsedContent) {
        this.setData({
          'formData.parsedContent': lastRequest.parsedContent || '',
          'formData.markdownContent': lastRequest.markdownContent || '',
          xhsImages: Array.isArray(lastRequest.xhsImages) ? lastRequest.xhsImages : []
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
        parsedContent: this.data.formData.parsedContent,
        markdownContent: this.data.formData.markdownContent,
        xhsImages: this.data.xhsImages
      })
    } catch (error) {
      console.error('保存请求数据失败:', error)
    }
  },

  saveDraft() {
    try {
      const parsedContent = (this.data.formData.parsedContent || '').trim()
      const markdown = (this.data.formData.markdownContent || '').trim()
      const link = (this.data.xhsLink || '').trim()
      if (!parsedContent && !markdown && !link) return

      wx.setStorageSync(STORAGE_KEYS.DRAFT_REQUEST, {
        timestamp: Date.now(),
        xhsLink: link,
        xhsImages: this.data.xhsImages,
        parsedContent,
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
      xhsImages: [],
      xhsParseProgress: 0,
      xhsParseError: '',
      xhsParseErrorCode: ''
    })
  },

  handleParsedContentInput(e) {
    this.setData({ 'formData.parsedContent': e.detail.value })
  },

  handleMarkdownContentInput(e) {
    this.setData({ 'formData.markdownContent': e.detail.value })
  },

  handleClearParsedContent() {
    this.setData({ 'formData.parsedContent': '', xhsImages: [] })
    this.saveCurrentRequest()
  },

  handleClearMarkdownContent() {
    this.setData({ 'formData.markdownContent': '' })
    this.saveCurrentRequest()
  },

  async handleConvertToMarkdown() {
    if (this.data.isConverting) return
    const parsed = (this.data.formData.parsedContent || '').trim()
    if (!parsed) return

    this.setData({ isConverting: true })
    try {
      wx.showLoading({ title: 'AI转换中...', mask: true })
      const res = await post(
        API_ENDPOINTS_LOCAL.MARKDOWN_CONVERT,
        { parsed_content: parsed, model: OPENAI_MODEL },
        { showLoading: false, timeout: 180000 }
      )
      const md = this.sanitizeItineraryText((res?.markdown_content || '').toString())
      if (!md) throw new Error('未获取到 Markdown 内容')

      // ✅ 与方案页（itinerary-change）使用同一套 Markdown 校验逻辑
      // 自动修复闭环已下沉到 Java 服务端，这里只做一次兜底校验。
      const candidate = md
      const check = validateItineraryMarkdown(candidate)
      if (!check.valid) {
        const msg = (check.errors || []).slice(0, 10).join('\n') || '格式不合规'
        throw new Error(`解析错误已经识别，请自行进行修改后再次进行尝试：\n${msg}`)
      }

      this.setData({ 'formData.markdownContent': candidate })
      this.saveCurrentRequest()
      wx.showToast({ title: '已生成 Markdown', icon: 'success' })
    } catch (e) {
      wx.showModal({
        title: '转换失败',
        content: e?.message || '请稍后重试',
        showCancel: false
      })
    } finally {
      wx.hideLoading()
      this.setData({ isConverting: false })
    }
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
      xhsParseErrorCode: '',
      xhsImages: []
    })

    if (this.progressTimer) clearInterval(this.progressTimer)
    this.progressTimer = setInterval(() => {
      const current = this.data.xhsParseProgress || 0
      if (current >= 90) return
      this.setData({ xhsParseProgress: current + 5 })
    }, 120)

    try {
      // If user pasted an xhslink short-link, do a fast capability check and surface a clearer error
      // when the gateway is not pointing to the updated backend.
      if (/(^|\s)https?:\/\/xhslink\.com\//i.test(link)) {
        try {
          await post(API_ENDPOINTS.XHS_RESOLVE_NOTE_ID, { link }, { showLoading: false, timeout: 15000 })
        } catch (e) {
          // If backend doesn't support the resolver endpoint (404) or returns a legacy error,
          // tell the user to switch to the local gateway / redeploy.
          const msg = (e?.message || '').toString()
          if ((e?.code || '') === 'NOT_FOUND' || msg.includes('Not Found') || msg.includes('404')) {
            const err = new Error('当前后端未更新（不支持 xhslink 分享短链解析），请切换到本地网关或重启后端容器后重试')
            err.code = 'PARSE_FAILED'
            throw err
          }
        }
      }

      const result = await post(API_ENDPOINTS.XHS_PARSE, { link }, { showLoading: false, timeout: 90000 })

      if (this.progressTimer) {
        clearInterval(this.progressTimer)
        this.progressTimer = null
      }
      this.setData({ xhsParseProgress: 100 })

      const markdown = this.sanitizeItineraryText((result?.generatedMarkdown || result?.raw_content || '').toString())
      if (!markdown || markdown.trim().length === 0) {
        const err = new Error('未获取到可导入的内容，请重试')
        err.code = 'PARSE_FAILED'
        throw err
      }

      this.setData({
        xhsImportStatus: 'idle',
        xhsImages: Array.isArray(result?.images)
          ? result.images
          : (Array.isArray(result?.image_urls) ? result.image_urls : []),
        'formData.parsedContent': markdown,
        'formData.markdownContent': ''
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

  handlePreviewXhsImage(e) {
    const urls = (this.data.xhsImages || []).filter(Boolean)
    if (urls.length === 0) return
    const index = Number(e?.currentTarget?.dataset?.index || 0)
    const current = urls[Math.max(0, Math.min(index, urls.length - 1))]
    wx.previewImage({ current, urls })
  },

  validateMarkdown() {
    const markdown = (this.data.formData.markdownContent || '').trim()
    if (!markdown) {
      wx.showToast({ title: '请先生成/填写 Markdown', icon: 'none' })
      return false
    }
    if (markdown.length < 50) {
      wx.showToast({ title: '内容过少，请导入更完整的行程', icon: 'none' })
      return false
    }

    const result = validateItineraryMarkdown(markdown)
    if (!result.valid) {
      wx.showModal({
        title: '格式不合规',
        content: (result.errors || []).slice(0, 10).join('\n') || 'Markdown 格式不合规',
        showCancel: false
      })
      return false
    }
    return true
  },

  handleSave() {
    if (this.data.isSubmitting) return
    if (!this.validateMarkdown()) return
    this.setData({ pendingLogoUrl: '' })

    const markdown = (this.data.formData.markdownContent || '').toString()
    const parsed = (this.data.formData.parsedContent || '').toString()
    const logoCandidates = this.getLogoCandidates(parsed || markdown)

    if (logoCandidates.length > 0) {
      this.openLogoPicker(markdown, logoCandidates)
      return
    }

    const defaultName = this.suggestPlanName()
    this.setData({
      planNameDialog: { visible: true, value: defaultName }
    })
  },

  suggestPlanName() {
    const md = (this.data.formData.markdownContent || '').trim()
    const parsed = (this.data.formData.parsedContent || '').trim()
    const source = md || parsed
    if (!source) return '团建方案'
    const firstLine = source.split('\n').map(s => s.trim()).find(Boolean) || ''
    const cleaned = firstLine.replace(/^#+\s*/, '').slice(0, 30)
    return cleaned || '团建方案'
  },

  handlePlanNameInput(e) {
    this.setData({ 'planNameDialog.value': e.detail.value })
  },

  handlePlanNameCancel() {
    this.setData({ planNameDialog: { ...this.data.planNameDialog, visible: false } })
  },

  handlePlanNameConfirm() {
    const v = (this.data.planNameDialog.value || '').trim()
    if (!v) {
      wx.showToast({ title: '请填写方案名称', icon: 'none' })
      return
    }
    this.setData({ planNameDialog: { ...this.data.planNameDialog, visible: false } })
    this.submitPlan(v, this.data.pendingLogoUrl || '')
  },

  async performSave(planName, markdown, logoUrl) {
    let logoStorage = ''
    if (logoUrl) {
      try {
        wx.showLoading({ title: '上传Logo...', mask: true })
        logoStorage = await this.uploadLogoFromUrl(logoUrl)
      } catch (e) {
        wx.hideLoading()
        const msg = e?.message || '上传失败'
        const proceed = await new Promise((resolve) => {
          wx.showModal({
            title: 'Logo 上传失败',
            content: `${msg}，是否继续保存（不设置Logo）？`,
            confirmText: '继续保存',
            cancelText: '取消',
            success: (res) => resolve(res?.confirm === true)
          })
        })
        if (!proceed) {
          throw new Error('已取消保存')
        }
      }
    }

    wx.showLoading({ title: '正在保存...', mask: true })
    const requestData = {
      markdown_content: markdown,
      plan_name: planName,
      ...(logoStorage ? { logo_storage: logoStorage } : {})
    }
    await post(API_ENDPOINTS.PLAN_SAVE, requestData, { showLoading: false, timeout: 45000 })
    wx.hideLoading()
    this.saveCurrentRequest()
    wx.setStorageSync(STORAGE_KEYS.MYPLANS_JUMP_TAB, 'draft')

    wx.showToast({ title: '已保存', icon: 'success', duration: 1200 })
    setTimeout(() => {
      wx.switchTab({ url: '/pages/myplans/myplans' })
    }, 300)
  },

  async submitPlan(planName, preselectedLogoUrl = '') {
    if (this.data.isSubmitting) return
    if (!this.validateMarkdown()) return

    this.setData({ isSubmitting: true })
    try {
      const originalMarkdown = (this.data.formData.markdownContent || '').toString()

      // 1) 过 GPT-5.2 一次：整理行程规划（后端 /markdown/optimize）
      wx.showLoading({ title: '整理行程中...', mask: true })
      const optimizedRes = await post(
        API_ENDPOINTS_LOCAL.MARKDOWN_OPTIMIZE,
        { markdown_content: originalMarkdown, model: OPENAI_MODEL },
        { showLoading: false, timeout: 180000, showError: false }
      )
      wx.hideLoading()

      const optimized = this.sanitizeItineraryText((optimizedRes?.markdown_content || originalMarkdown).toString())

      // 2) Markdown 校验（按行）：非「##Day」或「时间行」直接删除
      const filtered = filterItineraryMarkdownLines(optimized)

      // 让用户看到最终将要保存的版本
      if (filtered && filtered !== originalMarkdown) {
        this.setData({ 'formData.markdownContent': filtered })
      }

      // 3) 最终按共享 v2 规则做一次严格校验
      const baseCheck = validateItineraryMarkdown(filtered)
      if (!baseCheck.valid) {
        const msg = (baseCheck.errors || []).slice(0, 10).join('\n') || '格式不合规'
        throw new Error(`格式不合规，无法保存：\n${msg}`)
      }

      // 若用户已在“保存”入口预选了 Logo，则直接走保存（不再二次弹窗）
      if (preselectedLogoUrl) {
        await this.performSave(planName, filtered, preselectedLogoUrl)
        return
      }

      await this.performSave(planName, filtered, '')
    } catch (error) {
      wx.hideLoading()
      wx.showModal({
        title: '保存失败',
        content: error?.message || '请稍后重试',
        showCancel: true,
        confirmText: '重试',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) this.submitPlan(planName)
        }
      })
    } finally {
      this.setData({ isSubmitting: false })
    }
  }
})
