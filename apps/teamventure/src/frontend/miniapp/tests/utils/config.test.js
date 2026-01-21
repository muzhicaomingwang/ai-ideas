/**
 * utils/config.js 单元测试
 *
 * 测试覆盖:
 *   - API_BASE_URL配置
 *   - STORAGE_KEYS常量
 *   - ERROR_CODES常量
 *   - ERROR_MESSAGES常量
 *   - API_ENDPOINTS常量
 *
 * 术语对照: ubiquitous-language-glossary.md Section 7.2
 */

// 注意：需要先配置环境变量或mock
process.env.NODE_ENV = 'test'

import { API_BASE_URL, STORAGE_KEYS, ERROR_CODES, ERROR_MESSAGES, API_ENDPOINTS, USE_MOCK_DATA } from '../../utils/config.js'

describe('Config - API_BASE_URL', () => {
  test('应该返回有效的URL字符串', () => {
    expect(API_BASE_URL).toBeDefined()
    expect(typeof API_BASE_URL).toBe('string')
    expect(API_BASE_URL).toMatch(/^https?:\/\//)
  })

  test('local环境应包含localhost', () => {
    // 根据当前环境判断
    if (USE_MOCK_DATA === false) {
      // local 环境默认走本地网关域名（通过 /etc/hosts 指向 127.0.0.1），也兼容直接用 localhost
      expect(
        API_BASE_URL.includes('localhost') || API_BASE_URL.includes('api.teamventure.com')
      ).toBe(true)
    }
  })
})

describe('Config - STORAGE_KEYS', () => {
  test('SESSION_TOKEN应该定义为"sessionToken"', () => {
    expect(STORAGE_KEYS.SESSION_TOKEN).toBe('sessionToken')
  })

  test('USER_INFO应该定义为"userInfo"', () => {
    expect(STORAGE_KEYS.USER_INFO).toBe('userInfo')
  })

  test('所有key应该是非空字符串', () => {
    Object.values(STORAGE_KEYS).forEach(key => {
      expect(typeof key).toBe('string')
      expect(key.length).toBeGreaterThan(0)
    })
  })
})

describe('Config - ERROR_CODES', () => {
  test('应该包含所有必需的错误码', () => {
    expect(ERROR_CODES.UNAUTHORIZED).toBe('UNAUTHORIZED')
    expect(ERROR_CODES.NETWORK_ERROR).toBe('NETWORK_ERROR')
    expect(ERROR_CODES.TIMEOUT).toBe('TIMEOUT')
    expect(ERROR_CODES.GENERATION_FAILED).toBe('GENERATION_FAILED')
    expect(ERROR_CODES.VALIDATION_ERROR).toBe('VALIDATION_ERROR')
  })

  test('所有错误码应该大写', () => {
    Object.values(ERROR_CODES).forEach(code => {
      expect(code).toBe(code.toUpperCase())
    })
  })
})

describe('Config - ERROR_MESSAGES', () => {
  test('每个错误码都应该有对应的错误信息', () => {
    Object.keys(ERROR_CODES).forEach(key => {
      const code = ERROR_CODES[key]
      expect(ERROR_MESSAGES[code]).toBeDefined()
      expect(typeof ERROR_MESSAGES[code]).toBe('string')
      expect(ERROR_MESSAGES[code].length).toBeGreaterThan(0)
    })
  })

  test('错误信息应该友好且具体', () => {
    expect(ERROR_MESSAGES[ERROR_CODES.UNAUTHORIZED]).toContain('登录')
    expect(ERROR_MESSAGES[ERROR_CODES.NETWORK_ERROR]).toContain('网络')
    expect(ERROR_MESSAGES[ERROR_CODES.TIMEOUT]).toContain('超时')
  })
})

describe('Config - API_ENDPOINTS', () => {
  test('用户登录端点应该定义正确', () => {
    expect(API_ENDPOINTS.USER_LOGIN).toBe('/auth/wechat/login')
  })

  test('用户刷新端点应该定义正确', () => {
    expect(API_ENDPOINTS.USER_REFRESH).toBe('/auth/wechat/refresh')
  })

  test('方案生成端点应该定义正确', () => {
    expect(API_ENDPOINTS.PLAN_GENERATE).toBe('/plans/generate')
  })

  test('方案列表端点应该定义正确', () => {
    expect(API_ENDPOINTS.PLAN_LIST).toBe('/plans')
  })

  test('所有端点应该以/开头', () => {
    Object.values(API_ENDPOINTS).forEach(endpoint => {
      expect(endpoint).toMatch(/^\//)
    })
  })

  test('所有端点不应该包含域名', () => {
    Object.values(API_ENDPOINTS).forEach(endpoint => {
      expect(endpoint).not.toMatch(/https?:\/\//)
    })
  })
})

describe('Config - USE_MOCK_DATA', () => {
  test('应该是布尔值', () => {
    expect(typeof USE_MOCK_DATA).toBe('boolean')
  })
})
