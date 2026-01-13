// pages/detail/detail.js
import { get, put, post } from '../../utils/request.js'
import { API_ENDPOINTS, PLAN_STATUS, PLAN_STATUS_NAMES } from '../../utils/config.js'
import { formatMoney, formatPerPerson, formatDuration, calculateDays } from '../../utils/util.js'

Page({
  data: {
    plan: null,
    planId: '',
    sections: {
      itinerary: true, // 默认展开行程
      map: false
    },
    selectedDay: 1,
    routeLoading: false,
    mapScale: 12, // 默认地图比例尺（动态计算）
    route: {
      markers: [],
      polyline: [],
      include_points: [],
      unresolved: []
    },
  },

  onLoad(options) {
    console.log('方案详情页加载', options)

    // 从 URL 参数获取方案数据
    if (options.plan) {
      try {
        const plan = JSON.parse(decodeURIComponent(options.plan))
        this.setData({ planId: plan?.plan_id || '' })
        this.processPlanData(plan)
      } catch (error) {
        console.error('解析方案数据失败:', error)
        this.showErrorAndBack('无法加载方案数据')
      }
    } else if (options.planId) {
      // 如果只有 planId，从服务器获取
      this.setData({ planId: options.planId })
      this.fetchPlanDetail(options.planId)
    } else {
      this.showErrorAndBack('缺少方案信息')
    }
  },

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

    // 计算天数
    const days = plan.duration_days ||
                 (plan.start_date && plan.end_date
                   ? calculateDays(plan.start_date, plan.end_date)
                   : 2)

    // 处理亮点（后端返回 highlights 数组，前端显示为单个字符串）
    let highlight = ''
    if (Array.isArray(plan.highlights) && plan.highlights.length > 0) {
      highlight = plan.highlights.join('、')
    } else if (typeof plan.highlights === 'string') {
      highlight = plan.highlights
    }

    // 处理展示数据
    const processedPlan = {
      ...plan,
      status: plan.status || PLAN_STATUS.DRAFT,
      status_label: PLAN_STATUS_NAMES[plan.status] || PLAN_STATUS_NAMES[PLAN_STATUS.DRAFT],
      itinerary_version: plan.itinerary_version || 1,
      budget_total: this.formatNumber(plan.budget_total),
      // 优先使用后端返回的人均费用，否则计算
      budget_per_person: plan.budget_per_person
        ? formatMoney(plan.budget_per_person) + ' 人均'
        : formatPerPerson(plan.budget_total, plan.people_count),
      duration: formatDuration(days),
      highlight,

      // 处理行程数据
      itinerary: this.processItinerary(plan.itinerary),
    }

    this.setData({ plan: processedPlan })
    this.initRouteAfterPlanLoaded()
  },

  initRouteAfterPlanLoaded() {
    const days = this.data.plan?.itinerary?.days || []
    const firstDay = days?.[0]?.day || 1
    this.setData({ selectedDay: firstDay })
    this.fetchRoute(firstDay)
  },

  async fetchRoute(day) {
    const planId = this.data.plan?.plan_id || this.data.planId
    if (!planId) return

    try {
      this.setData({ routeLoading: true })
      const endpoint = API_ENDPOINTS.PLAN_ROUTE.replace(':id', planId) + `?day=${encodeURIComponent(day)}`
      const data = await get(endpoint)

      // Extract map type and static map URL from backend response
      const mapType = data?.mapType || 'interactive'
      const staticMapUrl = data?.staticMapUrl || ''

      // Fix: Ensure markers have width and height to avoid rendering errors
      if (data && data.markers) {
        data.markers = data.markers.map(marker => ({
          ...marker,
          width: marker.width || 32,
          height: marker.height || 32
        }))
      }

      // Enhance polyline with better styling for visibility
      if (data && data.polyline) {
        data.polyline = data.polyline.map(line => ({
          ...line,
          color: line.color || '#1890ff',        // Primary blue color
          width: line.width || 6,                // Thicker line for visibility
          borderColor: line.borderColor || '#ffffff',  // White border for contrast
          borderWidth: line.borderWidth || 2,    // Border width
          dottedLine: false                      // Solid line
        }))
      }

      // Calculate dynamic map scale based on route bounds
      const scale = this.calculateMapScale(data?.include_points || [])

      this.setData({
        route: {
          ...(data || {}),
          mapType,
          staticMapUrl,
          markers: data?.markers || [],
          polyline: data?.polyline || [],
          include_points: data?.include_points || [],
          unresolved: data?.unresolved || []
        },
        mapScale: scale
      })
    } catch (e) {
      console.error('获取路线失败:', e)
      this.setData({
        route: {
          mapType: 'interactive',
          staticMapUrl: '',
          markers: [],
          polyline: [],
          include_points: [],
          unresolved: []
        }
      })
    } finally {
      this.setData({ routeLoading: false })
    }
  },

  /**
   * Calculate appropriate map scale based on route bounds
   * @param {Array} includePoints - Array of {latitude, longitude} objects
   * @returns {Number} - Map scale value (3-20, larger = more zoomed in)
   */
  calculateMapScale(includePoints) {
    if (!includePoints || includePoints.length === 0) {
      return 12 // Default scale
    }

    // Find bounding box
    let minLat = includePoints[0].latitude
    let maxLat = includePoints[0].latitude
    let minLng = includePoints[0].longitude
    let maxLng = includePoints[0].longitude

    includePoints.forEach(point => {
      minLat = Math.min(minLat, point.latitude)
      maxLat = Math.max(maxLat, point.latitude)
      minLng = Math.min(minLng, point.longitude)
      maxLng = Math.max(maxLng, point.longitude)
    })

    // Calculate geographic span
    const latSpan = maxLat - minLat
    const lngSpan = maxLng - minLng
    const maxSpan = Math.max(latSpan, lngSpan)

    // Map span to scale (empirical mapping for WeChat map)
    // Smaller span = larger scale (more zoomed in)
    // Scale ranges from 3 (zoomed out) to 20 (zoomed in)
    if (maxSpan > 1.0) return 5   // Very large area (>100km)
    if (maxSpan > 0.5) return 8   // Large area (50-100km)
    if (maxSpan > 0.1) return 11  // Medium area (10-50km)
    if (maxSpan > 0.05) return 13 // Small area (5-10km)
    if (maxSpan > 0.01) return 15 // Very small area (1-5km)
    return 17                     // Tiny area (<1km)
  },

  handleSelectDay(e) {
    const day = Number(e.currentTarget.dataset.day)
    if (!day || day === this.data.selectedDay) return
    this.setData({ selectedDay: day })
    this.fetchRoute(day)
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
    this.setData({
      'plan.itinerary': processed,
      'plan.itinerary_version': itineraryVersion || (this.data.plan?.itinerary_version || 1) + 1
    })
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
        items: day.items || []
      }))
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

    // 二次确认
    const confirmResult = await this.showConfirmModal(
      '通晒此方案',
      '提交后将进入通晒流程，团队成员可查看此方案'
    )

    if (!confirmResult) return

    try {
      wx.showLoading({ title: '提交中...', mask: true })

      // 调用通晒 API
      const endpoint = API_ENDPOINTS.PLAN_SUBMIT_REVIEW.replace(':id', plan.plan_id)
      await put(endpoint, {}, { showLoading: false })

      wx.hideLoading()

      // 更新状态为"通晒中"
      this.setData({
        'plan.status': PLAN_STATUS.REVIEWING,
        'plan.status_label': PLAN_STATUS_NAMES[PLAN_STATUS.REVIEWING]
      })

      // 成功提示
      wx.showToast({
        title: '已提交通晒',
        icon: 'success',
        duration: 2000
      })

      // 上报埋点
      console.log('方案通晒埋点:', {
        plan_id: plan.plan_id,
        plan_type: plan.plan_type,
        budget_total: plan.budget_total,
        timestamp: new Date().toISOString()
      })
    } catch (error) {
      wx.hideLoading()
      console.error('提交通晒失败:', error)

      wx.showModal({
        title: '提交失败',
        content: error.message || '请稍后重试',
        showCancel: false
      })
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

    return {
      title: `${plan?.plan_name || '团建方案'} - ${plan?.budget_per_person || ''}`,
      path: `/pages/detail/detail?planId=${plan?.plan_id}`,
      imageUrl: '' // TODO: 添加分享图片
    }
  }
})
