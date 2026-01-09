const path = require('path')
const automator = require('miniprogram-automator')

function resolvePort() {
  const port = Number(process.env.WECHAT_AUTOMATOR_PORT || 9420)
  return Number.isFinite(port) ? port : 9420
}

function resolveCliPath() {
  return (
    process.env.WECHAT_DEVTOOLS_CLI ||
    '/Applications/wechatwebdevtools.app/Contents/MacOS/cli'
  )
}

function resolveProjectPath() {
  return process.env.MINIAPP_PROJECT_PATH || path.resolve(process.cwd())
}

describe('行程变更 E2E', () => {
  /** @type {import('miniprogram-automator').MiniProgram} */
  let miniProgram

  beforeAll(async () => {
    miniProgram = await automator.launch({
      cliPath: resolveCliPath(),
      projectPath: resolveProjectPath(),
      port: resolvePort(),
      timeout: 120000,
      trustProject: true
    })

    // 让 showModal 不阻塞，并且可断言内容
    await miniProgram.evaluate(() => {
      wx.__lastModal = null
      wx.showModal = function (opts) {
        wx.__lastModal = opts || null
        if (opts && typeof opts.success === 'function') {
          opts.success({ confirm: true, cancel: false })
        }
      }
      wx.showToast = function () {}
      wx.showLoading = function () {}
      wx.hideLoading = function () {}
    })
  })

  afterAll(async () => {
    if (miniProgram) await miniProgram.close()
  })

  test('可打开变更页、校验、提交并回显版本+1', async () => {
    // 启用请求 mock（request.js 支持本地开关）
    await miniProgram.callWxMethod('setStorageSync', 'useMockData', true)

    const detailPage = await miniProgram.reLaunch('/pages/detail/detail?planId=plan_mock_001')
    await detailPage.waitFor(500)

    const changeBtn = await detailPage.$('.btn-itinerary-change')
    expect(changeBtn).toBeTruthy()

    // 初始版本显示 v1
    const v1 = await detailPage.$('.panel-version')
    expect(await v1.text()).toContain('v1')

    await changeBtn.tap()

    const changePage = await miniProgram.currentPage()
    await changePage.waitFor('.markdown-editor')

    // 校验按钮（弹窗内容通过 showModal mock 获取）
    const validateBtn = await changePage.$('.btn-secondary')
    await validateBtn.tap()
    await changePage.waitFor(200)

    const modal = await miniProgram.evaluate(() => wx.__lastModal)
    expect(modal && modal.title).toBe('校验结果')
    expect(modal && modal.content).toContain('校验通过')

    // 修改 markdown（保证仍合规），并提交
    const editor = await changePage.$('.markdown-editor')
    await editor.input('\n- 21:50 - 22:00 | 测试追加 | | \n')

    const submitBtn = await changePage.$('.btn-primary')
    await submitBtn.tap()

    // 返回详情页后版本应变为 v2
    const detailPage2 = await miniProgram.currentPage()
    await detailPage2.waitFor(500)
    const v2 = await detailPage2.$('.panel-version')
    expect(await v2.text()).toContain('v2')
  })
})
