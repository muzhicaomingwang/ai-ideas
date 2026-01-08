# 前端单元测试指南

## 快速开始

### 1. 安装依赖

```bash
cd /Users/qitmac001395/workspace/QAL/ideas/apps/teamventure/src/frontend/miniapp
npm install
```

### 2. 运行测试

```bash
# 运行所有测试
npm test

# 生成覆盖率报告
npm run test:coverage

# 监听模式（开发时使用）
npm run test:watch

# 查看覆盖率报告
open coverage/index.html
```

### 3. 运行ESLint

```bash
# 检查代码规范
npm run lint

# 自动修复简单问题
npm run lint:fix
```

---

## 测试文件结构

```
tests/
├── setup.js                 # Jest全局配置（mock wx对象）
├── utils/
│   ├── config.test.js      # ✅ 已创建（19个测试用例）
│   ├── request.test.js     # ⏸️ 待创建
│   └── format.test.js      # ⏸️ 待创建
└── pages/
    ├── login.test.js        # ⏸️ 待创建
    ├── home.test.js         # ⏸️ 待创建
    └── index.test.js        # ⏸️ 待创建
```

---

## 测试编写规范

### 命名约定

**测试文件**: `{filename}.test.js`
**测试套件**: `describe('模块名 - 功能', () => {})`
**测试用例**: `test('应该...', () => {})`

### 示例

```javascript
/**
 * utils/format.js 单元测试
 */

import { formatPrice, formatDate } from '../../utils/format.js'

describe('Format - formatPrice', () => {
  test('应该正确格式化正整数', () => {
    expect(formatPrice(10000)).toBe('¥10,000')
    expect(formatPrice(1000)).toBe('¥1,000')
    expect(formatPrice(100)).toBe('¥100')
  })

  test('应该处理小数', () => {
    expect(formatPrice(1234.56)).toBe('¥1,234.56')
  })

  test('应该处理边界值', () => {
    expect(formatPrice(0)).toBe('¥0')
    expect(formatPrice(null)).toBe('-')
    expect(formatPrice(undefined)).toBe('-')
  })
})

describe('Format - formatDate', () => {
  test('应该格式化YYYY-MM-DD为中文日期', () => {
    expect(formatDate('2026-01-08')).toBe('2026年1月8日')
  })

  test('应该处理无效日期', () => {
    expect(formatDate(null)).toBe('-')
    expect(formatDate('')).toBe('-')
  })
})
```

---

## Mock wx API

### setup.js已配置

测试中可以直接使用mock的wx对象：

```javascript
test('应该调用wx.showLoading', () => {
  someFunction()  // 内部调用了 wx.showLoading

  expect(wx.showLoading).toHaveBeenCalledWith({
    title: '加载中...',
    mask: true
  })
})

test('应该从storage读取token', () => {
  wx.getStorageSync.mockReturnValue('test_token')

  const token = getToken()  // 内部调用 wx.getStorageSync

  expect(wx.getStorageSync).toHaveBeenCalledWith('sessionToken')
  expect(token).toBe('test_token')
})
```

### 常用Mock模式

```javascript
beforeEach(() => {
  // 每个测试前重置mock
  jest.clearAllMocks()

  // 设置默认行为
  wx.getStorageSync.mockReturnValue(null)
})

test('示例测试', () => {
  // 为特定测试设置返回值
  wx.getStorageSync.mockReturnValueOnce('specific_value')

  // 或设置多个调用的返回值
  wx.request
    .mockImplementationOnce(options => {
      options.success({ statusCode: 200, data: mockData })
    })
})
```

---

## 覆盖率目标

### utils层（目标: 95%）

| 文件 | 行覆盖率 | 分支覆盖率 | 函数覆盖率 |
|------|---------|-----------|-----------|
| config.js | 100% | 100% | 100% |
| request.js | 90%+ | 85%+ | 90%+ |
| format.js | 95%+ | 90%+ | 95%+ |

### pages层（目标: 70%）

| 文件 | 行覆盖率 | 分支覆盖率 | 函数覆盖率 |
|------|---------|-----------|-----------|
| login/login.js | 75%+ | 70%+ | 80%+ |
| home/home.js | 65%+ | 60%+ | 70%+ |
| index/index.js | 70%+ | 65%+ | 75%+ |

