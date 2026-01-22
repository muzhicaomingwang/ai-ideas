# AI辅助产品开发实战课程大纲 v2.0

> 面向零代码基础的产品人员，通过AI编程助手实现完整小程序产品
> 案例项目：TeamVenture AI团建策划助手（微信小程序）
> 核心工具：Claude Code（主力）、Cursor（辅助）

---

## 课程设计原则

1. **MVP优先** - 先实现最小可用版本，再迭代优化
2. **Claude Code主导** - 90%的代码由AI生成，学员专注理解业务逻辑
3. **5分钟单元** - 每个学习单元控制在5分钟内，便于碎片化学习
4. **即时验证** - 每个单元都有明确的验证点，确保学习效果

---

## Lesson 0：课程导学与环境准备（30分钟）

### 学习目标
- 理解AI辅助开发的核心理念
- 完成开发环境的基础配置
- 熟悉本课程的案例项目背景

---

### 单元0.1：课程介绍与学习方法（5分钟）

#### 本课程是什么
- 面向**零代码基础**的产品人员
- 通过AI编程助手（Claude Code）实现完整小程序
- 案例项目：TeamVenture AI团建策划助手

#### 学习方法
1. **观察** - 看AI如何生成代码
2. **理解** - 理解代码的业务含义（不需要记住语法）
3. **验证** - 在真实环境中运行验证
4. **迭代** - 根据效果调整需求描述

#### 你不需要
- ❌ 记住任何编程语法
- ❌ 理解底层技术原理
- ❌ 有任何编程经验

#### 你需要做的
- ✅ 清晰描述产品需求
- ✅ 验证功能是否符合预期
- ✅ 学会与AI高效沟通

**验证点**：理解"AI辅助开发"与"传统编程学习"的区别

---

### 单元0.2：VPN与网络环境配置（5分钟）

#### 为什么需要VPN
- Claude Code 等AI工具需要访问国际网络
- 部分开发文档托管在国际站点

#### 推荐方案
| 方案 | 适用场景 | 参考价格 |
|------|---------|---------|
| 机场服务 | 个人学习 | ¥20-50/月 |
| 企业VPN | 公司环境 | 咨询IT部门 |

#### 配置要点
1. 选择**全局代理**模式（而非PAC模式）
2. 验证：访问 `https://claude.ai` 能正常打开
3. 终端代理：确保命令行工具也能访问

#### 常见问题
- **问**：连接不稳定怎么办？
- **答**：切换节点，优先选择日本/新加坡节点

**验证点**：能够正常访问 claude.ai 网站

---

### 单元0.3：Git版本控制基础（5分钟）

#### Git是什么
- 代码的"时光机"，可以回退到任意历史版本
- 团队协作的基础工具

#### 核心概念（只需理解，不需记忆）
| 概念 | 类比 | 说明 |
|------|------|------|
| Repository | 文件夹 | 存放项目所有文件的地方 |
| Commit | 存档点 | 保存当前状态的快照 |
| Branch | 平行世界 | 可以同时存在多个版本 |
| Pull/Push | 上传/下载 | 与云端同步代码 |

#### 安装Git
- **Mac**: 终端输入 `git --version`，如未安装会提示安装
- **Windows**: 下载 Git for Windows

#### 常用命令（Claude Code会自动执行）
```bash
git status    # 查看当前状态
git add .     # 添加所有修改
git commit    # 保存当前版本
git push      # 上传到云端
```

**验证点**：终端输入 `git --version` 显示版本号

---

### 单元0.4：Claude Code工具介绍（5分钟）

#### Claude Code是什么
- Anthropic公司开发的AI编程助手
- 可以理解自然语言需求，生成完整代码
- 支持多种编程语言和框架

#### 核心能力
1. **代码生成** - 根据需求描述生成代码
2. **代码解释** - 解释现有代码的功能
3. **问题修复** - 分析错误并提供修复方案
4. **代码重构** - 优化现有代码结构

#### 与Cursor的区别
| 特性 | Claude Code | Cursor |
|------|-------------|--------|
| 定位 | 终端AI助手 | IDE集成AI |
| 交互方式 | 命令行对话 | 编辑器内对话 |
| 适用场景 | 项目级任务 | 文件级编辑 |
| 本课程角色 | **主力工具** | 辅助工具 |

#### 安装Claude Code
```bash
# 需要Node.js环境
npm install -g @anthropic-ai/claude-code
```

**验证点**：终端输入 `claude --version` 显示版本号

---

### 单元0.5：微信小程序基础概念（5分钟）

#### 小程序是什么
- 运行在微信内的轻量级应用
- 无需下载安装，即用即走
- 适合工具类、服务类产品

#### 技术架构（了解即可）
```
小程序结构
├── app.json          # 全局配置
├── app.js            # 全局逻辑
├── pages/            # 页面目录
│   ├── index/        # 首页
│   │   ├── index.wxml    # 页面结构（类似HTML）
│   │   ├── index.wxss    # 页面样式（类似CSS）
│   │   └── index.js      # 页面逻辑
│   └── ...
└── utils/            # 工具函数
```

#### 开发工具
- **微信开发者工具**：官方IDE，用于预览和调试
- 下载地址：微信公众平台 → 开发 → 开发者工具

#### 本地存储API（核心）
```javascript
// 保存数据
wx.setStorageSync('key', value)

// 读取数据
const data = wx.getStorageSync('key')

// 删除数据
wx.removeStorageSync('key')
```

**验证点**：成功安装微信开发者工具并创建测试项目

---

### 单元0.6：案例项目介绍 - TeamVenture（5分钟）

#### 产品定位
**TeamVenture** 是一款AI团建策划助手，帮助HR/行政人员快速生成团建方案。

#### 核心功能
1. **需求收集** - 输入团建人数、预算、偏好等
2. **方案生成** - AI智能生成3套差异化方案
3. **方案管理** - 保存、对比、确认方案
4. **供应商对接** - 一键联系合作供应商

#### 用户旅程
```
输入需求 → AI生成方案 → 查看对比 → 确认方案 → 联系供应商
```

#### 技术栈概览
| 层级 | 技术选型 | 说明 |
|------|---------|------|
| 前端 | 微信小程序 | 本课程重点 |
| 后端 | Spring Boot + Python | AI服务集成 |
| 数据库 | MySQL | 方案数据存储 |
| 部署 | Docker | 容器化部署 |

#### 本课程范围
- ✅ Lesson 1-3：前端小程序核心功能
- ⏳ 后续课程：后端服务、部署上线

**验证点**：理解TeamVenture的产品定位和核心功能

---

### Lesson 0 课后作业

1. **环境检查清单**
   - [ ] VPN配置完成，能访问 claude.ai
   - [ ] Git已安装，`git --version` 正常
   - [ ] Claude Code已安装
   - [ ] 微信开发者工具已安装

2. **思考题**
   - 作为产品人员，你认为AI辅助开发最大的价值是什么？
   - TeamVenture还可以增加哪些功能来提升用户体验？

---

## Lesson 1：小红书内容导入功能（60分钟）

### 学习目标
- 理解小程序页面跳转与参数传递
- 掌握本地存储的增删改查操作
- 实现完整的内容导入功能闭环

---

### Phase 1：需求理解与页面设计（15分钟）

#### 单元1.1：功能需求分析（5分钟）

##### 业务背景
HR在小红书看到优质团建攻略，希望一键导入到TeamVenture生成方案。

##### 用户故事
```
作为HR，我希望能够导入小红书的团建攻略链接，
以便AI能参考这些内容生成更符合我需求的方案。
```

##### 功能拆解
| 步骤 | 用户操作 | 系统响应 |
|------|---------|---------|
| 1 | 粘贴小红书链接 | 解析链接获取内容 |
| 2 | 确认导入 | 存储到本地 |
| 3 | 查看已导入列表 | 展示所有导入内容 |
| 4 | 删除不需要的 | 从本地移除 |

##### 数据结构设计
```javascript
// 单条导入记录
{
  id: "import_001",           // 唯一标识
  sourceUrl: "https://...",   // 小红书链接
  title: "三亚团建攻略",       // 内容标题
  summary: "适合30人...",     // 内容摘要
  importTime: 1705123456789   // 导入时间戳
}
```

**验证点**：能够描述完整的功能流程

---

#### 单元1.2：页面结构设计（5分钟）

##### 页面规划
| 页面 | 路径 | 功能 |
|------|------|------|
| 导入页 | /pages/import/import | 粘贴链接、确认导入 |
| 列表页 | /pages/imports/imports | 查看已导入内容 |

##### 导入页UI设计
```
┌─────────────────────────────┐
│     小红书内容导入           │
├─────────────────────────────┤
│                             │
│  请粘贴小红书链接：          │
│  ┌───────────────────────┐  │
│  │ https://...           │  │
│  └───────────────────────┘  │
│                             │
│  ┌───────────────────────┐  │
│  │      解析内容         │  │
│  └───────────────────────┘  │
│                             │
│  ─────────────────────────  │
│  解析结果：                  │
│  标题：三亚团建攻略          │
│  摘要：适合30人规模...       │
│                             │
│  ┌───────────────────────┐  │
│  │      确认导入         │  │
│  └───────────────────────┘  │
│                             │
└─────────────────────────────┘
```

