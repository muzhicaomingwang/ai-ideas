# PRD｜TeamVenture（AI团建策划助手）Web应用 MVP

- **产品代号**：TeamVenture
- **模块**：AI团建策划助手（Team Building Assistant）
- **产品形态**：Web应用（SaaS） + 后端服务（AI编排/供应商API/数据分析） + LLM API
- **版本**：v0.1（MVP）
- **目标用户**：toProC（企业HR/行政人员）
- **更新日期**：2025-12-29
- **基于**：[市场调研报告](../docs/teamventure-market-research.md) 2025-12-29

---

## 1. 背景与机会

### 1.1 市场现状

企业组织团建时面临三大痛点：
1. **策划复杂**：需协调场地、行程、餐饮、活动、交通等多个环节，HR缺少专业经验
2. **成本高昂**：外包给第三方团建公司，人均1000-2000元（含30%服务商利润）
3. **效率低下**：方案沟通周期3-7天，反复修改，沟通成本高

**市场数据**：
- 50%企业人均团建预算>600元，周边团建需求增长124%
- 传统服务商抽佣20-30%，可替代空间大
- **专门的团建管理SaaS工具几乎空白**（最大机会）

### 1.2 机会点

**TeamVenture = AI驱动的端到端团建助手**
- **15分钟生成完整方案**（vs 传统3-7天）
- **成本降低50%+**（去除中间商佣金）
- **智能决策支持**（vs 简单信息聚合）

---

## 2. JTBD 定义（核心 Job）

### 2.1 Job Story

**当**我作为HR需要为50人团队策划一次2天1夜的团建，
**但**我既缺少团建经验又不想支付高昂的第三方服务费，
**以便于**我能在15分钟内获得3套完整方案（预算/行程/供应商），
**这样**我可以从"焦头烂额的协调者"转变为"手握多套方案的决策者"，
**并且**成本降低50%，效率提升3倍。

### 2.2 完成 Job 的 Outcomes（可测）

| 维度 | 传统方式 | TeamVenture目标 | 测量指标 |
|------|---------|----------------|---------|
| **方案生成速度** | 3-7天 | 15分钟内 | 首次生成完成时间中位数 |
| **成本降低** | 人均1000-2000元 | 人均500-1000元 | 对比传统服务商报价 |
| **方案满意度** | 需反复沟通 | 首次满意率>60% | NPS/方案采纳率 |
| **决策效率** | 单一方案 | 3套方案对比 | 用户选择方案的时间 |
| **使用复杂度** | 需学习 | 5分钟上手 | 首次完成任务时间 |

---

## 3. 目标与非目标

### 3.1 目标（MVP v0.1）

**核心目标**：
- ✅ 提供**AI驱动的方案生成**：基于预算/人数/偏好/地点，15分钟生成3套完整方案
- ✅ 实现**供应商智能匹配**：自动对接民宿/场地/活动供应商，价格透明可比价
- ✅ 支持**基础行程管理**：方案确认后，自动生成行程表，支持导出/分享

**成功指标**：
- 前100家种子用户完成度>80%
- 方案生成成功率>95%
- 用户NPS>30

### 3.2 非目标（v0.1 不做）

- ❌ 不做现场执行服务（不派工作人员到场）
- ❌ 不做供应商资质审核（初期依赖平台评分）
- ❌ 不做财务系统对接（无发票管理/报销流程）
- ❌ 不做移动端APP（先验证Web版本）
- ❌ 不做实时应急响应（24/7客服）

---

## 4. 目标用户（ICP）与场景

### 4.1 ICP（优先级排序）

#### ICP-1（P0 - 首要目标）：中型企业HR/行政
```
企业规模：50-200人
行业：互联网/科技/咨询
角色：HR/行政/HRBP
年龄：25-35岁
痛点：
- 每年需组织2-4次团建
- 缺少团建策划经验
- 预算有限（人均<1000元）
- 考核压力大（员工满意度）
- 不想外包（成本高）
决策因素：成本、口碑、省心程度
```

#### ICP-2（P1 - 次要目标）：小型企业创始人/COO
```
企业规模：20-50人
行业：创业公司
角色：创始人/COO/运营负责人
痛点：
- 预算极度有限
- 亲自组织团建
- 希望凝聚团队
决策因素：性价比、简单易用
```

#### ICP-3（P2 - 长期目标）：大型企业HRBP
```
企业规模：200-500人
行业：传统企业/金融/制造
角色：HRBP/区域HR
痛点：
- 多部门团建需求
- 需要标准化流程
- 合规要求高
决策因素：合规性、可追溯、批量管理
```

### 4.2 高频使用场景

| 场景 | 触发时机 | 典型需求 | 紧急程度 |
|------|---------|---------|---------|
| **年度团建** | Q2/Q4旺季 | 50-100人，2天1夜，预算充足 | 🟢 提前1-2个月 |
| **季度团建** | 季度末 | 20-50人，1天，周边游 | 🟡 提前2-4周 |
| **新员工破冰** | 入职季 | 10-30人，半天，轻活动 | 🔴 提前1周 |
| **部门团建** | 项目完成后 | 10-20人，1天，庆功宴 | 🔴 紧急（3天内） |
| **管理层团建** | 不定期 | 5-15人，高端场地 | 🟢 提前1个月 |

### 4.3 用户画像示例

**张敏｜30岁｜互联网公司HRBP**
- **背景**：负责120人产品研发团队的HR工作
- **团建频次**：每季度1次（年4次）
- **预算**：人均800元左右
- **痛点**：
  - "去年外包给第三方，花了10万，员工觉得很无聊"
  - "自己组织过一次，协调场地、餐饮累死了"
  - "老板问我为什么这么贵，我也说不清楚"
- **期望**：
  - 快速生成几套方案给老板选
  - 价格透明，能证明性价比
  - 不要太操心，但也不想完全失控

---

## 5. 核心功能（MVP范围）

### 5.1 功能优先级

