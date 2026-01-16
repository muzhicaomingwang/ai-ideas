// pages/index/index.js
import { post } from '../../utils/request.js'
import { API_ENDPOINTS, STORAGE_KEYS } from '../../utils/config.js'

const app = getApp()

// Markdown 模板（预填充示例，用户直接修改即可）
const MARKDOWN_TEMPLATE = `# 团建行程方案

## 基本信息
- **天数**: 3天2夜
- **预算**: ¥500 - ¥800/人

## 行程路线
- **出发地**: 北京
- **到达地**: 青岛
- **途径地**: 济南（可选，不需要请删除）

## 交通安排
### 去程
- **方式**: 高铁G123次（北京南 → 青岛北，8:00-12:30）
- 或: 航班CA1234（如需要请修改）

### 返程
- **方式**: 高铁G456次（青岛北 → 北京南，15:00-19:30）
- 或: 航班CA5678（如需要请修改）

## 住宿安排
### 第一日
- **入住**: 青岛XX酒店（四星级，海景房优先）

### 第二日
- **出发**: 青岛XX酒店
- **入住**: 崂山XX度假村（度假型酒店）

### 第三日
- **出发**: 崂山XX度假村

## 活动偏好
- 户外拓展（团队协作类活动）
- 海边休闲（沙滩运动、篝火晚会）
- 美食体验（海鲜大餐、特色小吃）

## 特殊要求
- 有2位老人需要无障碍设施
- 3人素食（需要准备素食餐）
- 如无特殊要求请删除此段
`

/**
 * 方案生成页面 - Markdown自由输入模式
 */
