# 课程实战案例使用指南

本目录包含 AI Coding 课程 Lesson 0 的三个实战案例代码：

1.  **mini-calculator**：简易计算器（入门级，包含详细代码注释）
2.  **mini-snake-game**：贪吃蛇游戏（进阶级，Canvas 绘图）
3.  **mini-travel-plan**：AI 行程规划 Demo（应用级，表单与页面交互）

## 🚀 如何运行

1.  打开 **微信开发者工具**。
2.  点击 **“导入项目”**（或“加号”图标）。
3.  选择对应的案例文件夹（例如 `mini-calculator`）。
4.  **AppID** 栏：
    *   如果您已有注册的小程序账号，请填入您的 **AppID**。
    *   如果您还没有账号，请点击 **“测试号”**（会自动生成一个测试 AppID）或选择 **“游客模式”**。
5.  点击 **“确定”** 即可打开项目。

## ⚠️ 常见报错说明

如果您使用 **“游客模式”** 或 **“测试号”** 运行项目，控制台可能会出现以下红色报错信息：

```text
Error: SystemError (appServiceSDKScriptError)
{"errMsg":"webapi_getwxaasyncsecinfo:fail "}
...
[Deprecation] SharedArrayBuffer will require cross-origin isolation...
```

### ✅ 解决方案
**请直接忽略这些报错，它们不会影响程序的正常运行。**

*   **原因**：游客模式下，开发者工具无法连接微信后台获取某些安全配置信息，因此会报错。
*   **消除方法**：在开发者工具右上角点击 **“详情”** -> **“基本信息”**，将 AppID 修改为您真实注册的小程序 AppID，刷新后报错即会消失。

## 📚 学习建议

建议按照以下顺序进行学习：
1.  先从 **mini-calculator** 开始，阅读 `index.wxml` 和 `index.js` 中的详细注释，理解小程序的基本结构。
2.  尝试修改 **mini-snake-game** 中的参数（如蛇的移动速度），体验代码修改带来的即时反馈。
3.  最后运行 **mini-travel-plan**，体验一个完整的多页面应用是如何工作的。
