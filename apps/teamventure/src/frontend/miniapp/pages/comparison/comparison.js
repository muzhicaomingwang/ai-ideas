// pages/comparison/comparison.js
import { PLAN_TYPE_NAMES } from '../../utils/config.js'
import { formatMoney, formatPerPerson } from '../../utils/util.js'

Page({
  data: {
    plans: [],
    selectedPlanId: '',
    comparisonExpanded: false
  },

  onLoad(options) {
    console.log('方案对比页加载', options)

    // 从 URL 参数获取方案数据
    if (options.plans) {
      try {
        const plans = JSON.parse(decodeURIComponent(options.plans))
        this.processPlanData(plans)
      } catch (error) {
        console.error('解析方案数据失败:', error)
        wx.showModal({
          title: '数据错误',
          content: '无法加载方案数据',
          showCancel: false,
          success: () => {
            wx.navigateBack()
          }
        })
      }
    } else {
      // 如果没有数据，返回上一页
      wx.showToast({
        title: '无方案数据',
        icon: 'none'
      })
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    }
  },

  /**
   * 处理方案数据
   */
  processPlanData(plans) {
    if (!plans || plans.length === 0) {
      wx.showToast({
        title: '暂无方案',
        icon: 'none'
      })
      return
    }

    // 处理每个方案的展示数据
    const processedPlans = plans.map((plan, index) => {
      return {
        ...plan,
        plan_type_label: PLAN_TYPE_NAMES[plan.plan_type] || '标准型',
        budget_total: this.formatNumber(plan.budget_total),
        budget_per_person: formatPerPerson(plan.budget_total, plan.people_count),
        accommodation_label: this.getAccommodationLabel(plan),
        activity_count: this.getActivityCount(plan),
        dining_label: this.getDiningLabel(plan),
        suitable_for: plan.suitable_for || ['性价比优先'],
        recommended: this.isRecommended(plan, index)
      }
    })

    // 默认选中推荐方案
    const recommendedPlan = processedPlans.find(p => p.recommended)
    const defaultSelectedId = recommendedPlan ? recommendedPlan.plan_id : processedPlans[0].plan_id

    this.setData({
      plans: processedPlans,
      selectedPlanId: defaultSelectedId
    })
  },

  /**
   * 判断是否为推荐方案
   */
  isRecommended(plan, index) {
    // 默认推荐中间方案（平衡型）
    return plan.plan_type === 'standard' || index === 1
  },

  /**
   * 获取住宿标签
   */
  getAccommodationLabel(plan) {
    const level = plan.preferences?.accommodation_level || plan.accommodation_level
    const labels = {
      budget: '农家乐',
      standard: '民宿',
      premium: '度假酒店'
    }
    return labels[level] || '标准住宿'
  },

  /**
   * 获取活动数量
   */
  getActivityCount(plan) {
    if (plan.itinerary && plan.itinerary.days) {
      let count = 0
      plan.itinerary.days.forEach(day => {
        if (day.items) {
          // 统计活动类型的行程项
          count += day.items.filter(item =>
            item.activity && item.activity.includes('活动')
          ).length
        }
      })
      return count || 2
    }
    // 默认根据方案类型返回
    return plan.plan_type === 'budget' ? 2 : plan.plan_type === 'premium' ? 4 : 3
  },

  /**
   * 获取餐饮标签
   */
  getDiningLabel(plan) {
    const style = plan.preferences?.dining_style?.[0] || plan.dining_style
    const labels = {
      local: '农家菜',
      bbq: '烧烤',
      hotpot: '火锅',
      western: '西餐'
    }

    if (Array.isArray(style)) {
      return labels[style[0]] || '特色餐'
    }

    return labels[style] || plan.plan_type === 'budget'
      ? '农家菜'
      : plan.plan_type === 'premium' ? '精品餐厅' : '特色餐'
  },

  /**
   * 格式化数字
   */
  formatNumber(num) {
    if (typeof num !== 'number') return num
    return num.toLocaleString('zh-CN')
  },

  /**
   * 选择方案
   */
  handleSelectPlan(e) {
    const planId = e.currentTarget.dataset.planId
    this.setData({
      selectedPlanId: planId
    })
  },

  /**
   * 查看详情
   */
  handleViewDetail(e) {
    const planId = e.currentTarget.dataset.planId
    const plan = this.data.plans.find(p => p.plan_id === planId)

    if (!plan) return

    // 跳转到详情页
    wx.navigateTo({
      url: `/pages/detail/detail?plan=${encodeURIComponent(JSON.stringify(plan))}`
    })
  },

  /**
   * 切换对比表格展开/折叠
   */
  toggleComparison() {
    this.setData({
      comparisonExpanded: !this.data.comparisonExpanded
    })
  },

  /**
   * 确认选择
   */
  handleConfirmSelection() {
    const { selectedPlanId, plans } = this.data

    if (!selectedPlanId) {
      wx.showToast({
        title: '请先选择方案',
        icon: 'none'
      })
      return
    }

    const selectedPlan = plans.find(p => p.plan_id === selectedPlanId)

    if (!selectedPlan) return

    // 跳转到详情页
    wx.navigateTo({
      url: `/pages/detail/detail?plan=${encodeURIComponent(JSON.stringify(selectedPlan))}`
    })
  },

  /**
   * 重新生成
   */
  handleRegenerate() {
    wx.showModal({
      title: '重新生成方案',
      content: '是否保留当前输入重新生成？',
      confirmText: '保留输入',
      cancelText: '全部重置',
      success: (res) => {
        if (res.confirm) {
          // 返回首页 Step 2（保留输入）
          wx.navigateBack({
            delta: 1
          })
        } else {
          // 返回首页 Step 1（清空输入）
          wx.navigateBack({
            delta: 1
          })
          // TODO: 通知首页清空数据
        }
      }
    })
  }
})
