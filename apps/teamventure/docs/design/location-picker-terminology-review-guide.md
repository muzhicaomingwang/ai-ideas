# LocationPicker模块术语规范评审指南

**评审目的**: 确保团队成员理解并遵循统一的术语规范
**评审时长**: 15分钟
**参与人员**: 前端、后端、产品、测试

---

## 快速概览（5分钟）

### 为什么需要术语统一？

**问题示例**：
```
产品说："用户选择目的地"
前端理解："选择城市"（使用三级联动picker）
后端理解："选择景点"（调用POI搜索API）
➡️ 结果：功能实现偏差，需返工
```

**术语统一后**：
```
产品说："用户选择目的地景点"
前端理解："使用LocationPicker组件，选择景点级地点"
后端理解："提供/api/v1/locations/suggest接口"
➡️ 结果：一次实现到位，无歧义
```

### 核心收益
- ✅ 减少沟通成本（无需反复解释）
- ✅ 降低开发返工率（需求理解一致）
- ✅ 提升代码可读性（术语见名知义）
- ✅ 方便新人上手（查术语表即懂）

---

## 核心术语速记卡（2分钟）

### 必须记住的10个术语

| 序号 | 术语 | 英文 | 记忆要点 |
|------|------|------|----------|
| 1 | **地点** | Location | 泛指任何位置（城市/景点/地标） |
| 2 | **景点/POI** | Attraction/POI | 旅游目的地（风景区、酒店、地标） |
| 3 | **出发地点** | Departure | 团建出发位置（细化到景点级） |
| 4 | **目的地点** | Destination | 团建目标位置（细化到景点级） |
| 5 | **搜索建议** | Suggestion | 搜索返回的候选地点列表 |
| 6 | **热门景点** | Hot Spot | 高热度推荐目的地 |
| 7 | **最近使用** | Recent Location | 用户历史选择的地点 |
| 8 | **LocationValue** | LocationValue | 标准地点数据对象（name+address+location） |
| 9 | **经度/纬度** | longitude/latitude | 使用完整单词（不用lng/lat缩写） |
| 10 | **地理编码** | Geocoding | 地址→坐标 / 坐标→地址转换 |

### 必须避免的术语

| ❌ 禁用 | ✅ 替换为 | 原因 |
|--------|---------|------|
| "位置" | "地点" | 统一业务术语（微信API除外） |
| "地方" | "地点" | 统一业务术语 |
| "place" | "location" | 统一代码术语 |
| "search" | "suggest" | 明确API语义（搜索建议） |
| "popular" | "hot-spots" | 统一热门景点术语 |

---

## 命名规范速查（3分钟）

### 各层命名风格

| 层级 | 风格 | 示例 | 工具辅助 |
|------|------|------|---------|
| **数据库字段** | `snake_case` | `poi_id`, `short_name` | MyBatis自动映射 |
| **Java字段** | `camelCase` | `poiId`, `shortName` | IDE自动提示 |
| **Java类名** | `PascalCase` | `LocationService`, `HotSpot` | 标准Java规范 |
| **API字段** | `snake_case` | `poi_id`, `hot_spots` | 与数据库一致 |
| **前端JS变量** | `camelCase` | `poiId`, `hotSpots` | 标准JS规范 |
| **组件名** | `kebab-case` | `location-picker` | 小程序规范 |

### LocationValue标准格式（必须严格遵守）

```javascript
{
  name: "莫干山风景名胜区",         // ✅ 使用name（而非poi_name）
  address: "浙江省湖州市德清县",    // ✅ 完整地址
  location: {                       // ✅ 嵌套对象
    longitude: 119.912722,          // ✅ 完整单词
    latitude: 30.562778
  },
  poi_id: "B000A7BD6C",            // ✅ snake_case
  poi_type: "scenic"                // ✅ snake_case
}
```

### API接口命名规范

| 接口 | 路径 | 方法名 | 参数名 | 响应字段 |
|------|------|--------|--------|---------|
| 搜索建议 | `/locations/suggest` | `suggest` | `keyword` | `suggestions` |
| 热门景点 | `/locations/hot-spots` | `hotSpots` | `province` | `hot_spots` |
| 逆地理编码 | `/locations/reverse-geocode` | `reverseGeocode` | `longitude`/`latitude` | `formatted_address` |

