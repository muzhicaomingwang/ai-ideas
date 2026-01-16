# TeamVenture 小程序

> AI 驱动的团建策划助手微信小程序

## 📋 项目概述

TeamVenture 是一款基于 AI 的团建策划助手小程序，帮助企业 HR 快速生成团建方案，降低成本 50%+。

### 核心功能

- 🤖 **AI 智能生成** - 15分钟生成 3 套完整方案
- 💰 **成本透明** - 明码标价，智能比价
- 🎯 **行程可编辑** - 支持行程变更与校验
- 📊 **方案对比** - 可视化对比，快速决策

---

## 🏗️ 项目结构

```
miniapp/
├── pages/                    # 页面目录
│   ├── index/               # 首页（生成方案）
│   │   ├── index.wxml       # 页面结构
│   │   ├── index.wxss       # 页面样式
│   │   ├── index.js         # 页面逻辑
│   │   └── index.json       # 页面配置
│   ├── login/               # 登录页
│   ├── comparison/          # 方案对比页
│   ├── detail/              # 方案详情页
│   └── myplans/             # 我的方案页
│
├── components/              # 组件目录
│   └── stepper/             # 数字输入组件
│
├── utils/                   # 工具类
│   ├── config.js            # 配置文件（API、常量）
│   ├── request.js           # 网络请求封装
│   └── util.js              # 通用工具函数
│
├── images/                  # 图片资源
│   ├── logo.png             # Logo
│   ├── tab-generate.png     # TabBar 图标
│   ├── tab-generate-active.png
│   ├── tab-myplans.png
│   └── tab-myplans-active.png
│
├── app.js                   # 小程序入口
├── app.json                 # 全局配置
├── app.wxss                 # 全局样式
├── project.config.json      # 项目配置
├── sitemap.json             # 索引配置
└── README.md                # 本文件
```

---

## 🚀 快速开始

### 前置要求

