// pages/myplans/myplans.js
import { get, post, del } from '../../utils/request.js'
import { API_ENDPOINTS, PLAN_STATUS_NAMES } from '../../utils/config.js'
import { formatRelativeTime, formatDuration, calculateDays } from '../../utils/util.js'

const app = getApp()

Page({
  data: {
    // Tab 筛选相关
    tabs: [
      { key: '', name: '全部' },
      { key: 'draft', name: '制定完成' },
      { key: 'reviewing', name: '通晒中' },
      { key: 'confirmed', name: '已确认' },
      { key: 'generating', name: '生成中' }
    ],
    currentTab: 'draft', // 默认选中"制定完成"

    // 方案列表
    plans: [],
    loading: true,
    loadingMore: false,
    hasMore: true,
    page: 1,
    pageSize: 10,

    // 左滑相关
    touchStartX: 0,
    touchStartY: 0
  },

  onLoad(options) {
    console.log('我的方案页加载', options)
  },

  onShow() {
    // 每次显示时重新加载
    this.resetAndLoad()
  },

  /**
   * Tab 切换
   */
  handleTabChange(e) {
    const key = e.currentTarget.dataset.key
    if (key === this.data.currentTab) return

    this.setData({
      currentTab: key,
      plans: [],
      page: 1,
      hasMore: true,
      loading: true
    })
    this.loadPlans()
  },

  /**
   * 重置并加载
   */
  resetAndLoad() {
    this.setData({
      plans: [],
      page: 1,
      hasMore: true,
      loading: true
    })
    this.loadPlans()
  },

  /**
   * 加载方案列表
   */
  async loadPlans() {
    const { page, pageSize, plans, loadingMore, currentTab } = this.data

    // 如果已经在加载，直接返回
    if (loadingMore) return

    try {
      if (page > 1) {
        this.setData({ loadingMore: true })
      }

      // 构建请求参数
      const params = {
        page,
        pageSize
      }
      // 如果有 Tab 筛选，添加 status 参数
      if (currentTab) {
        params.status = currentTab
      }

      // 调用 API
      const result = await get(API_ENDPOINTS.PLAN_LIST, params)

      // 处理数据
      const newPlans = this.processPlans(result.plans || [])

      this.setData({
        plans: [...plans, ...newPlans],
        hasMore: result.hasMore !== false,
        loading: false,
        loadingMore: false
      })
    } catch (error) {
      console.error('加载方案列表失败:', error)

      this.setData({
        loading: false,
        loadingMore: false
      })

      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }
  },

  /**
   * 处理方案数据
   */
  processPlans(plans) {
    return plans.map(plan => {
      const days = plan.duration_days ||
                   (plan.start_date && plan.end_date
                     ? calculateDays(plan.start_date, plan.end_date)
                     : 2)

      return {
        ...plan,
        status_label: PLAN_STATUS_NAMES[plan.status] || '草稿',
        budget_total: this.formatNumber(plan.budget_total),
        duration: formatDuration(days),
        relative_time: formatRelativeTime(plan.created_at || plan.generated_at),
        translateX: 0 // 左滑位移
      }
    })
  },

  /**
   * 格式化数字
   */
  formatNumber(num) {
    if (typeof num !== 'number') return num
    return num.toLocaleString('zh-CN')
  },

  /**
   * 查看方案详情
   */
  handleViewPlan(e) {
    const planId = e.currentTarget.dataset.planId
    const index = e.currentTarget.dataset.index
    const plan = this.data.plans[index]

    // 生成中/失败的方案不能查看详情
    if (plan && (plan.status === 'generating' || plan.status === 'failed')) {
      wx.showToast({
        title: plan.status === 'generating' ? '方案生成中，请稍候' : '方案生成失败',
        icon: 'none'
      })
      return
    }

    if (!planId) return

    wx.navigateTo({
      url: `/pages/detail/detail?planId=${planId}`
    })
  },

  /**
   * 刷新单个方案状态
   */
  async handleRefreshPlan(e) {
    const planId = e.currentTarget.dataset.planId
    const index = e.currentTarget.dataset.index

    if (!planId || index === undefined) return

    const plan = this.data.plans[index]
    if (plan.refreshing) return // 防止重复刷新

    try {
      // 设置刷新状态
      this.setData({
        [`plans[${index}].refreshing`]: true
      })

      // 调用 API 获取最新状态
      const endpoint = API_ENDPOINTS.PLAN_DETAIL.replace(':id', planId)
      const result = await get(endpoint)

      // 处理返回的数据
      const updatedPlan = this.processPlans([result])[0]
      updatedPlan.refreshing = false
      updatedPlan.translateX = 0

      // 更新列表中的方案
      this.setData({
        [`plans[${index}]`]: updatedPlan
      })

      // 状态变化提示
      if (result.status !== 'generating') {
        wx.showToast({
          title: '方案已生成完成',
          icon: 'success'
        })
      } else {
        wx.showToast({
          title: '仍在生成中',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('刷新方案状态失败:', error)

      this.setData({
        [`plans[${index}].refreshing`]: false
      })

      wx.showToast({
        title: '刷新失败',
        icon: 'none'
      })
    }
  },

  /**
   * 重新生成失败的方案
   */
  handleRetryGenerate(e) {
    const planId = e.currentTarget.dataset.planId
    const index = e.currentTarget.dataset.index

    if (!planId || index === undefined) return

    const plan = this.data.plans[index]

    // 跳转到首页并预填请求参数
    wx.switchTab({
      url: '/pages/index/index',
      success: () => {
        // 如果有原始请求参数，可以存储到本地供首页读取
        if (plan.people_count || plan.departure_city) {
          wx.setStorageSync('retryRequest', {
            people_count: plan.people_count,
            departure_city: plan.departure_city,
            budget_max: plan.budget_total,
            start_date: plan.start_date,
            end_date: plan.end_date
          })
        }
      }
    })
  },

  /**
   * 去生成方案
   */
  handleGoCreate() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  },

  /**
   * 触摸开始
   */
  handleTouchStart(e) {
    const touch = e.touches[0]
    this.setData({
      touchStartX: touch.clientX,
      touchStartY: touch.clientY
    })
  },

  /**
   * 触摸移动
   */
  handleTouchMove(e) {
    const touch = e.touches[0]
    const { touchStartX, touchStartY } = this.data
    const index = e.currentTarget.dataset.index

    const deltaX = touch.clientX - touchStartX
    const deltaY = touch.clientY - touchStartY

    // 判断是否为横向滑动
    if (Math.abs(deltaX) > Math.abs(deltaY)) {
      const maxSlide = -120 // 按钮宽度

      // 左滑
      if (deltaX < -10) {
        const translateX = Math.max(deltaX * 0.5, maxSlide)
        this.setData({
          [`plans[${index}].translateX`]: translateX
        })
      } else if (deltaX > 10) {
      // 右滑（恢复）
        this.setData({
          [`plans[${index}].translateX`]: 0
        })
      }
    }
  },

  /**
   * 触摸结束
   */
  handleTouchEnd(e) {
    const index = e.currentTarget.dataset.index
    const plan = this.data.plans[index]
    const currentTranslateX = plan.translateX || 0
    const targetSlide = -120

    // 如果左滑超过一半，显示操作按钮
    if (currentTranslateX < targetSlide / 2) {
      this.setData({
        [`plans[${index}].translateX`]: targetSlide
      })
    } else {
      // 否则恢复
      this.setData({
        [`plans[${index}].translateX`]: 0
      })
    }
  },

  /**
   * 删除方案
   */
  async handleDelete(e) {
    const planId = e.currentTarget.dataset.planId
    const index = e.currentTarget.dataset.index

    if (!planId) return

    // 二次确认
    const confirmResult = await this.showConfirmModal(
      '删除方案',
      '确定要删除此方案吗？'
    )

    if (!confirmResult) {
      // 恢复卡片位置
      this.setData({
        [`plans[${index}].translateX`]: 0
      })
      return
    }

    try {
      wx.showLoading({ title: '删除中...', mask: true })

      // 调用删除 API
      const endpoint = API_ENDPOINTS.PLAN_DETAIL.replace(':id', planId)
      await del(endpoint)

      wx.hideLoading()

      // 从列表中移除
      const plans = this.data.plans.filter((_, i) => i !== index)
      this.setData({ plans })

      wx.showToast({
        title: '删除成功',
        icon: 'success'
      })
    } catch (error) {
      wx.hideLoading()
      console.error('删除方案失败:', error)

      // 恢复卡片位置
      this.setData({
        [`plans[${index}].translateX`]: 0
      })

      wx.showModal({
        title: '删除失败',
        content: error.message || '请稍后重试',
        showCancel: false
      })
    }
  },

  /**
   * 归档方案
   */
  async handleArchive(e) {
    const planId = e.currentTarget.dataset.planId
    const index = e.currentTarget.dataset.index

    if (!planId) return

    // 二次确认
    const confirmResult = await this.showConfirmModal(
      '归档方案',
      '归档后方案将不在列表显示，确定归档吗？',
      '#1890ff'
    )

    if (!confirmResult) {
      // 恢复卡片位置
      this.setData({
        [`plans[${index}].translateX`]: 0
      })
      return
    }

    try {
      wx.showLoading({ title: '归档中...', mask: true })

      // 调用归档 API
      const endpoint = API_ENDPOINTS.PLAN_DETAIL.replace(':id', planId) + '/archive'
      await post(endpoint)

      wx.hideLoading()

      // 从列表中移除
      const plans = this.data.plans.filter((_, i) => i !== index)
      this.setData({ plans })

      wx.showToast({
        title: '归档成功',
        icon: 'success'
      })
    } catch (error) {
      wx.hideLoading()
      console.error('归档方案失败:', error)

      // 恢复卡片位置
      this.setData({
        [`plans[${index}].translateX`]: 0
      })

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
  showConfirmModal(title, content, confirmColor = '#f5222d') {
    return new Promise((resolve) => {
      wx.showModal({
        title,
        content,
        confirmColor,
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
   * 下拉刷新
   */
  onPullDownRefresh() {
    this.resetAndLoad()
    setTimeout(() => {
      wx.stopPullDownRefresh()
    }, 1000)
  },

  /**
   * 触底加载更多
   */
  onReachBottom() {
    const { hasMore, loadingMore } = this.data

    if (!hasMore || loadingMore) return

    this.setData({
      page: this.data.page + 1
    })

    this.loadPlans()
  }
})