Page({
  data: {
    formData: {
      markdownContent: MARKDOWN_TEMPLATE // 默认预填充模板
    },
    placeholder: '请修改模板中的示例内容为您的实际需求',

    // AI填充弹窗
    showAIFillDialog: false,
    aiFillData: {
      days: '',
      origin: '',
      destination: ''
    },

    // AI生成状态: normal | generating | generated | error
    aiGenerateStatus: 'normal',
    generateProgress: 0,

    // 保存原始内容（用于生成失败时恢复）
    originalContent: ''
  },

  // 表单修改标志
  formModified: false,

  // 进度模拟定时器
  progressTimer: null,

  onLoad(options) {
    console.log('生成方案页面加载', options)

    // 检查登录状态
    if (!app.globalData.isLogin) {
      wx.redirectTo({
        url: '/pages/login/login'
      })
      return
    }

    // 尝试恢复上次的输入（如果有草稿，会覆盖默认模板）
    this.loadLastRequest()
  },

  onShow() {
    // 检查是否有保存的草稿
    this.checkDraft()
  },

  onHide() {
    // 页面隐藏时自动保存草稿
    this.saveDraft()
  },

  onUnload() {
    // 页面卸载时清除定时器
    if (this.progressTimer) {
      clearInterval(this.progressTimer)
    }
  },

  /**
   * 加载上次的请求数据
   */
  loadLastRequest() {
    try {
      const lastRequest = wx.getStorageSync(STORAGE_KEYS.LATEST_REQUEST)
      if (lastRequest && lastRequest.markdownContent) {
        this.setData({
          'formData.markdownContent': lastRequest.markdownContent
        })
      }
    } catch (error) {
      console.error('加载上次请求失败:', error)
    }
  },

  /**
   * 保存当前请求数据
   */
  saveCurrentRequest() {
    try {
      wx.setStorageSync(STORAGE_KEYS.LATEST_REQUEST, this.data.formData)
    } catch (error) {
      console.error('保存请求数据失败:', error)
    }
  },

  /**
   * Markdown 输入处理
   */
  handleMarkdownInput(e) {
    const value = e.detail.value
    this.setData({
      'formData.markdownContent': value
    })
    this.markFormModified()
  },

  /**
   * 重置为空白模板
   */
  handleShowTemplate() {
    // 生成中不允许操作
    if (this.data.aiGenerateStatus === 'generating') {
      return
    }

    wx.showModal({
      title: '重置模板',
      content: '确定要重置为空白模板吗？当前内容将被清空。',
      showCancel: true,
      confirmText: '重置',
      cancelText: '取消',
      confirmColor: '#ff6b35',
      success: (res) => {
        if (res.confirm) {
          this.setData({
            'formData.markdownContent': MARKDOWN_TEMPLATE,
            aiGenerateStatus: 'normal'
          })
          this.markFormModified()
          wx.showToast({
            title: '已重置模板',
            icon: 'success'
          })
        }
      }
    })
  },

  /**
   * 表单验证
   */
  validateForm() {
    const { markdownContent } = this.data.formData

    if (!markdownContent || markdownContent.trim().length === 0) {
      wx.showToast({ title: '请输入行程描述', icon: 'none' })
      return false
    }

    if (markdownContent.trim().length < 50) {
      wx.showToast({ title: '行程描述至少需要50个字符，请补充更多信息', icon: 'none' })
      return false
    }

    return true
  },

  /**
   * 生成方案
   */
  async handleGenerate() {
    // 先验证表单
    if (!this.validateForm()) {
      return
    }

    const { formData } = this.data

    try {
      wx.showLoading({
        title: '正在生成方案...',
        mask: true
      })

      /**
       * 构建请求数据 - Markdown格式
       * 后端将解析Markdown内容提取结构化信息
       */
      const requestData = {
        markdown_content: formData.markdownContent
      }

      console.log('生成方案请求:', requestData)

      // 调用 API - 这是异步的，只返回 plan_request_id
      const result = await post(API_ENDPOINTS.PLAN_GENERATE, requestData, {
        showLoading: false,
        timeout: 120000 // 2分钟超时
      })

      wx.hideLoading()

      console.log('生成方案响应:', result)

      // 保存当前请求
      this.saveCurrentRequest()

      // 清除草稿（生成成功后不需要保留草稿）
      this.clearDraft()

      // 方案生成是异步的，result 包含 { plan_request_id, status: "generating" }
      // 提示用户并跳转到我的方案页等待
      wx.showModal({
        title: '提交成功',
        content: 'AI正在为您生成方案，预计需要1-2分钟。请在"我的方案"中查看结果。',
        showCancel: false,
        confirmText: '去查看',
        success: () => {
          // 跳转到我的方案页
          wx.switchTab({
            url: '/pages/myplans/myplans'
          })
        }
      })
    } catch (error) {
      wx.hideLoading()
      console.error('生成方案失败:', error)

      wx.showModal({
        title: '生成失败',
        content: error.message || '请稍后重试',
        showCancel: true,
        confirmText: '重试',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            this.handleGenerate()
          }
        }
      })
    }
  },

  /**
   * 标记表单已修改
   */
  markFormModified() {
    this.formModified = true
  },

  /**
   * 保存草稿
   */
  saveDraft() {
    // 只有在表单被修改时才保存
    if (!this.formModified) {
      return
    }

    // 只有内容不为空时才保存
    if (!this.data.formData.markdownContent || this.data.formData.markdownContent.trim().length === 0) {
      return
    }

    try {
      const draftData = {
        formData: this.data.formData,
        timestamp: Date.now()
      }

      wx.setStorageSync(STORAGE_KEYS.DRAFT_REQUEST, draftData)
      console.log('草稿已自动保存')
    } catch (error) {
      console.error('保存草稿失败:', error)
    }
  },

  /**
   * 检查草稿
   */
  checkDraft() {
    try {
      const draft = wx.getStorageSync(STORAGE_KEYS.DRAFT_REQUEST)

      if (!draft || !draft.timestamp) {
        return
      }

      // 检查草稿是否在24小时内
      const hoursPassed = (Date.now() - draft.timestamp) / (1000 * 60 * 60)
      if (hoursPassed > 24) {
        // 草稿过期，删除
        wx.removeStorageSync(STORAGE_KEYS.DRAFT_REQUEST)
        return
      }

      // 检查当前表单是否为初始状态
      const isCurrentFormEmpty = this.isFormEmpty()

      // 只有当前表单为空且有草稿时才提示恢复
      if (isCurrentFormEmpty) {
        this.showDraftRecoveryDialog(draft)
      }
    } catch (error) {
      console.error('检查草稿失败:', error)
    }
  },

  /**
   * 检查表单是否为空（初始状态）
   */
  isFormEmpty() {
    const { markdownContent } = this.data.formData
    return !markdownContent || markdownContent.trim().length === 0
  },

  /**
   * 显示草稿恢复对话框
   */
  showDraftRecoveryDialog(draft) {
    const timeAgo = this.formatTimeAgo(draft.timestamp)

    wx.showModal({
      title: '发现未完成的方案',
      content: `您${timeAgo}有一个未完成的方案，是否继续编辑？`,
      confirmText: '继续编辑',
      cancelText: '重新开始',
      confirmColor: '#1890ff',
      success: (res) => {
        if (res.confirm) {
          // 恢复草稿
          this.recoverDraft(draft)
        } else {
          // 删除草稿
          this.clearDraft()
        }
      }
    })
  },

  /**
   * 恢复草稿
   */
  recoverDraft(draft) {
    this.setData({
      formData: draft.formData || { markdownContent: '' }
    })

    this.formModified = true

    wx.showToast({
      title: '已恢复草稿',
      icon: 'success'
    })
  },

  /**
   * 清除草稿
   */
  clearDraft() {
    try {
      wx.removeStorageSync(STORAGE_KEYS.DRAFT_REQUEST)
      this.formModified = false
    } catch (error) {
      console.error('清除草稿失败:', error)
    }
  },

  /**
   * 格式化时间差
   */
  formatTimeAgo(timestamp) {
    const minutesAgo = Math.floor((Date.now() - timestamp) / (1000 * 60))

    if (minutesAgo < 1) return '刚才'
    if (minutesAgo < 60) return `${minutesAgo}分钟前`

    const hoursAgo = Math.floor(minutesAgo / 60)
    if (hoursAgo < 24) return `${hoursAgo}小时前`

    const daysAgo = Math.floor(hoursAgo / 24)
    return `${daysAgo}天前`
  },

  // ==================== AI填充功能 ====================

  /**
   * 显示AI填充弹窗
   */
  handleShowAIFillDialog() {
    // 生成中不允许操作
    if (this.data.aiGenerateStatus === 'generating') {
      return
    }

    this.setData({
      showAIFillDialog: true,
      // 重置填充数据
      'aiFillData.days': '',
      'aiFillData.origin': '',
      'aiFillData.destination': ''
    })
  },

  /**
   * 关闭AI填充弹窗
   */
  handleCloseAIFillDialog() {
    this.setData({
      showAIFillDialog: false
    })
  },

  /**
   * 阻止事件冒泡
   */
  stopPropagation() {
    // 阻止点击弹窗内容时关闭
  },

  /**
   * 天数输入
   */
  handleDaysInput(e) {
    const value = e.detail.value
    this.setData({
      'aiFillData.days': value
    })
  },

  /**
   * 出发地输入
   */
  handleOriginInput(e) {
    this.setData({
      'aiFillData.origin': e.detail.value
    })
  },

  /**
   * 到达地输入
   */
  handleDestinationInput(e) {
    this.setData({
      'aiFillData.destination': e.detail.value
    })
  },

  /**
   * 确认AI填充
   */
  handleConfirmAIFill() {
    const { days, origin, destination } = this.data.aiFillData

    // 验证天数
    if (!days || days.toString().trim().length === 0) {
      wx.showToast({ title: '请输入天数', icon: 'none' })
      return
    }

    const daysNum = parseInt(days)
    if (isNaN(daysNum) || daysNum < 1 || daysNum > 9) {
      wx.showToast({ title: '天数必须是1-9之间的数字', icon: 'none' })
      return
    }

    // 验证出发地
    if (!origin || origin.trim().length === 0) {
      wx.showToast({ title: '请输入出发地', icon: 'none' })
      return
    }

    // 验证到达地
    if (!destination || destination.trim().length === 0) {
      wx.showToast({ title: '请输入到达地', icon: 'none' })
      return
    }

    // 保存原始内容（用于失败恢复）
    this.setData({
      originalContent: this.data.formData.markdownContent
    })

    // 关闭弹窗，进入生成状态
    this.setData({
      showAIFillDialog: false,
      aiGenerateStatus: 'generating',
      generateProgress: 0
    })

    // 模拟AI生成过程
    this.simulateAIGeneration(daysNum, origin, destination)
  },

  /**
   * 模拟AI生成过程
   */
  simulateAIGeneration(days, origin, destination) {
    // 清除之前的定时器
    if (this.progressTimer) {
      clearInterval(this.progressTimer)
    }

    // 进度条动画（0% → 100%，耗时1.5秒）
    let progress = 0
    this.progressTimer = setInterval(() => {
      progress += 5
      this.setData({
        generateProgress: Math.min(progress, 95) // 最多到95%，等真正生成完才到100%
      })

      if (progress >= 95) {
        clearInterval(this.progressTimer)
      }
    }, 75) // 每75ms增加5%

    // 模拟AI思考时间（1.5秒后生成）
    setTimeout(() => {
      try {
        // 生成AI模板
        const generatedTemplate = this.generateAITemplate(days, origin, destination)

        // 进度到100%
        this.setData({
          generateProgress: 100
        })

        // 短暂停留让用户看到100%
        setTimeout(() => {
          // 填充生成的内容
          this.setData({
            'formData.markdownContent': generatedTemplate,
            aiGenerateStatus: 'generated',
            generateProgress: 0
          })

          this.markFormModified()

          wx.showToast({
            title: 'AI填充完成',
            icon: 'success',
            duration: 1500
          })
        }, 300)
      } catch (error) {
        // 生成失败，恢复原始内容
        console.error('AI生成失败:', error)
        this.handleGenerationError()
      }
    }, 1500)
  },

  /**
   * 处理生成失败
   */
  handleGenerationError() {
    // 清除定时器
    if (this.progressTimer) {
      clearInterval(this.progressTimer)
    }

    // 恢复原始内容
    this.setData({
      'formData.markdownContent': this.data.originalContent,
      aiGenerateStatus: 'normal',
      generateProgress: 0
    })

    wx.showToast({
      title: 'AI生成失败，请重试',
      icon: 'none',
      duration: 2000
    })
  },

  /**
   * 生成AI智能模板
   * @param {number} days - 天数（1-9天）
   * @param {string} origin - 出发地
   * @param {string} destination - 到达地
   * @returns {string} - 生成的Markdown模板
   */
  generateAITemplate(days, origin, destination) {
    // 基础信息
    const basicInfo = `# 团建行程方案

## 基本信息
- **天数**: ${days}天${days > 1 ? (days - 1) + '夜' : ''}
- **预算**: ¥500 - ¥800/人

## 行程路线
- **出发地**: ${origin}
- **到达地**: ${destination}`

    // 途经点逻辑
    let waypoints = ''
    if (days >= 5 && days <= 6) {
      waypoints = '\n- **途径地**: （建议第3天，请填写具体城市）'
    } else if (days === 7 || days === 8) {
      waypoints = '\n- **途径地1**: （建议第3天，请填写具体城市）\n- **途径地2**: （建议第5天，请填写具体城市）'
    } else if (days >= 9) {
      waypoints = '\n- **途径地1**: （建议第3天，请填写具体城市）\n- **途径地2**: （建议第5天，请填写具体城市）\n- **途径地3**: （建议第7天，请填写具体城市）'
    }

    // 交通安排
    const transportation = `

## 交通安排
### 去程
- **方式**: 高铁/航班（${origin} → ${destination}，请填写具体班次和时间）

### 返程
- **方式**: 高铁/航班（${destination} → ${origin}，请填写具体班次和时间）`

    // 住宿安排（根据天数生成）
    const accommodation = this.generateAccommodation(days, origin, destination)

    // 活动偏好（基础模板）
    const activities = `

## 活动偏好
- 团队协作（如：拓展训练、团队挑战）
- 文化体验（如：当地特色、历史古迹）
- 休闲娱乐（如：美食品鉴、自由活动）

## 特殊要求
- 如有老人/小孩、饮食限制等特殊需求，请在此填写
- 如无特殊要求可删除此段`

    return basicInfo + waypoints + transportation + accommodation + activities
  },

  /**
   * 生成住宿安排（基于天数和位移-驻留逻辑）
   * @param {number} days - 天数
   * @param {string} origin - 出发地
   * @param {string} destination - 到达地
   * @returns {string} - 住宿安排Markdown
   */
  generateAccommodation(days, origin, destination) {
    let accommodation = '\n\n## 住宿安排'

    if (days === 1) {
      // 1天：位移→驻留→位移（无住宿）
      accommodation += '\n<!-- 1天行程无需住宿安排 -->'
      return accommodation
    }

    // 2天及以上：根据位移-驻留逻辑生成
    for (let day = 1; day <= days; day++) {
      accommodation += `\n### 第${this.numberToChinese(day)}日`

      if (day === 1) {
        // 第1天：位移→驻留（入住）
        accommodation += `\n- **入住**: ${destination}XX酒店（请填写具体酒店名称和星级）`
      } else if (day === days) {
        // 最后1天：驻留→位移（离店，无入住）
        accommodation += `\n- **出发**: ${destination}XX酒店\n<!-- 当日返程，无需入住 -->`
      } else if (days >= 5 && this.isWaypointDay(day, days)) {
        // 途经点日（5/7/9天）：驻留→位移→驻留
        const waypointIndex = this.getWaypointIndex(day, days)
        accommodation += `\n- **出发**: 前一站酒店`
        accommodation += `\n- **入住**: 途径地${waypointIndex}XX酒店（请填写具体酒店名称）`
      } else {
        // 中间日：驻留（换酒店或续住）
        accommodation += `\n- **出发**: ${destination}XX酒店`
        accommodation += `\n- **入住**: ${destination}XX度假村（或续住前一酒店）`
      }
    }

    return accommodation
  },

  /**
   * 判断是否为途经点日
   */
  isWaypointDay(day, totalDays) {
    if (totalDays >= 5 && totalDays <= 6 && day === 3) return true
    if ((totalDays === 7 || totalDays === 8) && (day === 3 || day === 5)) return true
    if (totalDays >= 9 && (day === 3 || day === 5 || day === 7)) return true
    return false
  },

  /**
   * 获取途经点索引
   */
  getWaypointIndex(day, totalDays) {
    if (totalDays >= 5 && totalDays <= 6 && day === 3) return 1
    if ((totalDays === 7 || totalDays === 8)) {
      if (day === 3) return 1
      if (day === 5) return 2
    }
    if (totalDays >= 9) {
      if (day === 3) return 1
      if (day === 5) return 2
      if (day === 7) return 3
    }
    return 1
  },

  /**
   * 数字转中文
   */
  numberToChinese(num) {
    const chinese = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
    if (num <= 10) return chinese[num - 1]
    return num.toString()
  }
})
