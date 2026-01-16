# AI智能填充 - 完整交互流程

## 状态机设计

```
┌─────────────────────────────────────────────────┐
│                 状态转换图                       │
└─────────────────────────────────────────────────┘

    [normal]          [generating]        [generated]
   (可编辑)           (生成中)            (已生成)
       │                  │                   │
       │  点击AI填充      │                   │
       ├─────────────────→│                   │
       │  弹窗填写        │  进度0%→100%      │
       │  确认            │  (1.5秒)          │
       │                  │                   │
       │                  ├──────────────────→│
       │                  │   生成成功         │
       │                  │                   │
       │                  │   生成失败         │
       │←─────────────────┤                   │
       │                  │                   │
       │  点击重置        │                   │
       │←─────────────────────────────────────┤
```

## 完整交互流程

### 阶段1: 正常状态（normal）

**UI表现**：
```
┌─────────────────────────────────────┐
│ ✏️ 直接修改示例  [✨AI填充] [🔄重置] │  ← 按钮可点击
├─────────────────────────────────────┤
│ # 团建行程方案                      │
│                                     │
│ ## 基本信息                         │  ← textarea可编辑
│ - **天数**: 3天2夜                  │
│ ...                                 │
└─────────────────────────────────────┘
```

**用户操作**：
- ✅ 可以手动编辑markdown
- ✅ 可以点击"AI填充"
- ✅ 可以点击"重置"
- ✅ 可以点击"AI 生成方案"

### 阶段2: 弹窗填写

**操作步骤**：
1. 点击"✨ AI填充"按钮
2. 弹出输入框
3. 填写：
   - 天数：`3`
   - 出发地：`北京`
   - 到达地：`青岛`
4. 点击"确认填充"

**校验规则**：
- 天数为空 → "请输入天数"
- 天数<1或>9 → "天数必须是1-9之间的数字"
- 出发地为空 → "请输入出发地"
- 到达地为空 → "请输入到达地"

### 阶段3: AI生成中（generating）

**UI表现**：
```
┌─────────────────────────────────────┐
│ ✏️ 直接修改示例  [✨AI填充] [🔄重置] │  ← 按钮禁用（灰色）
├─────────────────────────────────────┤
│  ⚡ AI 生成中 🔄                    │  ← loading卡片
│                                     │
│  ████████░░░░░░░░░░░░ 40%          │  ← 进度条
│                                     │
│  正在为您生成个性化团建方案          │
└─────────────────────────────────────┘
```

**状态特征**：
- ⚡ 闪电图标旋转动画
- 🔄 刷新图标旋转动画
- 进度条从0% → 100%（1.5秒）
- 所有按钮禁用（"AI填充"、"重置"、"AI 生成方案"）
- textarea不可见

**技术实现**：
```javascript
// 1. 关闭弹窗，切换状态
aiGenerateStatus: 'generating'
generateProgress: 0

// 2. 启动进度条动画（每75ms增加5%）
setInterval(() => {
  progress += 5
  setData({ generateProgress: Math.min(progress, 95) })
}, 75)

// 3. 模拟AI生成（1.5秒后）
setTimeout(() => {
  generateProgress: 100
  // 再延迟300ms展示100%
  setTimeout(() => {
    aiGenerateStatus: 'generated'
    填充markdown内容
  }, 300)
}, 1500)
```

### 阶段4: 生成成功（generated）

**UI表现**：
```
┌─────────────────────────────────────┐
│ ✏️ 直接修改示例  [✨AI填充] [🔄重置] │  ← 按钮恢复可点击
├─────────────────────────────────────┤
│ # 团建行程方案                      │
│                                     │
│ ## 基本信息                         │  ← 显示生成的内容
│ - **天数**: 3天2夜                  │  ← 可继续编辑
│ - **人数**: 30人                    │
│ ...                                 │
└─────────────────────────────────────┘
```

**状态特征**：
- textarea恢复显示
- 内容为AI生成的markdown
- 所有按钮恢复可用
- 显示Toast: "AI填充完成"

**用户操作**：
- ✅ 可以继续手动修改
- ✅ 可以再次点击"AI填充"（重新生成）
- ✅ 可以点击"重置"
- ✅ 可以点击"AI 生成方案"

### 阶段5: 生成失败（error → normal）

