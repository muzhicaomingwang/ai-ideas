// 配置文件

// 🧪 测试模式开关（本地测试时设为 true，使用模拟数据）
export const USE_MOCK_DATA = false

// 环境配置
const ENV = 'local' // local | dev | beta | prod

// API 基础地址配置
const API_BASE_URLS = {
  local: 'https://api.teamventure.com/api/v1',     // 本地开发环境（/etc/hosts绑定 + HTTPS）
  dev: 'https://dev-api.teamventure.com/api/v1',   // 开发环境
  beta: 'https://beta-api.teamventure.com/api/v1', // 测试环境
  prod: 'https://api.teamventure.com/api/v1'       // 生产环境
}

// 当前环境的 API 基础地址
export const API_BASE_URL = API_BASE_URLS[ENV]

// API 端点
export const API_ENDPOINTS = {
  // 用户相关
  USER_LOGIN: '/auth/wechat/login',
  USER_REGISTER: '/users/register',
  USER_INFO: '/users/info',

  // 方案相关
  PLAN_GENERATE: '/plans/generate',
  PLAN_LIST: '/plans',
  PLAN_DETAIL: '/plans/:id',
  PLAN_EXPORT: '/plans/:id/export',
  PLAN_CONFIRM: '/plans/:id/confirm',

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
  DRAFT_REQUEST: 'draftRequest'  // 草稿数据（自动保存）
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

// 方案状态
export const PLAN_STATUS = {
  DRAFT: 'draft',
  CONFIRMED: 'confirmed',
  CANCELLED: 'cancelled'
}

// 方案状态名称映射
export const PLAN_STATUS_NAMES = {
  [PLAN_STATUS.DRAFT]: '草稿',
  [PLAN_STATUS.CONFIRMED]: '已确认',
  [PLAN_STATUS.CANCELLED]: '已取消'
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

// 餐饮偏好
export const DINING_PREFERENCES = [
  { value: 'local', label: '农家菜' },
  { value: 'bbq', label: '烧烤' },
  { value: 'hotpot', label: '火锅' },
  { value: 'western', label: '西餐' }
]

// 错误码
export const ERROR_CODES = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT: 'TIMEOUT',
  UNAUTHORIZED: 'UNAUTHORIZED',
  BUDGET_TOO_LOW: 'BUDGET_TOO_LOW',
  NO_SUPPLIERS: 'NO_SUPPLIERS',
  GENERATION_FAILED: 'GENERATION_FAILED'
}

// 错误消息映射
export const ERROR_MESSAGES = {
  [ERROR_CODES.NETWORK_ERROR]: '网络连接失败，请检查网络设置',
  [ERROR_CODES.TIMEOUT]: '请求超时，请稍后重试',
  [ERROR_CODES.UNAUTHORIZED]: '登录已过期，请重新登录',
  [ERROR_CODES.BUDGET_TOO_LOW]: '预算不足，请调整预算或缩减需求',
  [ERROR_CODES.NO_SUPPLIERS]: '未找到符合条件的供应商',
  [ERROR_CODES.GENERATION_FAILED]: '方案生成失败，请稍后重试'
}