**记忆口诀**：
- 路径用`/locations`（统一入口）
- 方法名直接体现功能（suggest, hotSpots, reverseGeocode）
- 参数名清晰明确（keyword而非q，province而非city）

---

## Code Review检查清单（5分钟）

### 必查项（每个PR都要核对）

**文件命名**：
- [ ] 组件目录：`components/location-picker/`（而非place-picker）
- [ ] Java类：`LocationService.java`, `LocationController.java`
- [ ] 测试类：`LocationServiceTest.java`

**API契约**：
- [ ] 接口路径：`/api/v1/locations/suggest`（而非/places/search）
- [ ] 请求参数：`keyword`, `type`, `province`, `limit`
- [ ] 响应字段：`suggestions`, `hot_spots`（snake_case）

**数据结构**：
- [ ] 数据库表名：`hot_destinations`
- [ ] 字段命名：`poi_id`, `poi_name`, `short_name`, `latitude`, `longitude`
- [ ] LocationValue格式：包含`name`, `address`, `location`

**代码变量**：
- [ ] Java：`List<PoiSuggestion> suggestions`（而非results）
- [ ] Java：`List<HotSpot> hotSpots`（而非popularSpots）
- [ ] 前端：`this.data.suggestions`（而非results）
- [ ] 前端：`this.data.hotSpots`（而非popularPlaces）

**UI文案**：
- [ ] 标签：使用"出发地点"、"目的地景点"
- [ ] 占位符：使用"请输入出发地点（景点/地标/酒店）"
- [ ] 区域标题：使用"最近使用"、"热门景点"、"搜索结果"

**注释规范**：
- [ ] Java注释使用完整术语（如"搜索地点建议"）
- [ ] 前端注释标明映射关系（如`// LocationValue对象`）
- [ ] 避免中英混用（如"搜索location"）

**日志规范**：
- [ ] 使用统一格式：`log.info("POI搜索: keyword={}, ...", ...)`
- [ ] 模块标识：前端用`[LocationPicker]`，后端用类名
- [ ] 避免缩写和口语化

---

## 常见错误示例（帮助记忆）

### ❌ 错误示例1：术语不统一
```java
// ❌ 错误
public List<PlaceResult> searchPlaces(String query) {
  List<Location> popular = getPopularLocations();
  return results;
}

// ✅ 正确
public List<PoiSuggestion> suggest(String keyword) {
  List<HotSpot> hotSpots = getHotSpots();
  return suggestions;
}
```

### ❌ 错误示例2：命名风格混乱
```javascript
// ❌ 错误（API字段混用camelCase）
{
  poiId: "B000A7BD6C",        // 应该是poi_id
  hotSpots: [...]             // 应该是hot_spots
}

// ✅ 正确（API统一snake_case）
{
  poi_id: "B000A7BD6C",
  hot_spots: [...]
}
```

### ❌ 错误示例3：LocationValue格式错误
```javascript
// ❌ 错误（字段名不规范）
{
  poi_name: "莫干山",         // 应该是name
  full_address: "浙江省...",  // 应该是address
  lng: 119.91,                // 应该是longitude
  lat: 30.56,                 // 应该是latitude
  type: "scenic"              // 应该是poi_type
}

// ✅ 正确
{
  name: "莫干山风景名胜区",
  address: "浙江省湖州市德清县",
  location: {
    longitude: 119.912722,
    latitude: 30.562778
  },
  poi_type: "scenic"
}
```

### ❌ 错误示例4：UI文案不规范
```xml
<!-- ❌ 错误 -->
<view class="label">出发城市</view>        <!-- 应该是"出发地点" -->
<input placeholder="请输入位置" />          <!-- 应该是"请输入出发地点（景点/地标/酒店）" -->
<view class="title">历史记录</view>        <!-- 应该是"最近使用" -->

<!-- ✅ 正确 -->
<view class="label">出发地点</view>
<input placeholder="请输入出发地点（景点/地标/酒店）" />
<view class="title">最近使用</view>
```

---

## 评审要点讨论（5分钟）

### 讨论点1：为什么用"地点"而非"位置"？

**答**：
- "地点"更符合业务语境（旅游目的地、团建地点）
- "位置"更偏向坐标概念（GPS位置、地图位置）
- 微信API使用"位置"是框架规范，保持不变
- 业务代码统一用"地点"，技术层可灵活