**触发条件**：
- 模板生成函数抛出异常
- 网络请求失败（如果调用远程AI）
- 超时（超过10秒未完成）

**UI表现**：
```
┌─────────────────────────────────────┐
│ ✏️ 直接修改示例  [✨AI填充] [🔄重置] │  ← 按钮恢复可点击
├─────────────────────────────────────┤
│ # 团建行程方案                      │
│                                     │
│ ## 基本信息                         │  ← 恢复原始内容
│ - **天数**: 3天2夜                  │
│ ...                                 │
└─────────────────────────────────────┘

显示Toast: "AI生成失败，请重试"
```

**处理逻辑**：
```javascript
try {
  // 生成模板
} catch (error) {
  // 恢复原始内容
  formData.markdownContent = originalContent
  aiGenerateStatus = 'normal'
  显示失败提示
}
```

## 交互细节

### 按钮禁用规则

| 按钮 | normal | generating | generated | error |
|------|--------|------------|-----------|-------|
| AI填充 | ✅ | ❌ | ✅ | ✅ |
| 重置 | ✅ | ❌ | ✅ | ✅ |
| AI 生成方案 | ✅ | ❌ | ✅ | ✅ |

### 进度条动画

**速度**：
- 每75ms增加5%
- 总耗时1.5秒到达95%
- 生成完成后跳到100%
- 停留300ms后展示结果

**视觉效果**：
```
0%   ░░░░░░░░░░░░░░░░░░░░
20%  ████░░░░░░░░░░░░░░░░
50%  ██████████░░░░░░░░░░
80%  ████████████████░░░░
95%  ███████████████████░
100% ████████████████████
```

### 刷新图标动画

**旋转速度**：
- 1.5秒旋转一圈
- 无限循环
- 与进度条同步

**CSS**：
```css
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-spin {
  animation: spin 1.5s linear infinite;
}
```

## 用户体验优化

### 视觉反馈
1. **弹窗关闭** → loading卡片渐入（300ms过渡）
2. **进度条增长** → 平滑动画（transition: width 0.3s）
3. **图标旋转** → 持续旋转营造"AI思考"感
4. **生成完成** → Toast提示 + 卡片淡出，textarea淡入

### 异常处理
1. **网络中断** → 10秒超时 → 显示"生成失败"
2. **数据异常** → catch错误 → 恢复原内容
3. **用户离开** → onHide时清除定时器

### 性能优化
1. **定时器清理** → onUnload时清除
2. **防抖处理** → 生成中禁用按钮
3. **内存管理** → 及时释放originalContent

## 测试场景

### 正常流程测试
```
1. 点击"AI填充"
   ↓
2. 输入: 3天、北京、青岛
   ↓
3. 点击"确认填充"
   ↓
4. 看到loading卡片（⚡旋转 + 🔄旋转）
   ↓
5. 进度条: 0% → 20% → 50% → 95% → 100%
   ↓
6. 1.8秒后显示生成的markdown
   ↓
7. Toast: "AI填充完成"
```

### 按钮禁用测试
```
1. 进入generating状态
   ↓
2. 尝试点击"AI填充" → 无响应 ✅
3. 尝试点击"重置" → 无响应 ✅
4. 尝试点击"AI 生成方案" → 无响应 ✅
   ↓
5. 生成完成后按钮恢复 ✅
```

### 失败恢复测试
```
1. 模拟生成失败（throw error）
   ↓
2. 内容恢复为原始markdown ✅
3. 状态回到normal ✅
4. 按钮恢复可用 ✅
5. Toast: "AI生成失败，请重试" ✅
```

## 代码文件清单

### WXML（pages/index/index.wxml）
- ✅ 添加状态判断：`wx:if="{{aiGenerateStatus === 'generating'}}"`
- ✅ 添加loading卡片UI
- ✅ 添加刷新图标动画
- ✅ 按钮添加禁用class：`{{aiGenerateStatus === 'generating' ? 'btn-disabled' : ''}}`

### WXSS（pages/index/index.wxss）
- ✅ 添加`.ai-generating-card`样式
- ✅ 添加`.loading-spin`旋转动画
- ✅ 添加`.progress-bar`进度条样式
- ✅ 添加`.btn-disabled`禁用样式

