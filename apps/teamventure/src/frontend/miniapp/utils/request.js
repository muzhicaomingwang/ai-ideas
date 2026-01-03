// 网络请求封装
import { API_BASE_URL, REQUEST_TIMEOUT, STORAGE_KEYS, ERROR_CODES, ERROR_MESSAGES, USE_MOCK_DATA, API_ENDPOINTS } from './config.js'
import { mockPlans } from './mock-data.js'

/**
 * 统一请求方法
 * @param {String} url - 请求地址
 * @param {String} method - 请求方法 GET/POST/PUT/DELETE
 * @param {Object} data - 请求数据
 * @param {Object} options - 其他配置
 * @returns {Promise}
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

        console.error(`[API ${method}] ${url} 失败:`, error)

        // 判断错误类型
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
      }
      // 方案列表
      else if (url === API_ENDPOINTS.PLAN_LIST) {
        mockResponse = {
          plans: mockPlans,
          total: mockPlans.length
        }
        console.log('[MOCK] 返回方案列表')
      }
      // 方案详情
      else if (url.startsWith('/plans/')) {
        const planId = url.split('/')[2]
        const plan = mockPlans.find(p => p.plan_id === planId)
        mockResponse = plan || mockPlans[0]
        console.log('[MOCK] 返回方案详情:', planId)
      }
      // 用户登录
      else if (url === API_ENDPOINTS.USER_LOGIN) {
        mockResponse = {
          sessionToken: 'mock_token_' + Date.now(),
          userInfo: {
            user_id: 'mock_user_001',
            nickname: '测试用户',
            avatar: 'https://via.placeholder.com/100'
          }
        }
        console.log('[MOCK] 返回登录信息')
      }
      // 确认方案
      else if (url.includes('/confirm')) {
        mockResponse = {
          success: true,
          confirmed_at: new Date().toISOString()
        }
        console.log('[MOCK] 确认方案成功')
      }
      // 默认响应
      else {
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
  // 清除登录信息
  wx.removeStorageSync(STORAGE_KEYS.SESSION_TOKEN)
  wx.removeStorageSync(STORAGE_KEYS.USER_INFO)

  // 提示用户
  wx.showToast({
    title: '登录已过期，请重新登录',
    icon: 'none',
    duration: 2000
  })

  // 跳转到登录页
  setTimeout(() => {
    wx.redirectTo({
      url: '/pages/login/login'
    })
  }, 2000)
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

export default {
  get,
  post,
  put,
  del,
  uploadFile
}