##### 列表页UI设计
```
┌─────────────────────────────┐
│     已导入内容              │
├─────────────────────────────┤
│ ┌─────────────────────────┐ │
│ │ 三亚团建攻略            │ │
│ │ 适合30人规模...         │ │
│ │ 2024-01-13 导入    [删除]│ │
│ └─────────────────────────┘ │
│ ┌─────────────────────────┐ │
│ │ 莫干山2日游推荐          │ │
│ │ 包含住宿餐饮...         │ │
│ │ 2024-01-12 导入    [删除]│ │
│ └─────────────────────────┘ │
└─────────────────────────────┘
```

**验证点**：理解两个页面的职责划分

---

#### 单元1.3：Claude Code实现页面框架（5分钟）

##### 向Claude Code描述需求
```
请帮我创建两个小程序页面：
1. 导入页（/pages/import/import）
   - 一个输入框用于粘贴链接
   - 一个"解析"按钮
   - 解析结果展示区域
   - 一个"确认导入"按钮

2. 列表页（/pages/imports/imports）
   - 展示已导入内容的列表
   - 每条记录显示标题、摘要、时间
   - 每条记录有删除按钮
```

##### Claude Code生成的代码结构
```
pages/
├── import/
│   ├── import.wxml      # 页面结构
│   ├── import.wxss      # 页面样式
│   ├── import.js        # 页面逻辑
│   └── import.json      # 页面配置
└── imports/
    ├── imports.wxml
    ├── imports.wxss
    ├── imports.js
    └── imports.json
```

##### 验证步骤
1. 在微信开发者工具中打开项目
2. 访问 `/pages/import/import` 查看导入页
3. 访问 `/pages/imports/imports` 查看列表页

**验证点**：两个页面能正常显示基础UI

---

### Phase 2：本地存储实现（20分钟）

#### 单元1.4：存储API详解（5分钟）

##### 小程序本地存储特点
| 特性 | 说明 |
|------|------|
| 容量 | 单个key最大1MB，总容量10MB |
| 持久性 | 除非用户删除小程序，否则永久保存 |
| 同步API | setStorageSync / getStorageSync |
| 异步API | setStorage / getStorage |

##### 本课程使用同步API
```javascript
// 保存数据（同步）
wx.setStorageSync('imports', importList)

// 读取数据（同步）
const importList = wx.getStorageSync('imports') || []

// 删除数据（同步）
wx.removeStorageSync('imports')
```

##### 为什么用同步API？
- 代码更简洁，易于理解
- 数据量小时性能差异可忽略
- 适合学习阶段

**验证点**：理解同步存储API的基本用法

---

#### 单元1.5：实现保存功能（5分钟）

##### 向Claude Code描述需求
```
请帮我实现导入页的保存功能：
1. 用户点击"确认导入"按钮
2. 将解析结果保存到本地存储
3. 存储key为"imports"，值为数组
4. 每条记录包含：id, sourceUrl, title, summary, importTime
5. 保存成功后提示用户
```

##### Claude Code生成的核心代码
```javascript
// pages/import/import.js
Page({
  data: {
    inputUrl: '',
    parsedResult: null
  },

  // 确认导入
  confirmImport() {
    if (!this.data.parsedResult) {
      wx.showToast({ title: '请先解析链接', icon: 'none' })
      return
    }

    // 读取现有数据
    const imports = wx.getStorageSync('imports') || []

    // 添加新记录
    const newImport = {
      id: 'import_' + Date.now(),
      sourceUrl: this.data.inputUrl,
      title: this.data.parsedResult.title,
      summary: this.data.parsedResult.summary,
      importTime: Date.now()
    }
    imports.unshift(newImport)  // 添加到开头

    // 保存回本地
    wx.setStorageSync('imports', imports)

    wx.showToast({ title: '导入成功', icon: 'success' })
  }
})
```

##### 验证步骤
1. 在导入页输入测试链接
2. 点击解析（暂时用模拟数据）
3. 点击确认导入
4. 在开发者工具的Storage面板查看数据

**验证点**：数据成功保存到本地存储

---

#### 单元1.6：实现读取功能（5分钟）

##### 向Claude Code描述需求
```
请帮我实现列表页的读取功能：
1. 页面加载时读取本地存储的imports数据
2. 将数据渲染到页面列表中
3. 如果没有数据，显示"暂无导入内容"
4. 时间戳转换为可读格式（如：2024-01-13 14:30）
```

##### Claude Code生成的核心代码
```javascript
// pages/imports/imports.js
Page({
  data: {
    importList: []
  },

  onLoad() {
    this.loadImports()
  },

  // 每次显示页面时刷新数据
  onShow() {
    this.loadImports()
  },

  loadImports() {
    const imports = wx.getStorageSync('imports') || []

    // 格式化时间
    const formattedList = imports.map(item => ({
      ...item,
      formattedTime: this.formatTime(item.importTime)
    }))

    this.setData({ importList: formattedList })
  },

  formatTime(timestamp) {
    const date = new Date(timestamp)
    return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')} ${String(date.getHours()).padStart(2,'0')}:${String(date.getMinutes()).padStart(2,'0')}`
  }
})
```

##### 对应的WXML模板
```xml
<!-- pages/imports/imports.wxml -->
<view class="container">
  <view wx:if="{{importList.length === 0}}" class="empty">
    暂无导入内容
  </view>

  <view wx:for="{{importList}}" wx:key="id" class="import-item">
    <view class="title">{{item.title}}</view>
    <view class="summary">{{item.summary}}</view>
    <view class="time">{{item.formattedTime}} 导入</view>
  </view>
</view>
```

**验证点**：列表页能正确显示已导入的内容

---

#### 单元1.7：实现删除功能（5分钟）

##### 向Claude Code描述需求
```
请帮我实现列表页的删除功能：
1. 每条记录右侧有删除按钮
2. 点击删除前弹出确认框
3. 确认后从本地存储中删除对应记录
4. 刷新列表显示
```

##### Claude Code生成的核心代码
```javascript
// pages/imports/imports.js 添加删除方法
deleteImport(e) {
  const id = e.currentTarget.dataset.id

  wx.showModal({
    title: '确认删除',
    content: '删除后无法恢复，确定要删除吗？',
    success: (res) => {
      if (res.confirm) {
        // 读取数据
        let imports = wx.getStorageSync('imports') || []

        // 过滤掉要删除的记录
        imports = imports.filter(item => item.id !== id)

        // 保存回本地
        wx.setStorageSync('imports', imports)

        // 刷新列表
        this.loadImports()

        wx.showToast({ title: '删除成功', icon: 'success' })
      }
    }
  })
}
```

##### WXML中绑定删除事件
```xml
<view class="import-item">
  <view class="content">
    <view class="title">{{item.title}}</view>
    <view class="summary">{{item.summary}}</view>
    <view class="time">{{item.formattedTime}} 导入</view>
  </view>
  <view class="delete-btn" bindtap="deleteImport" data-id="{{item.id}}">
    删除
  </view>
</view>
```

**验证点**：能成功删除指定记录，列表实时更新

---

### Phase 3：页面跳转与参数传递（15分钟）

#### 单元1.8：页面跳转方式（5分钟）

##### 小程序页面跳转API
| API | 说明 | 适用场景 |
|-----|------|---------|
| wx.navigateTo | 保留当前页，跳转到新页 | 详情页 |
| wx.redirectTo | 关闭当前页，跳转到新页 | 登录后跳转 |
| wx.switchTab | 跳转到tabBar页面 | 底部导航 |
| wx.navigateBack | 返回上一页 | 完成操作后返回 |

##### 常用跳转代码
```javascript
// 跳转到导入页
wx.navigateTo({
  url: '/pages/import/import'
})

// 带参数跳转
wx.navigateTo({
  url: '/pages/import/import?from=home'
})

// 返回上一页
wx.navigateBack()

// 返回并传递数据（通过事件通道）
const pages = getCurrentPages()
const prevPage = pages[pages.length - 2]
prevPage.setData({ needRefresh: true })
wx.navigateBack()
```

**验证点**：理解不同跳转方式的使用场景

---

#### 单元1.9：从首页跳转到导入页（5分钟）

##### 向Claude Code描述需求
```
请帮我在首页添加一个"导入小红书内容"的入口：
1. 首页添加一个明显的导入按钮
2. 点击后跳转到导入页
3. 导入页右上角有"查看已导入"按钮，跳转到列表页
```

##### Claude Code生成的首页代码
```xml
<!-- pages/index/index.wxml -->
<view class="container">
  <!-- 其他首页内容 -->

  <view class="import-entry" bindtap="goToImport">
    <image src="/images/xiaohongshu.png" class="icon"/>
    <text>导入小红书内容</text>
    <text class="arrow">></text>
  </view>