### JS（pages/index/index.js）
- ✅ 添加状态字段：`aiGenerateStatus`
- ✅ 添加进度字段：`generateProgress`
- ✅ 添加原始内容备份：`originalContent`
- ✅ 实现`simulateAIGeneration`方法
- ✅ 实现`handleGenerationError`方法
- ✅ onUnload时清除定时器

## 关键代码片段

### 状态切换
```javascript
// 确认填充 → 进入生成状态
handleConfirmAIFill() {
  // 保存原始内容
  this.setData({ originalContent: this.data.formData.markdownContent })

  // 切换状态
  this.setData({
    showAIFillDialog: false,
    aiGenerateStatus: 'generating',
    generateProgress: 0
  })

  // 启动模拟生成
  this.simulateAIGeneration(days, origin, destination)
}
```

### 进度模拟
```javascript
simulateAIGeneration() {
  let progress = 0
  this.progressTimer = setInterval(() => {
    progress += 5
    this.setData({
      generateProgress: Math.min(progress, 95)
    })
  }, 75) // 每75ms增加5%

  setTimeout(() => {
    clearInterval(this.progressTimer)
    // 生成完成
    this.setData({
      generateProgress: 100,
      aiGenerateStatus: 'generated',
      'formData.markdownContent': generatedTemplate
    })
  }, 1500)
}
```

### 按钮禁用
```xml
<!-- WXML -->
<view class="action-btn {{aiGenerateStatus === 'generating' ? 'btn-disabled' : ''}}">
</view>

<button disabled="{{aiGenerateStatus === 'generating'}}">
</button>
```

```css
/* WXSS */
.btn-disabled {
  opacity: 0.4;
  pointer-events: none;  /* 禁止点击 */
}
```

## 演示效果

### 时间线（总计1.8秒）

```
T = 0.0s  用户点击"确认填充"
          ↓
          弹窗关闭
          loading卡片显示
          进度0%，图标开始旋转

T = 0.3s  进度20% ████░░░░░░░░░░░░░░░░

T = 0.6s  进度40% ████████░░░░░░░░░░░░

T = 0.9s  进度60% ████████████░░░░░░░░

T = 1.2s  进度80% ████████████████░░░░

T = 1.5s  进度95% ███████████████████░
          AI生成完成，进度跳到100%

T = 1.8s  loading卡片消失
          textarea显示生成内容
          Toast: "AI填充完成"
```

### 按钮状态变化

```
T = 0.0s  [✨AI填充] [🔄重置]  ← 可点击
          ↓ 确认填充

T = 0.1s  [✨AI填充] [🔄重置]  ← 变灰，禁用
          （opacity: 0.4, pointer-events: none）

T = 1.8s  [✨AI填充] [🔄重置]  ← 恢复可点击
          （opacity: 1.0, pointer-events: auto）
```

## 已知限制

1. **进度条为模拟**：不代表真实AI处理进度
2. **生成时间固定**：1.5秒，不随天数变化
3. **不支持取消**：生成过程中无法中断
4. **单例执行**：同一时间只能有一个生成任务

## 未来优化方向

### 短期（P1）
- [ ] 添加"取消生成"按钮
- [ ] 根据天数动态调整生成时间（1天快，9天慢）
- [ ] 生成完成后高亮显示修改部分

### 中期（P2）
- [ ] 接入真实AI生成接口
- [ ] 显示真实进度（解析需求 30% → 规划路线 60% → 生成内容 100%）
- [ ] 支持流式输出（逐段显示生成的内容）

### 长期（P3）
- [ ] AI学习用户偏好
- [ ] 多模板切换（海岛/山区/城市）
- [ ] 语音输入需求

## 验收标准

### 必须通过（P0）
- [x] 点击"确认填充"后立即显示loading卡片
- [x] 进度条平滑增长（0% → 100%）
- [x] 图标旋转动画流畅
- [x] 生成中所有按钮禁用
- [x] 1.8秒后显示生成的markdown
- [x] 生成失败能恢复原内容

### 建议通过（P1）
- [ ] loading卡片有渐入动画
- [ ] 进度条颜色为渐变色
- [ ] Toast提示清晰友好

## 更新记录

**2026-01-16 16:00**
- 实现AI生成状态机（normal/generating/generated/error）
- 添加loading卡片UI（进度条 + 旋转图标）
- 实现按钮禁用逻辑（生成中不可操作）
- 添加进度模拟动画（1.5秒）
- 实现失败恢复机制
