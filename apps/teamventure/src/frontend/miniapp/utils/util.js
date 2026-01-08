// 通用工具函数

/**
 * 格式化日期
 * @param {Date|String|Number} date - 日期
 * @param {String} format - 格式 (YYYY-MM-DD HH:mm:ss)
 * @returns {String}
 */
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

/**
 * 格式化相对时间
 * @param {Date|String|Number} date - 日期
 * @returns {String}
 */
export function formatRelativeTime(date) {
  if (!date) return ''

  const d = new Date(date)
  if (isNaN(d.getTime())) return ''

  const now = new Date()
  const diff = now - d
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 7) {
    return formatDate(date, 'YYYY-MM-DD')
  } else if (days > 0) {
    return `${days}天前`
  } else if (hours > 0) {
    return `${hours}小时前`
  } else if (minutes > 0) {
    return `${minutes}分钟前`
  } else {
    return '刚刚'
  }
}

/**
 * 格式化金额
 * @param {Number} amount - 金额
 * @param {Boolean} showSymbol - 是否显示货币符号
 * @returns {String}
 */
export function formatMoney(amount, showSymbol = true) {
  if (typeof amount !== 'number') return '0'

  const formatted = amount.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
  return showSymbol ? `¥${formatted}` : formatted
}

/**
 * 格式化人均金额
 * @param {Number} total - 总金额
 * @param {Number} peopleCount - 人数
 * @returns {String}
 */
export function formatPerPerson(total, peopleCount) {
  if (!peopleCount || peopleCount <= 0) return '¥0'
  const perPerson = Math.round(total / peopleCount)
  return `¥${perPerson}/人`
}

/**
 * 计算天数
 * @param {String|Date} startDate - 开始日期
 * @param {String|Date} endDate - 结束日期
 * @returns {Number}
 */
export function calculateDays(startDate, endDate) {
  if (!startDate || !endDate) return 0

  const start = new Date(startDate)
  const end = new Date(endDate)

  if (isNaN(start.getTime()) || isNaN(end.getTime())) return 0

  const diff = end - start
  const days = Math.ceil(diff / (1000 * 60 * 60 * 24)) + 1

  return days > 0 ? days : 0
}

/**
 * 格式化行程描述
 * @param {Number} days - 天数
 * @returns {String}
 */
export function formatDuration(days) {
  if (days <= 0) return ''
  if (days === 1) return '1天'
  return `${days}天${days - 1}夜`
}

/**
 * 脱敏手机号
 * @param {String} phone - 手机号
 * @returns {String}
 */
export function maskPhone(phone) {
  if (!phone || phone.length !== 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

/**
 * 脱敏邮箱
 * @param {String} email - 邮箱
 * @returns {String}
 */
export function maskEmail(email) {
  if (!email || !email.includes('@')) return email
  const [username, domain] = email.split('@')
  const maskedUsername = username.length > 3
    ? username.substring(0, 3) + '****'
    : username + '****'
  return `${maskedUsername}@${domain}`
}

/**
 * 防抖函数
 * @param {Function} fn - 函数
 * @param {Number} delay - 延迟时间（毫秒）
 * @returns {Function}
 */
export function debounce(fn, delay = 300) {
  let timer = null
  return function(...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

/**
 * 节流函数
 * @param {Function} fn - 函数
 * @param {Number} interval - 间隔时间（毫秒）
 * @returns {Function}
 */
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

/**
 * 深拷贝
 * @param {Object} obj - 对象
 * @returns {Object}
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj)
  if (obj instanceof Array) return obj.map(item => deepClone(item))

  const cloned = {}
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      cloned[key] = deepClone(obj[key])
    }
  }
  return cloned
}

/**
 * 判断是否为空对象
 * @param {Object} obj - 对象
 * @returns {Boolean}
 */
export function isEmptyObject(obj) {
  return obj === null || obj === undefined || Object.keys(obj).length === 0
}

/**
 * 生成唯一 ID
 * @returns {String}
 */
export function generateId() {
  return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

/**
 * 校验手机号
 * @param {String} phone - 手机号
 * @returns {Boolean}
 */
export function validatePhone(phone) {
  return /^1[3-9]\d{9}$/.test(phone)
}

/**
 * 校验邮箱
 * @param {String} email - 邮箱
 * @returns {Boolean}
 */
export function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

/**
 * 打电话
 * @param {String} phone - 手机号
 */
export function makePhoneCall(phone) {
  wx.makePhoneCall({
    phoneNumber: phone,
    fail: (error) => {
      console.error('拨打电话失败:', error)
      wx.showToast({
        title: '拨打失败',
        icon: 'none'
      })
    }
  })
}

/**
 * 复制到剪贴板
 * @param {String} text - 文本
 * @param {String} successMsg - 成功提示
 */
export function copyToClipboard(text, successMsg = '复制成功') {
  wx.setClipboardData({
    data: text,
    success: () => {
      wx.showToast({
        title: successMsg,
        icon: 'success'
      })
    },
    fail: (error) => {
      console.error('复制失败:', error)
      wx.showToast({
        title: '复制失败',
        icon: 'none'
      })
    }
  })
}

/**
 * 预览图片
 * @param {String} current - 当前图片
 * @param {Array} urls - 图片列表
 */
export function previewImage(current, urls = []) {
  wx.previewImage({
    current,
    urls: urls.length ? urls : [current]
  })
}

/**
 * 保存图片到相册
 * @param {String} url - 图片地址
 */
export function saveImageToPhotosAlbum(url) {
  // 先下载图片
  wx.downloadFile({
    url,
    success: (res) => {
      // 保存到相册
      wx.saveImageToPhotosAlbum({
        filePath: res.tempFilePath,
        success: () => {
          wx.showToast({
            title: '已保存到相册',
            icon: 'success'
          })
        },
        fail: (error) => {
          console.error('保存失败:', error)
          wx.showToast({
            title: '保存失败',
            icon: 'none'
          })
        }
      })
    },
    fail: (error) => {
      console.error('下载失败:', error)
      wx.showToast({
        title: '下载失败',
        icon: 'none'
      })
    }
  })
}

export default {
  formatDate,
  formatRelativeTime,
  formatMoney,
  formatPerPerson,
  calculateDays,
  formatDuration,
  maskPhone,
  maskEmail,
  debounce,
  throttle,
  deepClone,
  isEmptyObject,
  generateId,
  validatePhone,
  validateEmail,
  makePhoneCall,
  copyToClipboard,
  previewImage,
  saveImageToPhotosAlbum
}