| 功能 | 优先级 | 目标 | MVP范围 |
|------|--------|------|---------|
| **智能方案生成** | P0 | 15分钟生成3套完整方案 | ✅ 完整实现 |
| **供应商智能匹配** | P0 | 自动匹配3-5家供应商 | ✅ 完整实现 |
| **方案对比与选择** | P0 | 可视化对比，一键选择 | ✅ 完整实现 |
| **基础行程管理** | P1 | 生成行程表，导出PDF | ✅ 简化版 |
| **参与者偏好收集** | P1 | 问卷收集用户偏好 | ⚠️ 简化版（预设选项） |
| **供应商直接联系** | P1 | 一键拨号/微信 | ✅ 完整实现 |
| **历史方案复用** | P2 | 查看历史方案，一键复用 | ⚠️ 仅查看，不支持复用 |
| **满意度追踪** | P2 | 团建后反馈收集 | ❌ 不做 |
| **实时应急预案** | P2 | 天气变化提醒 | ❌ 不做 |

### 5.2 功能详细说明

#### 功能1：智能方案生成（P0 - 核心）

**输入**：
- 基础信息：人数、预算、日期、出发地
- 偏好信息：活动类型（拓展/休闲/文化/运动）、住宿标准、餐饮偏好
- 特殊需求：是否有老人/小孩、身体限制

**AI处理**：
- 分析团队画像（人数规模/预算区间/偏好标签）
- 匹配供应商资源库（场地/民宿/活动/餐饮）
- 生成3套差异化方案（经济型/平衡型/品质型）

**输出**：
- 方案A/B/C：完整行程表 + 预算明细 + 供应商推荐
- 每套方案包含：
  - 行程安排（时间轴）
  - 活动项目（具体内容）
  - 住宿方案（酒店/民宿信息）
  - 餐饮安排（早中晚餐）
  - 交通方案（大巴/自驾）
  - 预算明细（逐项费用）

**核心逻辑**：
```
1. 根据预算和人数计算人均预算区间
2. 根据出发地和日期筛选可用供应商
3. 根据偏好标签匹配活动类型
4. 生成3套不同价格档次的方案
5. 每套方案确保预算±10%范围内
```

---

#### 功能2：供应商智能匹配（P0）

**供应商类型**：
- 场地方：拓展基地、度假村、民宿、农家乐
- 活动方：真人CS、皮划艇、徒步向导、团队游戏教练
- 餐饮方：农家菜、BBQ、团餐配送
- 交通方：大巴租赁、自驾路线规划

**匹配逻辑**：
```python
# 供应商评分算法（伪代码）
def match_suppliers(budget, location, preferences):
    suppliers = query_database(location, category)
    for supplier in suppliers:
        score = 0
        score += price_match_score(supplier.price, budget)  # 30%权重
        score += rating_score(supplier.rating)  # 25%权重
        score += distance_score(supplier.location, start_point)  # 20%权重
        score += preference_match(supplier.tags, preferences)  # 25%权重
    return top_5(suppliers, score)
```

**展示信息**：
- 供应商名称 + 评分（⭐4.5/5.0）
- 价格区间（明码标价）
- 距离/位置（地图展示）
- 特色标签（#适合拓展 #亲子友好 #湖景房）
- 联系方式（一键拨号/微信）

---

#### 功能3：方案对比与选择（P0）

**对比维度**：
| 维度 | 方案A（经济型） | 方案B（平衡型） | 方案C（品质型） |
|------|----------------|----------------|----------------|
| **总预算** | ¥35,000 | ¥45,000 | ¥60,000 |
| **人均成本** | ¥700/人 | ¥900/人 | ¥1,200/人 |
| **住宿标准** | 农家乐（6人间） | 民宿（2人间） | 度假酒店（标间） |
| **活动丰富度** | 2个项目 | 3个项目 | 4个项目 |
| **餐饮标准** | 农家菜 | 特色餐+BBQ | 精品餐厅 |
| **适合人群** | 预算有限 | 性价比优先 | 重视体验 |

**交互设计**：
- 3列卡片并排展示
- 鼠标悬停显示详情
- 点击"选择此方案"进入下一步
- 支持"调整方案"（修改部分项目）

---

#### 功能4：基础行程管理（P1 - 简化版）

**行程表生成**：
```
【2天1夜团建行程表】- 50人

Day 1（周六）
08:30 - 09:00  公司集合，统一大巴出发
09:00 - 11:00  前往目的地（预计2小时）
11:00 - 12:00  酒店check-in，行李寄存
12:00 - 13:30  午餐：农家菜（预算¥50/人）
13:30 - 16:30  团队拓展活动：真人CS对抗赛（教练：2人）
16:30 - 18:00  自由活动 / 湖边漫步
18:00 - 20:00  晚餐 + 团队游戏
20:00 - 21:30  篝火晚会 / KTV
21:30         回房间休息

Day 2（周日）
08:00 - 09:00  早餐（酒店自助餐）
09:00 - 11:30  户外徒步 / 团队协作游戏
11:30 - 13:00  午餐
13:00 - 15:00  返程
15:00         到达公司，活动结束

【费用明细】
交通：¥4,000（大巴往返）
住宿：¥15,000（50人 x ¥150/人/晚）
餐饮：¥10,000（3餐 x ¥200/人）
活动：¥5,000（真人CS + 拓展教练）
其他：¥1,000（物料/应急）
总计：¥45,000（人均¥900）
```

**功能**：
- 自动生成行程表（基于方案数据）
- 支持导出PDF（可打印分发）
- 支持分享链接（参与者查看）
- 支持添加到日历

---

## 6. 用户流程（核心路径）

### 6.1 主流程：15分钟完成方案生成

```
【步骤1：输入基础信息】（2分钟）
用户进入首页
    ↓
填写表单：
- 人数：[50人]
- 预算：[¥35,000 - ¥50,000]
- 日期：[2025-05-10 ~ 2025-05-11]
- 出发地：[北京市朝阳区]
    ↓
点击"下一步"

【步骤2：选择偏好】（2分钟）
选择活动类型：
☑ 团队拓展  ☐ 休闲度假  ☐ 文化体验  ☐ 运动挑战
    ↓
选择住宿标准：
☐ 经济型（农家乐） ☑ 舒适型（民宿） ☐ 品质型（酒店）
    ↓
选择餐饮偏好：
☑ 农家菜  ☐ 西餐  ☐ 火锅  ☐ 烧烤
    ↓
特殊需求：[无]
    ↓
点击"生成方案"

【步骤3：AI生成方案】（1分钟）
显示加载动画：
"🤖 正在为您匹配最佳供应商..."
"🔍 已找到27家符合条件的场地..."
"📊 正在生成3套差异化方案..."
"✅ 方案生成完成！"

【步骤4：查看并对比方案】（5分钟）
展示3套方案卡片（A/B/C）
    ↓
用户查看每套方案详情：
- 完整行程表
- 预算明细
- 供应商信息
- 特色亮点
    ↓
对比3套方案差异
    ↓
选择"方案B（平衡型）"

【步骤5：确认方案】（3分钟）
进入方案详情页
    ↓
用户可以：
- 调整部分项目（如更换住宿）
- 查看供应商联系方式
- 导出行程表PDF
    ↓
点击"确认此方案"

【步骤6：联系供应商】（2分钟）
显示供应商联系方式：
- 场地方：张经理 138****1234 [一键拨号]
- 活动方：李教练 139****5678 [添加微信]
- 餐饮方：王老板 137****9012 [一键拨号]
    ↓
用户保存方案
    ↓
流程结束

总耗时：15分钟（目标）
```