</view>
```

```javascript
// pages/index/index.js
Page({
  goToImport() {
    wx.navigateTo({
      url: '/pages/import/import'
    })
  }
})
```

##### 导入页的导航栏配置
```json
// pages/import/import.json
{
  "navigationBarTitleText": "导入小红书内容",
  "usingComponents": {}
}
```

**验证点**：能从首页成功跳转到导入页

---

#### 单元1.10：导入成功后的跳转（5分钟）

##### 向Claude Code描述需求
```
请优化导入成功后的体验：
1. 导入成功后询问用户是否查看已导入列表
2. 用户点击"查看"则跳转到列表页
3. 用户点击"继续导入"则清空输入框，留在当前页
```

##### Claude Code生成的优化代码
```javascript
// pages/import/import.js
confirmImport() {
  // ... 保存逻辑 ...

  wx.showModal({
    title: '导入成功',
    content: '是否查看已导入内容？',
    confirmText: '查看',
    cancelText: '继续导入',
    success: (res) => {
      if (res.confirm) {
        wx.navigateTo({
          url: '/pages/imports/imports'
        })
      } else {
        // 清空输入，继续导入
        this.setData({
          inputUrl: '',
          parsedResult: null
        })
      }
    }
  })
}
```

**验证点**：导入成功后弹出选择框，两个选项都能正常工作

---

### Phase 4：功能完善与优化（10分钟）

#### 单元1.11：链接解析模拟（5分钟）

##### 为什么先用模拟数据？
- 真实解析需要后端服务支持
- 前端逻辑验证完成后再对接
- 符合MVP开发理念

##### 向Claude Code描述需求
```
请实现链接解析的模拟逻辑：
1. 检查链接是否是小红书格式
2. 模拟解析延迟（1秒）
3. 返回模拟的标题和摘要
```

##### Claude Code生成的模拟代码
```javascript
// pages/import/import.js
parseLink() {
  const url = this.data.inputUrl.trim()

  // 校验链接格式
  if (!url.includes('xiaohongshu.com') && !url.includes('xhslink.com')) {
    wx.showToast({ title: '请输入小红书链接', icon: 'none' })
    return
  }

  wx.showLoading({ title: '解析中...' })

  // 模拟解析延迟
  setTimeout(() => {
    wx.hideLoading()

    // 模拟解析结果
    this.setData({
      parsedResult: {
        title: '团建攻略：' + Math.random().toString(36).substr(2, 6),
        summary: '这是一篇关于团建的优质内容，包含行程安排、预算建议等实用信息...'
      }
    })
  }, 1000)
}
```

**验证点**：输入小红书链接能成功"解析"出模拟数据

---

#### 单元1.12：用户体验优化（5分钟）

##### 向Claude Code描述需求
```
请优化导入功能的用户体验：
1. 输入框placeholder提示"请粘贴小红书链接"
2. 解析按钮在无输入时禁用
3. 确认导入按钮在无解析结果时禁用
4. 添加加载状态显示
5. 列表为空时显示引导文案
```

##### Claude Code生成的优化代码
```xml
<!-- pages/import/import.wxml -->
<view class="container">
  <input
    class="url-input"
    placeholder="请粘贴小红书链接"
    value="{{inputUrl}}"
    bindinput="onInputChange"
  />

  <button
    class="parse-btn {{inputUrl ? '' : 'disabled'}}"
    disabled="{{!inputUrl}}"
    bindtap="parseLink"
  >
    解析内容
  </button>

  <view wx:if="{{parsedResult}}" class="result">
    <view class="result-title">{{parsedResult.title}}</view>
    <view class="result-summary">{{parsedResult.summary}}</view>
  </view>

  <button
    class="confirm-btn {{parsedResult ? '' : 'disabled'}}"
    disabled="{{!parsedResult}}"
    bindtap="confirmImport"
  >
    确认导入
  </button>
</view>
```

```css
/* pages/import/import.wxss */
.disabled {
  background-color: #cccccc;
  color: #666666;
}

.url-input {
  border: 1px solid #ddd;
  padding: 20rpx;
  border-radius: 8rpx;
  margin-bottom: 20rpx;
}

.parse-btn, .confirm-btn {
  background-color: #07c160;
  color: white;
  margin: 20rpx 0;
}

.result {
  background-color: #f5f5f5;
  padding: 20rpx;
  border-radius: 8rpx;
  margin: 20rpx 0;
}
```

**验证点**：按钮状态正确，交互流畅

---

### Lesson 1 课后作业

#### 实践任务
1. **功能增强**：为已导入列表添加搜索功能，支持按标题搜索
2. **数据校验**：添加重复链接检测，避免重复导入同一内容
3. **批量操作**：实现批量删除功能

#### 思考题
1. 如果需要限制导入数量（如最多20条），应该在哪里添加校验？
2. 本地存储有10MB容量限制，如果数据量大应该如何处理？

#### 代码提交
将完成的代码提交到Git仓库，提交信息格式：
```
feat(import): 完成小红书内容导入功能

- 实现链接解析与保存
- 实现已导入列表展示
- 实现删除功能
```

---

## Lesson 2：方案状态机管理（60分钟）

### 学习目标
- 理解状态机在产品设计中的应用
- 掌握状态流转的实现方法
- 实现方案的完整生命周期管理

---

### Phase 1：状态机设计（15分钟）

#### 单元2.1：什么是状态机（5分钟）

##### 生活中的状态机
| 场景 | 状态 | 触发条件 |
|------|------|---------|
| 订单 | 待付款→已付款→已发货→已收货 | 用户操作/系统事件 |
| 文章 | 草稿→待审核→已发布→已下架 | 作者/审核员操作 |
| 方案 | 草稿→生成中→已完成→已确认 | 用户操作/AI完成 |

##### 状态机的三要素
1. **状态（State）** - 事物当前所处的阶段
2. **事件（Event）** - 触发状态变化的动作
3. **转换（Transition）** - 从一个状态到另一个状态的过程

##### 为什么需要状态机？
- **防止非法操作** - 草稿不能直接变成已确认
- **追踪生命周期** - 知道方案经历了哪些阶段
- **触发关联逻辑** - 状态变化时执行相应操作

**验证点**：能举出生活中的状态机例子

---

#### 单元2.2：方案状态设计（5分钟）

##### TeamVenture方案状态定义

```
┌──────────────────────────────────────────────────────────────┐
│                     方案状态流转图                            │
│                                                              │
│   ┌─────────┐    提交生成    ┌────────────┐                  │
│   │  DRAFT  │ ──────────────→│ GENERATING │                  │
│   │  草稿   │                │   生成中   │                  │
│   └─────────┘                └─────┬──────┘                  │
│        ↑                          │                          │
│        │ 修改                     │ AI完成                   │
│        │                          ↓                          │
│   ┌─────────┐    确认方案    ┌────────────┐                  │
│   │CONFIRMED│ ←─────────────│ COMPLETED  │                  │
│   │  已确认  │               │   已完成   │                  │
│   └────┬────┘                └────────────┘                  │
│        │                                                     │
│        │ 归档                                                │
│        ↓                                                     │
│   ┌─────────┐                                               │
│   │ARCHIVED │                                               │
│   │  已归档  │                                               │
│   └─────────┘                                               │
└──────────────────────────────────────────────────────────────┘
```

##### 状态说明
| 状态 | 英文 | 说明 | 可执行操作 |
|------|------|------|-----------|
| 草稿 | DRAFT | 用户正在填写需求 | 编辑、提交生成、删除 |
| 生成中 | GENERATING | AI正在生成方案 | 等待（不可操作） |
| 已完成 | COMPLETED | AI生成完成 | 查看、确认、修改 |
| 已确认 | CONFIRMED | 用户确认采用 | 查看、联系供应商、归档 |
| 已归档 | ARCHIVED | 活动已结束 | 查看 |

**验证点**：能解释每个状态的含义和转换条件

---

#### 单元2.3：状态转换规则（5分钟）

##### 合法的状态转换
| 当前状态 | 允许转换到 | 触发条件 |
|---------|-----------|---------|
| DRAFT | GENERATING | 用户点击"生成方案" |
| GENERATING | COMPLETED | AI生成完成（系统自动） |
| GENERATING | DRAFT | 生成失败（系统自动） |
| COMPLETED | CONFIRMED | 用户点击"确认方案" |
| COMPLETED | DRAFT | 用户点击"修改需求" |
| CONFIRMED | ARCHIVED | 用户点击"归档" |

##### 非法的状态转换（应被阻止）
- ❌ DRAFT → COMPLETED（不能跳过生成过程）
- ❌ COMPLETED → ARCHIVED（必须先确认）
- ❌ ARCHIVED → 任何状态（归档后不可修改）

##### 状态校验代码逻辑
```javascript
// 检查状态转换是否合法
function canTransition(fromStatus, toStatus) {
  const allowedTransitions = {
    'DRAFT': ['GENERATING'],
    'GENERATING': ['COMPLETED', 'DRAFT'],
    'COMPLETED': ['CONFIRMED', 'DRAFT'],
    'CONFIRMED': ['ARCHIVED'],
    'ARCHIVED': []
  }
  return allowedTransitions[fromStatus]?.includes(toStatus) || false
}
```

**验证点**：能判断哪些状态转换是合法的

---

### Phase 2：状态管理实现（20分钟）

#### 单元2.4：数据结构设计（5分钟）

##### 方案数据结构
```javascript
// 完整的方案数据结构
const plan = {
  id: "plan_001",                    // 方案ID
  status: "DRAFT",                   // 当前状态

  // 需求信息
  requirement: {
    teamSize: 30,                    // 团队人数
    budget: 500,                     // 人均预算
    duration: 2,                     // 活动天数
    preferences: ["户外", "团队协作"], // 偏好标签
    importedContents: ["import_001"] // 导入的小红书内容ID
  },

  // AI生成的方案内容
  content: {
    title: "三亚两日团建方案",
    itinerary: [...],                // 行程安排
    budgetBreakdown: {...},          // 预算明细
    suppliers: [...]                 // 推荐供应商
  },

  // 时间戳
  createdAt: 1705123456789,
  updatedAt: 1705123456789,
  confirmedAt: null,
  archivedAt: null,

  // 状态变更历史
  statusHistory: [
    { status: "DRAFT", timestamp: 1705123456789, reason: "创建" }
  ]
}
```

##### 存储结构
```javascript
// 本地存储的key
const STORAGE_KEYS = {
  PLANS: 'teamventure_plans',      // 所有方案列表
  CURRENT_PLAN: 'current_plan_id'  // 当前编辑的方案ID
}
```

**验证点**：理解方案数据结构的各个字段

---

#### 单元2.5：创建方案（DRAFT状态）（5分钟）

##### 向Claude Code描述需求
```
请帮我实现创建新方案的功能：
1. 用户点击"新建方案"按钮
2. 创建一个状态为DRAFT的新方案
3. 保存到本地存储
4. 跳转到需求填写页面
```

##### Claude Code生成的代码
```javascript
// utils/planManager.js
const STORAGE_KEY = 'teamventure_plans'

