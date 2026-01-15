// 配置文件

// 🧪 测试模式开关（本地测试时设为 true，使用模拟数据）
export const USE_MOCK_DATA = false

// 环境配置
// - develop: 本地联调（local）
// - trial:  测试环境（beta）
// - release: 生产环境（prod）
//
// 可通过本地存储覆盖：wx.setStorageSync('apiEnv', 'dev'|'beta'|'prod'|'local')
const DEFAULT_ENV = 'local' // local | dev | beta | prod

function detectEnv() {
  try {
    const baseUrlOverride = wx.getStorageSync('apiBaseUrl')
    if (baseUrlOverride) return 'local'

    const override = wx.getStorageSync('apiEnv')
    if (override) return override

    const info = wx.getAccountInfoSync?.()
    const envVersion = info?.miniProgram?.envVersion

    if (envVersion === 'release') return 'prod'
    if (envVersion === 'trial') return 'beta'
    if (envVersion === 'develop') return 'local'
  } catch (e) {
    // ignore
  }
  return DEFAULT_ENV
}

const ENV = detectEnv()

// API 基础地址配置
const API_BASE_URLS = {
  local: 'http://api.teamventure.com/api/v1', // 本地开发环境（通过Nginx网关，需配置 /etc/hosts: 127.0.0.1 api.teamventure.com）
  dev: 'https://dev-api.teamventure.com/api/v1', // 开发环境
  beta: 'https://beta-api.teamventure.com/api/v1', // 测试环境
  prod: 'https://api.teamventure.com/api/v1' // 生产环境
}

// 当前环境的 API 基础地址
const storedApiBaseUrl = wx.getStorageSync('apiBaseUrl')
console.log('[DEBUG config.js] storedApiBaseUrl:', JSON.stringify(storedApiBaseUrl))
console.log('[DEBUG config.js] ENV:', ENV)
console.log('[DEBUG config.js] API_BASE_URLS[ENV]:', JSON.stringify(API_BASE_URLS[ENV]))

export const API_BASE_URL = storedApiBaseUrl || API_BASE_URLS[ENV]
console.log('[DEBUG config.js] 最终API_BASE_URL:', JSON.stringify(API_BASE_URL))

export const CURRENT_ENV = ENV

// API 端点
export const API_ENDPOINTS = {
  // 用户相关
  USER_LOGIN: '/auth/wechat/login',
  USER_REFRESH: '/auth/wechat/refresh',
  USER_REGISTER: '/users/register',
  USER_INFO: '/users/info',

  // 方案相关
  PLAN_GENERATE: '/plans/generate',
  PLAN_LIST: '/plans',
  PLAN_DETAIL: '/plans/:id',
  PLAN_EXPORT: '/plans/:id/export',
  PLAN_CONFIRM: '/plans/:id/confirm',
  PLAN_SUBMIT_REVIEW: '/plans/:id/submit-review',
  PLAN_REVERT_REVIEW: '/plans/:id/revert-review',
  PLAN_ARCHIVE: '/plans/:id/archive',
  PLAN_UPDATE_ITINERARY: '/plans/:id/itinerary',
  PLAN_ROUTE: '/plans/:id/route',

  // 供应商相关
  SUPPLIER_SEARCH: '/suppliers/search',
  SUPPLIER_DETAIL: '/suppliers/:id',
  SUPPLIER_CONTACT: '/suppliers/:id/contact'
}

// 请求超时时间（毫秒）
export const REQUEST_TIMEOUT = 60000

// 存储 keys
export const STORAGE_KEYS = {
  SESSION_TOKEN: 'sessionToken',
  USER_INFO: 'userInfo',
  LATEST_REQUEST: 'latestRequest',
  DRAFT_REQUEST: 'draftRequest' // 草稿数据（自动保存）
}

// 方案类型
export const PLAN_TYPES = {
  BUDGET: 'budget',
  STANDARD: 'standard',
  PREMIUM: 'premium'
}

// 方案类型名称映射
export const PLAN_TYPE_NAMES = {
  [PLAN_TYPES.BUDGET]: '经济型',
  [PLAN_TYPES.STANDARD]: '平衡型',
  [PLAN_TYPES.PREMIUM]: '品质型'
}

// 方案状态（与后端 api-design.md v1.5 保持一致，共 6 种状态）
export const PLAN_STATUS = {
  GENERATING: 'generating',
  FAILED: 'failed',
  DRAFT: 'draft',
  REVIEWING: 'reviewing',
  CONFIRMED: 'confirmed',
  ARCHIVED: 'archived'
}

// 方案状态名称映射（与后端 api-design.md v1.5 保持一致）
export const PLAN_STATUS_NAMES = {
  [PLAN_STATUS.GENERATING]: '生成中',
  [PLAN_STATUS.FAILED]: '生成失败',
  [PLAN_STATUS.DRAFT]: '制定完成',
  [PLAN_STATUS.REVIEWING]: '通晒中',
  [PLAN_STATUS.CONFIRMED]: '已确认',
  [PLAN_STATUS.ARCHIVED]: '已归档'
}

// 活动类型
export const ACTIVITY_TYPES = [
  { value: 'team_building', label: '团队拓展' },
  { value: 'leisure', label: '休闲度假' },
  { value: 'culture', label: '文化体验' },
  { value: 'sports', label: '运动挑战' }
]

// 住宿标准
export const ACCOMMODATION_LEVELS = [
  { value: 'budget', label: '经济型' },
  { value: 'standard', label: '舒适型' },
  { value: 'premium', label: '品质型' }
]

// 行程类型
export const TRIP_TYPES = [
  {
    value: 'regional',
    label: '周边游',
    icon: '🚗',
    description: '周边城市2-3天短途'
  },
  {
    value: 'domestic',
    label: '国内游',
    icon: '✈️',
    description: '国内跨省长途旅行'
  },
  {
    value: 'international',
    label: '出境游',
    icon: '🌏',
    description: '出国旅行'
  },
  {
    value: 'custom',
    label: '自定义',
    icon: '✏️',
    description: '自由描述行程需求'
  }
]

// 错误码
export const ERROR_CODES = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT: 'TIMEOUT',
  UNAUTHORIZED: 'UNAUTHORIZED',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  BUDGET_TOO_LOW: 'BUDGET_TOO_LOW',
  NO_SUPPLIERS: 'NO_SUPPLIERS',
  GENERATION_FAILED: 'GENERATION_FAILED'
}

// 错误消息映射
export const ERROR_MESSAGES = {
  [ERROR_CODES.NETWORK_ERROR]: '网络连接失败，请检查网络设置或后端服务是否已启动',
  [ERROR_CODES.TIMEOUT]: '请求超时，请稍后重试',
  [ERROR_CODES.UNAUTHORIZED]: '登录已过期，请重新登录',
  [ERROR_CODES.VALIDATION_ERROR]: '参数校验失败，请检查输入内容',
  [ERROR_CODES.BUDGET_TOO_LOW]: '预算不足，请调整预算或缩减需求',
  [ERROR_CODES.NO_SUPPLIERS]: '未找到符合条件的供应商',
  [ERROR_CODES.GENERATION_FAILED]: '方案生成失败，请稍后重试'
}