### 6.2 次要流程：历史方案查看

```
用户登录
    ↓
点击"我的方案"
    ↓
查看历史方案列表
    ↓
点击某个方案查看详情
    ↓
可以导出或分享
```

---

## 7. 页面与交互设计

### 7.1 页面结构

```
TeamVenture Web应用
│
├── 首页（Landing Page）
│   ├── Hero区：核心价值主张
│   ├── 快速开始表单
│   ├── 功能介绍
│   └── 用户评价
│
├── 方案生成流程（Wizard）
│   ├── Step 1：基础信息
│   ├── Step 2：偏好选择
│   ├── Step 3：生成中（Loading）
│   └── Step 4：方案展示
│
├── 方案对比页（Comparison）
│   ├── 3列方案卡片
│   ├── 对比表格
│   └── 选择按钮
│
├── 方案详情页（Detail）
│   ├── 完整行程表
│   ├── 预算明细
│   ├── 供应商信息
│   ├── 联系方式
│   └── 操作按钮（导出/分享/确认）
│
├── 我的方案（Dashboard）
│   ├── 历史方案列表
│   ├── 状态跟踪
│   └── 数据统计
│
└── 设置页（Settings）
    ├── 账号信息
    ├── 企业信息
    └── 偏好设置
```

### 7.2 关键页面设计

#### 页面1：首页（Landing Page）

**Hero区**：
```
┌─────────────────────────────────────────────┐
│                                             │
│         🤖 TeamVenture                      │
│      AI驱动的团建策划助手                    │
│                                             │
│      15分钟生成完整方案 | 成本降低50%+        │
│                                             │
│  [ 预算 ] [ 人数 ] [ 日期 ]                 │
│  [     立即开始生成方案     ]               │
│                                             │
│  ✓ 已为 500+ 企业节省 200万+ 团建成本        │
│                                             │
└─────────────────────────────────────────────┘
```

**功能介绍**：
```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ 智能生成  │  │ 智能匹配  │  │ 透明比价  │
│ 15分钟    │  │ 3-5家    │  │ 省50%+   │
│ 3套方案   │  │ 供应商    │  │ 明码标价  │
└──────────┘  └──────────┘  └──────────┘
```

---

#### 页面2：方案生成 - Step 1（基础信息）

```
┌─────────────────────────────────────────────┐
│  TeamVenture  [首页] [我的方案] [登录]       │
├─────────────────────────────────────────────┤
│                                             │
│  告诉我们您的团建需求                        │
│  ────────────────────────────                │
│                                             │
│  👥 参与人数                                 │
│  [  50  ] 人                                │
│                                             │
│  💰 预算范围                                 │
│  ¥ [ 35,000 ] - ¥ [ 50,000 ]              │
│  （人均 ¥700 - ¥1,000）                     │
│                                             │
│  📅 活动日期                                 │
│  [ 2025-05-10 ] 至 [ 2025-05-11 ]         │
│  （周六 - 周日，2天1夜）                     │
│                                             │
│  📍 出发地点                                 │
│  [ 北京市朝阳区 ]  🔍 搜索                   │
│                                             │
│                    [ 下一步 → ]             │
│                                             │
└─────────────────────────────────────────────┘
```

---

#### 页面3：方案生成 - Step 3（生成中）

```
┌─────────────────────────────────────────────┐
│  TeamVenture                                │
├─────────────────────────────────────────────┤
│                                             │
│              🤖                             │
│                                             │
│        正在为您生成方案...                   │
│                                             │
│  ✓ 已分析您的团队画像                        │
│  ✓ 已匹配 27 家供应商                        │
│  ⏳ 正在生成 3 套差异化方案...               │
│                                             │
│  [████████████░░░░░] 80%                   │
│                                             │
│  预计还需 15 秒                              │
│                                             │
└─────────────────────────────────────────────┘
```

---

#### 页面4：方案对比（Comparison）