// 创建新方案
function createPlan() {
  const plans = wx.getStorageSync(STORAGE_KEY) || []

  const newPlan = {
    id: 'plan_' + Date.now(),
    status: 'DRAFT',
    requirement: {
      teamSize: null,
      budget: null,
      duration: null,
      preferences: [],
      importedContents: []
    },
    content: null,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    confirmedAt: null,
    archivedAt: null,
    statusHistory: [
      { status: 'DRAFT', timestamp: Date.now(), reason: '创建新方案' }
    ]
  }

  plans.unshift(newPlan)
  wx.setStorageSync(STORAGE_KEY, plans)
  wx.setStorageSync('current_plan_id', newPlan.id)

  return newPlan
}

module.exports = { createPlan }
```

```javascript
// pages/index/index.js
const planManager = require('../../utils/planManager')

Page({
  createNewPlan() {
    const plan = planManager.createPlan()
    wx.navigateTo({
      url: '/pages/requirement/requirement?planId=' + plan.id
    })
  }
})
```

**验证点**：点击创建按钮后能生成DRAFT状态的方案

---

#### 单元2.6：提交生成（DRAFT→GENERATING）（5分钟）

##### 向Claude Code描述需求
```
请帮我实现提交生成功能：
1. 用户填写完需求后点击"生成方案"
2. 校验必填字段（人数、预算、天数）
3. 将状态从DRAFT改为GENERATING
4. 记录状态变更历史
5. 跳转到等待页面
```

##### Claude Code生成的代码
```javascript
// utils/planManager.js 添加方法

// 更新方案状态
function updatePlanStatus(planId, newStatus, reason) {
  const plans = wx.getStorageSync(STORAGE_KEY) || []
  const planIndex = plans.findIndex(p => p.id === planId)

  if (planIndex === -1) {
    throw new Error('方案不存在')
  }

  const plan = plans[planIndex]

  // 校验状态转换是否合法
  if (!canTransition(plan.status, newStatus)) {
    throw new Error(`不能从 ${plan.status} 转换到 ${newStatus}`)
  }

  // 更新状态
  plan.status = newStatus
  plan.updatedAt = Date.now()
  plan.statusHistory.push({
    status: newStatus,
    timestamp: Date.now(),
    reason: reason || '状态变更'
  })

  // 特殊状态处理
  if (newStatus === 'CONFIRMED') {
    plan.confirmedAt = Date.now()
  } else if (newStatus === 'ARCHIVED') {
    plan.archivedAt = Date.now()
  }

  plans[planIndex] = plan
  wx.setStorageSync(STORAGE_KEY, plans)

  return plan
}

// 检查状态转换是否合法
function canTransition(fromStatus, toStatus) {
  const allowedTransitions = {
    'DRAFT': ['GENERATING'],
    'GENERATING': ['COMPLETED', 'DRAFT'],
    'COMPLETED': ['CONFIRMED', 'DRAFT'],
    'CONFIRMED': ['ARCHIVED'],
    'ARCHIVED': []
  }
  return allowedTransitions[fromStatus]?.includes(toStatus) || false
}

module.exports = { createPlan, updatePlanStatus, canTransition }
```

**验证点**：提交后状态变为GENERATING

---

#### 单元2.7：生成完成（GENERATING→COMPLETED）（5分钟）

##### 向Claude Code描述需求
```
请帮我实现AI生成完成的处理：
1. 模拟AI生成过程（延迟3秒）
2. 生成完成后状态改为COMPLETED
3. 填充模拟的方案内容
4. 自动跳转到方案详情页
```

##### Claude Code生成的代码
```javascript
// pages/generating/generating.js
const planManager = require('../../utils/planManager')

Page({
  data: {
    planId: null,
    progress: 0
  },

  onLoad(options) {
    this.setData({ planId: options.planId })
    this.simulateGeneration()
  },

  simulateGeneration() {
    // 模拟进度更新
    const progressInterval = setInterval(() => {
      if (this.data.progress < 90) {
        this.setData({ progress: this.data.progress + 10 })
      }
    }, 300)

    // 模拟AI生成（3秒后完成）
    setTimeout(() => {
      clearInterval(progressInterval)
      this.setData({ progress: 100 })

      // 更新方案状态和内容
      try {
        const plan = planManager.updatePlanStatus(
          this.data.planId,
          'COMPLETED',
          'AI生成完成'
        )

        // 填充模拟内容
        planManager.updatePlanContent(this.data.planId, {
          title: '精选团建方案',
          itinerary: [
            { day: 1, activities: ['破冰游戏', '团队午餐', '户外拓展'] },
            { day: 2, activities: ['主题工作坊', '总结分享', '返程'] }
          ],
          budgetBreakdown: {
            accommodation: 200,
            catering: 150,
            activities: 100,
            transport: 50
          }
        })

        wx.redirectTo({
          url: '/pages/plan-detail/plan-detail?planId=' + this.data.planId
        })
      } catch (error) {
        wx.showToast({ title: error.message, icon: 'none' })
      }
    }, 3000)
  }
})
```

**验证点**：等待3秒后自动跳转到详情页，状态为COMPLETED

---

### Phase 3：列表展示与操作（15分钟）

#### 单元2.8：方案列表展示（5分钟）

##### 向Claude Code描述需求
```
请帮我实现方案列表页：
1. 显示所有方案，按更新时间倒序
2. 每个方案显示：标题、状态、更新时间
3. 不同状态显示不同颜色的标签
4. 点击方案进入详情页
```

##### Claude Code生成的代码
```xml
<!-- pages/plans/plans.wxml -->
<view class="container">
  <view wx:if="{{plans.length === 0}}" class="empty">
    <text>暂无方案，点击下方按钮创建</text>
  </view>

  <view wx:for="{{plans}}" wx:key="id" class="plan-card" bindtap="goToDetail" data-id="{{item.id}}">
    <view class="plan-header">
      <text class="plan-title">{{item.content.title || '未命名方案'}}</text>
      <text class="status-tag {{item.status}}">{{statusMap[item.status]}}</text>
    </view>
    <view class="plan-info">
      <text>{{item.requirement.teamSize || '?'}}人 | </text>
      <text>¥{{item.requirement.budget || '?'}}/人 | </text>
      <text>{{item.requirement.duration || '?'}}天</text>
    </view>
    <view class="plan-time">
      更新于 {{item.formattedTime}}
    </view>
  </view>

  <view class="create-btn" bindtap="createNewPlan">
    + 新建方案
  </view>
