# 🧪 微信开发者工具本地测试指南

## ✅ 配置已就绪

当前配置已经可以直接在微信开发者工具中运行了！

---

## 📋 测试前检查清单

### 1. ✅ 项目文件结构
```
✅ app.js, app.json, app.wxss
✅ 5 个页面（login, index, comparison, detail, myplans）
✅ 1 个组件（stepper）
✅ 3 个工具类（config, request, util）
✅ 配置文件（project.config.json, sitemap.json）
```

### 2. ⚠️ 图片资源（可选）
```
⚠️ TabBar 图标已临时移除，不影响测试
💡 如需图标，查看 images/README.md
```

### 3. ⚙️ 后端服务（可选）
```
⚠️ 需要后端 API 才能完整测试所有功能
💡 可以先测试 UI 和交互，后端调用会提示网络错误（正常）
```

---

## 🚀 启动步骤

### Step 1: 打开微信开发者工具

下载地址：https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html

### Step 2: 导入项目

1. 点击"+"或"导入项目"
2. 选择项目目录：
   ```
   /Users/qitmac001395/workspace/QAL/ideas/apps/teamventure/src/frontend/miniapp
   ```
3. AppID 选择：
   - **测试号**（推荐）- 选择"测试号"，无需注册
   - **真实 AppID** - 如果有小程序账号，输入 AppID

### Step 3: 项目设置

**重要**：在微信开发者工具中配置以下选项

#### 3.1 开发环境设置
```
菜单：设置 → 项目设置

✅ 勾选：不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书
✅ 勾选：启用调试基础库
✅ 基础库版本：选择 2.33.0 或更高
```

#### 3.2 本地设置
```
菜单：设置 → 本地设置

✅ 勾选：启用自动编译
✅ 勾选：启用代码提示
✅ 勾选：启用代码格式化
```

### Step 4: 编译运行

点击工具栏的"编译"按钮，或者快捷键：
- macOS: `⌘ + B`
- Windows: `Ctrl + B`

---

## 📱 测试模式

### ✅ 当前配置：模拟数据模式已启用

**重要提示**：项目已配置为使用模拟数据进行测试！

在 `utils/config.js` 中：
```javascript
export const USE_MOCK_DATA = true  // ✅ 已启用
```

这意味着：
- ✅ 所有 API 请求会自动返回模拟数据
- ✅ 无需启动后端服务即可测试完整流程
- ✅ 控制台会显示 `[MOCK]` 标记的日志
- ✅ 模拟 800ms 网络延迟，体验更真实

### 模式 1: 模拟器测试（推荐）

**优点**：
- 快速调试
- 可以查看控制台日志
- 方便调试网络请求
- 自动使用模拟数据

**操作**：
直接在开发者工具中测试，无需真机

### 模式 2: 真机调试

**优点**：
- 真实环境测试
- 测试性能和体验
- 测试真实网络请求

**操作**：
1. 点击工具栏"预览"或"真机调试"
2. 扫描二维码
3. 在手机上打开

---

## 🎯 功能测试清单

### 阶段 1: UI 测试（不依赖后端）

#### ✅ 登录页
- [ ] 页面正常显示
- [ ] 渐变背景效果正常
- [ ] 功能亮点卡片显示
- [ ] 用户协议勾选框正常

#### ✅ 生成方案页（首页）
- [ ] TabBar 切换正常
- [ ] Step 1 表单显示正常
- [ ] 人数 Stepper 组件工作正常
- [ ] 快捷按钮（20/50/100人）点击正常
- [ ] 日期选择器弹出正常
- [ ] 人均预算实时计算正确
- [ ] 天数计算正确
- [ ] 点击"下一步"跳转到 Step 2
- [ ] Step 2 偏好选择显示正常
- [ ] 标签（Chip）多选/单选正常
- [ ] 点击"上一步"返回 Step 1

#### ✅ 我的方案页
- [ ] 空状态显示正常
- [ ] "去生成方案"按钮跳转正常

### 阶段 2: 交互测试（模拟数据）

#### ✅ 模拟数据已自动集成

**无需手动添加测试数据！** 系统已自动集成模拟数据：

- 3 个完整的团建方案（经济型、平衡型、品质型）
- 每个方案包含详细行程
- 在 `utils/mock-data.js` 中查看完整数据

**测试流程**：
1. 在首页填写团建需求表单
2. 点击"生成方案"
3. 系统自动返回 3 个模拟方案（无需后端）
4. 可以正常查看对比、详情等所有功能

#### 📝 模拟数据示例（仅供参考，无需手动添加）

以下是系统自动返回的模拟数据结构：