- [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
- 微信小程序账号（或使用测试号）

### 安装步骤

1. **克隆项目**
   ```bash
   cd apps/teamventure/src/frontend/miniapp
   ```

2. **打开微信开发者工具**
   - 选择"导入项目"
   - 项目目录：选择 `miniapp` 文件夹
   - AppID：输入你的小程序 AppID（或选择测试号）

3. **配置后端地址**

   编辑 `utils/config.js`，修改 API 地址（本地联调需要先启动后端 `java-business-service` 并确认 `8080` 端口可用）：
   ```javascript
   const API_BASE_URLS = {
     dev: 'http://localhost:8080/api/v1',        // 本地开发
     beta: 'https://beta-api.teamventure.com/api/v1',
     prod: 'https://api.teamventure.com/api/v1'
   }
   ```
   开发者工具里也可临时覆盖（Console 执行）：`wx.setStorageSync('apiBaseUrl', 'http://127.0.0.1:8080/api/v1')`（真机调试请改为你的电脑局域网 IP）。

4. **准备图片资源**（见下方"图片资源"部分）

5. **点击"编译"按钮**

---

## 📱 页面说明

### 1. 登录页（/pages/login）

**功能**：
- 微信一键登录
- 用户协议确认

**交互流程**：
```
进入登录页 → 微信授权 → 后端登录 → 跳转首页
```

---

### 2. 生成方案页（/pages/index）

**功能**：
- Markdown 自由输入模式
- 预填充示例模板（用户直接修改）
- 支持草稿自动保存（24小时内）
- 一键重置模板

**Markdown 模板结构**：
```markdown
## 基本信息
- 天数、人数、预算

## 行程路线
- 出发地、到达地、途径地

## 交通安排
- 去程、返程（高铁/航班）

## 住宿安排
- 每日入住/出发酒店

## 活动偏好
- 活动类型（如户外拓展、美食体验）

## 特殊要求
- 老人/小孩、饮食限制等
```

**交互流程**：
```
查看预填充示例 → 修改示例内容 → 生成方案 → 跳转我的方案页
```

**设计亮点**：
- ✅ 使用可编辑示例代替下划线占位符
- ✅ 用户选中文本即可修改，无需删除
- ✅ 降低理解成本，提供清晰格式示例

---

### 3. 方案对比页（/pages/comparison）

**功能**：
- 3 套方案并列展示
- 详细对比表格（可展开/折叠）
- 推荐标识
- 重新生成

**交互流程**：
```
查看 3 套方案 → 选择方案 → 查看详情 / 确认选择
```

---

### 4. 方案详情页（/pages/detail）

**功能**：
- 方案概览（预算、人均、天数）
- 行程安排（时间轴）
- 确认方案

**交互流程**：
```
查看详情 → 确认方案
```

**折叠面板**：
- 默认展开：行程安排

---

### 5. 我的方案页（/pages/myplans）

**功能**：
- 历史方案列表
- 状态标识（草稿/已确认/已取消）
- 左滑删除
- 下拉刷新
- 上拉加载更多

**交互流程**：
```
查看列表 → 点击卡片 → 查看详情
左滑卡片 → 删除方案
```

**空状态**：
- 显示"还没有方案"
- 提供"去生成方案"按钮

---

## 🎨 图片资源

### 必需的图片文件

请准备以下图片并放入 `images/` 目录：

#### 1. Logo（登录页）
- **文件名**: `logo.png`
- **尺寸**: 160px × 160px (@2x: 320px × 320px)
- **格式**: PNG（透明背景）
- **用途**: 登录页顶部

#### 2. TabBar 图标

**生成方案**：
- `tab-generate.png` - 未选中态（48px × 48px）
- `tab-generate-active.png` - 选中态（48px × 48px）

**我的方案**：
- `tab-myplans.png` - 未选中态（48px × 48px）
- `tab-myplans-active.png` - 选中态（48px × 48px）

**设计建议**：
- 使用简洁的线性图标
- 选中态使用蓝色 (#1890ff)
- 未选中态使用灰色 (#666666)

#### 临时替代方案

如果暂时没有图片，可以：
1. 使用纯色占位图
2. 或使用 iconfont 图标代替
3. 或暂时注释掉 `app.json` 中的 TabBar 图标配置

---

## ⚙️ 配置说明

### 环境配置

在 `utils/config.js` 中修改 `ENV` 变量：

```javascript
const ENV = 'dev'  // dev | beta | prod
```

### API 端点

所有 API 端点定义在 `utils/config.js` 的 `API_ENDPOINTS` 中。

### 常量配置

- `PLAN_TYPES` - 方案类型
- `ACTIVITY_TYPES` - 活动类型选项
- `ACCOMMODATION_LEVELS` - 住宿标准选项

---

## 🧪 测试

### 本地测试

1. 确保后端服务已启动
2. 微信开发者工具选择"真机调试"或"预览"
3. 扫码在真机上测试

### 模拟数据

如果后端尚未就绪，可以在页面 JS 文件中使用模拟数据：

```javascript
// pages/comparison/comparison.js
onLoad(options) {
  // 使用模拟数据
  const mockPlans = [
    {
      plan_id: 'mock_1',
      plan_name: '经济实惠·怀柔山野团建',
      plan_type: 'budget',
      budget_total: 35000,
      people_count: 50,
      // ...
    },
    // ...
  ]

  this.processPlanData(mockPlans)
}
```

---

## 📝 开发规范

### 命名规范

- **页面文件夹**: 小写字母 + 连字符（如 `my-plans`）
- **组件文件夹**: 小写字母 + 连字符（如 `stepper`）
- **变量命名**: 驼峰式（如 `planData`）
- **常量命名**: 大写 + 下划线（如 `API_BASE_URL`）

### 代码风格

- 使用 2 空格缩进
- 字符串优先使用单引号
- 函数注释使用 JSDoc 格式

### Git 提交规范

```
feat: 添加方案对比页
fix: 修复登录失败问题
style: 优化详情页样式
docs: 更新 README
```

---

## 🐛 常见问题

### 1. 图片不显示

**原因**: 图片路径错误或文件缺失

**解决**:
- 检查图片路径是否正确（以 `/` 开头）
- 确认图片文件已放入 `images/` 目录

### 2. 网络请求失败

**原因**:
- 后端服务未启动
- API 地址配置错误
- 小程序域名未配置

**解决**:
- 开发阶段：开发者工具勾选"不校验合法域名"
- 生产环境：在小程序后台配置服务器域名

### 3. 登录失败

**原因**:
- 后端登录接口未实现
- AppID 配置错误

**解决**:
- 检查后端 `/api/v1/users/login` 接口
- 确认 AppID 与后端配置一致

### 4. 页面跳转失败

**原因**: 页面路径错误

**解决**:
- 检查 `app.json` 中的页面路径
- 使用绝对路径（以 `/pages/` 开头）

---

## 📚 参考文档

- [微信小程序官方文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)
- [UX/UI 设计规范](../../docs/design/miniapp-ux-ui-specification.md)
- [后端 API 文档](../../docs/api/openapi-specification.md)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 License

MIT License

---

**最后更新**: 2026-01-16
**维护者**: TeamVenture 开发团队