</view>
```

```javascript
// pages/plans/plans.js
Page({
  data: {
    plans: [],
    statusMap: {
      'DRAFT': '草稿',
      'GENERATING': '生成中',
      'COMPLETED': '已完成',
      'CONFIRMED': '已确认',
      'ARCHIVED': '已归档'
    }
  },

  onShow() {
    this.loadPlans()
  },

  loadPlans() {
    const plans = wx.getStorageSync('teamventure_plans') || []
    const formattedPlans = plans.map(p => ({
      ...p,
      formattedTime: this.formatTime(p.updatedAt)
    }))
    this.setData({ plans: formattedPlans })
  },

  formatTime(timestamp) {
    const date = new Date(timestamp)
    return `${date.getMonth()+1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2,'0')}`
  },

  goToDetail(e) {
    const planId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: '/pages/plan-detail/plan-detail?planId=' + planId
    })
  }
})
```

```css
/* pages/plans/plans.wxss */
.status-tag {
  padding: 4rpx 12rpx;
  border-radius: 4rpx;
  font-size: 24rpx;
}
.status-tag.DRAFT { background: #f0f0f0; color: #666; }
.status-tag.GENERATING { background: #e6f7ff; color: #1890ff; }
.status-tag.COMPLETED { background: #f6ffed; color: #52c41a; }
.status-tag.CONFIRMED { background: #fff7e6; color: #fa8c16; }
.status-tag.ARCHIVED { background: #f5f5f5; color: #999; }
```

**验证点**：列表正确显示所有方案，状态标签颜色正确

---

#### 单元2.9：状态操作按钮（5分钟）

##### 向Claude Code描述需求
```
请帮我在方案详情页添加状态操作按钮：
1. DRAFT状态：显示"生成方案"按钮
2. COMPLETED状态：显示"确认方案"和"修改需求"按钮
3. CONFIRMED状态：显示"联系供应商"和"归档"按钮
4. ARCHIVED状态：不显示操作按钮
5. GENERATING状态：显示"生成中..."禁用按钮
```

##### Claude Code生成的代码
```xml
<!-- pages/plan-detail/plan-detail.wxml -->
<view class="action-buttons">
  <!-- DRAFT状态 -->
  <block wx:if="{{plan.status === 'DRAFT'}}">
    <button class="btn-primary" bindtap="submitGenerate">生成方案</button>
    <button class="btn-default" bindtap="deletePlan">删除</button>
  </block>

  <!-- GENERATING状态 -->
  <block wx:elif="{{plan.status === 'GENERATING'}}">
    <button class="btn-disabled" disabled>生成中...</button>
  </block>

  <!-- COMPLETED状态 -->
  <block wx:elif="{{plan.status === 'COMPLETED'}}">
    <button class="btn-primary" bindtap="confirmPlan">确认方案</button>
    <button class="btn-default" bindtap="modifyRequirement">修改需求</button>
  </block>

  <!-- CONFIRMED状态 -->
  <block wx:elif="{{plan.status === 'CONFIRMED'}}">
    <button class="btn-primary" bindtap="contactSupplier">联系供应商</button>
    <button class="btn-default" bindtap="archivePlan">归档</button>
  </block>

  <!-- ARCHIVED状态：无操作按钮 -->
</view>
```

```javascript
// pages/plan-detail/plan-detail.js
const planManager = require('../../utils/planManager')

Page({
  data: {
    planId: null,
    plan: null
  },

  onLoad(options) {
    this.setData({ planId: options.planId })
  },

  onShow() {
    this.loadPlan()
  },

  loadPlan() {
    const plans = wx.getStorageSync('teamventure_plans') || []
    const plan = plans.find(p => p.id === this.data.planId)
    this.setData({ plan })
  },

  // 提交生成
  submitGenerate() {
    try {
      planManager.updatePlanStatus(this.data.planId, 'GENERATING', '用户提交生成')
      wx.redirectTo({
        url: '/pages/generating/generating?planId=' + this.data.planId
      })
    } catch (error) {
      wx.showToast({ title: error.message, icon: 'none' })
    }
  },

  // 确认方案
  confirmPlan() {
    wx.showModal({
      title: '确认方案',
      content: '确认后可联系供应商执行，确定吗？',
      success: (res) => {
        if (res.confirm) {
          try {
            planManager.updatePlanStatus(this.data.planId, 'CONFIRMED', '用户确认方案')
            this.loadPlan()
            wx.showToast({ title: '已确认', icon: 'success' })
          } catch (error) {
            wx.showToast({ title: error.message, icon: 'none' })
          }
        }
      }
    })
  },

  // 修改需求（回到DRAFT）
  modifyRequirement() {
    try {
      planManager.updatePlanStatus(this.data.planId, 'DRAFT', '用户修改需求')
      wx.navigateTo({
        url: '/pages/requirement/requirement?planId=' + this.data.planId
      })
    } catch (error) {
      wx.showToast({ title: error.message, icon: 'none' })
    }
  },

  // 归档
  archivePlan() {
    wx.showModal({
      title: '归档方案',
      content: '归档后将不能修改，确定吗？',
      success: (res) => {
        if (res.confirm) {
          try {
            planManager.updatePlanStatus(this.data.planId, 'ARCHIVED', '用户归档')
            this.loadPlan()
            wx.showToast({ title: '已归档', icon: 'success' })
          } catch (error) {
            wx.showToast({ title: error.message, icon: 'none' })
          }
        }
      }
    })
  }
})
```

**验证点**：不同状态下显示正确的操作按钮

---

#### 单元2.10：状态变更历史（5分钟）

##### 向Claude Code描述需求
```
请帮我在方案详情页添加状态变更历史展示：
1. 显示方案经历的所有状态变更
2. 每条记录显示：状态、时间、原因
3. 按时间倒序排列
4. 放在页面底部，可折叠
```

##### Claude Code生成的代码
```xml
<!-- pages/plan-detail/plan-detail.wxml 添加 -->
<view class="status-history">
  <view class="history-header" bindtap="toggleHistory">
    <text>状态变更历史</text>
    <text class="arrow {{showHistory ? 'up' : 'down'}}">▼</text>
  </view>

  <view wx:if="{{showHistory}}" class="history-list">
    <view wx:for="{{plan.statusHistory}}" wx:key="timestamp" class="history-item">
      <view class="history-status">
        <text class="status-dot {{item.status}}"></text>
        <text>{{statusMap[item.status]}}</text>
      </view>
      <view class="history-info">
        <text class="history-reason">{{item.reason}}</text>
        <text class="history-time">{{formatTime(item.timestamp)}}</text>
      </view>
    </view>
  </view>
</view>
```

```javascript
// pages/plan-detail/plan-detail.js 添加
Page({
  data: {
    // ... 其他data
    showHistory: false,
    statusMap: {
      'DRAFT': '草稿',
      'GENERATING': '生成中',
      'COMPLETED': '已完成',
      'CONFIRMED': '已确认',
      'ARCHIVED': '已归档'
    }
  },

  toggleHistory() {
    this.setData({ showHistory: !this.data.showHistory })
  },

  formatTime(timestamp) {
    const date = new Date(timestamp)
    return `${date.getMonth()+1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2,'0')}`
  }
})
```

```css
/* pages/plan-detail/plan-detail.wxss 添加 */
.status-history {
  margin-top: 40rpx;
  border-top: 1px solid #eee;
  padding-top: 20rpx;
}

.history-header {
  display: flex;
  justify-content: space-between;
  padding: 20rpx;
  background: #f5f5f5;
  border-radius: 8rpx;
}

.arrow { transition: transform 0.3s; }
.arrow.up { transform: rotate(180deg); }

.history-item {
  display: flex;
  justify-content: space-between;
  padding: 16rpx 20rpx;
  border-bottom: 1px solid #f0f0f0;
}

.status-dot {
  display: inline-block;
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  margin-right: 10rpx;
}
.status-dot.DRAFT { background: #999; }
.status-dot.GENERATING { background: #1890ff; }
.status-dot.COMPLETED { background: #52c41a; }
.status-dot.CONFIRMED { background: #fa8c16; }
.status-dot.ARCHIVED { background: #999; }
```

**验证点**：能查看方案的完整状态变更历史

---

### Phase 4：异常处理与优化（10分钟）

#### 单元2.11：生成失败处理（5分钟）

##### 向Claude Code描述需求
```
请帮我处理AI生成失败的情况：
1. 生成超时（超过30秒）自动失败
2. 失败后状态回退到DRAFT
3. 显示友好的错误提示
4. 提供"重试"按钮
```

##### Claude Code生成的代码
```javascript
// pages/generating/generating.js 优化
Page({
  data: {
    planId: null,
    progress: 0,
    failed: false,
    errorMessage: ''
  },

  onLoad(options) {
    this.setData({ planId: options.planId })
    this.startGeneration()
  },

  startGeneration() {
    // 设置超时计时器
    this.timeoutTimer = setTimeout(() => {
      this.handleFailure('生成超时，请稍后重试')
    }, 30000)

    this.simulateGeneration()
  },

  simulateGeneration() {
    // 模拟进度
    this.progressInterval = setInterval(() => {
      if (this.data.progress < 90 && !this.data.failed) {
        this.setData({ progress: this.data.progress + 10 })
      }
    }, 300)

    // 模拟成功/失败（90%成功率）
    setTimeout(() => {
      if (Math.random() > 0.1) {
        this.handleSuccess()
      } else {
        this.handleFailure('AI服务暂时不可用')
      }
    }, 3000)
  },

  handleSuccess() {
    this.clearTimers()
    this.setData({ progress: 100 })

    try {
      planManager.updatePlanStatus(this.data.planId, 'COMPLETED', 'AI生成完成')
      planManager.updatePlanContent(this.data.planId, this.generateMockContent())

      wx.redirectTo({
        url: '/pages/plan-detail/plan-detail?planId=' + this.data.planId
      })
    } catch (error) {
      this.handleFailure(error.message)
    }
  },

  handleFailure(message) {
    this.clearTimers()

    // 状态回退到DRAFT
    try {
      planManager.updatePlanStatus(this.data.planId, 'DRAFT', '生成失败: ' + message)
    } catch (e) {
      console.error('状态回退失败', e)
    }

    this.setData({
      failed: true,
      errorMessage: message
    })
  },

  retry() {
    this.setData({
      progress: 0,
      failed: false,
      errorMessage: ''
    })

    // 重新设置为GENERATING
    try {
      planManager.updatePlanStatus(this.data.planId, 'GENERATING', '用户重试')
      this.startGeneration()
    } catch (error) {
      wx.showToast({ title: error.message, icon: 'none' })
    }
  },

  clearTimers() {
    if (this.timeoutTimer) clearTimeout(this.timeoutTimer)
    if (this.progressInterval) clearInterval(this.progressInterval)
  },

  onUnload() {
    this.clearTimers()
  }
})
```

```xml
<!-- pages/generating/generating.wxml -->
<view class="container">
  <view wx:if="{{!failed}}" class="generating">
    <view class="progress-bar">
      <view class="progress-fill" style="width: {{progress}}%"></view>
    </view>
    <text class="progress-text">AI正在生成方案... {{progress}}%</text>
    <text class="tip">预计需要10-30秒</text>
  </view>

  <view wx:else class="failed">
    <image src="/images/error.png" class="error-icon"/>
    <text class="error-message">{{errorMessage}}</text>
    <button class="btn-primary" bindtap="retry">重试</button>
    <button class="btn-default" bindtap="goBack">返回修改</button>
  </view>
</view>
```

**验证点**：生成失败时显示错误信息和重试按钮，状态正确回退

---

#### 单元2.12：数据一致性保护（5分钟）

##### 向Claude Code描述需求
```
请帮我添加数据一致性保护措施：
1. 防止重复提交（按钮防抖）
2. 页面离开时的状态保存
3. 数据版本校验（防止旧数据覆盖新数据）
```

##### Claude Code生成的代码
```javascript
// utils/planManager.js 添加版本校验

// 更新方案（带版本校验）
function updatePlan(planId, updates) {
  const plans = wx.getStorageSync(STORAGE_KEY) || []
  const planIndex = plans.findIndex(p => p.id === planId)

  if (planIndex === -1) {
    throw new Error('方案不存在')
  }

  const plan = plans[planIndex]

  // 版本校验：如果传入了updatedAt，检查是否是最新版本
  if (updates._expectedVersion && plan.updatedAt !== updates._expectedVersion) {
    throw new Error('数据已被修改，请刷新后重试')
  }

  // 合并更新
  const updatedPlan = {
    ...plan,
    ...updates,
    updatedAt: Date.now()
  }
  delete updatedPlan._expectedVersion

  plans[planIndex] = updatedPlan
  wx.setStorageSync(STORAGE_KEY, plans)

  return updatedPlan
}

module.exports = { createPlan, updatePlanStatus, updatePlan, canTransition }
```

```javascript
// 页面中的防抖处理
Page({
  data: {
    isSubmitting: false
  },

  async submitGenerate() {
    // 防止重复提交
    if (this.data.isSubmitting) return
    this.setData({ isSubmitting: true })

    try {
      await planManager.updatePlanStatus(this.data.planId, 'GENERATING', '用户提交')
      wx.redirectTo({
        url: '/pages/generating/generating?planId=' + this.data.planId
      })
    } catch (error) {
      wx.showToast({ title: error.message, icon: 'none' })
      this.setData({ isSubmitting: false })
    }
  },

  // 页面离开时保存草稿
  onHide() {
    if (this.data.plan?.status === 'DRAFT') {
      this.saveDraft()
    }
  },

  saveDraft() {
    const formData = this.getFormData()
    try {
      planManager.updatePlan(this.data.planId, {
        requirement: formData,
        _expectedVersion: this.data.plan.updatedAt
      })
    } catch (error) {
      console.warn('草稿保存失败', error)
    }
  }
})
```

**验证点**：快速多次点击按钮只触发一次，页面切换时自动保存

---

### Lesson 2 课后作业

#### 实践任务
1. **状态扩展**：添加一个"审核中"(REVIEWING)状态，插入到COMPLETED和CONFIRMED之间
2. **批量操作**：实现批量归档已确认的方案
3. **状态统计**：在列表页顶部显示各状态的方案数量

#### 思考题
1. 如果要支持"撤销"操作（回退到上一个状态），需要如何设计？
2. 多人协作场景下，如何处理状态冲突？

#### 代码提交
```
feat(plan): 实现方案状态机管理

- 定义5个状态及合法转换规则
- 实现状态变更与历史记录
- 添加异常处理与数据保护
```

---

## Lesson 3：用户权限与数据隔离（60分钟）

### 学习目标
- 理解用户认证与授权的基本概念
- 掌握微信登录流程的实现
- 实现用户数据的安全隔离

---

### Phase 1：用户认证基础（15分钟）

#### 单元3.1：认证vs授权（5分钟）

##### 概念区分
| 概念 | 英文 | 问题 | 示例 |
|------|------|------|------|
| 认证 | Authentication | 你是谁？ | 登录验证用户名密码 |
| 授权 | Authorization | 你能做什么？ | 判断用户是否有删除权限 |

##### 认证方式对比
| 方式 | 适用场景 | 特点 |
|------|---------|------|
| 用户名密码 | 传统Web应用 | 需要用户记忆 |
| 手机验证码 | 移动端应用 | 无需密码，依赖手机 |
| 微信登录 | 微信生态应用 | 一键授权，无需注册 |
| SSO单点登录 | 企业应用 | 一次登录，多处使用 |

##### 微信小程序的认证方式
- 用户无需注册、无需密码
- 通过微信账号一键授权
- 获取用户的 `openid` 作为唯一标识

**验证点**：理解认证与授权的区别

---

#### 单元3.2：微信登录流程（5分钟）

##### 登录时序图
```
用户          小程序          开发者服务器        微信服务器
 │              │                 │                  │
 │   打开小程序  │                 │                  │
 │─────────────→│                 │                  │
 │              │                 │                  │
 │              │   wx.login()    │                  │
 │              │────────────────────────────────────→│
 │              │                 │                  │
 │              │   返回code      │                  │
 │              │←────────────────────────────────────│
 │              │                 │                  │
 │              │   发送code      │                  │
 │              │────────────────→│                  │
 │              │                 │                  │
 │              │                 │  code换openid    │
 │              │                 │─────────────────→│
 │              │                 │                  │
 │              │                 │  返回openid      │
 │              │                 │←─────────────────│
 │              │                 │                  │
 │              │   返回token     │                  │
 │              │←────────────────│                  │
 │              │                 │                  │
```

##### 关键概念
| 概念 | 说明 | 有效期 |
|------|------|--------|
| code | 临时登录凭证 | 5分钟 |
| openid | 用户在该小程序的唯一标识 | 永久 |
| token | 开发者自定义的登录态 | 自定义（如7天） |

##### 为什么需要token？
- openid 是敏感信息，不应在前端存储
- token 可以设置过期时间，更安全
- token 可以携带额外信息（如用户角色）

**验证点**：能描述微信登录的完整流程

---

#### 单元3.3：JWT Token简介（5分钟）

##### 什么是JWT
- JSON Web Token 的缩写
- 一种安全传输信息的开放标准
- 可以验证信息的完整性

##### JWT结构
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiJ1c2VyXzEyMyIsImlhdCI6MTcwNTEyMzQ1Nn0.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

┌─────────────────┬─────────────────┬─────────────────┐
│     Header      │     Payload     │    Signature    │
│   （算法类型）   │    （数据）      │    （签名）      │
└─────────────────┴─────────────────┴─────────────────┘
```

##### Payload 常用字段
| 字段 | 全称 | 说明 |
|------|------|------|
| sub | Subject | 用户ID |
| iat | Issued At | 签发时间 |
| exp | Expiration | 过期时间 |
| iss | Issuer | 签发者 |

##### 本项目的Token设计
```javascript
// Payload 示例
{
  "sub": "user_123456",      // 用户ID
  "iat": 1705123456,         // 签发时间
  "exp": 1705728256          // 过期时间（7天后）
}
```

**验证点**：理解JWT的基本结构

---

### Phase 2：登录功能实现（20分钟）

#### 单元3.4：前端登录逻辑（5分钟）

##### 向Claude Code描述需求
```
请帮我实现微信登录功能：
1. 应用启动时检查本地是否有有效token
2. 如果没有token或token过期，调用wx.login获取code
3. 将code发送到后端换取token
4. 将token保存到本地存储
```

##### Claude Code生成的代码
```javascript
// utils/auth.js
const API_BASE = 'https://api.teamventure.com'

// 检查登录状态
async function checkLogin() {
  const token = wx.getStorageSync('auth_token')
  const expireTime = wx.getStorageSync('token_expire')

  // 检查token是否存在且未过期
  if (token && expireTime && Date.now() < expireTime) {
    return true
  }

  // 需要重新登录
  return await login()
}

// 执行登录
async function login() {
  try {
    // 1. 调用wx.login获取code
    const loginRes = await wxLogin()

    // 2. 发送code到后端
    const tokenRes = await requestToken(loginRes.code)

    // 3. 保存token
    saveToken(tokenRes.token, tokenRes.expireIn)

    return true
  } catch (error) {
    console.error('登录失败', error)
    return false
  }
}

// 封装wx.login为Promise
function wxLogin() {
  return new Promise((resolve, reject) => {
    wx.login({
      success: resolve,
      fail: reject
    })
  })
}

// 请求token
async function requestToken(code) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API_BASE}/api/v1/auth/wx-login`,
      method: 'POST',
      data: { code },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message || '登录失败'))
        }
      },
      fail: reject
    })
  })
}

// 保存token
function saveToken(token, expireIn) {
  const expireTime = Date.now() + expireIn * 1000
  wx.setStorageSync('auth_token', token)
  wx.setStorageSync('token_expire', expireTime)
}

// 获取token
function getToken() {
  return wx.getStorageSync('auth_token')
}

// 清除登录状态
function logout() {
  wx.removeStorageSync('auth_token')
  wx.removeStorageSync('token_expire')
}

module.exports = { checkLogin, login, getToken, logout }
```

**验证点**：登录代码结构清晰，包含完整的错误处理

---

#### 单元3.5：全局登录检查（5分钟）

##### 向Claude Code描述需求
```
请帮我在应用启动时自动检查登录状态：
1. 在app.js的onLaunch中检查登录
2. 如果未登录，跳转到登录页
3. 如果已登录，正常进入首页
```

##### Claude Code生成的代码
```javascript
// app.js
const auth = require('./utils/auth')

App({
  globalData: {
    isLoggedIn: false,
    userInfo: null
  },

  async onLaunch() {
    // 检查登录状态
    const isLoggedIn = await auth.checkLogin()
    this.globalData.isLoggedIn = isLoggedIn

    if (!isLoggedIn) {
      // 跳转到登录页
      wx.reLaunch({
        url: '/pages/login/login'
      })
    }
  },

  // 提供给页面调用的登录方法
  async doLogin() {
    const success = await auth.login()
    if (success) {
      this.globalData.isLoggedIn = true
      return true
    }
    return false
  }
})
```

```javascript
// pages/login/login.js
const app = getApp()

Page({
  data: {
    isLoading: false
  },

  async handleLogin() {
    if (this.data.isLoading) return
    this.setData({ isLoading: true })

    const success = await app.doLogin()

    if (success) {
      wx.reLaunch({
        url: '/pages/index/index'
      })
    } else {
      wx.showToast({
        title: '登录失败，请重试',
        icon: 'none'
      })
      this.setData({ isLoading: false })
    }
  }
})
```

```xml
<!-- pages/login/login.wxml -->
<view class="container">
  <image src="/images/logo.png" class="logo"/>
  <text class="title">TeamVenture</text>
  <text class="subtitle">AI团建策划助手</text>

  <button
    class="login-btn"
    bindtap="handleLogin"
    loading="{{isLoading}}"
  >
    微信一键登录
  </button>

  <text class="agreement">
    登录即表示同意《用户协议》和《隐私政策》
  </text>
</view>
```

**验证点**：未登录时自动跳转到登录页

---

#### 单元3.6：请求拦截器（5分钟）

##### 向Claude Code描述需求
```
请帮我封装统一的请求方法：
1. 自动在请求头中添加token
2. 统一处理401未授权错误
3. 自动刷新过期的token
```

##### Claude Code生成的代码
```javascript
// utils/request.js
const auth = require('./auth')
const API_BASE = 'https://api.teamventure.com'

// 统一请求方法
async function request(options) {
  const token = auth.getToken()

  const config = {
    url: API_BASE + options.url,
    method: options.method || 'GET',
    data: options.data,
    header: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
      ...options.header
    }
  }

  return new Promise((resolve, reject) => {
    wx.request({
      ...config,
      success: async (res) => {
        // 401未授权，尝试重新登录
        if (res.statusCode === 401) {
          const loginSuccess = await handleUnauthorized()
          if (loginSuccess) {
            // 重试原请求
            const retryResult = await request(options)
            resolve(retryResult)
          } else {
            reject(new Error('登录已过期，请重新登录'))
          }
          return
        }

        // 其他错误
        if (res.statusCode >= 400) {
          reject(new Error(res.data.message || '请求失败'))
          return
        }

        resolve(res.data)
      },
      fail: (error) => {
        reject(new Error('网络请求失败'))
      }
    })
  })
}