```javascript
// 这是系统自动返回的数据，无需手动添加
const mockPlans = [
    {
      plan_id: 'mock_1',
      plan_name: '经济实惠·怀柔山野团建',
      plan_type: 'budget',
      budget_total: 35000,
      people_count: 50,
      start_date: '2025-05-10',
      end_date: '2025-05-11',
      duration_days: 2,
      recommended: false,
      suitable_for: ['预算有限', '注重性价比'],
      preferences: {
        accommodation_level: 'budget',
      },
      itinerary: {
        days: [
          {
            day: 1,
            date: '2025-05-10',
            items: [
              {
                time_start: '08:30',
                time_end: '09:00',
                activity: '公司集合，统一大巴出发',
                location: '公司楼下'
              }
            ]
          }
        ]
      }
    },
    {
      plan_id: 'mock_2',
      plan_name: '平衡之选·密云水库度假',
      plan_type: 'standard',
      budget_total: 45000,
      people_count: 50,
      start_date: '2025-05-10',
      end_date: '2025-05-11',
      duration_days: 2,
      recommended: true,
      suitable_for: ['性价比优先', '体验均衡'],
      preferences: {
        accommodation_level: 'standard',
      },
      itinerary: { days: [] }
    },
    {
      plan_id: 'mock_3',
      plan_name: '品质体验·古北水镇团建',
      plan_type: 'premium',
      budget_total: 60000,
      people_count: 50,
      start_date: '2025-05-10',
      end_date: '2025-05-11',
      duration_days: 2,
      recommended: false,
      suitable_for: ['重视体验', '预算充足'],
      preferences: {
        accommodation_level: 'premium',
      },
      itinerary: { days: [] }
    }
  ]

  this.processPlanData(mockPlans)
}
```

#### ✅ 方案对比页测试
- [ ] 3 张方案卡片横向滚动
- [ ] 推荐标签显示
- [ ] 点击卡片选中状态切换
- [ ] 对比表格展开/折叠
- [ ] 点击"查看详情"跳转详情页
- [ ] 点击"选择此方案"跳转详情页

#### ✅ 方案详情页测试
- [ ] 概览卡片显示完整
- [ ] 行程面板展开/折叠

### 阶段 3: 后端联调测试

#### 🔧 切换到真实后端模式

当后端服务准备好后，编辑 `utils/config.js`:

```javascript
// 1. 关闭模拟数据模式
export const USE_MOCK_DATA = false  // ❌ 改为 false

// 2. 配置后端地址
const ENV = 'dev'  // 开发环境

const API_BASE_URLS = {
  dev: 'http://localhost:8080/api/v1'  // 确保后端已启动
}
```

**重要**：
- 先启动后端服务
- 确认后端地址正确
- 在微信开发者工具中勾选"不校验合法域名"

#### ✅ 网络请求测试
- [ ] 登录 API 调用成功
- [ ] 生成方案 API 调用成功
- [ ] 获取方案列表 API 调用成功
- [ ] 确认方案 API 调用成功

---

## 🐛 常见问题与解决

### 问题 1: 编译失败

**现象**：点击编译后报错

**可能原因**：
- 文件路径错误
- JSON 格式错误
- 缺少必需文件

**解决**：
1. 查看控制台错误提示
2. 检查报错的文件和行号
3. 确认所有 JSON 文件格式正确

### 问题 2: 页面显示空白

**现象**：页面一片空白

**可能原因**：
- WXML 语法错误
- 数据未正确加载
- 条件渲染导致不显示

**解决**：
1. 打开调试器（Console 面板）
2. 查看是否有错误日志
3. 检查 data 数据是否正确

### 问题 3: 网络请求失败

**现象**：提示"网络错误"或"请求失败"

**可能原因**：
- 后端服务未启动
- API 地址配置错误
- 未勾选"不校验合法域名"

**解决**：
1. 确认后端服务已启动
2. 检查 `utils/config.js` 中的地址
3. 确认已勾选"不校验合法域名"

### 问题 4: TabBar 不显示

**现象**：底部 TabBar 没有显示

**可能原因**：
- 页面不是 TabBar 页面
- TabBar 配置错误

**解决**：
1. 确认当前页面是 `pages/index/index` 或 `pages/myplans/myplans`
2. 检查 `app.json` 中的 tabBar 配置

### 问题 5: 真机调试报错

**现象**：真机上运行报错，但模拟器正常

**可能原因**：
- 网络环境不同（真机无法访问 localhost）
- 权限问题
- 基础库版本不兼容

**解决**：
1. 使用内网穿透工具（如 ngrok）暴露本地服务
2. 或部署后端到云服务器
3. 检查手机基础库版本

---

## 📊 调试技巧

### 1. 使用 Console 查看日志

```javascript
console.log('页面数据:', this.data)
console.log('API 响应:', result)
```

### 2. 使用 Network 面板查看请求

工具栏 → Network → 查看所有网络请求

### 3. 使用 AppData 面板查看数据

工具栏 → AppData → 查看页面实时数据

### 4. 使用 Storage 面板查看缓存

工具栏 → Storage → 查看本地存储

### 5. 使用 Wxml 面板查看结构

工具栏 → Wxml → 查看页面 DOM 结构

---

## ✅ 测试完成检查

测试完成后，确认以下功能正常：

- [ ] 所有页面可以正常打开
- [ ] 页面间跳转流畅
- [ ] 表单输入和验证正常
- [ ] TabBar 切换正常
- [ ] 数据显示正确
- [ ] 交互反馈及时
- [ ] 没有明显的性能问题

---

## 🎯 下一步

测试通过后，可以：

1. **准备图片资源** - 添加 TabBar 图标和 Logo
2. **连接真实后端** - 测试完整业务流程
3. **优化性能** - 根据测试结果优化
4. **提交审核** - 准备上线

---

## 📞 需要帮助？

遇到问题可以：
1. 查看微信开发者工具文档
2. 查看本项目的 README.md
3. 查看 UX/UI 设计规范文档

---

**祝测试顺利！** 🎉