```
┌───────────────────────────────────────────────────────────┐
│  TeamVenture  [返回首页] [我的方案] [退出]                  │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  为您生成了 3 套方案，请选择最适合您的：                    │
│  ─────────────────────────────────────────                │
│                                                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                  │
│  │ 方案A    │  │ 方案B    │  │ 方案C    │                  │
│  │ 经济型   │  │ 平衡型   │  │ 品质型   │   ⭐推荐          │
│  │         │  │         │  │         │                  │
│  │ ¥35,000 │  │ ¥45,000 │  │ ¥60,000 │                  │
│  │ ¥700/人 │  │ ¥900/人 │  │¥1,200/人│                  │
│  │         │  │         │  │         │                  │
│  │ 农家乐   │  │ 民宿     │  │ 度假酒店 │                  │
│  │ 2个活动  │  │ 3个活动  │  │ 4个活动  │                  │
│  │ 农家菜   │  │ 特色餐   │  │ 精品餐厅 │                  │
│  │         │  │         │  │         │                  │
│  │[查看详情]│  │[查看详情]│  │[查看详情]│                  │
│  │[选择方案]│  │[选择方案]│  │[选择方案]│                  │
│  └─────────┘  └─────────┘  └─────────┘                  │
│                                                           │
│  [ 查看详细对比表 ▼ ]                                      │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

---

## 8. AI能力设计

### 8.1 AI模块架构

```
┌─────────────────────────────────────────┐
│         用户输入（表单数据）              │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│     AI Agent 1: 需求理解与标准化          │
│  - 解析用户输入                          │
│  - 标准化预算/人数/日期/偏好              │
│  - 识别特殊需求                          │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│     AI Agent 2: 供应商智能匹配            │
│  - 查询供应商数据库                      │
│  - 计算匹配分数                          │
│  - 返回Top 5供应商                       │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│     AI Agent 3: 方案生成与优化            │
│  - 生成3套差异化方案                     │
│  - 预算优化（控制在±10%）                │
│  - 行程合理性检查                        │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│     AI Agent 4: 方案描述生成              │
│  - 生成方案亮点描述                      │
│  - 生成完整行程表文案                    │
│  - 生成预算说明                          │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│         输出：3套完整方案                 │
└─────────────────────────────────────────┘
```

### 8.2 核心AI Prompt设计

#### Prompt 1：需求理解与标准化

```python
PROMPT_PARSE_REQUIREMENTS = """
你是一个专业的团建策划助手。用户提供了以下团建需求，请分析并标准化：

用户输入：
- 人数：{people_count}
- 预算：{budget_min} - {budget_max}
- 日期：{start_date} - {end_date}
- 出发地：{departure_location}
- 活动偏好：{activity_preferences}
- 住宿标准：{accommodation_level}
- 餐饮偏好：{dining_preferences}
- 特殊需求：{special_requirements}

请输出JSON格式的标准化需求：
{
  "team_size": "small|medium|large",  // <30小型, 30-100中型, >100大型
  "budget_per_person": 700,  // 人均预算
  "duration_days": 2,  // 天数
  "activity_type": ["outdoor", "team_building"],  // 活动类型标签
  "accommodation_level": "budget|standard|premium",  // 住宿档次
  "dining_style": ["local", "bbq"],  // 餐饮风格
  "constraints": ["no_elderly", "budget_conscious"],  // 约束条件
  "search_radius_km": 150  // 搜索半径（根据日期推断）
}
"""
```

#### Prompt 2：方案生成

```python
PROMPT_GENERATE_PLAN = """
你是一个专业的团建策划师。根据以下信息生成一个完整的团建方案：

标准化需求：
{standardized_requirements}

匹配的供应商（已按评分排序）：
{matched_suppliers}

请生成一个**{plan_type}**（经济型/平衡型/品质型）的完整方案，包含：

1. 方案概览
   - 方案名称（有吸引力的标题）
   - 核心亮点（3个bullet points）
   - 适合人群

2. 完整行程表
   Day 1:
   - 08:30-09:00 ...
   Day 2:
   - ...

3. 预算明细
   - 交通：¥X
   - 住宿：¥X
   - 餐饮：¥X
   - 活动：¥X
   - 其他：¥X
   - 总计：¥X（人均¥X）

4. 供应商推荐
   - 场地方：[名称] + [联系方式] + [评分]
   - 活动方：...
   - 餐饮方：...

5. 特别说明
   - 注意事项
   - 应急预案

要求：
- 预算控制在 ¥{budget_min} - ¥{budget_max} 之间
- 行程安排合理（时间衔接顺畅）
- 活动丰富度与预算匹配
- 语言简洁专业，易于理解

输出JSON格式。
"""
```

#### Prompt 3：方案描述生成

```python
PROMPT_GENERATE_DESCRIPTION = """
请为以下团建方案生成吸引人的描述文案：

方案名称：{plan_name}
核心数据：
- 人均：¥{per_person_cost}
- 天数：{duration_days}天{duration_days-1}夜
- 活动：{activity_count}个项目
- 住宿：{accommodation_type}

请生成：
1. 一句话亮点（15字以内，突出性价比或特色）
2. 方案简介（50字，吸引HR点击查看详情）
3. 适合人群标签（3个，如"预算有限"、"注重团队凝聚"）

风格要求：
- 专业但不生硬
- 突出实际价值
- 避免夸大宣传
"""
```

### 8.3 AI能力边界与兜底

| 场景 | AI能力 | 兜底机制 |
|------|--------|---------|
| **供应商匹配失败** | AI找不到符合条件的供应商 | 人工推荐备选方案 |
| **预算无法满足** | 用户预算过低 | 提示调整预算或缩减项目 |
| **特殊需求识别** | 无法理解复杂需求 | 转人工客服 |
| **方案不合理** | 时间冲突/逻辑错误 | 规则引擎二次校验 |
| **生成失败** | LLM API超时 | 降级到规则模板生成 |

---

## 9. 数据结构设计

### 9.1 核心数据模型

#### 表1：用户表（users）

```sql
CREATE TABLE users (
  -- 说明：
  -- - 对外暴露/跨系统传递的主键建议使用全局唯一ID（ULID/UUID），避免依赖自增ID
  -- - 下方示例以 PostgreSQL 风格书写（JSONB/CHECK/TIMESTAMPTZ）；如选 MySQL 需改写语法
  user_id TEXT PRIMARY KEY,  -- e.g. user_01JHxxxx（ULID）或 UUID
  email VARCHAR(255) NOT NULL,
  name VARCHAR(100),
  phone VARCHAR(20),
  company_name VARCHAR(200),
  company_size TEXT CHECK (company_size IN ('small', 'medium', 'large')),  -- <50, 50-200, >200
  role VARCHAR(50),  -- HR, 行政, 创始人
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_login_at TIMESTAMPTZ,
  subscription_status TEXT CHECK (subscription_status IN ('trial', 'paid', 'expired')) DEFAULT 'trial'
);
```

```sql
-- Comments（字段释义）
COMMENT ON TABLE users IS 'TeamVenture 用户表（企业HR/行政等登录用户）';
COMMENT ON COLUMN users.user_id IS '用户全局唯一ID（ULID/UUID），对外可暴露';
COMMENT ON COLUMN users.email IS '登录邮箱（唯一）';
COMMENT ON COLUMN users.name IS '用户姓名/称呼';
COMMENT ON COLUMN users.phone IS '手机号（可选；如涉及隐私需脱敏/加密存储）';
COMMENT ON COLUMN users.company_name IS '公司名称';
COMMENT ON COLUMN users.company_size IS '公司规模：small(<50)/medium(50-200)/large(>200)';
COMMENT ON COLUMN users.role IS '用户角色：HR/行政/创始人等';
COMMENT ON COLUMN users.created_at IS '创建时间';
COMMENT ON COLUMN users.last_login_at IS '最近登录时间';
COMMENT ON COLUMN users.subscription_status IS '订阅状态：trial/paid/expired';

-- Unique Indexes（唯一索引，显式写法）
CREATE UNIQUE INDEX ux_users_email ON users (email);