// 处理未授权
async function handleUnauthorized() {
  // 清除旧token
  auth.logout()

  // 尝试重新登录
  const success = await auth.login()

  if (!success) {
    // 跳转到登录页
    wx.reLaunch({
      url: '/pages/login/login'
    })
  }

  return success
}

// 便捷方法
const get = (url, data) => request({ url, method: 'GET', data })
const post = (url, data) => request({ url, method: 'POST', data })
const put = (url, data) => request({ url, method: 'PUT', data })
const del = (url, data) => request({ url, method: 'DELETE', data })

module.exports = { request, get, post, put, del }
```

**验证点**：请求自动带上token，401时自动刷新

---

#### 单元3.7：Token刷新机制（5分钟）

##### 向Claude Code描述需求
```
请帮我实现token刷新机制：
1. token有效期7天
2. 当token剩余有效期不足1天时自动刷新
3. 刷新失败时不影响当前请求
```

##### Claude Code生成的代码
```javascript
// utils/auth.js 添加刷新逻辑

// 检查是否需要刷新token
function shouldRefreshToken() {
  const expireTime = wx.getStorageSync('token_expire')
  if (!expireTime) return false

  // 剩余时间不足1天时刷新
  const oneDayMs = 24 * 60 * 60 * 1000
  return (expireTime - Date.now()) < oneDayMs
}

