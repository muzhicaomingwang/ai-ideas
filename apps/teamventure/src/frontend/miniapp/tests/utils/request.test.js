import { jest } from '@jest/globals'
import { post } from '../../utils/request.js'
import { API_ENDPOINTS, ERROR_CODES } from '../../utils/config.js'

describe('utils/request - network error mapping', () => {
  let consoleErrorSpy

  beforeEach(() => {
    jest.clearAllMocks()
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
    global.wx.getStorageSync.mockImplementation((key) => {
      if (key === 'useMockData') return false
      return null
    })
  })

  afterEach(() => {
    consoleErrorSpy?.mockRestore()
  })

  test('maps errno -102 to connection refused message', async () => {
    global.wx.request.mockImplementation(({ fail }) => {
      fail({ errMsg: 'request:fail (errno -102)', errno: -102 })
    })

    await expect(post(API_ENDPOINTS.USER_LOGIN, {}, { showLoading: false, showError: false })).rejects.toMatchObject({
      code: ERROR_CODES.NETWORK_ERROR,
      message: expect.stringContaining('连接被拒绝')
    })
  })

  test('maps ERR_CONNECTION_REFUSED to connection refused message', async () => {
    global.wx.request.mockImplementation(({ fail }) => {
      fail({ errMsg: 'request:fail net::ERR_CONNECTION_REFUSED' })
    })

    await expect(post(API_ENDPOINTS.USER_LOGIN, {}, { showLoading: false, showError: false })).rejects.toMatchObject({
      code: ERROR_CODES.NETWORK_ERROR,
      message: expect.stringContaining('连接被拒绝')
    })
  })
})