-- Indexes（常用查询路径）
CREATE INDEX idx_users_created_at ON users (created_at);
CREATE INDEX idx_users_last_login_at ON users (last_login_at);
CREATE INDEX idx_users_subscription_status ON users (subscription_status);
```

#### 表2：团建方案表（plans）

```sql
CREATE TABLE plans (
  plan_id TEXT PRIMARY KEY,  -- e.g. plan_01JHxxxx（ULID）或 UUID
  user_id TEXT NOT NULL REFERENCES users(user_id),
  plan_name VARCHAR(200),
  plan_type TEXT CHECK (plan_type IN ('budget', 'standard', 'premium')),  -- 经济/平衡/品质
  status TEXT CHECK (status IN ('draft', 'confirmed', 'cancelled')) DEFAULT 'draft',

  -- 基础信息
  people_count INT NOT NULL,
  budget_total DECIMAL(10,2),
  budget_per_person DECIMAL(10,2),
  start_date DATE,
  end_date DATE,
  duration_days INT,
  departure_location VARCHAR(200),

  -- 偏好信息（JSON）
  preferences JSONB,  -- {"activity_types": [], "accommodation": "", ...}

  -- 生成的方案内容（JSON）
  itinerary JSONB,  -- 完整行程表
  budget_breakdown JSONB,  -- 预算明细
  suppliers JSONB,  -- 供应商信息（或做关联表）

  -- 元数据
  generated_at TIMESTAMPTZ,
  confirmed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

```sql
-- Comments（字段释义）
COMMENT ON TABLE plans IS '团建方案表（一次需求会生成多套方案，每套为一条记录）';
COMMENT ON COLUMN plans.plan_id IS '方案全局唯一ID（ULID/UUID），对外可暴露';
COMMENT ON COLUMN plans.user_id IS '所属用户ID（users.user_id）';
COMMENT ON COLUMN plans.plan_name IS '方案名称';
COMMENT ON COLUMN plans.plan_type IS '方案档位：budget/standard/premium';
COMMENT ON COLUMN plans.status IS '方案状态：draft/confirmed/cancelled';
COMMENT ON COLUMN plans.people_count IS '参与人数';
COMMENT ON COLUMN plans.budget_total IS '总预算（元）';
COMMENT ON COLUMN plans.budget_per_person IS '人均预算（元）';
COMMENT ON COLUMN plans.start_date IS '开始日期';
COMMENT ON COLUMN plans.end_date IS '结束日期';
COMMENT ON COLUMN plans.duration_days IS '总天数';
COMMENT ON COLUMN plans.departure_location IS '出发地（文本/行政区划）';
COMMENT ON COLUMN plans.preferences IS '用户偏好（JSONB），用于复用与检索';
COMMENT ON COLUMN plans.itinerary IS '行程明细（JSONB）';
COMMENT ON COLUMN plans.budget_breakdown IS '预算明细（JSONB）';
COMMENT ON COLUMN plans.suppliers IS '方案中使用/推荐的供应商快照（JSONB；也可拆为关联表）';
COMMENT ON COLUMN plans.generated_at IS '生成完成时间';
COMMENT ON COLUMN plans.confirmed_at IS '用户确认时间';
COMMENT ON COLUMN plans.created_at IS '创建时间';
COMMENT ON COLUMN plans.updated_at IS '更新时间（需应用层维护）';

-- Indexes（常用查询路径）
CREATE INDEX idx_plans_user_id_created_at ON plans (user_id, created_at DESC);
CREATE INDEX idx_plans_status_created_at ON plans (status, created_at DESC);
CREATE INDEX idx_plans_plan_type ON plans (plan_type);
CREATE INDEX idx_plans_generated_at ON plans (generated_at);
CREATE INDEX idx_plans_confirmed_at ON plans (confirmed_at);
CREATE INDEX idx_plans_preferences_gin ON plans USING GIN (preferences);
```

#### 表3：供应商表（suppliers）

```sql
CREATE TABLE suppliers (
  supplier_id TEXT PRIMARY KEY,  -- e.g. sup_01JHxxxx（ULID）或 UUID
  name VARCHAR(200) NOT NULL,
  category TEXT CHECK (category IN ('venue', 'activity', 'dining', 'accommodation', 'transportation')),
  subcategory VARCHAR(100),  -- 如：真人CS, 民宿, 农家菜

  -- 位置信息
  province VARCHAR(50),
  city VARCHAR(50),
  district VARCHAR(50),
  address VARCHAR(500),
  latitude DECIMAL(10,6),
  longitude DECIMAL(10,6),

  -- 基础信息
  description TEXT,
  capacity_min INT,  -- 最小接待人数
  capacity_max INT,  -- 最大接待人数
  price_range_min DECIMAL(10,2),
  price_range_max DECIMAL(10,2),

  -- 评价信息
  rating DECIMAL(3,2),  -- 4.5
  review_count INT DEFAULT 0,

  -- 联系信息
  contact_name VARCHAR(100),
  contact_phone VARCHAR(20),
  contact_wechat VARCHAR(100),

  -- 标签（JSON）
  tags JSONB,  -- ["适合拓展", "湖景房", "亲子友好"]

  -- 状态
  status TEXT CHECK (status IN ('active', 'inactive')) DEFAULT 'active',
  verified BOOLEAN DEFAULT FALSE,  -- 是否平台认证

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

```sql
-- Comments（字段释义）
COMMENT ON TABLE suppliers IS '供应商表（场地/活动/餐饮/住宿/交通等资源方）';
COMMENT ON COLUMN suppliers.supplier_id IS '供应商全局唯一ID（ULID/UUID）';
COMMENT ON COLUMN suppliers.name IS '供应商名称';
COMMENT ON COLUMN suppliers.category IS '供应商类别：venue/activity/dining/accommodation/transportation';
COMMENT ON COLUMN suppliers.subcategory IS '子类目（如：真人CS/民宿/农家菜）';
COMMENT ON COLUMN suppliers.province IS '省';
COMMENT ON COLUMN suppliers.city IS '市';
COMMENT ON COLUMN suppliers.district IS '区/县';
COMMENT ON COLUMN suppliers.address IS '详细地址';
COMMENT ON COLUMN suppliers.latitude IS '纬度';
COMMENT ON COLUMN suppliers.longitude IS '经度';
COMMENT ON COLUMN suppliers.description IS '资源描述';
COMMENT ON COLUMN suppliers.capacity_min IS '最小接待人数';
COMMENT ON COLUMN suppliers.capacity_max IS '最大接待人数';
COMMENT ON COLUMN suppliers.price_range_min IS '价格区间下限（元）';
COMMENT ON COLUMN suppliers.price_range_max IS '价格区间上限（元）';
COMMENT ON COLUMN suppliers.rating IS '评分（如 4.5）';
COMMENT ON COLUMN suppliers.review_count IS '评价数';
COMMENT ON COLUMN suppliers.contact_name IS '联系人';
COMMENT ON COLUMN suppliers.contact_phone IS '联系电话';
COMMENT ON COLUMN suppliers.contact_wechat IS '联系微信';
COMMENT ON COLUMN suppliers.tags IS '标签（JSONB 数组）';
COMMENT ON COLUMN suppliers.status IS '状态：active/inactive';
COMMENT ON COLUMN suppliers.verified IS '是否平台认证';
COMMENT ON COLUMN suppliers.created_at IS '创建时间';
COMMENT ON COLUMN suppliers.updated_at IS '更新时间（需应用层维护）';

-- Indexes（检索/筛选/排序）
CREATE INDEX idx_suppliers_city_category_status ON suppliers (city, category, status);
CREATE INDEX idx_suppliers_capacity ON suppliers (capacity_min, capacity_max);
CREATE INDEX idx_suppliers_price_range ON suppliers (price_range_min, price_range_max);
CREATE INDEX idx_suppliers_rating ON suppliers (rating DESC);
CREATE INDEX idx_suppliers_tags_gin ON suppliers USING GIN (tags);
```

#### 表4：匹配记录表（plan_supplier_matches）

```sql
CREATE TABLE plan_supplier_matches (
  -- 关联表通常可用组合主键，避免引入自增ID
  plan_id TEXT NOT NULL REFERENCES plans(plan_id),
  supplier_id TEXT NOT NULL REFERENCES suppliers(supplier_id),
  match_score DECIMAL(5,2),  -- AI计算的匹配分数
  selected BOOLEAN DEFAULT FALSE,  -- 用户是否选择
  contacted BOOLEAN DEFAULT FALSE,  -- 是否已联系

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (plan_id, supplier_id)
);
```

```sql
-- Comments（字段释义）
COMMENT ON TABLE plan_supplier_matches IS '方案与供应商匹配结果（用于推荐、比价与用户选择跟踪）';
COMMENT ON COLUMN plan_supplier_matches.plan_id IS '方案ID（plans.plan_id）';
COMMENT ON COLUMN plan_supplier_matches.supplier_id IS '供应商ID（suppliers.supplier_id）';
COMMENT ON COLUMN plan_supplier_matches.match_score IS '匹配分（AI/规则综合评分）';
COMMENT ON COLUMN plan_supplier_matches.selected IS '用户是否选中该供应商';
COMMENT ON COLUMN plan_supplier_matches.contacted IS '用户是否已联系该供应商';
COMMENT ON COLUMN plan_supplier_matches.created_at IS '创建时间';

-- Indexes（反向查询与运营统计）
CREATE INDEX idx_plan_supplier_matches_supplier_id ON plan_supplier_matches (supplier_id);
CREATE INDEX idx_plan_supplier_matches_selected ON plan_supplier_matches (selected);
CREATE INDEX idx_plan_supplier_matches_contacted ON plan_supplier_matches (contacted);
CREATE INDEX idx_plan_supplier_matches_created_at ON plan_supplier_matches (created_at DESC);
```

### 9.2 JSON字段详细结构

#### preferences JSON 示例

```json
{
  "activity_types": ["team_building", "outdoor"],
  "accommodation_level": "standard",
  "dining_style": ["local", "bbq"],
  "special_requirements": "无老人和小孩",
  "budget_constraints": "严格控制预算",
  "team_profile": {
    "industry": "互联网",
    "average_age": 28,
    "male_ratio": 0.6
  }
}
```

#### itinerary JSON 示例

```json
{
  "days": [
    {
      "day": 1,
      "date": "2025-05-10",
      "items": [
        {
          "time_start": "08:30",
          "time_end": "09:00",
          "activity": "公司集合，统一大巴出发",
          "location": "公司楼下",
          "note": "请提前10分钟到达"
        },
        {
          "time_start": "09:00",
          "time_end": "11:00",
          "activity": "前往目的地",
          "location": "大巴车上",
          "cost": 4000,
          "supplier_id": 123
        }
        // ... more items
      ]
    },
    {
      "day": 2,
      // ...
    }
  ]
}
```

#### budget_breakdown JSON 示例

```json
{
  "categories": [
    {
      "category": "交通",
      "items": [
        {
          "item": "大巴往返",
          "quantity": "1辆 x 2天",
          "unit_price": 2000,
          "total": 4000,
          "supplier_id": 123
        }
      ],
      "subtotal": 4000
    },
    {
      "category": "住宿",
      "items": [
        {
          "item": "民宿标间",
          "quantity": "25间 x 1晚",
          "unit_price": 300,
          "total": 7500,
          "supplier_id": 456
        }
      ],
      "subtotal": 7500
    }
    // ... more categories
  ],
  "total": 45000,
  "per_person": 900
}
```

---

## 10. API设计

### 10.1 API列表

| API | 方法 | 功能 | 优先级 |
|-----|------|------|--------|
| `/api/plans/generate` | POST | 生成团建方案 | P0 |
| `/api/plans/{id}` | GET | 获取方案详情 | P0 |
| `/api/plans` | GET | 获取用户方案列表 | P1 |
| `/api/plans/{id}/export` | GET | 导出方案PDF | P1 |
| `/api/suppliers/search` | GET | 搜索供应商 | P1 |
| `/api/suppliers/{id}` | GET | 获取供应商详情 | P1 |
| `/api/users/register` | POST | 用户注册 | P0 |
| `/api/users/login` | POST | 用户登录 | P0 |

### 10.2 核心API详细设计

#### API 1：生成团建方案

```
POST /api/plans/generate
```

**Request Body**:
```json
{
  "people_count": 50,
  "budget_min": 35000,
  "budget_max": 50000,
  "start_date": "2025-05-10",
  "end_date": "2025-05-11",
  "departure_location": "北京市朝阳区",
  "preferences": {
    "activity_types": ["team_building", "outdoor"],
    "accommodation_level": "standard",
    "dining_style": ["local", "bbq"],
    "special_requirements": "无"
  }
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "plans": [
      {
        "plan_id": "plan_01JHXXXXXXXEXAMPLE0000000000",
        "plan_type": "budget",
        "plan_name": "经济实惠·怀柔山野团建",
        "highlight": "人均¥700，2个精选活动，农家乐住宿",
        "summary": "适合预算有限的团队，在怀柔山区进行真人CS和徒步活动，体验农家菜和篝火晚会，性价比超高。",
        "budget_total": 35000,
        "budget_per_person": 700,
        "itinerary": { /* 完整行程JSON */ },
        "budget_breakdown": { /* 预算明细JSON */ },
        "suppliers": [ /* 供应商列表 */ ],
        "suitable_for": ["预算有限", "注重性价比", "喜欢户外"]
      },
      {
        "plan_id": "plan_01JHXXXXXXXEXAMPLE0000000001",
        "plan_type": "standard",
        "plan_name": "平衡之选·密云水库度假",
        // ...
      },
      {
        "plan_id": "plan_01JHXXXXXXXEXAMPLE0000000002",
        "plan_type": "premium",
        "plan_name": "品质体验·古北水镇团建",
        // ...
      }
    ],
    "generation_time_ms": 45000,  // 生成耗时
    "alternatives_count": 27  // 候选供应商数量
  }
}
```

**Error Response** (400 Bad Request):
```json
{
  "success": false,
  "error": {
    "code": "BUDGET_TOO_LOW",
    "message": "根据您的人数和日期，建议预算至少为¥40,000",
    "suggestion": "您可以：1) 增加预算 2) 减少天数 3) 缩减活动项目"
  }
}
```

---

#### API 2：获取方案详情

```
GET /api/plans/{plan_id}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "plan_id": "plan_01JHXXXXXXXEXAMPLE0000000000",
    "plan_name": "经济实惠·怀柔山野团建",
    "status": "confirmed",
    "people_count": 50,
    "budget_total": 35000,
    "itinerary": {
      "days": [
        {
          "day": 1,
          "date": "2025-05-10",
          "items": [
            {
              "time_start": "08:30",
              "time_end": "09:00",
              "activity": "公司集合，统一大巴出发",
              "location": "公司楼下"
            }
            // ... more items
          ]
        }
      ]
    },
    "budget_breakdown": { /* 详细预算 */ },
    "suppliers": [
      {
        "supplier_id": 123,
        "name": "怀柔山庄",
        "category": "accommodation",
        "rating": 4.5,
        "contact_phone": "138****1234",
        "contact_wechat": "huairou_shanzhunag"
      }
      // ... more suppliers
    ],
    "created_at": "2025-12-29T10:30:00Z",
    "confirmed_at": "2025-12-29T11:15:00Z"
  }
}
```

---

## 11. 埋点与指标

### 11.1 核心指标体系

#### 北极星指标
**成功生成并确认的方案数**（Weekly Active Plans）

#### 一级指标

| 指标 | 定义 | 目标值 | 测量方式 |
|------|------|--------|---------|
| **方案生成成功率** | 完成生成/发起生成 | >95% | 埋点统计 |
| **方案确认率** | 确认方案数/生成方案数 | >30% | 埋点统计 |
| **平均生成时间** | 从提交到展示的时长 | <60秒 | 服务端日志 |
| **用户留存率（D7）** | 7天后再次使用的用户占比 | >40% | 用户行为分析 |
| **NPS** | 用户推荐意愿 | >30 | 问卷调查 |

#### 二级指标

| 维度 | 指标 | 目标 |
|------|------|------|
| **转化漏斗** | 首页访问→提交需求→查看方案→确认方案 | 50%→80%→40% |
| **用户满意度** | 方案满意度评分（1-5星） | >4.0 |
| **成本效率** | 实际成本 vs 传统服务商报价 | 降低>40% |
| **供应商覆盖** | 可用供应商数量（按区域） | 每个热门城市>50家 |
| **客诉率** | 投诉数/总方案数 | <5% |

### 11.2 埋点事件设计

#### 关键埋点事件

| 事件名称 | 触发时机 | 参数 | 优先级 |
|---------|---------|------|--------|
| `page_view` | 页面访问 | page_name, referrer | P0 |
| `plan_generate_start` | 用户点击"生成方案" | people_count, budget, date | P0 |
| `plan_generate_success` | 方案生成成功 | plan_ids[], generation_time_ms | P0 |
| `plan_generate_failed` | 方案生成失败 | error_code, error_message | P0 |
| `plan_view` | 查看方案详情 | plan_id, plan_type | P0 |
| `plan_compare` | 对比多个方案 | plan_ids[] | P1 |
| `plan_confirm` | 确认方案 | plan_id, budget_total | P0 |
| `supplier_contact` | 联系供应商 | supplier_id, contact_method | P0 |
| `plan_export` | 导出方案PDF | plan_id, export_format | P1 |
| `plan_share` | 分享方案 | plan_id, share_channel | P1 |

#### 埋点代码示例

```javascript
// 用户点击"生成方案"
trackEvent('plan_generate_start', {
  people_count: 50,
  budget_min: 35000,
  budget_max: 50000,
  duration_days: 2,
  departure_location: '北京市朝阳区',
  activity_types: ['team_building', 'outdoor'],
  user_id: 'user_123',
  session_id: 'session_456',
  timestamp: '2025-12-29T10:30:00Z'
});