// 静默刷新token
async function silentRefresh() {
  if (!shouldRefreshToken()) return

  try {
    const loginRes = await wxLogin()
    const tokenRes = await requestToken(loginRes.code)
    saveToken(tokenRes.token, tokenRes.expireIn)
    console.log('Token已静默刷新')
  } catch (error) {
    // 刷新失败不影响正常使用，下次再试
    console.warn('Token刷新失败', error)
  }
}

// 修改checkLogin，增加刷新检查
async function checkLogin() {
  const token = wx.getStorageSync('auth_token')
  const expireTime = wx.getStorageSync('token_expire')

  if (token && expireTime && Date.now() < expireTime) {
    // 已登录，检查是否需要刷新
    silentRefresh()  // 异步执行，不阻塞
    return true
  }

  return await login()
}

module.exports = {
  checkLogin,
  login,
  getToken,
  logout,
  silentRefresh
}
```

**验证点**：快过期的token会自动静默刷新

---

### Phase 3：数据隔离实现（15分钟）

#### 单元3.8：用户数据隔离原理（5分钟）

##### 数据隔离的重要性
- 用户A不能看到用户B的方案
- 每个用户只能操作自己的数据
- 防止越权访问

##### 数据隔离示意图

```
┌──────────────────────────────────────────────────────────────┐
│                    用户数据隔离                               │
│                                                              │
│   用户A                          用户B                       │
│   ┌─────────────┐               ┌─────────────┐             │
│   │ 方案1(DRAFT)│               │ 方案3(DONE) │             │
│   │ 方案2(DONE) │               │ 方案4(DRAFT)│             │
│   └─────────────┘               └─────────────┘             │
│         ↑                              ↑                    │
│         │ 只能访问                      │ 只能访问           │
│         │                              │                    │
│   ┌─────┴─────┐                 ┌──────┴────┐              │
│   │  Token A  │                 │  Token B  │              │
│   └───────────┘                 └───────────┘              │
└──────────────────────────────────────────────────────────────┘
```

##### 实现方式
1. **后端隔离**（推荐）：API根据token中的userId过滤数据
2. **前端隔离**（本地存储）：按userId分开存储

##### 本地存储的隔离方案
```javascript
// 不隔离（所有用户共用）
wx.getStorageSync('plans')

// 隔离（按用户分开）
wx.getStorageSync(`plans_${userId}`)
```

**验证点**：理解数据隔离的必要性和实现方式

---

#### 单元3.9：获取用户ID（5分钟）

##### 向Claude Code描述需求
```
请帮我实现从token中解析用户ID：
1. 解析JWT的payload部分
2. 提取sub字段作为userId
3. 提供获取userId的工具方法
```

##### Claude Code生成的代码
```javascript
// utils/auth.js 添加

// 从token中解析用户信息
function parseToken(token) {
  if (!token) return null

  try {
    // JWT格式: header.payload.signature
    const parts = token.split('.')
    if (parts.length !== 3) return null

    // 解码payload（Base64）
    const payload = JSON.parse(atob(parts[1]))
    return payload
  } catch (error) {
    console.error('Token解析失败', error)
    return null
  }
}

// Base64解码（小程序环境）
function atob(str) {
  return decodeURIComponent(
    escape(
      wx.base64ToArrayBuffer ?
        String.fromCharCode.apply(null, new Uint8Array(wx.base64ToArrayBuffer(str))) :
        Buffer.from(str, 'base64').toString('binary')
    )
  )
}

// 获取当前用户ID
function getUserId() {
  const token = getToken()
  const payload = parseToken(token)
  return payload?.sub || null
}

// 获取当前用户信息
function getUserInfo() {
  const token = getToken()
  return parseToken(token)
}

module.exports = {
  checkLogin,
  login,
  getToken,
  logout,
  silentRefresh,
  getUserId,
  getUserInfo
}
```

**验证点**：能正确从token中获取userId

---

#### 单元3.10：本地存储隔离（5分钟）

##### 向Claude Code描述需求
```
请帮我修改planManager，实现按用户隔离存储：
1. 存储key加上userId前缀
2. 确保用户只能访问自己的数据
3. 提供数据迁移方法（兼容旧版本）
```

##### Claude Code生成的代码
```javascript
// utils/planManager.js 修改

const auth = require('./auth')

// 获取用户专属的存储key
function getStorageKey() {
  const userId = auth.getUserId()
  if (!userId) {
    throw new Error('用户未登录')
  }
  return `plans_${userId}`
}

// 获取所有方案
function getAllPlans() {
  const key = getStorageKey()
  return wx.getStorageSync(key) || []
}

// 保存所有方案
function saveAllPlans(plans) {
  const key = getStorageKey()
  wx.setStorageSync(key, plans)
}

// 创建新方案（修改后）
function createPlan() {
  const plans = getAllPlans()
  const userId = auth.getUserId()

  const newPlan = {
    id: 'plan_' + Date.now(),
    userId: userId,  // 记录所属用户
    status: 'DRAFT',
    // ... 其他字段
  }

  plans.unshift(newPlan)
  saveAllPlans(plans)

  return newPlan
}

// 获取单个方案（带权限校验）
function getPlan(planId) {
  const plans = getAllPlans()
  const plan = plans.find(p => p.id === planId)

  // 额外校验（虽然key已隔离，但双重保险）
  if (plan && plan.userId !== auth.getUserId()) {
    throw new Error('无权访问此方案')
  }

  return plan || null
}

