// 临时脚本：清理可能错误的Storage配置
// 在app.js的onLaunch中调用一次

export function cleanupStorageUrls() {
  try {
    const apiBaseUrl = wx.getStorageSync('apiBaseUrl')
    
    console.log('[Storage Check] apiBaseUrl:', apiBaseUrl)
    
    // 检查是否包含weapp协议或格式错误
    if (apiBaseUrl && (
      apiBaseUrl.includes('weapp:') ||
      apiBaseUrl.includes('http:/127.0.0.1') ||  // 少了一个斜杠
      apiBaseUrl.includes('http:/')  // 格式错误
    )) {
      console.warn('[Storage Fix] 检测到错误的apiBaseUrl，正在清理...')
      wx.removeStorageSync('apiBaseUrl')
      console.log('[Storage Fix] 已清理，将使用默认配置')
      return true
    }
    
    return false
  } catch (e) {
    console.error('[Storage Fix] 清理失败:', e)
    return false
  }
}
