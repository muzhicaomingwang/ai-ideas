// pages/detail/detail.js
import { put } from '../../utils/request.js'
import { API_ENDPOINTS, PLAN_STATUS, PLAN_STATUS_NAMES } from '../../utils/config.js'
import { formatMoney, formatPerPerson, formatDuration, calculateDays, makePhoneCall, copyToClipboard } from '../../utils/util.js'

Page({
  data: {
    plan: null,
    sections: {
      itinerary: true,   // 默认展开行程
      budget: false,
      suppliers: false
    }
  },

  onLoad(options) {
    console.log('方案详情页加载', options)

    // 从 URL 参数获取方案数据
    if (options.plan) {
      try {
        const plan = JSON.parse(decodeURIComponent(options.plan))
        this.processPlanData(plan)
      } catch (error) {
        console.error('解析方案数据失败:', error)
        this.showErrorAndBack('无法加载方案数据')
      }
    } else if (options.planId) {
      // 如果只有 planId，从服务器获取
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
                 (plan.start_date && plan.end_date ?
                  calculateDays(plan.start_date, plan.end_date) : 2)

    // 处理展示数据
    const processedPlan = {
      ...plan,
      status: plan.status || PLAN_STATUS.DRAFT,
      status_label: PLAN_STATUS_NAMES[plan.status] || PLAN_STATUS_NAMES[PLAN_STATUS.DRAFT],
      budget_total: this.formatNumber(plan.budget_total),
      budget_per_person: formatPerPerson(plan.budget_total, plan.people_count),
      duration: formatDuration(days),

      // 处理行程数据
      itinerary: this.processItinerary(plan.itinerary),

      // 处理预算明细
      budget_breakdown: this.processBudget(plan.budget_breakdown),

      // 处理供应商信息
      suppliers: this.processSuppliers(plan.suppliers)
    }

    this.setData({ plan: processedPlan })
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
   * 处理预算数据
   */
  processBudget(budget) {
    if (!budget || !budget.categories) {
      return {
        categories: [],
        total: 0
      }
    }

    return {
      categories: budget.categories.map(cat => ({
        ...cat,
        subtotal: this.formatNumber(cat.subtotal),
        items: cat.items.map(item => ({
          ...item,
          total: this.formatNumber(item.total)
        }))
      })),
      total: this.formatNumber(budget.total)
    }
  },

  /**
   * 处理供应商数据
   */
  processSuppliers(suppliers) {
    if (!suppliers || !Array.isArray(suppliers)) {
      return []
    }

    const categoryLabels = {
      venue: '场地',
      activity: '活动',
      dining: '餐饮',
      accommodation: '住宿',
      transportation: '交通'
    }

    return suppliers.map(supplier => ({
      ...supplier,
      category_label: categoryLabels[supplier.category] || supplier.category,
      price: supplier.price_range_min && supplier.price_range_max ?
             `¥${supplier.price_range_min}-${supplier.price_range_max}` :
             supplier.price || ''
    }))
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
   * 拨打电话
   */
  handleCallPhone(e) {
    const phone = e.currentTarget.dataset.phone
    const supplierId = e.currentTarget.dataset.supplierId

    if (!phone) {
      wx.showToast({ title: '无联系电话', icon: 'none' })
      return
    }

    makePhoneCall(phone)

    // 上报埋点
    this.trackSupplierContact(supplierId, 'phone')
  },

  /**
   * 复制微信号
   */
  handleCopyWechat(e) {
    const wechat = e.currentTarget.dataset.wechat
    const supplierId = e.currentTarget.dataset.supplierId

    if (!wechat) {
      wx.showToast({ title: '无微信号', icon: 'none' })
      return
    }

    copyToClipboard(wechat, '微信号已复制')

    // 上报埋点
    this.trackSupplierContact(supplierId, 'wechat')
  },

  /**
   * 上报供应商联系埋点
   */
  trackSupplierContact(supplierId, method) {
    // TODO: 调用埋点 API
    console.log('供应商联系埋点:', {
      plan_id: this.data.plan?.plan_id,
      supplier_id: supplierId,
      contact_method: method,
      timestamp: new Date().toISOString()
    })
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

    // 二次确认
    const confirmResult = await this.showConfirmModal(
      '确认此方案',
      '确认后方案将保存到"我的方案"中'
    )

    if (!confirmResult) return

    try {
      wx.showLoading({ title: '确认中...', mask: true })

      // 调用确认 API
      const endpoint = API_ENDPOINTS.PLAN_CONFIRM.replace(':id', plan.plan_id)
      await put(endpoint, {}, { showLoading: false })

      wx.hideLoading()

      // 更新状态
      this.setData({
        'plan.status': PLAN_STATUS.CONFIRMED,
        'plan.status_label': PLAN_STATUS_NAMES[PLAN_STATUS.CONFIRMED]
      })

      // 成功提示
      wx.showToast({
        title: '方案已确认',
        icon: 'success',
        duration: 2000
      })

      // 上报埋点
      console.log('方案确认埋点:', {
        plan_id: plan.plan_id,
        plan_type: plan.plan_type,
        budget_total: plan.budget_total,
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
   * 显示确认对话框
   */
  showConfirmModal(title, content) {
    return new Promise((resolve) => {
      wx.showModal({
        title: title,
        content: content,
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