### 讨论点2：为什么用"suggest"而非"search"？

**答**：
- "suggest"明确语义：提供搜索建议（类似Google搜索框）
- "search"太宽泛：不明确是全文搜索还是自动补全
- 前端变量也用`suggestions`（而非results），保持一致

### 讨论点3：为什么经纬度用完整单词？

**答**：
- 提升代码可读性（新人无需猜测lng是什么）
- 避免歧义（lng可能被误解为language）
- 虽然高德API用缩写，但我们内部代码用完整形式
- 性能影响可忽略（字段名长度不影响性能）

### 讨论点4：LocationValue格式为何这样设计？

**答**：
- `name`: 用户看到的显示名（必需）
- `address`: 完整地址（用于展示和提取省市区，必需）
- `location`: 精确坐标（可选，用于地图和距离计算）
- `poi_id`: 高德ID（可选，用于获取POI详情）
- `poi_type`: 类型（可选，用于图标和筛选）

设计原则：必需字段最小化，可选字段支持渐进增强

---

## 执行计划（团队协作）

### Week 1: 术语学习（本周）
- [ ] 所有成员阅读术语表（`ubiquitous-language-glossary.md` v1.4）
- [ ] 前端成员重点关注：LocationValue格式、UI文案规范
- [ ] 后端成员重点关注：API命名、数据库字段、日志规范
- [ ] 产品成员重点关注：业务术语定义、UI文案

### Week 2-3: 开发阶段
- [ ] PR Review时严格检查术语（使用checklist）
- [ ] 发现不规范术语时，及时指出并修正
- [ ] 新增的注释/文档都使用统一术语

### Week 4: 上线前复查
- [ ] 全量代码术语检查（运行检查脚本）
- [ ] 用户界面文案终审（产品负责）
- [ ] API文档终审（技术负责）

---

## 术语检查工具（辅助）

### 自动化检查脚本（建议）

**检查数据库字段命名**：
```bash
# 检查是否有不规范的字段名（如location_name而非poi_name）
grep -r "location_name\|place_name\|poi_title" apps/teamventure/src/database/

# 检查是否有lat/lng缩写
grep -r "\blat\b|\blng\b" apps/teamventure/src/backend/ --include="*.java"
```

**检查Java类命名**：
```bash
# 检查是否有Place相关的类名
find apps/teamventure/src/backend/ -name "*Place*.java"

# 检查是否有不规范的Service/Controller
find apps/teamventure/src/backend/ -name "*PoiService*.java" -o -name "*PlaceController*.java"
```

**检查前端UI文案**：
```bash
# 检查是否有不规范的占位符
grep -r "请输入位置\|输入地方\|搜索地点" apps/teamventure/src/frontend/miniapp/pages/ --include="*.wxml"

# 检查是否有不规范的标签文案
grep -r "出发城市\|起点\|终点" apps/teamventure/src/frontend/miniapp/pages/ --include="*.wxml"
```

### Code Review辅助清单（打印使用）

**前端PR Review**：
```
□ 组件命名：location-picker（而非place-picker）
□ 变量命名：suggestions, hotSpots, recentLocations
□ UI文案：出发地点、目的地景点、最近使用、热门景点
□ 占位符：规范完整（见文档）
□ LocationValue格式：严格符合标准
□ 注释清晰：标明字段映射关系
```

**后端PR Review**：
```
□ 类命名：LocationService, LocationController（而非PlaceService）
□ 方法命名：suggest(), hotSpots()（而非search(), getPopular()）
□ 字段命名：snake_case，POI字段有poi_前缀
□ API路径：/api/v1/locations/...
□ 响应字段：suggestions, hot_spots（snake_case）
□ 日志规范：使用统一格式和术语
□ 注释完整：方法注释说明参数和返回值
```

**数据库PR Review**：
```
□ 表名：hot_destinations
□ 字段：poi_id, poi_name, short_name（而非name/title）
□ 坐标字段：latitude, longitude（完整单词）
□ 索引命名：idx_province, idx_popularity
□ 迁移脚本：符合版本号规范（V1.1.0__description.sql）
```

---

## 团队同步会议议程（15分钟）

### 议程1：背景介绍（3分钟）
- 为什么要做LocationPicker模块？
- 为什么需要术语统一？
- 术语不统一的真实案例分享

