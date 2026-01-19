// pages/detail/detail.js
import { get, put, post } from '../../utils/request.js'
import { API_ENDPOINTS, PLAN_STATUS, PLAN_STATUS_NAMES } from '../../utils/config.js'
import { formatMoney, formatPerPerson, formatDuration, calculateDays } from '../../utils/util.js'

Page({
  data: {
    plan: null,
    planId: '',
    sections: {
      itinerary: true // 默认展开行程
    },
    itineraryUi: { days: [] },
    linkedItineraryDraft: null, // 预留：未来需要时再落库
    confirmDateDialog: {
      visible: false,
      startDate: ''
    },
    itineraryEdit: {
      dirty: false,
      saving: false,
      baseVersion: 1
    },
    cardEditor: {
      visible: false,
      mode: 'edit', // edit | insert_left | insert_right
      day: 1,
      index: 0,
      type: 'nearby', // transport | nearby | accommodation
      activity: '',
      location: '',
      note: '',
      time_start: '',
      time_end: ''
    },
  },

  onLoad(options) {
    console.log('方案详情页加载', options)

    // 【紧急修复】禁用微信性能监控，避免_reportShowPage的URIError
    // 这是微信开发者工具的Bug，与我们的代码无关
    if (typeof this.__disablePageReporter__ !== 'undefined') {
      this.__disablePageReporter__ = true
    }

    try {
      // 从服务器获取方案详情（只支持planId参数）
      if (options.planId) {
        this.setData({ planId: options.planId })
        this.fetchPlanDetail(options.planId)
      } else {
        this.showErrorAndBack('缺少方案ID')
      }
    } catch (e) {
      console.error('页面加载异常:', e)
      // 捕获但不阻断，继续执行
    }
  },

  noop() {},

  /**
   * 显示错误并返回
   */
  showErrorAndBack(message) {
    wx.showModal({
      title: '提示',
      content: message,
      showCancel: false,
      success: () => {
        wx.navigateBack()
      }
    })
  },

  /**
   * 从服务器获取方案详情
   */
  async fetchPlanDetail(planId) {
    try {
      wx.showLoading({ title: '加载中...', mask: true })

      const endpoint = API_ENDPOINTS.PLAN_DETAIL.replace(':id', planId)
      const plan = await get(endpoint)

      wx.hideLoading()
      this.processPlanData(plan)
    } catch (error) {
      wx.hideLoading()
      console.error('获取方案详情失败:', error)
      this.showErrorAndBack('加载失败，请稍后重试')
    }
  },

  /**
   * 处理方案数据
   */
  processPlanData(plan) {
    if (!plan) {
      this.showErrorAndBack('方案数据为空')
      return
    }

    // 计算天数：以行程天数为准，确保与“行程安排”一致
    const itineraryDayCount = Array.isArray(plan.itinerary?.days) ? plan.itinerary.days.length : 0
    const days = itineraryDayCount > 0
      ? itineraryDayCount
      : (plan.duration_days ||
        (plan.start_date && plan.end_date ? calculateDays(plan.start_date, plan.end_date) : 2))

    // 处理亮点（后端返回 highlights 数组，前端显示为单个字符串）
    let highlight = ''
    if (Array.isArray(plan.highlights) && plan.highlights.length > 0) {
      highlight = plan.highlights.join('、')
    } else if (typeof plan.highlights === 'string') {
      highlight = plan.highlights
    }

    // 处理展示数据（只提取需要的字段，避免序列化问题）
    const processedPlan = {
      plan_id: plan.plan_id,
      plan_name: plan.plan_name,
      plan_type: plan.plan_type,
      status: plan.status || PLAN_STATUS.DRAFT,
      status_label: PLAN_STATUS_NAMES[plan.status] || PLAN_STATUS_NAMES[PLAN_STATUS.DRAFT],
      itinerary_version: plan.itinerary_version || 1,
      budget_total: this.formatNumber(plan.budget_total),
      budget_per_person: plan.budget_per_person
        ? formatMoney(plan.budget_per_person) + ' 人均'
        : formatPerPerson(plan.budget_total, plan.people_count),
      duration: formatDuration(days),
      duration_days: days,
      people_count: plan.people_count,
      departure_city: plan.departure_city,
      destination: plan.destination,
      destination_city: plan.destination_city,
      summary: plan.summary,
      highlight,
      itinerary: this.processItinerary(plan.itinerary),
      start_date: plan.start_date,
      end_date: plan.end_date,
      recommended: plan.recommended
    }

    const { itineraryUi, linkedItineraryDraft } = this.buildItineraryUi(processedPlan.itinerary, processedPlan.start_date)
    this.setData({
      plan: processedPlan,
      itineraryUi,
      linkedItineraryDraft,
      itineraryEdit: {
        ...this.data.itineraryEdit,
        dirty: false,
        saving: false,
        baseVersion: processedPlan.itinerary_version || 1
      }
    })
  },

  classifyItineraryItem(item) {
    const kind = item?.meta?.kind
    if (kind === 'transport' || kind === 'nearby' || kind === 'accommodation') return kind
    const text = `${item?.activity || ''} ${item?.location || ''} ${item?.note || ''}`.trim()
    const t = text.toLowerCase()

    const accommodationKeywords = ['入住', '酒店', '民宿', '住宿', '休息', '退房', '办理入住', 'checkin', 'checkout']
    const transportKeywords = ['出发', '前往', '到达', '返程', '集合', '地铁', '公交', '打车', '网约车', '骑行', '自驾', '高铁', '动车', '航班', '飞机', '换乘', '步行', '接驳', '大巴']

    if (accommodationKeywords.some(k => text.includes(k) || t.includes(k))) return 'accommodation'
    if (transportKeywords.some(k => text.includes(k) || t.includes(k))) return 'transport'
    return 'nearby'
  },

  buildItineraryUi(itinerary, startDate) {
    const days = Array.isArray(itinerary?.days) ? itinerary.days : []
    const draft = {
      days: days.map(d => ({
        ...d,
        items: Array.isArray(d?.items) ? d.items.map(it => ({ ...it })) : []
      }))
    }

    const dateLabelByDay = this.buildDateLabelByDay(draft.days, startDate)

    const uiDays = draft.days.map((d) => {
      const items = Array.isArray(d?.items) ? d.items : []
      const cards = items.map((it, idx) => {
        const type = this.classifyItineraryItem(it)
        const typeLabel = type === 'transport' ? '交通' : (type === 'accommodation' ? '住宿' : '周边游')
        const time = it?.time_start && it?.time_end ? `${it.time_start} - ${it.time_end}` : (it?.time_start || it?.time_end || '')
        const title = String(it?.activity || '').trim()
        const subtitle = String(it?.location || it?.note || '').trim()
        return {
          ...it,
          _key: it?._key || `${d.day || 'day'}_${idx}_${it?.time_start || ''}_${title}`,
          type,
          typeLabel,
          time,
          title,
          subtitle,
          itemIndex: idx,
        }
      })

      return {
        day: d.day,
        dateLabel: dateLabelByDay[Number(d.day)] || '',
        cards
      }
    })

    return {
      itineraryUi: { days: uiDays },
      linkedItineraryDraft: draft,
    }
  },

  /**
   * 跳转到行程变更页（Markdown 编辑）
   */
  goItineraryChange() {
    const planId = this.data.plan?.plan_id || this.data.planId
    if (!planId) {
      wx.showToast({ title: '缺少方案ID', icon: 'none' })
      return
    }

    wx.navigateTo({
      url: `/pages/itinerary-change/itinerary-change?planId=${encodeURIComponent(planId)}`,
      events: {
        itineraryUpdated: (payload) => {
          if (!payload?.itinerary) return
          this.applyItineraryUpdate(payload.itinerary, payload.itinerary_version)
        }
      },
      success: (res) => {
        res.eventChannel?.emit?.('init', {
          itinerary: this.data.plan?.itinerary,
          itinerary_version: this.data.plan?.itinerary_version || 1
        })
      }
    })
  },

  applyItineraryUpdate(itinerary, itineraryVersion) {
    const processed = this.processItinerary(itinerary)
    const { itineraryUi, linkedItineraryDraft } = this.buildItineraryUi(processed, this.data.plan?.start_date)
    this.setData({
      'plan.itinerary': processed,
      'plan.itinerary_version': itineraryVersion || (this.data.plan?.itinerary_version || 1) + 1,
      itineraryUi,
      linkedItineraryDraft,
      itineraryEdit: {
        ...this.data.itineraryEdit,
        dirty: false,
        saving: false,
        baseVersion: itineraryVersion || (this.data.plan?.itinerary_version || 1) + 1
      }
    })
  },

  buildDateLabelByDay(days, startDate) {
    const out = {}
    const s = String(startDate || '').trim()
    if (!s) return out
    const base = new Date(s)
    if (isNaN(base.getTime())) return out

    const addDays = (d, delta) => {
      const next = new Date(d.getTime())
      next.setDate(next.getDate() + delta)
      const yyyy = next.getFullYear()
      const mm = String(next.getMonth() + 1).padStart(2, '0')
      const dd = String(next.getDate()).padStart(2, '0')
      return `${yyyy}-${mm}-${dd}`
    }

    ;(Array.isArray(days) ? days : []).forEach((d) => {
      const dayNum = Number(d?.day)
      if (!dayNum || Number.isNaN(dayNum)) return
      out[dayNum] = addDays(base, dayNum - 1)
    })
    return out
  },

  /**
   * 处理行程数据
   */
  processItinerary(itinerary) {
    if (!itinerary || !itinerary.days) {
      return { days: [] }
    }

    return {
      days: itinerary.days.map(day => ({
        ...day,
        items: (day.items || []).map((it, idx) => ({
          ...it,
          _key: `${day.day || 'day'}_${idx}_${it?.time_start || ''}_${it?.activity || ''}`
        }))
      }))
    }
  },

  normalizeTime(v) {
    const s = String(v || '').trim()
    if (!s) return ''
    const m = s.match(/^(\d{1,2}):(\d{2})$/)
    if (!m) return ''
    const hh = Number(m[1])
    const mm = Number(m[2])
    if (Number.isNaN(hh) || Number.isNaN(mm)) return ''
    if (hh < 0 || hh > 23 || mm < 0 || mm > 59) return ''
    return `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}`
  },

  openCardActionSheet(e) {
    const day = Number(e.currentTarget.dataset.day)
    const index = Number(e.currentTarget.dataset.index)
    if (!day || Number.isNaN(index)) return

    wx.showActionSheet({
      itemList: ['左侧 +1 卡片', '右侧 +1 卡片', '修改此卡片'],
      success: (res) => {
        if (res.tapIndex === 0) this.openCardEditor('insert_left', day, index)
        if (res.tapIndex === 1) this.openCardEditor('insert_right', day, index)
        if (res.tapIndex === 2) this.openCardEditor('edit', day, index)
      }
    })
  },

  openCardEditor(mode, day, index) {
    const itinerary = this.data.plan?.itinerary
    const days = Array.isArray(itinerary?.days) ? itinerary.days : []
    const d = days.find(x => Number(x?.day) === Number(day))
    const items = Array.isArray(d?.items) ? d.items : []

    let payload = {
      visible: true,
      mode,
      day,
      index,
      type: 'nearby',
      activity: '',
      location: '',
      note: '',
      time_start: '',
      time_end: ''
    }

    if (mode === 'edit') {
      const it = items[index]
      if (!it) return
      payload = {
        ...payload,
        type: this.classifyItineraryItem(it),
        activity: String(it.activity || ''),
        location: String(it.location || ''),
        note: String(it.note || ''),
        time_start: String(it.time_start || ''),
        time_end: String(it.time_end || '')
      }
    }

    this.setData({ cardEditor: payload })
  },

  closeCardEditor() {
    this.setData({ cardEditor: { ...this.data.cardEditor, visible: false } })
  },

  handleCardEditorTypeSelect(e) {
    const type = String(e.currentTarget.dataset.type || '')
    if (!['transport', 'nearby', 'accommodation'].includes(type)) return
    this.setData({ 'cardEditor.type': type })
  },

  handleCardEditorInput(e) {
    const field = String(e.currentTarget.dataset.field || '')
    const value = e.detail.value
    if (!['activity', 'location', 'note', 'time_start', 'time_end'].includes(field)) return
    this.setData({ [`cardEditor.${field}`]: value })
  },

  applyCardEditToItinerary(updated) {
    const itinerary = this.data.plan?.itinerary
    if (!itinerary || !Array.isArray(itinerary.days)) return
    const days = itinerary.days.map(d => ({ ...d, items: Array.isArray(d.items) ? d.items.slice() : [] }))

    const day = Number(updated.day)
    const dIdx = days.findIndex(x => Number(x?.day) === day)
    if (dIdx < 0) return

    const items = days[dIdx].items
    const insertAt = updated.mode === 'insert_left'
      ? updated.index
      : updated.mode === 'insert_right'
        ? updated.index + 1
        : updated.index

    const itemPayload = {
      activity: updated.activity,
      location: updated.location,
      note: updated.note,
      ...(updated.time_start ? { time_start: updated.time_start } : {}),
      ...(updated.time_end ? { time_end: updated.time_end } : {}),
      meta: { ...(items[updated.index]?.meta || {}), kind: updated.type }
    }

    if (updated.mode === 'edit') {
      items[updated.index] = { ...(items[updated.index] || {}), ...itemPayload }
    } else {
      items.splice(insertAt, 0, itemPayload)
    }

    // Re-key items for stable rendering
    days[dIdx].items = items.map((it, idx) => ({
      ...it,
      _key: `${day}_${idx}_${it?.time_start || ''}_${it?.activity || ''}`
    }))

    const newItinerary = { days }
    const { itineraryUi, linkedItineraryDraft } = this.buildItineraryUi(newItinerary, this.data.plan?.start_date)
    this.setData({
      'plan.itinerary': newItinerary,
      itineraryUi,
      linkedItineraryDraft,
      itineraryEdit: { ...this.data.itineraryEdit, dirty: true }
    })
  },

  handleCardEditorConfirm() {
    const ce = this.data.cardEditor
    const activity = String(ce.activity || '').trim()
    if (!activity) {
      wx.showToast({ title: '请填写内容', icon: 'none' })
      return
    }

    const timeStart = this.normalizeTime(ce.time_start)
    const timeEnd = this.normalizeTime(ce.time_end)
    if ((ce.time_start && !timeStart) || (ce.time_end && !timeEnd)) {
      wx.showToast({ title: '时间格式需为 HH:MM', icon: 'none' })
      return
    }

    const updated = {
      ...ce,
      activity,
      location: String(ce.location || '').trim(),
      note: String(ce.note || '').trim(),
      time_start: timeStart,
      time_end: timeEnd,
    }

    this.applyCardEditToItinerary(updated)
    this.closeCardEditor()
  },

  async handleSaveItineraryEdits() {
    if (this.data.itineraryEdit.saving) return
    const planId = this.data.plan?.plan_id || this.data.planId
    if (!planId) return
    const itinerary = this.data.plan?.itinerary
    if (!itinerary) return

    try {
      this.setData({ itineraryEdit: { ...this.data.itineraryEdit, saving: true } })
      wx.showLoading({ title: '保存中...', mask: true })
      const endpoint = API_ENDPOINTS.PLAN_UPDATE_ITINERARY.replace(':id', planId)
      const resp = await put(
        endpoint,
        { itinerary, base_version: this.data.itineraryEdit.baseVersion || 1 },
        { showLoading: false, showError: false }
      )
      wx.hideLoading()

      const latestItinerary = resp?.itinerary || itinerary
      const latestVersion = resp?.itinerary_version || (this.data.itineraryEdit.baseVersion + 1)
      this.applyItineraryUpdate(latestItinerary, latestVersion)
      wx.showToast({ title: '已保存', icon: 'success' })
    } catch (e) {
      wx.hideLoading()
      this.setData({ itineraryEdit: { ...this.data.itineraryEdit, saving: false } })
      if (e?.code === 'CAS_CONFLICT' && e?.data?.itinerary) {
        const latestVersion = Number(e.data.itinerary_version || 1)
        this.applyItineraryUpdate(e.data.itinerary, latestVersion)
        wx.showModal({
          title: '行程已更新',
          content: '检测到行程在你修改过程中已发生变化，已刷新到最新版本，请重新编辑后再保存。',
          showCancel: false
        })
        return
      }
      wx.showModal({ title: '保存失败', content: e?.message || '请稍后重试', showCancel: false })
    }
  },

  /**
   * 格式化数字
   */
  formatNumber(num) {
    if (typeof num !== 'number') return num
    return num.toLocaleString('zh-CN')
  },

  /**
   * 切换折叠面板
   */
  toggleSection(e) {
    const section = e.currentTarget.dataset.section
    const key = `sections.${section}`
    this.setData({
      [key]: !this.data.sections[section]
    })
  },

  /**
   * 提交通晒（将方案提交给团队审阅）
   */
  async handleSubmitReview() {
    const { plan } = this.data

    if (!plan || !plan.plan_id) {
      wx.showToast({ title: '方案信息错误', icon: 'none' })
      return
    }

    // 选择出发日期（未确定前不展示 day 具体日期）
    const today = new Date()
    const yyyy = today.getFullYear()
    const mm = String(today.getMonth() + 1).padStart(2, '0')
    const dd = String(today.getDate()).padStart(2, '0')
    const defaultDate = plan.start_date || `${yyyy}-${mm}-${dd}`
    this.setData({
      confirmDateDialog: { visible: true, startDate: defaultDate }
    })
  },

  handleConfirmDateChange(e) {
    this.setData({ 'confirmDateDialog.startDate': e.detail.value })
  },

  handleConfirmDateCancel() {
    this.setData({ confirmDateDialog: { ...this.data.confirmDateDialog, visible: false } })
  },

  async handleConfirmDateOk() {
    const { plan } = this.data
    const startDate = String(this.data.confirmDateDialog.startDate || '').trim()
    if (!startDate) {
      wx.showToast({ title: '请选择出发日期', icon: 'none' })
      return
    }

    try {
      wx.showLoading({ title: '提交中...', mask: true })
      const endpoint = API_ENDPOINTS.PLAN_SUBMIT_REVIEW.replace(':id', plan.plan_id)
      await put(endpoint, { start_date: startDate }, { showLoading: false, showError: false })

      wx.hideLoading()
      this.setData({
        confirmDateDialog: { ...this.data.confirmDateDialog, visible: false },
        'plan.status': PLAN_STATUS.REVIEWING,
        'plan.status_label': PLAN_STATUS_NAMES[PLAN_STATUS.REVIEWING],
        'plan.start_date': startDate
      })

      const { itineraryUi, linkedItineraryDraft } = this.buildItineraryUi(this.data.plan?.itinerary, startDate)
      this.setData({ itineraryUi, linkedItineraryDraft })

      wx.showToast({ title: '已提交通晒', icon: 'success', duration: 2000 })
    } catch (e) {
      wx.hideLoading()
      wx.showModal({ title: '提交失败', content: e?.message || '请稍后重试', showCancel: false })
    }
  },

  /**
   * 确认方案
   */
  async handleConfirmPlan() {
    const { plan } = this.data

    if (!plan || !plan.plan_id) {
      wx.showToast({ title: '方案信息错误', icon: 'none' })
      return
    }

    const confirmResult = await this.showConfirmModal(
      '确认此方案',
      '确认后方案将正式生效，是否继续？'
    )

    if (!confirmResult) return

    try {
      wx.showLoading({ title: '确认中...', mask: true })

      const endpoint = API_ENDPOINTS.PLAN_CONFIRM.replace(':id', plan.plan_id)
      await post(endpoint, {}, { showLoading: false })

      wx.hideLoading()

      this.setData({
        'plan.status': PLAN_STATUS.CONFIRMED,
        'plan.status_label': PLAN_STATUS_NAMES[PLAN_STATUS.CONFIRMED]
      })

      wx.showToast({
        title: '方案已确认',
        icon: 'success',
        duration: 2000
      })

      console.log('方案确认埋点:', {
        plan_id: plan.plan_id,
        timestamp: new Date().toISOString()
      })
    } catch (error) {
      wx.hideLoading()
      console.error('确认方案失败:', error)

      wx.showModal({
        title: '确认失败',
        content: error.message || '请稍后重试',
        showCancel: false
      })
    }
  },

  /**
   * 取消方案（撤回通晒，回到草稿状态）
   */
  async handleCancelPlan() {
    const { plan } = this.data

    if (!plan || !plan.plan_id) {
      wx.showToast({ title: '方案信息错误', icon: 'none' })
      return
    }

    const confirmResult = await this.showConfirmModal(
      '取消通晒',
      '取消后方案将回到草稿状态，是否继续？'
    )

    if (!confirmResult) return

    try {
      wx.showLoading({ title: '取消中...', mask: true })

      const endpoint = API_ENDPOINTS.PLAN_REVERT_REVIEW.replace(':id', plan.plan_id)
      await post(endpoint, {}, { showLoading: false })

      wx.hideLoading()

      this.setData({
        'plan.status': PLAN_STATUS.DRAFT,
        'plan.status_label': PLAN_STATUS_NAMES[PLAN_STATUS.DRAFT]
      })

      wx.showToast({
        title: '已取消通晒',
        icon: 'success',
        duration: 2000
      })

      console.log('方案取消埋点:', {
        plan_id: plan.plan_id,
        timestamp: new Date().toISOString()
      })
    } catch (error) {
      wx.hideLoading()
      console.error('取消方案失败:', error)

      wx.showModal({
        title: '取消失败',
        content: error.message || '请稍后重试',
        showCancel: false
      })
    }
  },

  /**
   * 归档方案
   */
  async handleArchivePlan() {
    const { plan } = this.data

    if (!plan || !plan.plan_id) {
      wx.showToast({ title: '方案信息错误', icon: 'none' })
      return
    }

    const confirmResult = await this.showConfirmModal(
      '归档此方案',
      '归档后方案将移至历史记录，是否继续？'
    )

    if (!confirmResult) return

    try {
      wx.showLoading({ title: '归档中...', mask: true })

      const endpoint = API_ENDPOINTS.PLAN_ARCHIVE.replace(':id', plan.plan_id)
      await post(endpoint, {}, { showLoading: false })

      wx.hideLoading()

      this.setData({
        'plan.status': PLAN_STATUS.ARCHIVED,
        'plan.status_label': PLAN_STATUS_NAMES[PLAN_STATUS.ARCHIVED]
      })

      wx.showToast({
        title: '已归档',
        icon: 'success',
        duration: 2000
      })

      console.log('方案归档埋点:', {
        plan_id: plan.plan_id,
        timestamp: new Date().toISOString()
      })

      // 归档后返回列表页
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    } catch (error) {
      wx.hideLoading()
      console.error('归档方案失败:', error)

      wx.showModal({
        title: '归档失败',
        content: error.message || '请稍后重试',
        showCancel: false
      })
    }
  },

  /**
   * 显示确认对话框
   */
  showConfirmModal(title, content) {
    return new Promise((resolve) => {
      wx.showModal({
        title,
        content,
        success: (res) => {
          resolve(res.confirm)
        },
        fail: () => {
          resolve(false)
        }
      })
    })
  },

  /**
   * 分享
   */
  onShareAppMessage() {
    const { plan } = this.data

    if (!plan) {
      return {
        title: '团建方案',
        path: '/pages/index/index',
        imageUrl: ''
      }
    }

    // 安全处理：确保所有字段都是字符串，避免编码问题
    const title = String(plan.plan_name || '团建方案')
    const subtitle = plan.budget_per_person ? String(plan.budget_per_person) : ''
    const shareTitle = subtitle ? `${title} - ${subtitle}` : title

    return {
      title: shareTitle,
      path: `/pages/detail/detail?planId=${plan.plan_id || ''}`,
      imageUrl: ''
    }
  }
})
