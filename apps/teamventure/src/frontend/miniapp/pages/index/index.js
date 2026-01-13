// pages/index/index.js
import { post } from '../../utils/request.js'
import { API_ENDPOINTS, ACTIVITY_TYPES, ACCOMMODATION_LEVELS, TRIP_TYPES, STORAGE_KEYS } from '../../utils/config.js'
import { formatDate, calculateDays, formatDuration, formatMoney, formatPerPerson } from '../../utils/util.js'
import { PROVINCES } from '../../utils/cities.js'

const app = getApp()

/**
 * 方案生成页面
 *
 * 字段语义说明：
 * - departureLocation（前端） → departure_city（API）：出发城市，团队从哪里出发（如公司所在地：上海市）
 * - destination（前端） → destination（API）：目的地，团建活动举办地点（如：杭州千岛湖）
 *
 * 显示格式："{departure_city} → {destination}"
 * 示例：上海市 → 杭州千岛湖
 */
Page({
  data: {
    currentStep: 1,

    /**
     * 表单数据
     * - departureLocation: 出发城市（团队从哪里出发，如公司所在地：上海市）
     * - destination: 目的地（团建活动举办地点，如：杭州千岛湖）
     */
    formData: {
      peopleCount: 50,
      budgetMin: '',
      budgetMax: '',
      startDate: '',
      endDate: '',

      // 新增：行程类型选择器
      tripType: 'regional', // 默认周边游

      // 新增：分类型的地点信息
      location: {
        regional: {
          departureCity: '',
          destinationCity: '',
          destinationLocation: ''
        },
        domestic: {
          departureCity: '',
          destinationCity: ''
        },
        international: {
          departureCity: '',
          destinationCountry: '',
          destinationCity: ''
        },
        custom: {
          description: ''
        }
      },

      // 保留旧字段以保持向后兼容
      departureLocation: '', // 出发城市（映射到API的departure_city）
      destination: '', // 目的地（团建活动地点）

      preferences: {
        activityTypes: [],
        accommodationLevel: 'standard',
        specialRequirements: ''
      }
    },

    // 选项数据
    activityTypes: ACTIVITY_TYPES,
    accommodationLevels: ACCOMMODATION_LEVELS,
    tripTypes: TRIP_TYPES,

    // 级联选择器状态（用于周边游省市区三级联动）
    provinceList: [],
    cityList: [],
    districtList: [],
    selectedProvinceIndex: -1,
    selectedCityIndex: -1,
    selectedDistrictIndex: -1,

    // 计算字段
    budgetPerPerson: '',
    budgetWarning: '',
    durationDays: '',
    minDate: formatDate(new Date(), 'YYYY-MM-DD')
  },

  // 表单修改标志
  formModified: false,
  // 初始表单数据（用于对比）
  initialFormData: null,

  onLoad(options) {
    console.log('首页加载', options)

    // 检查登录状态
    if (!app.globalData.isLogin) {
      wx.redirectTo({
        url: '/pages/login/login'
      })
      return
    }

    // 保存初始表单数据
    this.initialFormData = JSON.parse(JSON.stringify(this.data.formData))

    // 初始化省份列表（用于周边游的三级联动选择器）
    this.setData({
      provinceList: PROVINCES
    })

    // 尝试恢复上次的输入
    this.loadLastRequest()
  },

  onShow() {
    // 更新最小日期
    this.setData({
      minDate: formatDate(new Date(), 'YYYY-MM-DD')
    })

    // 检查是否有保存的草稿
    this.checkDraft()
  },

  onHide() {
    // 页面隐藏时自动保存草稿
    this.saveDraft()
  },

  /**
   * 加载上次的请求数据
   */
  loadLastRequest() {
    try {
      const lastRequest = wx.getStorageSync(STORAGE_KEYS.LATEST_REQUEST)
      if (lastRequest) {
        const merged = {
          ...this.data.formData,
          ...lastRequest,
          preferences: {
            ...(this.data.formData.preferences || {}),
            ...(lastRequest.preferences || {})
          }
        }
        this.setData({ formData: this.normalizeFormData(merged) })
        this.updateCalculatedFields()
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
   * Step 1: 基础信息输入
   */

  // 人数变化
  handlePeopleCountChange(e) {
    const value = e.detail.value
    this.setData({
      'formData.peopleCount': value
    })
    this.updateBudgetPerPerson()
    this.markFormModified()
  },

  // 快捷人数选择
  handleQuickPeople(e) {
    const value = parseInt(e.currentTarget.dataset.value)
    this.setData({
      'formData.peopleCount': value
    })
    this.updateBudgetPerPerson()
    this.markFormModified()
  },

  // 行程类型选择
  handleTripTypeChange(e) {
    const tripType = e.currentTarget.dataset.value
    const { formData } = this.data

    // 切换类型时重置对应的location字段
    formData.tripType = tripType
    formData.location = {
      regional: { departureCity: '', destinationProvince: '', destinationCity: '', destinationLocation: '' },
      domestic: { departureCity: '', destinationCity: '' },
      international: { departureCity: '', destinationCountry: '', destinationCity: '' },
      custom: { description: '' }
    }

    this.setData({
      formData,
      // 重置级联选择器状态
      provinceList: [],
      cityList: [],
      districtList: [],
      selectedProvinceIndex: -1,
      selectedCityIndex: -1,
      selectedDistrictIndex: -1
    })
    this.markFormModified()
  },

  // === 周边游：省市区三级联动处理器 ===
  handleRegionalDepartureCityInput(e) {
    this.setData({
      'formData.location.regional.departureCity': e.detail.value
    })
    this.markFormModified()
  },

  handleProvinceChange(e) {
    const index = parseInt(e.detail.value)
    const { provinceList } = this.data
    const province = provinceList[index]

    this.setData({
      selectedProvinceIndex: index,
      'formData.location.regional.destinationProvince': province.name,
      cityList: province.cities || [],
      districtList: [],
      selectedCityIndex: -1,
      selectedDistrictIndex: -1,
      'formData.location.regional.destinationCity': '',
      'formData.location.regional.destinationLocation': ''
    })
    this.markFormModified()
  },

  handleCityChange(e) {
    const index = parseInt(e.detail.value)
    const { cityList } = this.data
    const city = cityList[index]

    this.setData({
      selectedCityIndex: index,
      'formData.location.regional.destinationCity': city.name,
      districtList: city.districts || [],
      selectedDistrictIndex: -1,
      'formData.location.regional.destinationLocation': ''
    })
    this.markFormModified()
  },

  handleDistrictChange(e) {
    const index = parseInt(e.detail.value)
    const { districtList } = this.data
    const district = districtList[index]

    this.setData({
      selectedDistrictIndex: index,
      'formData.location.regional.destinationLocation': district.name
    })
    this.markFormModified()
  },

  // === 国内游：出发城市+目的地城市处理器 ===
  handleDomesticDepartureCityInput(e) {
    this.setData({
      'formData.location.domestic.departureCity': e.detail.value
    })
    this.markFormModified()
  },

  handleDomesticDestinationCityInput(e) {
    this.setData({
      'formData.location.domestic.destinationCity': e.detail.value
    })
    this.markFormModified()
  },

  // === 出境游：出发城市+国家+城市处理器 ===
  handleInternationalDepartureCityInput(e) {
    this.setData({
      'formData.location.international.departureCity': e.detail.value
    })
    this.markFormModified()
  },

  handleInternationalDestinationCountryInput(e) {
    this.setData({
      'formData.location.international.destinationCountry': e.detail.value
    })
    this.markFormModified()
  },

  handleInternationalDestinationCityInput(e) {
    this.setData({
      'formData.location.international.destinationCity': e.detail.value
    })
    this.markFormModified()
  },

  // === 自定义：自由描述处理器 ===
  handleCustomDescriptionInput(e) {
    this.setData({
      'formData.location.custom.description': e.detail.value
    })
    this.markFormModified()
  },

  // 最低预算输入
  handleBudgetMinInput(e) {
    const value = e.detail.value
    this.setData({
      'formData.budgetMin': value
    })
    this.updateBudgetPerPerson()
    this.markFormModified()
  },

  // 最高预算输入
  handleBudgetMaxInput(e) {
    const value = e.detail.value
    this.setData({
      'formData.budgetMax': value
    })
    this.updateBudgetPerPerson()
    this.markFormModified()
  },

  // 开始日期变化
  handleStartDateChange(e) {
    const value = e.detail.value
    this.setData({
      'formData.startDate': value
    })
    this.updateDurationDays()
    this.markFormModified()
  },

  // 结束日期变化
  handleEndDateChange(e) {
    const value = e.detail.value
    this.setData({
      'formData.endDate': value
    })
    this.updateDurationDays()
    this.markFormModified()
  },

  // 出发城市输入
  handleDepartureLocationInput(e) {
    const value = e.detail.value
    this.setData({
      'formData.departureLocation': value
    })
    this.markFormModified()
  },

  // 目的地输入
  handleDestinationInput(e) {
    const value = e.detail.value
    this.setData({
      'formData.destination': value
    })
    this.markFormModified()
  },

  /**
   * Step 2: 偏好选择
   */

  // 活动类型切换
  handleActivityTypeToggle(e) {
    const value = e.currentTarget.dataset.value
    const current = this.data.formData?.preferences?.activityTypes
    const activityTypes = Array.isArray(current) ? current.slice() : []
    const index = activityTypes.indexOf(value)

    if (index > -1) {
      activityTypes.splice(index, 1)
    } else {
      activityTypes.push(value)
    }

    this.setData({
      'formData.preferences.activityTypes': activityTypes
    })
    this.markFormModified()
  },

  // 住宿标准变化
  handleAccommodationLevelChange(e) {
    const value = e.currentTarget.dataset.value
    this.setData({
      'formData.preferences.accommodationLevel': value
    })
    this.markFormModified()
  },

  // 特殊需求输入
  handleSpecialRequirementsInput(e) {
    const value = e.detail.value
    this.setData({
      'formData.preferences.specialRequirements': value
    })
    this.markFormModified()
  },

  /**
   * 步骤导航
   */

  // 下一步
  handleNextStep() {
    if (!this.validateStep1()) {
      return
    }

    this.setData({
      currentStep: 2
    })

    // 保存当前输入
    this.saveCurrentRequest()
  },

  // 上一步
  handleBackStep() {
    this.setData({
      currentStep: 1
    })
  },

  // 验证第一步
  validateStep1() {
    const { peopleCount, budgetMin, budgetMax, startDate, endDate, tripType, location } = this.data.formData

    if (!peopleCount || peopleCount < 1) {
      wx.showToast({ title: '请输入参与人数', icon: 'none' })
      return false
    }

    if (!budgetMin || !budgetMax) {
      wx.showToast({ title: '请输入预算范围', icon: 'none' })
      return false
    }

    const min = parseFloat(budgetMin)
    const max = parseFloat(budgetMax)

    if (min <= 0) {
      wx.showToast({ title: '最低预算必须大于0', icon: 'none' })
      return false
    }

    if (max < min) {
      wx.showToast({ title: '最高预算不能低于最低预算', icon: 'none' })
      return false
    }

    if (!startDate || !endDate) {
      wx.showToast({ title: '请选择活动日期', icon: 'none' })
      return false
    }

    // 验证行程类型已选择
    if (!tripType) {
      wx.showToast({ title: '请选择行程类型', icon: 'none' })
      return false
    }

    // 根据行程类型验证不同的必填字段
    switch (tripType) {
      case 'regional':
        if (!location.regional.departureCity) {
          wx.showToast({ title: '请输入出发城市', icon: 'none' })
          return false
        }
        if (!location.regional.destinationProvince) {
          wx.showToast({ title: '请选择目的地省份', icon: 'none' })
          return false
        }
        if (!location.regional.destinationCity) {
          wx.showToast({ title: '请选择目的地城市', icon: 'none' })
          return false
        }
        break

      case 'domestic':
        if (!location.domestic.departureCity) {
          wx.showToast({ title: '请输入出发城市', icon: 'none' })
          return false
        }
        if (!location.domestic.destinationCity) {
          wx.showToast({ title: '请输入目的地城市', icon: 'none' })
          return false
        }
        break

      case 'international':
        if (!location.international.departureCity) {
          wx.showToast({ title: '请输入出发城市', icon: 'none' })
          return false
        }
        if (!location.international.destinationCountry) {
          wx.showToast({ title: '请输入目的地国家', icon: 'none' })
          return false
        }
        break

      case 'custom':
        if (!location.custom.description || location.custom.description.trim().length === 0) {
          wx.showToast({ title: '请输入行程描述', icon: 'none' })
          return false
        }
        if (location.custom.description.trim().length < 10) {
          wx.showToast({ title: '行程描述至少需要10个字符', icon: 'none' })
          return false
        }
        break

      default:
        wx.showToast({ title: '未知的行程类型', icon: 'none' })
        return false
    }

    return true
  },

  /**
   * 映射表单数据到API请求格式
   * 将新的分类型location结构映射到后端API所需的字段格式
   */
  mapFormDataToAPIRequest() {
    const { formData } = this.data
    const { tripType, location } = formData
    console.log('📍 [Mapping Input]', { tripType, location })

    // 根据行程类型映射字段
    switch (tripType) {
      case 'regional':
        formData.departureLocation = location.regional.departureCity
        formData.destination = location.regional.destinationLocation || location.regional.destinationCity
        break
      case 'domestic':
        formData.departureLocation = location.domestic.departureCity
        formData.destination = location.domestic.destinationCity
        break
      case 'international':
        formData.departureLocation = location.international.departureCity
        formData.destination = `${location.international.destinationCountry} ${location.international.destinationCity}`.trim()
        break
      case 'custom':
        // 自定义类型可能没有明确的出发城市
        formData.destination = location.custom.description
        break
    }
    console.log('📍 [Mapping Output]', { departureLocation: formData.departureLocation, destination: formData.destination })

    this.setData({ formData })
  },

  /**
   * 生成方案
   */
  async handleGenerate() {
    const { formData } = this.data
    console.log('📍 [Before Mapping]', { tripType: formData.tripType, location: formData.location })

    // 映射新的分类型location结构到后端API格式
    this.mapFormDataToAPIRequest()
    console.log('📍 [After Mapping]', { departureLocation: formData.departureLocation, destination: formData.destination })

    try {
      wx.showLoading({
        title: '正在生成方案...',
        mask: true
      })

      /**
       * 构建请求数据
       * 字段映射：
       * - departure_city: 出发城市（团队从哪里出发，如：上海市）
       * - destination: 目的地（团建活动举办地点，如：杭州千岛湖）
       */
      const requestData = {
        people_count: formData.peopleCount,
        budget_min: parseFloat(formData.budgetMin),
        budget_max: parseFloat(formData.budgetMax),
        start_date: formData.startDate,
        end_date: formData.endDate,
        departure_city: formData.departureLocation, // 出发城市（团队从哪里出发）
        destination: formData.destination || '', // 目的地（团建活动举办地点，可选）
        preferences: {
          activity_types: formData.preferences.activityTypes,
          accommodation_level: formData.preferences.accommodationLevel,
          special_requirements: formData.preferences.specialRequirements
        }
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
   * 更新计算字段
   */

  updateCalculatedFields() {
    this.updateBudgetPerPerson()
    this.updateDurationDays()
  },

  updateBudgetPerPerson() {
    const { peopleCount, budgetMin, budgetMax } = this.data.formData

    if (!budgetMin && !budgetMax) {
      this.setData({ budgetPerPerson: '', budgetWarning: '' })
      return
    }

    const min = parseFloat(budgetMin) || 0
    const max = parseFloat(budgetMax) || 0

    if (min > 0 && max > 0 && peopleCount > 0) {
      const minPerPerson = Math.round(min / peopleCount)
      const maxPerPerson = Math.round(max / peopleCount)
      this.setData({
        budgetPerPerson: `¥${minPerPerson} - ¥${maxPerPerson}`,
        budgetWarning: minPerPerson < 300 ? '预算可能偏低，建议适当调整' : ''
      })
    } else {
      this.setData({ budgetPerPerson: '', budgetWarning: '' })
    }
  },

  updateDurationDays() {
    const { startDate, endDate } = this.data.formData

    if (startDate && endDate) {
      const days = calculateDays(startDate, endDate)
      this.setData({
        durationDays: days > 0 ? formatDuration(days) : ''
      })
    } else {
      this.setData({ durationDays: '' })
    }
  },

  /**
   * 标记表单已修改
   */
  markFormModified() {
    this.formModified = true
  },

  /**
   * 检查表单是否被修改
   */
  isFormModified() {
    if (!this.initialFormData) return false

    const current = JSON.stringify(this.data.formData)
    const initial = JSON.stringify(this.initialFormData)

    return current !== initial
  },

  /**
   * 保存草稿
   */
  saveDraft() {
    // 只有在表单被修改且不在第一步默认状态时才保存
    if (!this.formModified && !this.isFormModified()) {
      return
    }

    try {
      const draftData = {
        formData: this.data.formData,
        currentStep: this.data.currentStep,
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
    const formData = this.normalizeFormData(this.data.formData)
    return !formData.budgetMin &&
           !formData.budgetMax &&
           !formData.startDate &&
           !formData.endDate &&
           !formData.departureLocation &&
           !formData.destination &&
           formData.preferences.activityTypes.length === 0 &&
           !formData.preferences.specialRequirements
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
      formData: this.normalizeFormData(draft.formData),
      currentStep: draft.currentStep || 1
    })

    this.updateCalculatedFields()
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

  normalizeFormData(raw) {
    const formData = raw && typeof raw === 'object' ? raw : {}
    const preferences = this.normalizePreferences(formData.preferences)
    return {
      ...this.data.formData,
      ...formData,
      preferences
    }
  },

  normalizePreferences(raw) {
    const p = raw && typeof raw === 'object' ? raw : {}
    return {
      activityTypes: Array.isArray(p.activityTypes) ? p.activityTypes : [],
      accommodationLevel: typeof p.accommodationLevel === 'string' && p.accommodationLevel ? p.accommodationLevel : 'standard',
      specialRequirements: typeof p.specialRequirements === 'string' ? p.specialRequirements : ''
    }
  }
})
