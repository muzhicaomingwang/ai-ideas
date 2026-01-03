// pages/myplans/myplans.js
import { get, del } from '../../utils/request.js'
import { API_ENDPOINTS, PLAN_STATUS_NAMES } from '../../utils/config.js'
import { formatRelativeTime, formatDuration, calculateDays } from '../../utils/util.js'

const app = getApp()

Page({
  data: {
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
    const { page, pageSize, plans, loadingMore } = this.data

    // 如果已经在加载，直接返回
    if (loadingMore) return

    try {
      if (page > 1) {
        this.setData({ loadingMore: true })
      }

      // 调用 API
      const result = await get(API_ENDPOINTS.PLAN_LIST, {
        page: page,
        pageSize: pageSize
      })

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
                   (plan.start_date && plan.end_date ?
                    calculateDays(plan.start_date, plan.end_date) : 2)

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

    if (!planId) return

    wx.navigateTo({
      url: `/pages/detail/detail?planId=${planId}`
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
      // 左滑
      if (deltaX < -10) {
        const translateX = Math.max(deltaX * 0.5, -160) // 限制最大左滑距离
        this.setData({
          [`plans[${index}].translateX`]: translateX
        })
      }
      // 右滑（恢复）
      else if (deltaX > 10) {
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
    const currentTranslateX = this.data.plans[index].translateX || 0

    // 如果左滑超过一半，显示删除按钮
    if (currentTranslateX < -80) {
      this.setData({
        [`plans[${index}].translateX`]: -160
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
   * 显示确认对话框
   */
  showConfirmModal(title, content) {
    return new Promise((resolve) => {
      wx.showModal({
        title: title,
        content: content,
        confirmColor: '#f5222d',
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
