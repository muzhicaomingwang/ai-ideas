// 网络请求封装
import { API_BASE_URL, CURRENT_ENV, REQUEST_TIMEOUT, STORAGE_KEYS, ERROR_CODES, ERROR_MESSAGES, USE_MOCK_DATA, API_ENDPOINTS } from './config.js'
import { mockPlans } from './mock-data.js'

let unauthorizedRedirectInProgress = false
let tokenRefreshInProgress = null // Promise for ongoing refresh, prevents concurrent refreshes

/**
 * 刷新 Token（如果即将过期）
 * Token Refresh: 自动检测token即将过期并刷新，实现无感续期
 *
 * 术语对照（ubiquitous-language-glossary.md Section 4.4）:
 *   - Token刷新 = Token Refresh = refreshTokenIfNeeded
 *   - 会话令牌 = Session Token = STORAGE_KEYS.SESSION_TOKEN
 *
 * 触发条件:
 *   - 每次API请求前自动调用（除登录和刷新接口本身）
 *   - 后端判断token剩余有效期 < 12小时时返回新token
 *
 * 并发控制:
 *   - 使用 tokenRefreshInProgress Promise 防止多个请求同时触发刷新
 *
 * 返回值:
 *   - true: 刷新成功或无需刷新
 *   - false: 刷新失败，需要重新登录
 *
 * 参考:
 *   - API设计: api-design.md Section 2.4
 *   - 后端实现: AuthService.refreshTokenIfNeeded
 */
