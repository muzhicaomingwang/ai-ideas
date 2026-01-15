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
    selectedMapType: '', // 当前选中的地图类型：'intercity' 或 'regional'
    availableMapTypes: [], // 当前day可用的地图类型列表
    allMaps: [], // 当前day的所有地图数据
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
      duration_days: plan.duration_days || days,
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

      // 新逻辑：处理双Map数据
      const maps = data?.maps || []

      // 【关键修复】：预处理allMaps，限制数据量，避免page.data过大导致微信序列化失败
      const processedMaps = maps.map(m => ({
        map_id: m.map_id,
        map_type: m.map_type,
        display_name: m.display_name,
        description: m.description,
        static_map_url: m.static_map_url,
        zoom_level: m.zoom_level,
        center: m.center,
        summary: m.summary,
        // 限制数组大小
        markers: (m.markers || []).slice(0, 20),  // markers通常<20个
        polyline: (m.polyline || []).slice(0, 5).map(line => {
          // 【关键】：限制每条polyline的points数组大小
          const points = (line.points || []).slice(0, 200).map(p => ({
            latitude: Number(p.latitude || 0),
            longitude: Number(p.longitude || 0)
          }))

          return {
            points,
            color: String(line.color || '#1890ff'),
            width: Number(line.width || 6),
            borderColor: String(line.borderColor || '#ffffff'),
            borderWidth: Number(line.borderWidth || 2),
            dottedLine: Boolean(line.dottedLine)
          }
        }),
        include_points: (m.include_points || []).slice(0, 200),  // 限制200个点
        segments: (m.segments || []).slice(0, 10).map(seg => {
          // 严格字段过滤，不使用spread
          const coordinates = (seg.coordinates || []).slice(0, 100).map(coord => ({
            latitude: Number(coord.latitude || 0),
            longitude: Number(coord.longitude || 0)
          }))

          return {
            distance: Number(seg.distance || 0),
            duration: Number(seg.duration || 0),
            mode: String(seg.mode || 'walking'),
            coordinates
          }
        })
      }))

      // 提取可用的地图类型
      const availableTypes = processedMaps.map(m => ({
        id: m.map_id,
        name: m.display_name || (m.map_id === 'intercity' ? '跨城路线' : '本地路线')
      }))

      // 默认选择第一个地图类型
      const defaultMapType = availableTypes.length > 0 ? availableTypes[0].id : ''

      // 设置当前显示的地图（使用预处理后的数据）
      this.setData({
        allMaps: processedMaps,  // 使用预处理后的数据，而非原始数据
        availableMapTypes: availableTypes,
        selectedMapType: defaultMapType
      })

      // 显示选中的地图
      this.displaySelectedMap()

    } catch (e) {
      console.error('获取路线失败:', e)
      this.setData({
        allMaps: [],
        availableMapTypes: [],
        selectedMapType: '',
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
   * 显示选中的地图
   */
  displaySelectedMap() {
    const { allMaps, selectedMapType } = this.data

    // 找到选中的地图
    const selectedMap = allMaps.find(m => m.map_id === selectedMapType)

    if (!selectedMap) {
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
      return
    }

    // 处理markers：只提取微信地图组件需要的字段
    const markers = (selectedMap.markers || []).map(marker => {
      const m = {
        id: marker.id,
        latitude: marker.latitude,
        longitude: marker.longitude,
        width: marker.width || 32,
        height: marker.height || 32
      }

      // 添加可选字段
      if (marker.title) m.title = String(marker.title)
      if (marker.label) {
        m.label = {
          content: String(marker.label.content || ''),
          color: String(marker.label.color || '#000000'),
          fontSize: Number(marker.label.fontSize || 14),
          bgColor: String(marker.label.bgColor || '#ffffff'),
          borderRadius: Number(marker.label.borderRadius || 0),
          padding: Number(marker.label.padding || 0)
        }
      }

      return m
    })

    // 处理polyline：只提取微信地图组件需要的字段
    const polyline = (selectedMap.polyline || []).map(line => {
      const points = (line.points || []).map(p => ({
        latitude: Number(p.latitude),
        longitude: Number(p.longitude)
      }))

      return {
        points,
        color: String(line.color || '#1890ff'),
        width: Number(line.width || 6),
        borderColor: String(line.borderColor || '#ffffff'),
        borderWidth: Number(line.borderWidth || 2),
        dottedLine: Boolean(line.dottedLine)
      }
    })

    // 计算地图比例尺
    const scale = this.calculateMapScale(selectedMap.include_points || [])

    // 限制include_points数量，避免data过大导致微信上报失败
    // 微信小程序地图组件通常只需要100-200个点就能绘制流畅的路线
    const includePoints = (selectedMap.include_points || []).slice(0, 200)

    // 限制segments数量和坐标点数量
    const segments = (selectedMap.segments || []).slice(0, 10).map(seg => ({
      ...seg,
      coordinates: (seg.coordinates || []).slice(0, 100)
    }))

    this.setData({
      route: {
        mapType: selectedMap.map_type || 'interactive',
        staticMapUrl: selectedMap.static_map_url || '',
        markers,
        polyline,
        include_points: includePoints,
        segments,
        unresolved: []
      },
      mapScale: scale
    })
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
   * 切换地图类型（跨城/本地）
   */
  handleSelectMapType(e) {
    const mapType = e.currentTarget.dataset.type
    if (!mapType || mapType === this.data.selectedMapType) return

    this.setData({ selectedMapType: mapType })
    this.displaySelectedMap()
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