// 数据迁移（从旧版本迁移到用户隔离版本）
function migrateData() {
  const userId = auth.getUserId()
  if (!userId) return

  const oldKey = 'teamventure_plans'
  const newKey = getStorageKey()

  const oldPlans = wx.getStorageSync(oldKey)
  if (oldPlans && oldPlans.length > 0) {
    // 只迁移当前用户的数据（或全部迁移给当前用户）
    const existingPlans = wx.getStorageSync(newKey) || []
    const migratedPlans = oldPlans.map(p => ({
      ...p,
      userId: userId
    }))

    wx.setStorageSync(newKey, [...existingPlans, ...migratedPlans])
    wx.removeStorageSync(oldKey)

    console.log(`已迁移 ${oldPlans.length} 条方案数据`)
  }
}

module.exports = {
  createPlan,
  getAllPlans,
  getPlan,
  updatePlanStatus,
  migrateData
}
```

**验证点**：不同用户的数据完全隔离

---

### Phase 4：权限校验与安全加固（10分钟）

#### 单元3.11：操作权限校验（5分钟）

##### 向Claude Code描述需求
```
请帮我添加操作权限校验：
1. 只有方案所有者才能修改/删除方案
2. 操作前校验用户身份
3. 非法操作返回友好提示
```

##### Claude Code生成的代码
```javascript
// utils/planManager.js 添加权限校验

// 校验方案归属权
function checkOwnership(planId) {
  const plan = getPlan(planId)

  if (!plan) {
    throw new Error('方案不存在')
  }

  if (plan.userId !== auth.getUserId()) {
    throw new Error('无权操作此方案')
  }

  return plan
}

// 更新方案状态（带权限校验）
function updatePlanStatus(planId, newStatus, reason) {
  // 先校验归属权
  const plan = checkOwnership(planId)

  // 再校验状态转换
  if (!canTransition(plan.status, newStatus)) {
    throw new Error(`无法从 ${plan.status} 转换到 ${newStatus}`)
  }

  // 执行更新
  const plans = getAllPlans()
  const index = plans.findIndex(p => p.id === planId)

  plans[index] = {
    ...plan,
    status: newStatus,
    updatedAt: Date.now(),
    statusHistory: [
      ...plan.statusHistory,
      { status: newStatus, timestamp: Date.now(), reason }
    ]
  }

  saveAllPlans(plans)
  return plans[index]
}

// 删除方案（带权限校验）
function deletePlan(planId) {
  // 校验归属权
  const plan = checkOwnership(planId)

  // 只有DRAFT状态可以删除
  if (plan.status !== 'DRAFT') {
    throw new Error('只能删除草稿状态的方案')
  }

  const plans = getAllPlans()
  const filteredPlans = plans.filter(p => p.id !== planId)
  saveAllPlans(filteredPlans)

  return true
}

module.exports = {
  createPlan,
  getAllPlans,
  getPlan,
  updatePlanStatus,
  deletePlan,
  migrateData,
  checkOwnership
}
```

**验证点**：尝试操作他人方案时返回错误提示

---

#### 单元3.12：安全最佳实践（5分钟）

##### 安全检查清单
| 检查项 | 说明 | 状态 |
|--------|------|------|
| Token存储 | 使用wx.setStorageSync，非明文 | ✅ |
| Token传输 | HTTPS + Authorization Header | ✅ |
| Token刷新 | 过期前自动刷新 | ✅ |
| 数据隔离 | 按userId分开存储 | ✅ |
| 权限校验 | 操作前校验归属 | ✅ |
| 错误处理 | 不暴露敏感信息 | ✅ |

##### 向Claude Code描述需求
```
请帮我添加安全日志记录：
1. 记录登录/登出事件
2. 记录敏感操作（删除、确认）
3. 日志不包含敏感信息
```

##### Claude Code生成的代码
```javascript
// utils/securityLog.js
const LOG_KEY = 'security_log'
const MAX_LOGS = 100  // 最多保留100条

// 记录安全事件
function log(action, details = {}) {
  const logs = wx.getStorageSync(LOG_KEY) || []

  const logEntry = {
    action,
    timestamp: Date.now(),
    // 不记录敏感信息，只记录脱敏后的标识
    userId: maskUserId(details.userId),
    planId: details.planId,
    result: details.success ? 'SUCCESS' : 'FAILED',
    reason: details.reason
  }

  logs.unshift(logEntry)

  // 限制日志数量
  if (logs.length > MAX_LOGS) {
    logs.splice(MAX_LOGS)
  }

  wx.setStorageSync(LOG_KEY, logs)
}

// 用户ID脱敏
function maskUserId(userId) {
  if (!userId) return null
  if (userId.length <= 6) return '***'
  return userId.slice(0, 3) + '***' + userId.slice(-3)
}

// 预定义的安全事件
const SecurityEvents = {
  LOGIN: 'LOGIN',
  LOGOUT: 'LOGOUT',
  TOKEN_REFRESH: 'TOKEN_REFRESH',
  PLAN_CREATE: 'PLAN_CREATE',
  PLAN_DELETE: 'PLAN_DELETE',
  PLAN_CONFIRM: 'PLAN_CONFIRM',
  PLAN_ARCHIVE: 'PLAN_ARCHIVE',
  UNAUTHORIZED_ACCESS: 'UNAUTHORIZED_ACCESS'
}

module.exports = { log, SecurityEvents }
```

```javascript
// 在auth.js中使用
const securityLog = require('./securityLog')

async function login() {
  try {
    // ... 登录逻辑 ...
    securityLog.log(securityLog.SecurityEvents.LOGIN, {
      userId: getUserId(),
      success: true
    })
    return true
  } catch (error) {
    securityLog.log(securityLog.SecurityEvents.LOGIN, {
      success: false,
      reason: error.message
    })
    return false
  }
}
```

**验证点**：敏感操作有日志记录，日志不包含完整敏感信息

---

### Lesson 3 课后作业

#### 实践任务
1. **会话管理**：实现"在其他设备登录时强制下线"功能
2. **权限升级**：添加"管理员"角色，管理员可以查看所有用户的方案
3. **数据导出**：实现用户数据导出功能（符合GDPR要求）

#### 思考题
1. 如果token被泄露，攻击者可以做什么？应该如何防范？
2. 本地存储的数据是否安全？有什么风险？

#### 代码提交
```
feat(auth): 实现用户认证与数据隔离

- 实现微信登录流程
- 实现token自动刷新
- 实现按用户数据隔离
- 添加操作权限校验
```

---

## 工具使用指南

### Claude Code vs Cursor 选择建议

| 场景 | 推荐工具 | 原因 |
|------|---------|------|
| 创建新页面/组件 | Claude Code | 需要生成多个文件 |
| 修改单个文件 | Cursor | 更精确的局部编辑 |
| 理解现有代码 | Claude Code | 可以分析整个项目 |
| 调试错误 | Claude Code | 可以查看多个相关文件 |
| 样式微调 | Cursor | 即时预览效果 |
| 重构代码 | Claude Code | 需要跨文件修改 |

### 高效Prompt技巧

#### 1. 明确上下文
```
❌ "帮我写一个登录功能"
✅ "在微信小程序中，帮我实现微信一键登录功能，
    需要调用wx.login获取code，然后发送到后端
    https://api.teamventure.com/api/v1/auth/wx-login
    换取JWT token"
```

#### 2. 分步骤请求
```
❌ "帮我实现完整的方案管理功能"
✅ "第一步：帮我创建方案的数据结构定义"
   "第二步：帮我实现创建方案的函数"
   "第三步：帮我实现方案列表页面"
```

#### 3. 提供示例
```
✅ "请帮我实现类似的错误处理逻辑：
    try {
      const result = await api.call()
      // 处理成功
    } catch (error) {
      wx.showToast({ title: error.message, icon: 'none' })
    }"
```

---

## 附录

### A. 技术栈版本

| 技术 | 版本 | 说明 |
|------|------|------|
| 微信开发者工具 | 1.06+ | 小程序开发IDE |
| Claude Code | 最新版 | 主力AI编程助手 |
| Cursor | 0.40+ | 辅助代码编辑器 |
| Node.js | 18+ | 本地开发环境 |
| Git | 2.40+ | 版本控制 |

### B. 参考资源

- [微信小程序官方文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)
- [Claude Code 使用指南](https://docs.anthropic.com/claude-code)
- [JWT官方介绍](https://jwt.io/introduction)
- [TeamVenture 项目仓库](https://github.com/your-org/teamventure)

### C. 常见问题FAQ

**Q: AI生成的代码有bug怎么办？**
A: 将错误信息完整复制给Claude Code，让它分析并修复。

**Q: 不理解AI生成的代码怎么办？**
A: 直接问"请解释这段代码的作用"，AI会用通俗语言解释。

**Q: 代码运行结果和预期不符怎么办？**
A: 描述"预期行为"和"实际行为"的差异，让AI帮你定位问题。

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0 | 2025-01-15 | 初始版本，3个Lesson |
| v2.0 | 2026-01-21 | 重大更新：<br>- 新增Lesson 0课程导学<br>- 工具体系调整（Claude Code主力，Cursor辅助）<br>- 细化为5分钟学习单元<br>- 增加课后作业和思考题 |