// 方案生成成功
trackEvent('plan_generate_success', {
  plan_ids: ['plan_01JHXXXXXXXEXAMPLE0000000000', 'plan_01JHXXXXXXXEXAMPLE0000000001', 'plan_01JHXXXXXXXEXAMPLE0000000002'],
  generation_time_ms: 45000,
  alternatives_count: 27,
  user_id: 'user_123',
  session_id: 'session_456',
  timestamp: '2025-12-29T10:30:45Z'
});
```

### 11.3 实验指标

为MVP阶段设计A/B测试的指标：

| 实验 | 对照组 | 实验组 | 核心指标 |
|------|--------|--------|---------|
| **方案数量** | 3套方案 | 5套方案 | 确认率、决策时间 |
| **方案排序** | 按预算排序 | 按推荐度排序 | 确认率、满意度 |
| **生成动画** | 简单进度条 | 动态文案提示 | 用户焦虑度、完成率 |
| **供应商展示** | 列表展示 | 卡片展示 | 联系供应商率 |

---

## 12. MVP实验计划

### 12.1 验证假设

| 假设 | 验证方法 | 成功标准 | 时间 |
|------|---------|---------|------|
| **H1: HR愿意为AI工具付费** | 种子用户访谈 + 转化漏斗 | 付费转化率>10% | Week 1-2 |
| **H2: 15分钟可生成满意方案** | 平均生成时间 + 方案确认率 | 生成<60秒, 确认率>30% | Week 1-4 |
| **H3: 成本可降低50%+** | 用户反馈 + 实际案例 | 对比传统报价降低>40% | Week 2-4 |
| **H4: 供应商资源可快速整合** | BD进度 + 覆盖率 | 北京周边供应商>50家 | Week 1-8 |

### 12.2 两周冲刺实验

**Week 1（概念验证）**:
- 开发最小可用原型（Wizard流程 + Mock数据）
- 招募10位种子用户试用
- 收集第一手反馈

**Week 2（功能验证）**:
- 完成AI方案生成（真实LLM调用）
- 对接3-5家供应商（手动录入）
- 邀请20位用户生成真实方案

**成功标准**:
- ✅ 10位种子用户中，>7位愿意付费
- ✅ 生成的方案被认为"比自己研究3天还要好"
- ✅ 至少1个方案被实际执行

### 12.3 数据收集计划

**定性数据**:
- 用户访谈记录（每周3-5人）
- 用户使用录屏（观察卡点）
- NPS调查 + 开放式反馈

**定量数据**:
- 埋点数据（全流程）
- 服务端性能日志
- 转化漏斗分析

---

## 13. 合规与隐私

### 13.1 数据隐私

**数据分类**:
- **敏感数据**: 企业名称、联系方式、预算信息
- **一般数据**: 方案内容、供应商信息

**保护措施**:
- ✅ 所有敏感数据加密存储
- ✅ 仅用户本人可查看自己的方案
- ✅ 不向供应商透露企业名称（匿名询价）
- ✅ 用户可随时删除所有数据

### 13.2 用户协议

**服务协议要点**:
- TeamVenture仅提供方案生成服务，不承担供应商服务质量责任
- 用户需自行验证供应商资质
- 最终价格以供应商报价为准

**免责声明**:
- 方案仅供参考，不保证完全适用
- 天气等不可抗力因素导致的变更，平台不承担责任

### 13.3 供应商合作规范

**入驻要求**:
- 营业执照
- 服务案例（至少3个）
- 用户评价（平均>4.0）

**平台规则**:
- 禁止虚假宣传
- 禁止恶意竞价
- 禁止私下交易（初期宽松，后期严格）

---

## 14. 技术栈与架构（简要）

### 14.1 技术选型

**前端**:
- React + TypeScript
- Ant Design / Chakra UI
- Vercel部署

**后端**:
- Node.js + Express / Python + FastAPI
- PostgreSQL（用户/方案数据）
- Redis（缓存/会话）

**AI/LLM**:
- OpenAI GPT-4 / Claude API
- LangChain（Agent编排）
- Prompt工程

**其他**:
- PDF生成：Puppeteer / wkhtmltopdf
- 地图服务：高德地图API
- 短信/邮件：阿里云

### 14.2 系统架构（简化）

```
┌─────────┐
│ 用户浏览器 │
└────┬────┘
     │ HTTPS
     ↓
