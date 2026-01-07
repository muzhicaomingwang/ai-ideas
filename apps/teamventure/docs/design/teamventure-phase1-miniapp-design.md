# TeamVenture Phase 1 - 小程序前端详细设计

**版本**: v1.0
**创建日期**: 2026-01-04
**作者**: TeamVenture开发团队
**用途**: 微信小程序前端完整架构设计文档

---

## 目录

1. [概述](#1-概述)
2. [工程结构设计](#2-工程结构设计)
3. [核心页面设计](#3-核心页面设计)
4. [网络请求封装](#4-网络请求封装)
5. [状态管理](#5-状态管理)
6. [性能优化](#6-性能优化)
7. [组件设计](#7-组件设计)
8. [工具函数库](#8-工具函数库)

---

## 1. 概述

### 1.1 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **微信小程序原生框架** | 最新版本 | 基础框架 |
| **WXML/WXSS/JavaScript** | ES6+ | UI + 逻辑 |
| **微信开发者工具** | 最新稳定版 | 开发调试 |

### 1.2 架构特点

- **原生开发**: 不使用第三方框架，性能优先
- **模块化设计**: 页面、组件、工具函数分离
- **Mock数据支持**: 便于前端独立开发和测试
- **渐进式增强**: 先实现核心功能，后优化体验

### 1.3 核心功能

1. **微信登录**: 一键登录 + 用户信息收集
2. **方案生成**: 两步表单 + 实时验证 + 草稿保存
3. **方案对比**: 3套方案并列展示 + 快速选择
4. **方案详情**: 完整行程 + 预算明细 + 供应商联系
5. **我的方案**: 分页列表 + 左滑删除 + 下拉刷新
6. **个人中心**: 用户信息展示 + 退出登录

---

## 2. 工程结构设计

### 2.1 目录结构

```
src/frontend/miniapp/
├── app.js                    # 小程序入口文件
├── app.json                  # 全局配置
├── app.wxss                  # 全局样式
├── sitemap.json              # 索引配置
├── project.config.json       # 项目配置
├── pages/                    # 页面目录
│   ├── home/                 # 首页（Banner + 推荐）
│   │   ├── home.js
│   │   ├── home.wxml
│   │   ├── home.wxss
│   │   └── home.json
│   ├── index/                # 生成方案页（核心功能）
│   │   ├── index.js          # 592行 - 两步表单逻辑
│   │   ├── index.wxml
│   │   ├── index.wxss
│   │   └── index.json
│   ├── myplans/              # 我的方案页
│   │   ├── myplans.js        # 301行 - 列表+左滑删除
│   │   ├── myplans.wxml
│   │   ├── myplans.wxss
│   │   └── myplans.json
│   ├── comparison/           # 方案对比页
│   │   ├── comparison.js
│   │   ├── comparison.wxml
│   │   ├── comparison.wxss
│   │   └── comparison.json
│   ├── detail/               # 方案详情页
│   │   ├── detail.js
│   │   ├── detail.wxml
│   │   ├── detail.wxss
│   │   └── detail.json
│   ├── login/                # 登录页
│   │   ├── login.js          # 241行 - 微信登录+信息收集
│   │   ├── login.wxml
│   │   ├── login.wxss
│   │   └── login.json
│   └── profile/              # 个人中心页
│       ├── profile.js
│       ├── profile.wxml
│       ├── profile.wxss
│       └── profile.json
├── components/               # 组件目录
│   └── stepper/              # 数字步进器组件
│       ├── stepper.js
│       ├── stepper.wxml
│       ├── stepper.wxss
│       └── stepper.json
└── utils/                    # 工具函数目录
    ├── request.js            # 327行 - 网络请求封装
    ├── config.js             # API配置+常量定义
    ├── util.js               # 340行 - 通用工具函数
    └── mock-data.js          # Mock数据
```

### 2.2 页面路由配置 (app.json)

```json
{
  "pages": [
    "pages/home/home",           // 首页（默认启动页）
    "pages/index/index",         // 生成方案页
    "pages/myplans/myplans",     // 我的方案页
    "pages/profile/profile",     // 个人中心页
    "pages/login/login",         // 登录页（非Tab）
    "pages/comparison/comparison", // 对比页（非Tab）
    "pages/detail/detail"        // 详情页（非Tab）
  ],
  "tabBar": {
    "list": [
      { "pagePath": "pages/home/home", "text": "首页" },
      { "pagePath": "pages/index/index", "text": "生成方案" },
      { "pagePath": "pages/myplans/myplans", "text": "我的方案" },
      { "pagePath": "pages/profile/profile", "text": "我的" }
    ]
  }
}
```

**路由设计说明**:
- **4个Tab页**: 首页、生成方案、我的方案、个人中心
- **3个非Tab页**: 登录、对比、详情（需要`wx.navigateTo`跳转）
- **默认启动页**: `pages/home/home`

### 2.3 全局配置 (app.json)

```json
{
  "window": {
    "navigationBarTitleText": "TeamVenture",
    "navigationBarBackgroundColor": "#1890ff",  // 蓝色主题
    "navigationBarTextStyle": "white",
    "backgroundColor": "#f5f5f5",
    "backgroundTextStyle": "light",
    "enablePullDownRefresh": false  // 仅部分页面启用
  },
  "permission": {
    "scope.userLocation": {
      "desc": "您的位置信息将用于推荐附近的团建方案"
    }
  },
  "lazyCodeLoading": "requiredComponents"  // 按需加载优化
}
```

---

## 3. 核心页面设计

### 3.1 登录页 (pages/login/login.js)

**设计要点**:
- 微信一键登录
- 用户信息收集（昵称 + 头像）
- 协议勾选

**关键代码** (241行):
```javascript
Page({
  data: {
    isLogin: false,
    agreed: true,             // 默认同意协议
    showUserForm: false,      // 是否显示信息收集表单
    avatarUrl: '',
    nickname: '',
    loginCode: ''             // 微信登录code
  },

  /**
   * 微信一键登录
   */
  async handleWechatLogin() {
    if (!this.data.agreed) {
      wx.showToast({ title: '请先同意用户协议和隐私政策', icon: 'none' })
      return
    }

    try {
      wx.showLoading({ title: '登录中...', mask: true })

      // 1. 获取微信登录凭证
      const loginRes = await this.wxLogin()
      console.log('微信登录成功，code:', loginRes.code)

      wx.hideLoading()

      // 2. 显示用户信息填写表单
      this.setData({
        loginCode: loginRes.code,
        showUserForm: true
      })

    } catch (error) {
      wx.hideLoading()
      wx.showModal({
        title: '登录失败',
        content: '获取微信登录凭证失败，请重试',
        showCancel: false
      })
    }
  },

  /**
   * 完成登录
   */
  async handleCompleteLogin() {
    const { avatarUrl, nickname, loginCode } = this.data

    if (!nickname || nickname.trim() === '') {
      wx.showToast({ title: '请输入昵称', icon: 'none' })
      return
    }

    try {
      wx.showLoading({ title: '登录中...', mask: true })

      // 调用后端登录接口
      const loginData = await post(API_ENDPOINTS.USER_LOGIN, {
        code: loginCode,
        nickname: nickname.trim(),
        avatarUrl: ''
      })

      // 保存登录信息
      wx.setStorageSync(STORAGE_KEYS.SESSION_TOKEN, loginData.sessionToken)
      wx.setStorageSync(STORAGE_KEYS.USER_INFO, loginData.userInfo)

      // 更新全局状态
      app.login(loginData.userInfo)

      wx.hideLoading()

      // 跳转到首页
      wx.switchTab({ url: '/pages/home/home' })

    } catch (error) {
      wx.hideLoading()
      wx.showModal({
        title: '登录失败',
        content: error.message || '网络错误，请稍后重试',
        showCancel: false
      })
    }
  },

  /**
   * 微信登录
   */
  wxLogin() {
    return new Promise((resolve, reject) => {
      wx.login({
        success: (res) => {
          if (res.code) {
            resolve(res)
          } else {
            reject(new Error('获取登录凭证失败'))
          }
        },
        fail: reject
      })
    })
  }
})
```

**登录流程**:
```
用户点击"微信一键登录"
  ↓
调用wx.login()获取code
  ↓
显示用户信息表单（昵称 + 头像）
  ↓
用户填写昵称并选择头像
  ↓
提交到后端 POST /api/v1/auth/wechat/login
  ↓
保存sessionToken和userInfo到Storage
  ↓
更新app.globalData.isLogin = true
  ↓
跳转到首页
```

### 3.2 生成方案页 (pages/index/index.js)

**设计要点**:
- **两步表单**: Step 1基础信息 → Step 2偏好选择
- **实时验证**: 预算、日期、人数校验
- **计算字段**: 人均预算、行程天数
- **草稿保存**: 表单数据自动保存，24小时过期

**数据模型** (592行):
```javascript
Page({
  data: {
    currentStep: 1,  // 当前步骤

    // 表单数据
    formData: {
      peopleCount: 50,
      budgetMin: '',
      budgetMax: '',
      startDate: '',
      endDate: '',
      departureLocation: '',
      destination: '',
      preferences: {
        activityTypes: [],           // 活动类型（多选）
        accommodationLevel: 'standard', // 住宿标准（单选）
        diningStyle: [],             // 餐饮偏好（多选）
        specialRequirements: ''      // 特殊需求（文本）
      }
    },

    // 计算字段
    budgetPerPerson: '',  // 人均预算
    budgetWarning: '',    // 预算警告
    durationDays: '',     // 行程天数
    minDate: formatDate(new Date(), 'YYYY-MM-DD')
  },

  formModified: false,  // 表单修改标志
  initialFormData: null // 初始表单数据
})
```

**关键逻辑**:

#### 1) 人数选择（快捷按钮 + 步进器）
```javascript
// 快捷人数选择
handleQuickPeople(e) {
  const value = parseInt(e.currentTarget.dataset.value)
  this.setData({ 'formData.peopleCount': value })
  this.updateBudgetPerPerson()
  this.markFormModified()
}

// 人数变化
handlePeopleCountChange(e) {
  const value = e.detail.value
  this.setData({ 'formData.peopleCount': value })
  this.updateBudgetPerPerson()
  this.markFormModified()
}
```

#### 2) 预算计算（人均预算 + 警告）
```javascript
updateBudgetPerPerson() {
  const { peopleCount, budgetMin, budgetMax } = this.data.formData

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
}
```

#### 3) 日期选择（天数自动计算）
```javascript
handleStartDateChange(e) {
  const value = e.detail.value
  this.setData({ 'formData.startDate': value })
  this.updateDurationDays()
  this.markFormModified()
}

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
}
```

#### 4) 表单验证（Step 1）
```javascript
validateStep1() {
  const { peopleCount, budgetMin, budgetMax, startDate, endDate, departureLocation } = this.data.formData

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

  if (!departureLocation) {
    wx.showToast({ title: '请输入出发地点', icon: 'none' })
    return false
  }

  return true
}
```

#### 5) 生成方案（发送请求）
```javascript
async handleGenerate() {
  const { formData } = this.data

  try {
    wx.showLoading({ title: '正在生成方案...', mask: true })

    // 构建请求数据
    const requestData = {
      people_count: formData.peopleCount,
      budget_min: parseFloat(formData.budgetMin),
      budget_max: parseFloat(formData.budgetMax),
      start_date: formData.startDate,
      end_date: formData.endDate,
      departure_city: formData.departureLocation,  // 后端字段名
      destination: formData.destination || '',
      preferences: {
        activity_types: formData.preferences.activityTypes,
        accommodation_level: formData.preferences.accommodationLevel,
        dining_style: formData.preferences.diningStyle,
        special_requirements: formData.preferences.specialRequirements
      }
    }

    console.log('生成方案请求:', requestData)

    // 调用 API
    const result = await post(API_ENDPOINTS.PLAN_GENERATE, requestData, {
      showLoading: false,
      timeout: 120000  // 2分钟超时
    })

    wx.hideLoading()

    // 保存当前请求
    this.saveCurrentRequest()

    // 清除草稿
    this.clearDraft()

    // 跳转到对比页
    wx.navigateTo({
      url: `/pages/comparison/comparison?plans=${encodeURIComponent(JSON.stringify(result.plans))}`
    })

  } catch (error) {
    wx.hideLoading()
    wx.showModal({
      title: '生成失败',
      content: error.message || '请稍后重试',
      showCancel: true,
      confirmText: '重试',
      success: (res) => {
        if (res.confirm) {
          this.handleGenerate()
        }
      }
    })
  }
}
```

#### 6) 草稿保存（自动保存 + 恢复）
```javascript
/**
 * 保存草稿
 */
saveDraft() {
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
}

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
      wx.removeStorageSync(STORAGE_KEYS.DRAFT_REQUEST)
      return
    }

    // 检查当前表单是否为空
    const isCurrentFormEmpty = this.isFormEmpty()

    if (isCurrentFormEmpty) {
      this.showDraftRecoveryDialog(draft)
    }

  } catch (error) {
    console.error('检查草稿失败:', error)
  }
}

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
    success: (res) => {
      if (res.confirm) {
        this.recoverDraft(draft)
      } else {
        this.clearDraft()
      }
    }
  })
}
```

**页面生命周期**:
```javascript
onLoad(options) {
  // 检查登录状态
  if (!app.globalData.isLogin) {
    wx.redirectTo({ url: '/pages/login/login' })
    return
  }

  // 保存初始表单数据
  this.initialFormData = JSON.parse(JSON.stringify(this.data.formData))

  // 尝试恢复上次的输入
  this.loadLastRequest()
},

onShow() {
  // 更新最小日期
  this.setData({ minDate: formatDate(new Date(), 'YYYY-MM-DD') })

  // 检查草稿
  this.checkDraft()
},

onHide() {
  // 页面隐藏时自动保存草稿
  this.saveDraft()
}
```

### 3.3 我的方案页 (pages/myplans/myplans.js)

**设计要点**:
- 分页加载（Page + PageSize）
- 左滑删除交互
- 下拉刷新 + 触底加载更多
- 空状态提示

**关键代码** (301行):
```javascript
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

  /**
   * 加载方案列表
   */
  async loadPlans() {
    const { page, pageSize, plans, loadingMore } = this.data

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
      this.setData({ loading: false, loadingMore: false })
      wx.showToast({ title: '加载失败', icon: 'none' })
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
        relative_time: formatRelativeTime(plan.created_at),
        translateX: 0  // 左滑位移
      }
    })
  },

  /**
   * 左滑删除 - 触摸开始
   */
  handleTouchStart(e) {
    const touch = e.touches[0]
    this.setData({
      touchStartX: touch.clientX,
      touchStartY: touch.clientY
    })
  },

  /**
   * 左滑删除 - 触摸移动
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
        const translateX = Math.max(deltaX * 0.5, -160)  // 限制最大距离
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
   * 左滑删除 - 触摸结束
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

    // 二次确认
    const confirmResult = await this.showConfirmModal(
      '删除方案',
      '确定要删除此方案吗？'
    )

    if (!confirmResult) {
      this.setData({ [`plans[${index}].translateX`]: 0 })
      return
    }

    try {
      wx.showLoading({ title: '删除中...', mask: true })

      const endpoint = API_ENDPOINTS.PLAN_DETAIL.replace(':id', planId)
      await del(endpoint)

      wx.hideLoading()

      // 从列表中移除
      const plans = this.data.plans.filter((_, i) => i !== index)
      this.setData({ plans })

      wx.showToast({ title: '删除成功', icon: 'success' })

    } catch (error) {
      wx.hideLoading()
      this.setData({ [`plans[${index}].translateX`]: 0 })
      wx.showModal({
        title: '删除失败',
        content: error.message || '请稍后重试',
        showCancel: false
      })
    }
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

    this.setData({ page: this.data.page + 1 })
    this.loadPlans()
  }
})
```

**左滑删除交互示意**:
```
正常状态: translateX = 0
  ↓
用户左滑（deltaX < -10）
  ↓
translateX = deltaX * 0.5（阻尼效果）
  ↓
触摸结束：
  - 滑动距离 > 80px → translateX = -160px（显示删除按钮）
  - 滑动距离 < 80px → translateX = 0（恢复）
  ↓
点击删除按钮
  ↓
二次确认弹窗
  ↓
调用DELETE API
  ↓
从列表移除
```

### 3.4 方案对比页 (pages/comparison/comparison.js)

**设计要点**:
- 3套方案并列展示（经济型、标准型、品质型）
- 横向滑动切换
- 一键选择方案
- 返回重新生成

**数据模型**:
```javascript
Page({
  data: {
    plans: [],  // 3套方案
    currentIndex: 1  // 当前查看的方案（默认标准型）
  },

  onLoad(options) {
    // 从URL参数获取方案
    const plansParam = options.plans
    if (plansParam) {
      const plans = JSON.parse(decodeURIComponent(plansParam))
      this.setData({ plans })
    }
  }
})
```

### 3.5 方案详情页 (pages/detail/detail.js)

**设计要点**:
- 方案概览（名称、预算、天数、类型）
- 行程安排（按天展示）
- 预算明细（分项展示）
- 供应商信息（联系方式、地图位置）
- 确认方案按钮

**关键功能**:
```javascript
/**
 * 确认方案
 */
async handleConfirmPlan() {
  try {
    wx.showLoading({ title: '确认中...', mask: true })

    await post(`/api/v1/plans/${this.data.planId}/confirm`)

    wx.hideLoading()

    wx.showToast({
      title: '确认成功',
      icon: 'success',
      duration: 2000
    })

    // 更新状态
    this.setData({ 'plan.status': 'CONFIRMED' })

  } catch (error) {
    wx.hideLoading()
    wx.showModal({
      title: '确认失败',
      content: error.message || '请稍后重试',
      showCancel: false
    })
  }
}

/**
 * 联系供应商
 */
handleContactSupplier(e) {
  const supplier = e.currentTarget.dataset.supplier

  wx.showActionSheet({
    itemList: ['拨打电话', '查看位置', '复制联系方式'],
    success: (res) => {
      switch (res.tapIndex) {
        case 0:  // 拨打电话
          makePhoneCall(supplier.phone)
          break
        case 1:  // 查看位置
          wx.openLocation({
            latitude: supplier.latitude,
            longitude: supplier.longitude,
            name: supplier.name,
            address: supplier.address
          })
          break
        case 2:  // 复制联系方式
          copyToClipboard(supplier.contact)
          break
      }
    }
  })
}
```

---

## 4. 网络请求封装

### 4.1 request.js 设计 (327行)

**核心功能**:
- 统一请求方法
- Token自动添加
- 错误统一处理
- Mock数据支持
- 超时控制

**完整实现**:
```javascript
import { API_BASE_URL, REQUEST_TIMEOUT, STORAGE_KEYS, ERROR_CODES, ERROR_MESSAGES, USE_MOCK_DATA } from './config.js'
import { mockPlans } from './mock-data.js'

let unauthorizedRedirectInProgress = false

/**
 * 统一请求方法
 */
function request(url, method = 'GET', data = {}, options = {}) {
  return new Promise((resolve, reject) => {
    // 🧪 测试模式：使用模拟数据
    if (USE_MOCK_DATA) {
      return handleMockRequest(url, method, data, options, resolve, reject)
    }

    // 获取 session token
    const sessionToken = wx.getStorageSync(STORAGE_KEYS.SESSION_TOKEN)

    // 构建完整 URL
    const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`

    // 请求头
    const header = {
      'Content-Type': 'application/json',
      ...options.header
    }

    // 添加 token
    if (sessionToken) {
      header['Authorization'] = `Bearer ${sessionToken}`
    }

    // 显示加载提示
    if (options.showLoading !== false) {
      wx.showLoading({
        title: options.loadingText || '加载中...',
        mask: true
      })
    }

    wx.request({
      url: fullUrl,
      method: method,
      data: data,
      header: header,
      timeout: options.timeout || REQUEST_TIMEOUT,
      success: (res) => {
        if (options.showLoading !== false) {
          wx.hideLoading()
        }

        console.log(`[API ${method}] ${url}`, { data, response: res })

        // 处理响应
        if (res.statusCode === 200) {
          // 成功响应
          if (res.data && res.data.success) {
            resolve(res.data.data)
          } else {
            // 业务错误
            const errorMsg = res.data?.error?.message || '请求失败'
            handleError(errorMsg, res.data?.error?.code, options)
            reject(res.data?.error || { message: errorMsg })
          }
        } else if (res.statusCode === 401) {
          // 未授权
          handleUnauthorized()
          reject({ code: ERROR_CODES.UNAUTHORIZED, message: ERROR_MESSAGES[ERROR_CODES.UNAUTHORIZED] })
        } else {
          // HTTP 错误
          const errorMsg = `请求失败 (${res.statusCode})`
          handleError(errorMsg, null, options)
          reject({ message: errorMsg })
        }
      },
      fail: (error) => {
        if (options.showLoading !== false) {
          wx.hideLoading()
        }

        console.error(`[API ${method}] ${url} 失败:`, error)

        let errorCode = ERROR_CODES.NETWORK_ERROR
        let errorMsg = ERROR_MESSAGES[ERROR_CODES.NETWORK_ERROR]

        if (error.errMsg && error.errMsg.includes('timeout')) {
          errorCode = ERROR_CODES.TIMEOUT
          errorMsg = ERROR_MESSAGES[ERROR_CODES.TIMEOUT]
        }

        handleError(errorMsg, errorCode, options)
        reject({ code: errorCode, message: errorMsg })
      }
    })
  })
}

/**
 * 处理未授权（跳转到登录页）
 */
function handleUnauthorized() {
  if (unauthorizedRedirectInProgress) return
  unauthorizedRedirectInProgress = true

  // 清除登录信息
  wx.removeStorageSync(STORAGE_KEYS.SESSION_TOKEN)
  wx.removeStorageSync(STORAGE_KEYS.USER_INFO)

  wx.showToast({
    title: '登录已过期，请重新登录',
    icon: 'none',
    duration: 2000
  })

  const resetFlag = () => {
    setTimeout(() => {
      unauthorizedRedirectInProgress = false
    }, 500)
  }

  wx.reLaunch({
    url: '/pages/login/login',
    success: resetFlag,
    fail: resetFlag
  })
}

/**
 * GET 请求
 */
export function get(url, data = {}, options = {}) {
  return request(url, 'GET', data, options)
}

/**
 * POST 请求
 */
export function post(url, data = {}, options = {}) {
  return request(url, 'POST', data, options)
}

/**
 * PUT 请求
 */
export function put(url, data = {}, options = {}) {
  return request(url, 'PUT', data, options)
}

/**
 * DELETE 请求
 */
export function del(url, data = {}, options = {}) {
  return request(url, 'DELETE', data, options)
}

/**
 * 上传文件
 */
export function uploadFile(url, filePath, options = {}) {
  return new Promise((resolve, reject) => {
    const sessionToken = wx.getStorageSync(STORAGE_KEYS.SESSION_TOKEN)
    const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`

    if (options.showLoading !== false) {
      wx.showLoading({ title: '上传中...', mask: true })
    }

    wx.uploadFile({
      url: fullUrl,
      filePath: filePath,
      name: options.name || 'file',
      header: {
        'Authorization': sessionToken ? `Bearer ${sessionToken}` : ''
      },
      formData: options.formData || {},
      success: (res) => {
        wx.hideLoading()
        if (res.statusCode === 200) {
          try {
            const data = JSON.parse(res.data)
            resolve(data)
          } catch (e) {
            resolve(res.data)
          }
        } else {
          handleError('上传失败', null, options)
          reject(res)
        }
      },
      fail: (error) => {
        wx.hideLoading()
        handleError('上传失败', null, options)
        reject(error)
      }
    })
  })
}
```

**设计要点**:
- **Token自动添加**: 从Storage读取，自动添加到Authorization header
- **401自动跳转**: 检测到401错误自动清除登录信息并跳转登录页
- **防抖处理**: `unauthorizedRedirectInProgress`防止多次401导致重复跳转
- **Loading管理**: 支持`showLoading: false`禁用加载提示
- **超时控制**: 默认30秒，可自定义

### 4.2 Mock数据支持

**配置开关** (config.js):
```javascript
export const USE_MOCK_DATA = false  // true: 使用Mock数据
```

**Mock数据处理** (request.js):
```javascript
function handleMockRequest(url, method, data, options, resolve, reject) {
  console.log(`[MOCK ${method}] ${url}`, data)

  // 模拟网络延迟
  setTimeout(() => {
    if (options.showLoading !== false) {
      wx.hideLoading()
    }

    try {
      let mockResponse = null

      // 方案生成
      if (url === API_ENDPOINTS.PLAN_GENERATE) {
        mockResponse = {
          plans: mockPlans,
          request_id: 'mock_req_' + Date.now()
        }
      }
      // 方案列表
      else if (url === API_ENDPOINTS.PLAN_LIST) {
        mockResponse = {
          plans: mockPlans,
          total: mockPlans.length
        }
      }
      // 用户登录
      else if (url === API_ENDPOINTS.USER_LOGIN) {
        mockResponse = {
          sessionToken: 'mock_token_' + Date.now(),
          userInfo: {
            user_id: 'mock_user_001',
            nickname: data.nickname || '测试用户',
            avatar: data.avatarUrl || ''
          }
        }
      }

      resolve(mockResponse)

    } catch (error) {
      reject({ code: ERROR_CODES.GENERATION_FAILED, message: '模拟数据处理失败' })
    }
  }, 800)  // 模拟 800ms 网络延迟
}
```

---

## 5. 状态管理

### 5.1 全局状态 (app.js)

**globalData定义**:
```javascript
App({
  globalData: {
    isLogin: false,      // 登录状态
    userInfo: null,      // 用户信息
    systemInfo: null     // 系统信息
  },

  /**
   * 检查登录状态
   */
  checkLoginStatus() {
    const sessionToken = wx.getStorageSync('sessionToken')
    const userInfo = wx.getStorageSync('userInfo')

    if (sessionToken && userInfo) {
      this.globalData.isLogin = true
      this.globalData.userInfo = userInfo
    } else {
      this.globalData.isLogin = false
    }
  },

  /**
   * 登录
   */
  login(userInfo) {
    this.globalData.isLogin = true
    this.globalData.userInfo = userInfo
    wx.setStorageSync('userInfo', userInfo)
  },

  /**
   * 退出登录
   */
  logout() {
    this.globalData.isLogin = false
    this.globalData.userInfo = null
    wx.removeStorageSync('sessionToken')
    wx.removeStorageSync('userInfo')
  }
})
```

**版本检查（清除旧数据）**:
```javascript
onLaunch(options) {
  const APP_VERSION = '1.0.1'
  const storedVersion = wx.getStorageSync('appVersion')

  if (storedVersion !== APP_VERSION) {
    console.log('检测到版本更新，清除旧数据...')
    wx.clearStorageSync()
    wx.setStorageSync('appVersion', APP_VERSION)
  }

  this.checkLoginStatus()
  this.getSystemInfo()
}
```

### 5.2 LocalStorage使用策略

**存储键定义** (config.js):
```javascript
export const STORAGE_KEYS = {
  SESSION_TOKEN: 'sessionToken',       // JWT Token
  USER_INFO: 'userInfo',               // 用户信息
  LATEST_REQUEST: 'latestRequest',     // 最近一次请求数据
  DRAFT_REQUEST: 'draftRequest',       // 草稿数据
  APP_VERSION: 'appVersion'            // 应用版本号
}
```

**存储数据结构**:
```javascript
// sessionToken (String)
"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

// userInfo (Object)
{
  "user_id": "user_01ke3abc123",
  "nickname": "张三",
  "avatar": "https://...",
  "phone": "",
  "company": ""
}

// latestRequest (Object)
{
  "peopleCount": 50,
  "budgetMin": "10000",
  "budgetMax": "15000",
  "startDate": "2026-02-01",
  "endDate": "2026-02-03",
  "departureLocation": "Beijing",
  "preferences": {...}
}

// draftRequest (Object)
{
  "formData": {...},
  "currentStep": 1,
  "timestamp": 1735968000000  // 用于判断过期
}
```

### 5.3 页面间数据传递

#### 1) URL参数传递（适合少量数据）
```javascript
// 跳转时传递planId
wx.navigateTo({
  url: `/pages/detail/detail?planId=${planId}`
})

// 接收页面
onLoad(options) {
  const planId = options.planId
}
```

#### 2) encodeURIComponent传递复杂数据
```javascript
// 跳转时传递3套方案
wx.navigateTo({
  url: `/pages/comparison/comparison?plans=${encodeURIComponent(JSON.stringify(plans))}`
})

// 接收页面
onLoad(options) {
  const plans = JSON.parse(decodeURIComponent(options.plans))
}
```

#### 3) Storage传递大数据
```javascript
// 发送页面
wx.setStorageSync('tempData', largeData)
wx.navigateTo({ url: '/pages/target/target' })

// 接收页面
onLoad() {
  const data = wx.getStorageSync('tempData')
  wx.removeStorageSync('tempData')
}
```

---

## 6. 性能优化

### 6.1 草稿自动保存

**策略**:
- 页面隐藏时自动保存（onHide）
- 24小时过期自动删除
- 页面显示时检测并提示恢复

**实现** (在index/index.js中):
```javascript
onHide() {
  this.saveDraft()  // 自动保存
},

checkDraft() {
  const draft = wx.getStorageSync(STORAGE_KEYS.DRAFT_REQUEST)
  if (!draft || !draft.timestamp) return

  const hoursPassed = (Date.now() - draft.timestamp) / (1000 * 60 * 60)
  if (hoursPassed > 24) {
    wx.removeStorageSync(STORAGE_KEYS.DRAFT_REQUEST)
    return
  }

  if (this.isFormEmpty()) {
    this.showDraftRecoveryDialog(draft)
  }
}
```

### 6.2 分页加载

**实现** (在myplans/myplans.js中):
```javascript
data: {
  page: 1,
  pageSize: 10,
  hasMore: true,
  loadingMore: false
},

async loadPlans() {
  if (this.data.loadingMore) return

  this.setData({ loadingMore: true })

  const result = await get(API_ENDPOINTS.PLAN_LIST, {
    page: this.data.page,
    pageSize: this.data.pageSize
  })

  this.setData({
    plans: [...this.data.plans, ...result.plans],
    hasMore: result.hasMore !== false,
    loadingMore: false
  })
},

onReachBottom() {
  if (!this.data.hasMore || this.data.loadingMore) return

  this.setData({ page: this.data.page + 1 })
  this.loadPlans()
}
```

### 6.3 防抖节流

**防抖实现** (util.js):
```javascript
export function debounce(fn, delay = 300) {
  let timer = null
  return function(...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

// 使用示例
const debouncedSearch = debounce(function(keyword) {
  console.log('搜索:', keyword)
}, 500)
```

**节流实现** (util.js):
```javascript
export function throttle(fn, interval = 300) {
  let lastTime = 0
  return function(...args) {
    const now = Date.now()
    if (now - lastTime >= interval) {
      lastTime = now
      fn.apply(this, args)
    }
  }
}

// 使用示例
const throttledScroll = throttle(function() {
  console.log('滚动事件')
}, 200)
```

### 6.4 按需加载

**配置** (app.json):
```json
{
  "lazyCodeLoading": "requiredComponents"
}
```

**效果**: 仅加载当前页面需要的组件，减少首屏加载时间

---

## 7. 组件设计

### 7.1 stepper组件 (数字步进器)

**功能**: 数字增减控制器，用于人数选择

**props**:
```javascript
properties: {
  value: {
    type: Number,
    value: 1
  },
  min: {
    type: Number,
    value: 1
  },
  max: {
    type: Number,
    value: 999
  },
  step: {
    type: Number,
    value: 1
  },
  disabled: {
    type: Boolean,
    value: false
  }
}
```

**事件**:
```javascript
methods: {
  handleMinus() {
    const newValue = Math.max(this.data.min, this.data.value - this.data.step)
    this.setData({ value: newValue })
    this.triggerEvent('change', { value: newValue })
  },

  handlePlus() {
    const newValue = Math.min(this.data.max, this.data.value + this.data.step)
    this.setData({ value: newValue })
    this.triggerEvent('change', { value: newValue })
  },

  handleInput(e) {
    let value = parseInt(e.detail.value) || this.data.min
    value = Math.max(this.data.min, Math.min(this.data.max, value))
    this.setData({ value })
    this.triggerEvent('change', { value })
  }
}
```

**使用示例**:
```html
<stepper
  value="{{formData.peopleCount}}"
  min="1"
  max="999"
  step="1"
  bind:change="handlePeopleCountChange"
/>
```

---

## 8. 工具函数库

### 8.1 util.js (340行)

**核心功能**:

#### 1) 日期格式化
```javascript
export function formatDate(date, format = 'YYYY-MM-DD') {
  if (!date) return ''

  const d = new Date(date)
  if (isNaN(d.getTime())) return ''

  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hour = String(d.getHours()).padStart(2, '0')
  const minute = String(d.getMinutes()).padStart(2, '0')
  const second = String(d.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hour)
    .replace('mm', minute)
    .replace('ss', second)
}
```

#### 2) 相对时间
```javascript
export function formatRelativeTime(date) {
  const now = new Date()
  const diff = now - new Date(date)
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 7) return formatDate(date, 'YYYY-MM-DD')
  if (days > 0) return `${days}天前`
  if (hours > 0) return `${hours}小时前`
  if (minutes > 0) return `${minutes}分钟前`
  return '刚刚'
}
```

#### 3) 金额格式化
```javascript
export function formatMoney(amount, showSymbol = true) {
  if (typeof amount !== 'number') return '0'

  const formatted = amount.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
  return showSymbol ? `¥${formatted}` : formatted
}

export function formatPerPerson(total, peopleCount) {
  if (!peopleCount || peopleCount <= 0) return '¥0'
  const perPerson = Math.round(total / peopleCount)
  return `¥${perPerson}/人`
}
```

#### 4) 天数计算
```javascript
export function calculateDays(startDate, endDate) {
  if (!startDate || !endDate) return 0

  const start = new Date(startDate)
  const end = new Date(endDate)

  const diff = end - start
  const days = Math.ceil(diff / (1000 * 60 * 60 * 24)) + 1

  return days > 0 ? days : 0
}

export function formatDuration(days) {
  if (days <= 0) return ''
  if (days === 1) return '1天'
  return `${days}天${days - 1}夜`
}
```

#### 5) 脱敏处理
```javascript
export function maskPhone(phone) {
  if (!phone || phone.length !== 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

export function maskEmail(email) {
  if (!email || !email.includes('@')) return email
  const [username, domain] = email.split('@')
  const maskedUsername = username.length > 3
    ? username.substring(0, 3) + '****'
    : username + '****'
  return `${maskedUsername}@${domain}`
}
```

#### 6) 微信能力封装
```javascript
export function makePhoneCall(phone) {
  wx.makePhoneCall({
    phoneNumber: phone,
    fail: (error) => {
      console.error('拨打电话失败:', error)
      wx.showToast({ title: '拨打失败', icon: 'none' })
    }
  })
}

export function copyToClipboard(text, successMsg = '复制成功') {
  wx.setClipboardData({
    data: text,
    success: () => {
      wx.showToast({ title: successMsg, icon: 'success' })
    },
    fail: (error) => {
      wx.showToast({ title: '复制失败', icon: 'none' })
    }
  })
}

export function previewImage(current, urls = []) {
  wx.previewImage({
    current: current,
    urls: urls.length ? urls : [current]
  })
}
```

---

## 附录

### A. 关键文件清单

**页面文件** (7个页面):
- `pages/home/home.js` - 首页
- `pages/index/index.js` - 生成方案页 (592行)
- `pages/myplans/myplans.js` - 我的方案页 (301行)
- `pages/profile/profile.js` - 个人中心页
- `pages/login/login.js` - 登录页 (241行)
- `pages/comparison/comparison.js` - 方案对比页
- `pages/detail/detail.js` - 方案详情页

**工具文件** (4个):
- `utils/request.js` - 网络请求封装 (327行)
- `utils/config.js` - 配置文件
- `utils/util.js` - 通用工具函数 (340行)
- `utils/mock-data.js` - Mock数据

**组件文件** (1个):
- `components/stepper/stepper.js` - 数字步进器组件

**全局文件** (3个):
- `app.js` - 小程序入口 (87行)
- `app.json` - 全局配置
- `app.wxss` - 全局样式

### B. API端点清单

**认证接口**:
- `POST /api/v1/auth/wechat/login`

**方案接口**:
- `POST /api/v1/plans/generate`
- `GET /api/v1/plans?page=1&pageSize=10`
- `GET /api/v1/plans/{planId}`
- `POST /api/v1/plans/{planId}/confirm`
- `POST /api/v1/plans/{planId}/supplier-contacts`

**供应商接口**:
- `GET /api/v1/suppliers/search?city=Beijing&category=accommodation`
- `GET /api/v1/suppliers/{supplierId}`

### C. 最佳实践

1. **命名规范**:
   - 页面文件: `pages/page-name/page-name.js`
   - 组件文件: `components/component-name/component-name.js`
   - 函数命名: 驼峰命名法 `handleClickButton`

2. **代码组织**:
   - 将复杂逻辑拆分为独立方法
   - 使用`try-catch`捕获异步错误
   - 及时清理定时器和监听器

3. **性能优化**:
   - 避免在`setData`中传递大对象
   - 使用`data-*`属性传递参数
   - 合理使用分页和懒加载

4. **用户体验**:
   - 所有异步操作提供Loading提示
   - 错误信息友好且可操作
   - 关键操作二次确认

---

**文档版本**: v1.0
**最后更新**: 2026-01-04
**维护者**: TeamVenture开发团队
