/**
 * 行程编辑器页面
 * 提供可视化表单编辑行程的功能
 */
const app = getApp()
const { validateItinerary, validateActivity } = require('../../utils/itinerary-validator')

Page({
  data: {
    planId: '',
    planTitle: '',
    itinerary: {
      days: []
    },
    // 编辑状态
    isEditing: false,
    hasChanges: false,
    isSaving: false,
    // 历史记录（撤销/重做）
    historyStack: [],
    historyIndex: -1,
    maxHistorySize: 20,
    // 弹窗控制
    showActivityEditor: false,
    editingActivity: null,
    editingDayIndex: -1,
    editingItemIndex: -1,
    // 验证错误
    validationErrors: [],
    // 拖拽状态
    dragInfo: {
      isDragging: false,
      dayIndex: -1,
      itemIndex: -1
    }
  },

  onLoad(options) {
    const { planId } = options
    if (planId) {
      this.setData({ planId })
      this.loadPlanData(planId)
    } else {
      wx.showToast({
        title: '缺少方案ID',
        icon: 'error'
      })
      setTimeout(() => wx.navigateBack(), 1500)
    }
  },

  onShow() {
    // 页面显示时检查是否需要刷新
  },

  onUnload() {
    // 页面卸载前检查是否有未保存的更改
    if (this.data.hasChanges) {
      // 自动保存草稿到本地存储
      this.saveDraftToLocal()
    }
  },

  /**
   * 加载方案数据
   */
  async loadPlanData(planId) {
    wx.showLoading({ title: '加载中...' })

    try {
      // 先检查本地是否有草稿
      const draft = wx.getStorageSync(`itinerary_draft_${planId}`)
      if (draft) {
        const useDraft = await this.showDraftConfirm()
        if (useDraft) {
          this.setData({
            planTitle: draft.planTitle,
            itinerary: draft.itinerary,
            hasChanges: true
          })
          this.pushHistory()
          wx.hideLoading()
          return
        } else {
          wx.removeStorageSync(`itinerary_draft_${planId}`)
        }
      }

      // 从服务器加载
      const token = wx.getStorageSync('token')
      const res = await new Promise((resolve, reject) => {
        wx.request({
          url: `${app.globalData.baseUrl}/plans/${planId}`,
          method: 'GET',
          header: { 'Authorization': `Bearer ${token}` },
          success: resolve,
          fail: reject
        })
      })

      if (res.statusCode === 200 && res.data.success) {
        const plan = res.data.data
        const itinerary = this.parseItinerary(plan.content)

        this.setData({
          planTitle: plan.title || '未命名方案',
          itinerary: itinerary
        })
        this.pushHistory()
      } else {
        throw new Error(res.data?.message || '加载失败')
      }
    } catch (error) {
      console.error('加载方案失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      })
    } finally {
      wx.hideLoading()
    }
  },

  /**
   * 解析行程内容
   * 支持JSON格式和Markdown格式
   */
  parseItinerary(content) {
    if (!content) {
      return { days: [this.createEmptyDay(1)] }
    }

    // 尝试JSON解析
    try {
      const parsed = JSON.parse(content)
      if (parsed.itinerary && parsed.itinerary.days) {
        return parsed.itinerary
      }
      if (parsed.days) {
        return parsed
      }
    } catch (e) {
      // 不是JSON，尝试Markdown解析
    }

    // Markdown解析
    return this.parseMarkdownItinerary(content)
  },

  /**
   * 解析Markdown格式的行程
   */
  parseMarkdownItinerary(markdown) {
    const days = []
    const dayRegex = /##\s*Day\s*(\d+)[:\s]*(.+)?/gi
    const itemRegex = /[-*]\s*(\d{1,2}:\d{2})\s*[-~]\s*(\d{1,2}:\d{2})\s*[:：]\s*(.+)/g

    const dayMatches = markdown.split(/(?=##\s*Day)/i)

    dayMatches.forEach((dayContent, index) => {
      if (!dayContent.trim()) return

      const dayMatch = dayContent.match(/##\s*Day\s*(\d+)[:\s]*(.+)?/i)
      if (!dayMatch) return

      const dayNum = parseInt(dayMatch[1])
      const dateStr = dayMatch[2]?.trim() || ''
      const items = []

      let itemMatch
      const itemRegexLocal = /[-*]\s*(\d{1,2}:\d{2})\s*[-~]\s*(\d{1,2}:\d{2})\s*[:：]\s*(.+)/g

      while ((itemMatch = itemRegexLocal.exec(dayContent)) !== null) {
        const activity = itemMatch[3].trim()
        const parts = activity.split(/[,，]/)

        items.push({
          id: this.generateItemId(),
          time_start: itemMatch[1],
          time_end: itemMatch[2],
          activity: parts[0]?.trim() || '',
          location: parts[1]?.trim() || '',
          note: parts.slice(2).join(',').trim() || ''
        })
      }

      days.push({
        day: dayNum,
        date: dateStr,
        items: items.length > 0 ? items : [this.createEmptyItem()]
      })
    })

    return {
      days: days.length > 0 ? days : [this.createEmptyDay(1)]
    }
  },

  /**
   * 生成唯一ID
   */
  generateItemId() {
    return 'item_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5)
  },

  /**
   * 创建空白天
   */
  createEmptyDay(dayNum) {
    const today = new Date()
    today.setDate(today.getDate() + dayNum - 1)
    const dateStr = today.toISOString().split('T')[0]

    return {
      day: dayNum,
      date: dateStr,
      items: [this.createEmptyItem()]
    }
  },

  /**
   * 创建空白活动项
   */
  createEmptyItem() {
    return {
      id: this.generateItemId(),
      time_start: '09:00',
      time_end: '10:00',
      activity: '',
      location: '',
      note: ''
    }
  },

  // ==================== 历史记录管理 ====================

  /**
   * 推入历史记录
   */
  pushHistory() {
    const { historyStack, historyIndex, maxHistorySize, itinerary } = this.data

    // 删除当前位置之后的历史
    const newStack = historyStack.slice(0, historyIndex + 1)

    // 添加当前状态
    newStack.push(JSON.parse(JSON.stringify(itinerary)))

    // 限制历史大小
    if (newStack.length > maxHistorySize) {
      newStack.shift()
    }

    this.setData({
      historyStack: newStack,
      historyIndex: newStack.length - 1
    })
  },

  /**
   * 撤销
   */
  undo() {
    const { historyStack, historyIndex } = this.data
    if (historyIndex > 0) {
      const newIndex = historyIndex - 1
      this.setData({
        itinerary: JSON.parse(JSON.stringify(historyStack[newIndex])),
        historyIndex: newIndex,
        hasChanges: true
      })
      this.validateAll()
    }
  },

  /**
   * 重做
   */
  redo() {
    const { historyStack, historyIndex } = this.data
    if (historyIndex < historyStack.length - 1) {
      const newIndex = historyIndex + 1
      this.setData({
        itinerary: JSON.parse(JSON.stringify(historyStack[newIndex])),
        historyIndex: newIndex,
        hasChanges: true
      })
      this.validateAll()
    }
  },

  /**
   * 检查是否可撤销
   */
  canUndo() {
    return this.data.historyIndex > 0
  },

  /**
   * 检查是否可重做
   */
  canRedo() {
    return this.data.historyIndex < this.data.historyStack.length - 1
  },

  // ==================== 天数操作 ====================

  /**
   * 添加新的一天
   */
  addDay() {
    const { itinerary } = this.data
    const newDayNum = itinerary.days.length + 1
    const newDay = this.createEmptyDay(newDayNum)

    // 根据前一天的日期计算新日期
    if (itinerary.days.length > 0) {
      const lastDay = itinerary.days[itinerary.days.length - 1]
      if (lastDay.date) {
        const lastDate = new Date(lastDay.date)
        lastDate.setDate(lastDate.getDate() + 1)
        newDay.date = lastDate.toISOString().split('T')[0]
      }
    }

    itinerary.days.push(newDay)

    this.setData({
      itinerary,
      hasChanges: true
    })
    this.pushHistory()
  },

  /**
   * 删除某一天
   */
  deleteDay(e) {
    const { dayIndex } = e.currentTarget.dataset
    const { itinerary } = this.data

    if (itinerary.days.length <= 1) {
      wx.showToast({
        title: '至少保留一天',
        icon: 'none'
      })
      return
    }

    wx.showModal({
      title: '确认删除',
      content: `确定要删除第 ${dayIndex + 1} 天的所有活动吗？`,
      success: (res) => {
        if (res.confirm) {
          itinerary.days.splice(dayIndex, 1)
          // 重新编号
          itinerary.days.forEach((day, idx) => {
            day.day = idx + 1
          })

          this.setData({
            itinerary,
            hasChanges: true
          })
          this.pushHistory()
          this.validateAll()
        }
      }
    })
  },

  /**
   * 修改日期
   */
  onDateChange(e) {
    const { dayIndex } = e.currentTarget.dataset
    const { value } = e.detail
    const { itinerary } = this.data

    itinerary.days[dayIndex].date = value

    this.setData({
      itinerary,
      hasChanges: true
    })
    this.pushHistory()
  },

  // ==================== 活动项操作 ====================

  /**
   * 添加活动项
   */
  addActivity(e) {
    const { dayIndex } = e.currentTarget.dataset
    const { itinerary } = this.data

    const newItem = this.createEmptyItem()

    // 根据前一个活动的结束时间设置开始时间
    const dayItems = itinerary.days[dayIndex].items
    if (dayItems.length > 0) {
      const lastItem = dayItems[dayItems.length - 1]
      newItem.time_start = lastItem.time_end
      // 默认时长1小时
      const [hours, mins] = lastItem.time_end.split(':').map(Number)
      const endHours = hours + 1
      newItem.time_end = `${String(endHours).padStart(2, '0')}:${String(mins).padStart(2, '0')}`
    }

    itinerary.days[dayIndex].items.push(newItem)

    this.setData({
      itinerary,
      hasChanges: true
    })
    this.pushHistory()
  },

  /**
   * 编辑活动项
   */
  editActivity(e) {
    const { dayIndex, itemIndex } = e.currentTarget.dataset
    const { itinerary } = this.data
    const activity = itinerary.days[dayIndex].items[itemIndex]

    this.setData({
      showActivityEditor: true,
      editingActivity: JSON.parse(JSON.stringify(activity)),
      editingDayIndex: dayIndex,
      editingItemIndex: itemIndex
    })
  },

  /**
   * 删除活动项
   */
  deleteActivity(e) {
    const { dayIndex, itemIndex } = e.currentTarget.dataset
    const { itinerary } = this.data

    const dayItems = itinerary.days[dayIndex].items
    if (dayItems.length <= 1) {
      wx.showToast({
        title: '至少保留一个活动',
        icon: 'none'
      })
      return
    }

    wx.showModal({
      title: '确认删除',
      content: '确定要删除这个活动吗？',
      success: (res) => {
        if (res.confirm) {
          dayItems.splice(itemIndex, 1)
          this.setData({
            itinerary,
            hasChanges: true
          })
          this.pushHistory()
          this.validateAll()
        }
      }
    })
  },

  /**
   * 复制活动项
   */
  copyActivity(e) {
    const { dayIndex, itemIndex } = e.currentTarget.dataset
    const { itinerary } = this.data
    const activity = itinerary.days[dayIndex].items[itemIndex]

    const newActivity = JSON.parse(JSON.stringify(activity))
    newActivity.id = this.generateItemId()

    // 插入到当前活动后面
    itinerary.days[dayIndex].items.splice(itemIndex + 1, 0, newActivity)

    this.setData({
      itinerary,
      hasChanges: true
    })
    this.pushHistory()

    wx.showToast({
      title: '已复制',
      icon: 'success'
    })
  },

  /**
   * 移动活动项（上移/下移）
   */
  moveActivity(e) {
    const { dayIndex, itemIndex, direction } = e.currentTarget.dataset
    const { itinerary } = this.data
    const items = itinerary.days[dayIndex].items

    const newIndex = direction === 'up' ? itemIndex - 1 : itemIndex + 1

    if (newIndex < 0 || newIndex >= items.length) {
      return
    }

    // 交换位置
    [items[itemIndex], items[newIndex]] = [items[newIndex], items[itemIndex]]

    this.setData({
      itinerary,
      hasChanges: true
    })
    this.pushHistory()
  },

  // ==================== 活动编辑器弹窗 ====================

  /**
   * 关闭活动编辑器
   */
  closeActivityEditor() {
    this.setData({
      showActivityEditor: false,
      editingActivity: null,
      editingDayIndex: -1,
      editingItemIndex: -1
    })
  },

  /**
   * 保存活动编辑
   */
  saveActivityEdit(e) {
    const { activity } = e.detail
    const { itinerary, editingDayIndex, editingItemIndex } = this.data

    // 验证
    const errors = validateActivity(activity)
    if (errors.length > 0) {
      wx.showToast({
        title: errors[0],
        icon: 'none'
      })
      return
    }

    itinerary.days[editingDayIndex].items[editingItemIndex] = activity

    this.setData({
      itinerary,
      hasChanges: true,
      showActivityEditor: false,
      editingActivity: null,
      editingDayIndex: -1,
      editingItemIndex: -1
    })
    this.pushHistory()
    this.validateAll()
  },

  /**
   * 活动编辑器字段变化
   */
  onActivityFieldChange(e) {
    const { field } = e.currentTarget.dataset
    const { value } = e.detail
    const { editingActivity } = this.data

    editingActivity[field] = value
    this.setData({ editingActivity })
  },

  // ==================== 验证 ====================

  /**
   * 验证所有数据
   */
  validateAll() {
    const { itinerary } = this.data
    const errors = validateItinerary(itinerary)
    this.setData({ validationErrors: errors })
    return errors.length === 0
  },

  // ==================== 保存 ====================

  /**
   * 保存到服务器
   */
  async save() {
    if (!this.validateAll()) {
      wx.showToast({
        title: '请修正错误后再保存',
        icon: 'none'
      })
      return
    }

    this.setData({ isSaving: true })
    wx.showLoading({ title: '保存中...' })

    try {
      const { planId, itinerary } = this.data
      const token = wx.getStorageSync('token')

      // 转换为存储格式
      const content = JSON.stringify({ itinerary })

      const res = await new Promise((resolve, reject) => {
        wx.request({
          url: `${app.globalData.baseUrl}/plans/${planId}/itinerary`,
          method: 'PUT',
          header: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          data: { content },
          success: resolve,
          fail: reject
        })
      })

      if (res.statusCode === 200 && res.data.success) {
        // 清除本地草稿
        wx.removeStorageSync(`itinerary_draft_${planId}`)

        this.setData({
          hasChanges: false
        })

        wx.showToast({
          title: '保存成功',
          icon: 'success'
        })
      } else {
        throw new Error(res.data?.message || '保存失败')
      }
    } catch (error) {
      console.error('保存失败:', error)
      wx.showToast({
        title: '保存失败',
        icon: 'error'
      })
    } finally {
      this.setData({ isSaving: false })
      wx.hideLoading()
    }
  },

  /**
   * 保存草稿到本地
   */
  saveDraftToLocal() {
    const { planId, planTitle, itinerary } = this.data
    wx.setStorageSync(`itinerary_draft_${planId}`, {
      planTitle,
      itinerary,
      savedAt: new Date().toISOString()
    })
  },

  /**
   * 显示草稿确认对话框
   */
  showDraftConfirm() {
    return new Promise((resolve) => {
      wx.showModal({
        title: '发现未保存的草稿',
        content: '是否恢复上次编辑的内容？',
        confirmText: '恢复',
        cancelText: '放弃',
        success: (res) => {
          resolve(res.confirm)
        }
      })
    })
  },

  /**
   * 返回上一页
   */
  goBack() {
    if (this.data.hasChanges) {
      wx.showModal({
        title: '提示',
        content: '有未保存的更改，确定要离开吗？',
        confirmText: '保存后离开',
        cancelText: '直接离开',
        success: (res) => {
          if (res.confirm) {
            this.save().then(() => {
              wx.navigateBack()
            })
          } else if (res.cancel) {
            wx.navigateBack()
          }
        }
      })
    } else {
      wx.navigateBack()
    }
  },

  /**
   * 预览行程
   */
  preview() {
    const { planId } = this.data
    wx.navigateTo({
      url: `/pages/detail/detail?planId=${planId}`
    })
  }
})