---

## 待创建的测试用例

### utils/request.test.js (预估12个用例)

```javascript
describe('Request - refreshTokenIfNeeded', () => {
  test('token不存在时返回false')
  test('token有效期充足时不刷新')
  test('token即将过期时自动刷新')
  test('并发请求只触发一次刷新')
  test('刷新失败时返回false')
})

describe('Request - GET方法', () => {
  test('成功请求返回data')
  test('401错误触发重新登录')
  test('网络错误显示toast')
  test('超时错误正确处理')
})

describe('Request - POST方法', () => {
  test('成功提交数据')
  test('参数验证失败返回错误')
  test('业务错误正确处理')
})
```

### pages/login/login.test.js (预估10个用例)

```javascript
describe('Login Page - handleContinue', () => {
  test('token有效时跳转首页')
  test('token无效时触发重新登录')
  test('显示"验证中..."加载提示')
  test('验证失败后清除登录状态')
})

describe('Login Page - handleReLogin', () => {
  test('清除所有登录相关storage')
  test('重置全局登录状态')
  test('显示"请重新登录"提示')
  test('页面状态重置为未登录')
})

describe('Login Page - handleWechatLogin', () => {
  test('协议未勾选时显示提示')
  test('wx.login成功后显示用户表单')
})
```

---

## 运行测试的预期输出

### 成功示例

```bash
$ npm test

PASS  tests/utils/config.test.js
  Config - API_BASE_URL
    ✓ 应该返回有效的URL字符串 (3 ms)
    ✓ local环境应包含localhost (1 ms)
  Config - STORAGE_KEYS
    ✓ SESSION_TOKEN应该定义为"sessionToken" (1 ms)
    ✓ USER_INFO应该定义为"userInfo" (1 ms)
    ✓ 所有key应该是非空字符串 (2 ms)
  Config - ERROR_CODES
    ✓ 应该包含所有必需的错误码 (1 ms)
    ✓ 所有错误码应该大写 (1 ms)
  Config - ERROR_MESSAGES
    ✓ 每个错误码都应该有对应的错误信息 (2 ms)
    ✓ 错误信息应该友好且具体 (1 ms)
  Config - API_ENDPOINTS
    ✓ 用户登录端点应该定义正确 (1 ms)
    ✓ 用户刷新端点应该定义正确 (1 ms)
    ✓ 方案生成端点应该定义正确 (1 ms)
    ✓ 方案列表端点应该定义正确 (1 ms)
    ✓ 所有端点应该以/开头 (1 ms)
    ✓ 所有端点不应该包含域名 (1 ms)
  Config - USE_MOCK_DATA
    ✓ 应该是布尔值 (1 ms)

Test Suites: 1 passed, 1 total
Tests:       19 passed, 19 total
Snapshots:   0 total
Time:        2.456 s
Coverage:    100% (config.js)
```

---

## 故障排查

### 问题1: 找不到模块

```
Cannot find module '../../utils/config.js'
```

**解决**:
- 检查import路径是否正确
- 确认文件确实存在
- 检查jest.config.js的roots配置

### 问题2: wx is not defined

```
ReferenceError: wx is not defined
```

**解决**:
- 确认jest.config.js中配置了 `setupFiles: ['<rootDir>/tests/setup.js']`
- 确认setup.js正确定义了 `global.wx`

### 问题3: Mock不生效

```
TypeError: wx.request is not a function
```

**解决**:
- 在测试前调用 `jest.clearAllMocks()`
- 确认setup.js中正确定义了该方法
- 检查是否有其他地方覆盖了mock

---

## 参考

- **测试配置指南**: `docs/qa/unit-testing-setup-guide.md`
- **领域统一语言**: `docs/design/ubiquitous-language-glossary.md`
- **API设计**: `docs/design/api-design.md`
- **Jest文档**: https://jestjs.io/
- **Expect断言**: https://jestjs.io/docs/expect

---

**创建时间**: 2026-01-08
**维护者**: 前端团队
