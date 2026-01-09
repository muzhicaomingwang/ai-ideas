# 小程序 E2E 自动化测试（miniprogram-automator）

## 前置条件

- 已安装「微信开发者工具」
- 开发者工具已开启「安全设置 -> 服务端口」（自动化依赖）

## 运行

在 `apps/teamventure/src/frontend/miniapp` 目录执行：

```bash
WECHAT_DEVTOOLS_CLI="/Applications/wechatwebdevtools.app/Contents/MacOS/cli" \
npm run test:e2e
```

说明：
- `WECHAT_DEVTOOLS_CLI`：微信开发者工具 cli 路径（macOS 常见如上；Windows/Linux 请改为你的实际路径）
- 如端口被占用可指定：`WECHAT_AUTOMATOR_PORT=9430`
- 如小程序工程不在当前目录可指定：`MINIAPP_PROJECT_PATH=/abs/path/to/miniapp`