┌─────────────┐
│  Web服务器   │ (Vercel / Nginx)
└────┬────────┘
     │
     ↓
┌─────────────────────────┐
│    API Gateway          │
└────┬───────────────┬────┘
     │               │
     ↓               ↓
┌──────────┐   ┌────────────┐
│ 业务逻辑层 │   │ AI Agent层 │
│ (Express) │   │ (LangChain)│
└────┬─────┘   └────┬───────┘
     │               │
     ↓               ↓
┌──────────┐   ┌────────────┐
│ 数据库    │   │  LLM API   │
│(PostgreSQL)│   │ (OpenAI)   │
└──────────┘   └────────────┘
```

---

## 15. 里程碑与路线图

### 15.1 MVP开发里程碑（8周）

| 周 | 里程碑 | 产出 |
|----|--------|------|
| **W1** | 原型设计 | Figma高保真原型 |
| **W2-3** | 前端开发 | Wizard流程 + 3个核心页面 |
| **W4-5** | 后端开发 | API接口 + 数据库 |
| **W5-6** | AI集成 | 方案生成Agent |
| **W6** | 供应商对接 | 手动录入50家供应商 |
| **W7** | 测试优化 | Bug修复 + 性能优化 |
| **W8** | 种子用户 | 招募100家企业试用 |

### 15.2 产品演进路线（6个月）

**v0.1 (Month 1-2)**: MVP上线
- 核心功能：方案生成 + 供应商匹配
- 目标用户：100家种子企业

**v0.2 (Month 3)**: 功能完善
- 新增：历史方案复用
- 新增：参与者偏好收集（问卷）
- 优化：AI生成质量

**v0.3 (Month 4-5)**: 规模化
- 供应商数量：>500家
- 覆盖城市：北上广深+10个二线城市
- 新增：移动端H5

**v1.0 (Month 6)**: 商业化
- 订阅付费模式上线
- 企业级功能：批量管理/权限控制
- 数据分析：ROI报告

---

## 16. 附录

### 16.1 参考文档

- [市场调研报告](../docs/teamventure-market-research.md)
- [竞品分析](../docs/teamventure-market-research.md#2-竞品分析)
- [定价策略](../docs/teamventure-market-research.md#3-定价策略分析)

### 16.2 术语表

| 术语 | 定义 |
|------|------|
| **toProC** | To Professional Consumer，面向专业消费者（企业HR/行政） |
| **MVP** | Minimum Viable Product，最小可行产品 |
| **NPS** | Net Promoter Score，净推荐值 |
| **ICP** | Ideal Customer Profile，理想客户画像 |
| **JTBD** | Jobs To Be Done，用户要完成的任务 |
| **LLM** | Large Language Model，大语言模型 |
| **SaaS** | Software as a Service，软件即服务 |

---

**文档版本**: v1.0
**最后更新**: 2025-12-29
**负责人**: [待定]
**审核状态**: ⏳ 待审核