### 议程2：核心术语讲解（5分钟）
- 10个必须记住的术语（见速记卡）
- LocationValue标准格式演示
- 命名风格速查表讲解

### 议程3：规范演示（5分钟）
- 正确示例演示（代码、文案、API）
- 错误示例纠正（常见错误）
- Code Review检查清单使用说明

### 议程4：答疑与确认（2分钟）
- 团队成员提问
- 确认大家理解规范
- 确认Code Review流程

---

## 快速参考资源

### 必读文档
1. **术语表（必读）**: `docs/design/ubiquitous-language-glossary.md` v1.4
   - Section 3.2：地点选择与POI核心术语
   - Section 6：反模式与禁用术语

2. **API设计（必读）**: `docs/design/api-design.md` v1.6
   - Section 4：Location API详细定义

3. **审计报告（选读）**: `docs/design/location-picker-terminology-audit.md`
   - 现有代码术语使用情况分析
   - 兼容性策略说明

### 在线查询
- **术语速查**：在术语表中搜索（Ctrl+F）
- **命名示例**：参考`components/stepper/stepper.js`组件模式
- **API示例**：参考`PlanController.java`现有接口

### 问题反馈
- 发现不规范术语：在PR Review中指出
- 术语定义有歧义：在团队群讨论并更新文档
- 建议新术语：提交Issue或在周会讨论

---

## 评审通过标准

### 团队成员
- [ ] 所有成员已阅读术语表v1.4
- [ ] 所有成员已阅读API设计v1.6第4章
- [ ] 所有成员理解LocationValue标准格式
- [ ] 前端成员理解UI文案规范
- [ ] 后端成员理解API命名规范
- [ ] 测试成员理解术语对照表（用于测试用例命名）

### 文档
- [ ] 术语表v1.4已更新
- [ ] API设计v1.6已更新
- [ ] 审计报告已创建
- [ ] 评审指南已创建（本文档）

### 流程
- [ ] Code Review检查清单已打印/分享
- [ ] 自动化检查脚本已准备（可选）
- [ ] 团队同步会议已安排

---

## 后续行动

**立即行动**（本周内）：
1. 所有成员阅读核心文档（术语表v1.4 + API设计v1.6第4章）
2. 前端/后端Lead在团队群发布术语规范公告
3. 在项目Wiki或Notion创建快速参考页

**持续行动**（开发期间）：
1. 每个PR Review时使用检查清单
2. 发现问题及时在群里讨论和纠正
3. 每周复盘：术语规范执行情况

**长期行动**（上线后）：
1. 新人入职时必读术语表
2. 每季度review术语表，更新版本
3. 考虑引入自动化lint工具（检查命名规范）

---

## 附录：术语表核心摘录（快速查阅）

### LocationPicker核心术语（Top 10）

1. **地点 (Location)** - 泛指任何地理位置
2. **景点/POI (Attraction/POI)** - 旅游目的地
3. **出发地点 (Departure)** - 团建出发位置
4. **目的地点 (Destination)** - 团建目标位置
5. **搜索建议 (Suggestion)** - 搜索返回的候选列表
6. **热门景点 (Hot Spot)** - 高热度推荐目的地
7. **最近使用 (Recent Location)** - 历史选择地点
8. **LocationValue** - 标准地点数据对象
9. **经度/纬度 (longitude/latitude)** - 完整单词（不缩写）
10. **地理编码 (Geocoding)** - 地址↔坐标转换

### 命名风格速查

- 数据库：`snake_case` (poi_id)
- Java：`camelCase` (poiId) + `PascalCase` (类名)
- API：`snake_case` (poi_id)
- 前端：`camelCase` (poiId)
- 组件：`kebab-case` (location-picker)

### 禁用术语 Top 5

1. ❌ "位置" → ✅ "地点"
2. ❌ "place" → ✅ "location"
3. ❌ "search" (接口名) → ✅ "suggest"
4. ❌ "results" (变量名) → ✅ "suggestions"
5. ❌ "popular" → ✅ "hot-spots"

---

**评审通过标准**: 团队所有成员签字确认已理解术语规范，并承诺在开发中遵循。

**签字区**（团队会议后填写）：
- 前端负责人：______  日期：______
- 后端负责人：______  日期：______
- 产品负责人：______  日期：______
- 测试负责人：______  日期：______