async function refreshTokenIfNeeded() {
  const sessionToken = wx.getStorageSync(STORAGE_KEYS.SESSION_TOKEN)
  if (!sessionToken) {
    return false
  }

  // 防止并发刷新
  if (tokenRefreshInProgress) {
    return tokenRefreshInProgress
  }

  tokenRefreshInProgress = new Promise((resolve) => {
    const fullUrl = `${API_BASE_URL}${API_ENDPOINTS.USER_REFRESH}`

    wx.request({
      url: fullUrl,
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${sessionToken}`
      },
      timeout: 10000,
      success: (res) => {
        if (res.statusCode === 200 && res.data && res.data.success) {
          const data = res.data.data
          // 后端返回 null 表示 token 仍然有效，无需刷新
          if (data && data.sessionToken) {
            // 更新存储的 token 和用户信息
            wx.setStorageSync(STORAGE_KEYS.SESSION_TOKEN, data.sessionToken)
            if (data.userInfo) {
              wx.setStorageSync(STORAGE_KEYS.USER_INFO, data.userInfo)
            }
            console.log('[Token] 已自动刷新')
            resolve(true)
          } else {
            console.log('[Token] 仍然有效，无需刷新')
            resolve(true)
          }
        } else if (res.statusCode === 401) {
          console.log('[Token] 刷新失败，需要重新登录')
          resolve(false)
        } else {
          console.log('[Token] 刷新请求异常:', res.statusCode)
          resolve(true) // 非 401 错误不阻止后续请求
        }
      },
      fail: (error) => {
        console.warn('[Token] 刷新请求失败:', { env: CURRENT_ENV, url: fullUrl, error })
        resolve(true) // 网络错误不阻止后续请求
      },
      complete: () => {
        tokenRefreshInProgress = null
      }
    })
  })

  return tokenRefreshInProgress
}

/**
 * 统一请求方法
 * @param {String} url - 请求地址
 * @param {String} method - 请求方法 GET/POST/PUT/DELETE
 * @param {Object} data - 请求数据
 * @param {Object} options - 其他配置
 * @returns {Promise}
 */
async function request(url, method = 'GET', data = {}, options = {}) {
  // 🧪 测试模式：使用模拟数据
  if (USE_MOCK_DATA) {
    return new Promise((resolve, reject) => {
      handleMockRequest(url, method, data, options, resolve, reject)
    })
  }

  // 在请求前尝试刷新 Token（跳过登录和刷新请求本身）
  if (url !== API_ENDPOINTS.USER_LOGIN && url !== API_ENDPOINTS.USER_REFRESH) {
    const refreshResult = await refreshTokenIfNeeded()
    if (refreshResult === false) {
      // Token 无效且刷新失败，需要重新登录
      handleUnauthorized()
      return Promise.reject({ code: ERROR_CODES.UNAUTHORIZED, message: ERROR_MESSAGES[ERROR_CODES.UNAUTHORIZED] })
    }
  }

  return new Promise((resolve, reject) => {
    // 获取 session token（刷新后可能已更新）
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
      header.Authorization = `Bearer ${sessionToken}`
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
      method,
      data,
      header,
      timeout: options.timeout || REQUEST_TIMEOUT,
      success: (res) => {
        // 隐藏加载提示
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
        // 隐藏加载提示
        if (options.showLoading !== false) {
          wx.hideLoading()
        }

        console.error(`[API ${method}] ${url} 失败:`, { env: CURRENT_ENV, baseUrl: API_BASE_URL, fullUrl, error })

        // 判断错误类型
        let errorCode = ERROR_CODES.NETWORK_ERROR
        let errorMsg = ERROR_MESSAGES[ERROR_CODES.NETWORK_ERROR]

        const rawErrMsg = error?.errMsg || ''
        if (/ECONNREFUSED|ERR_CONNECTION_REFUSED/i.test(rawErrMsg)) {
          errorMsg = `连接被拒绝：后端服务未启动或端口不可达（${API_BASE_URL}）`
        }

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
 * 🧪 处理模拟请求（测试模式）
 */
function handleMockRequest(url, method, data, options, resolve, reject) {
  console.log(`[MOCK ${method}] ${url}`, data)

  // 显示加载提示
  if (options.showLoading !== false) {
    wx.showLoading({
      title: options.loadingText || '加载中...',
      mask: true
    })
  }

  // 模拟网络延迟
  setTimeout(() => {
    // 隐藏加载提示
    if (options.showLoading !== false) {
      wx.hideLoading()
    }

    // 根据不同的 API 端点返回模拟数据
    try {
      let mockResponse = null

      // 方案生成
      if (url === API_ENDPOINTS.PLAN_GENERATE) {
        mockResponse = {
          plans: mockPlans,
          request_id: 'mock_req_' + Date.now()
        }
        console.log('[MOCK] 返回 3 个模拟方案')
      } else if (url === API_ENDPOINTS.PLAN_LIST) {
      // 方案列表
        mockResponse = {
          plans: mockPlans,
          total: mockPlans.length
        }
        console.log('[MOCK] 返回方案列表')
      } else if (url.startsWith('/plans/')) {
      // 方案详情
        const planId = url.split('/')[2]
        const plan = mockPlans.find(p => p.plan_id === planId)
        mockResponse = plan || mockPlans[0]
        console.log('[MOCK] 返回方案详情:', planId)
      } else if (url === API_ENDPOINTS.USER_LOGIN) {
      // 用户登录
        // 如果登录时提供了头像和昵称，则使用提供的值
        const nickname = data.nickname || '测试用户'
        const avatar = data.avatarUrl || ''

        mockResponse = {
          sessionToken: 'mock_token_' + Date.now(),
          userInfo: {
            user_id: 'mock_user_001',
            nickname,
            avatar
          }
        }
        console.log('[MOCK] 返回登录信息:', mockResponse.userInfo)
      } else if (url.includes('/confirm')) {
      // 确认方案
        mockResponse = {
          success: true,
          confirmed_at: new Date().toISOString()
        }
        console.log('[MOCK] 确认方案成功')
      } else {
      // 默认响应
        mockResponse = {
          success: true,
          message: 'Mock response'
        }
        console.log('[MOCK] 返回默认响应')
      }

      // 成功返回
      resolve(mockResponse)
    } catch (error) {
      console.error('[MOCK] 处理失败:', error)
      reject({
        code: ERROR_CODES.GENERATION_FAILED,
        message: '模拟数据处理失败'
      })
    }
  }, 800) // 模拟 800ms 网络延迟
}

/**
 * 处理错误
 */
function handleError(message, code, options) {
  if (options.showError !== false) {
    wx.showToast({
      title: message,
      icon: 'none',
      duration: 2000
    })
  }
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

  // 提示用户
  wx.showToast({
    title: '登录已过期，请重新登录',
    icon: 'none',
    duration: 2000
  })

  // 立即跳转到登录页，避免多次 401 堆积导致“刚登录又被跳回登录页”
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

    // 显示加载提示
    if (options.showLoading !== false) {
      wx.showLoading({
        title: '上传中...',
        mask: true
      })
    }

    wx.uploadFile({
      url: fullUrl,
      filePath,
      name: options.name || 'file',
      header: {
        Authorization: sessionToken ? `Bearer ${sessionToken}` : ''
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

export default {
  get,
  post,
  put,
  del,
  uploadFile
}
