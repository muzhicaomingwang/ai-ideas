# TeamVenture 领域统一语言词汇表 (Ubiquitous Language Glossary)

**创建日期**: 2026-01-06
**版本**: v1.5
**目的**: 确保全链路字段命名一致性，消除"翻译损耗"

**最新更新**: 新增地图服务（MapService）模块术语定义（v1.5）

---

## 1. 核心原则

> DDD 核心原则：团队使用统一的术语，从业务讨论、代码命名到文档表述保持一致，避免"翻译损耗"。

**命名规范**:
- **数据库字段**: `snake_case` (例: `departure_city`)
- **Java 字段**: `snake_case` (与数据库保持一致，MyBatis-Plus 自动映射)
- **API 字段**: `snake_case` (例: `departure_city`)
- **前端 JS 变量**: `camelCase` (例: `departureLocation`)，需显式注释映射关系

---

## 2. 核心实体字段定义

### 2.1 用户与会话 (Identity Domain)

| 中文术语 | 英文术语 | 数据库字段 | Java字段 | API字段 | 前端字段 | 说明 |
|---------|---------|-----------|----------|--------|---------|------|
| 用户ID | User ID | `user_id` | `userId` | `user_id` | `userId` | 前缀 `user_`，ULID格式 |
| 微信OpenID | WeChat OpenID | `wechat_openid` | `wechatOpenid` | `openid` | - | 不暴露给前端 |
| 昵称 | Nickname | `nickname` | `nickname` | `nickname` | `nickname` | |
| 头像URL | Avatar URL | `avatar_url` | `avatarUrl` | `avatar` | `avatarUrl` | API简化为avatar |
| 头像占位符 | Avatar Placeholder | - | - | - | `avatarPlaceholder` | 未上传头像时显示emoji 👤 |
| 会话令牌 | Session Token | `session_token` | `sessionToken` | `sessionToken` | `token` | JWT格式 |
| 登录状态 | Login Status | - | - | - | `isLogin` | Boolean，全局状态 |
| 用户信息 | User Info | - | `UserInfo` | `userInfo` | `userInfo` | 聚合对象（userId+nickname+avatar等） |

### 2.2 方案请求 (Plan Request)

| 中文术语 | 英文术语 | 数据库字段 | Java字段 | API字段 | 前端字段 | 说明 |
|---------|---------|-----------|----------|--------|---------|------|
| 方案请求ID | Plan Request ID | `plan_request_id` | `planRequestId` | `plan_request_id` | `planRequestId` | 前缀 `plan_req_` |
| 参与人数 | People Count | `people_count` | `peopleCount` | `people_count` | `peopleCount` | 正整数 |
| 最低预算 | Budget Min | `budget_min` | `budgetMin` | `budget_min` | `budgetMin` | 单位：元 |
| 最高预算 | Budget Max | `budget_max` | `budgetMax` | `budget_max` | `budgetMax` | 单位：元 |
| 开始日期 | Start Date | `start_date` | `startDate` | `start_date` | `startDate` | YYYY-MM-DD |
| 结束日期 | End Date | `end_date` | `endDate` | `end_date` | `endDate` | YYYY-MM-DD |
| **出发城市** | **Departure City** | `departure_city` | `departureCity` | `departure_city` | `departureLocation` | ⚠️ 前端字段名不同，需映射 |
| **目的地** | **Destination** | `destination` | `destination` | `destination` | `destination` | 团建活动举办地点 |
| **目的地城市** | **Destination City** | `destination_city` | `destinationCity` | `destination_city` | - | 目的地所属行政城市（用于季节/价格配置） |
| 偏好设置 | Preferences | `preferences` | `preferencesJson` | `preferences` | `preferences` | JSON对象 |
| 请求状态 | Status | `status` | `status` | `status` | `status` | CREATING/GENERATING/COMPLETED/FAILED |

#### 2.2.1 偏好设置字段 (Preferences)

| 中文术语 | API字段（统一） | 常见误用/旧字段 | 说明 |
|---------|----------------|----------------|------|
| 活动类型 | `activity_types` | `activityTypes` | 数组，多选 |
| 住宿标准 | `accommodation_level` | `accommodation` | 单选：budget/standard/premium |
| 特殊需求 | `special_requirements` | - | 字符串（可为空） |

### 2.3 方案 (Plan)

| 中文术语 | 英文术语 | 数据库字段 | Java字段 | API字段 | 前端字段 | 说明 |
|---------|---------|-----------|----------|--------|---------|------|
| 方案ID | Plan ID | `plan_id` | `planId` | `plan_id` | `planId` | 前缀 `plan_` |
| **方案名称** | **Plan Name** | `plan_name` | `planName` | `plan_name` | `planName` | ✅ 统一使用 plan_name |
| 方案类型 | Plan Type | `plan_type` | `planType` | `plan_type` | `planType` | budget/standard/premium |
| 方案摘要 | Summary | `summary` | `summary` | `summary` | `summary` | |
| 亮点 | Highlights | `highlights` | `highlights` | `highlights` | `highlights` | JSON数组 |
| 行程安排 | Itinerary | `itinerary` | `itinerary` | `itinerary` | `itinerary` | JSON对象 |
| 预算明细（非MVP） | Budget Breakdown | `budget_breakdown` | `budgetBreakdown` | `budget_breakdown` | - | DB 保留字段，MVP 不对外输出 |
| **供应商快照（非MVP）** | **Supplier Snapshots** | `supplier_snapshots` | `supplierSnapshots` | `supplier_snapshots` | - | DB 保留字段，MVP 不对外输出 |
| 总预算 | Budget Total | `budget_total` | `budgetTotal` | `budget_total` | `budgetTotal` | 冗余字段 |
| 人均预算 | Budget Per Person | `budget_per_person` | `budgetPerPerson` | `budget_per_person` | `budgetPerPerson` | 冗余字段 |
| 天数 | Duration Days | `duration_days` | `durationDays` | `duration_days` | `durationDays` | |
| **出发城市** | **Departure City** | `departure_city` | `departureCity` | `departure_city` | `departureCity` | 从请求继承 |
| **目的地** | **Destination** | `destination` | `destination` | `destination` | `destination` | 从请求继承 |
| **目的地城市** | **Destination City** | `destination_city` | `destinationCity` | `destination_city` | - | 从请求继承/可由地图补全 |
| **评价数** | **Review Count** | `review_count` | `reviewCount` | `review_count` | - | 通晒后反馈收集 |
| **平均分** | **Average Score** | `average_score` | `averageScore` | `average_score` | - | 通晒后反馈收集（0-5，可为空） |
| 方案状态 | Status | `status` | `status` | `status` | `status` | draft/confirmed |
| 确认时间 | Confirmed Time | `confirmed_time` | `confirmedTime` | `confirmed_time` | `confirmedTime` | |
| 创建时间 | Created At | `create_time` | `createTime` | `created_at` | `created_at` | API 统一 `created_at`（前端列表使用） |

### 2.4 供应商 (Supplier, 非MVP)

| 中文术语 | 英文术语 | 数据库字段 | Java字段 | API字段 | 前端字段 | 说明 |
|---------|---------|-----------|----------|--------|---------|------|
| 供应商ID | Supplier ID | `supplier_id` | `supplierId` | `supplier_id` | `supplierId` | 前缀 `sup_` |
| 供应商名称 | Name | `name` | `name` | `name` | `name` | |
| 品类 | Category | `category` | `category` | `category` | `category` | accommodation/dining/activity/transportation |
| 城市 | City | `city` | `city` | `city` | `city` | |
| 联系电话 | Contact Phone | `contact_phone` | `contactPhone` | `contact_phone` | `contactPhone` | |
| 联系微信 | Contact WeChat | `contact_wechat` | `contactWechat` | `contact_wechat` | `contactWechat` | |
| 价格区间(低) | Price Min | `price_min` | `priceMin` | `price_min` | `priceMin` | |
| 价格区间(高) | Price Max | `price_max` | `priceMax` | `price_max` | `priceMax` | |
| 评分 | Rating | `rating` | `rating` | `rating` | `rating` | 0-5 |

---

## 3. 关键字段语义详解

### 3.1 出发城市与目的地

| 字段 | 中文名 | 语义说明 | 示例值 | 使用场景 |
|------|--------|----------|--------|----------|
| `departure_city` | 出发城市 | 团队从哪里出发，通常是公司所在城市 | 上海市 | 行程规划起点、交通费用计算 |
| `destination` | 目的地 | 团建活动举办地点（可视为“目的地聚合”的展示名） | 千岛湖洲际酒店 | 行程安排、POI推荐 |
| `destination_city` | 目的地城市 | 目的地所属行政城市（季节/价格配置维度） | 杭州 | 季节配置、住宿/交通参考价 |

**前端显示格式**: `{departure_city} → {destination}`
**示例**: 上海市 → 杭州千岛湖

**前端字段映射**:
```javascript
// pages/index/index.js
formData.departureLocation  →  API: departure_city  // 出发城市
formData.destination        →  API: destination     // 目的地
```

### 3.2 地点选择与POI (Location Selection & POI) ⭐ v1.4新增

#### 3.2.1 核心术语定义

| 中文术语 | 英文术语 | 代码标识 | 说明 | ❌ 避免使用 |
|---------|---------|---------|------|-----------|
| **地点** | **Location** | `Location` | 泛指任何地理位置（城市/景点/地标/酒店等） | 位置、地方 |
| **景点** | **Attraction/POI** | `POI` | 旅游目的地（风景区、主题公园、名胜古迹） | 地标、场所、兴趣点 |
| **POI** | **Point of Interest** | `POI` | 兴趣点（高德地图标准术语），包括景点/酒店/地标/商圈等 | 位置点、地点 |
| **出发地点** | **Departure Location** | `departure` | 团建活动的出发位置（细化到景点/地标维度） | 出发城市、起点 |
| **目的地点** | **Destination Location** | `destination` | 团建活动的目标位置（细化到景点/地标维度） | 目的城市、终点 |
| **地点值** | **LocationValue** | `LocationValue` | 包含name/address/location的完整数据对象 | 地点对象、位置数据 |
| **搜索建议** | **Suggestion** | `suggestion` | 基于关键词返回的候选地点列表项 | 自动补全、搜索结果 |
| **热门景点** | **Hot Spot** | `hotSpot` | 高热度的推荐目的地 | 推荐景点、热门地点 |
| **最近使用** | **Recent Location** | `recentLocation` | 用户历史选择过的地点 | 历史地点、常用地点 |
| **地理编码** | **Geocoding** | `geocode` | 地址文本→经纬度坐标的转换 | 地址解析、坐标转换 |
| **逆地理编码** | **Reverse Geocoding** | `reverseGeocode` | 经纬度坐标→地址文本的转换 | 反向解析、坐标转地址 |

#### 3.2.2 LocationValue 数据结构（标准格式）

**定义**：LocationValue 是地点选择的统一数据格式，用于前后端传递地点信息。

```typescript
interface LocationValue {
  name: string;              // 地点名称，如"莫干山风景名胜区"
  address: string;           // 完整地址，如"浙江省湖州市德清县"
  location?: {               // 经纬度（可选）
    longitude: number;       // 经度（GCJ-02坐标系，高德/微信）
    latitude: number;        // 纬度（GCJ-02坐标系）
  };
  poi_id?: string;          // 高德POI ID（可选），如"B000A7BD6C"
  poi_type?: string;        // POI类型（可选）：scenic/hotel/activity/district
}
```

**示例值**：
```javascript
{
  name: "莫干山风景名胜区",
  address: "浙江省湖州市德清县",
  location: {
    longitude: 119.912722,
    latitude: 30.562778
  },
  poi_id: "B000A7BD6C",
  poi_type: "scenic"
}
```

**使用场景**：
- 前端：LocationPicker组件的props.value和events.change
- 前端：formData.location.regional.departure/destination
- 后端：可选，用于接收前端传来的经纬度信息

#### 3.2.3 POI类型枚举

| POI类型值 | 中文名 | 说明 | 图标建议 |
|----------|--------|------|---------|
| `scenic` | 景点 | 风景区、名胜古迹、主题公园 | 📍 |
| `hotel` | 酒店 | 住宿场所（度假村、民宿、酒店） | 🏨 |
| `activity` | 活动场所 | 团建活动场地（拓展基地、会议中心） | 🎯 |
| `district` | 行政区 | 区县级行政区划 | 📌 |
| `landmark` | 地标 | 地标性建筑、广场、车站 | 🏛️ |
| `current` | 当前位置 | 用户当前所在位置（通过wx.getLocation获取） | 📍 |
| `map_selected` | 地图选点 | 用户通过地图手动选择的位置 | 🗺️ |

#### 3.2.4 数据库表设计

**表名**: `hot_destinations` （热门目的地表）

| 数据库字段 | Java字段 | API字段 | 类型 | 说明 |
|-----------|---------|--------|------|------|
| `province_code` | `provinceCode` | `province_code` | VARCHAR(10) | 省份代码（如"330000"） |
| `province_name` | `provinceName` | `province_name` | VARCHAR(50) | 省份名称（如"浙江省"） |
| `city_name` | `cityName` | `city_name` | VARCHAR(50) | 城市名称（如"湖州市"） |
| `poi_id` | `poiId` | `poi_id` | VARCHAR(50) | 高德POI ID |
| `poi_name` | `poiName` | `poi_name` | VARCHAR(100) | POI全名 |
| `short_name` | `shortName` | `short_name` | VARCHAR(50) | POI简称（用于标签显示） |
| `poi_type` | `poiType` | `poi_type` | VARCHAR(20) | POI类型（见枚举） |
| `latitude` | `latitude` | `latitude` | DECIMAL(10,6) | 纬度 |
| `longitude` | `longitude` | `longitude` | DECIMAL(10,6) | 经度 |
| `popularity` | `popularity` | `popularity` | INT | 热度值（用于排序，0-100） |

**注意**：
- 经纬度字段使用完整单词`latitude`/`longitude`（而非缩写`lat`/`lng`）
- POI相关字段统一使用`poi_`前缀

#### 3.2.5 API接口命名

| 接口路径 | 方法 | 用途 | 术语说明 |
|---------|------|------|---------|
| `/api/v1/locations/suggest` | GET | 搜索地点建议 | 使用`suggest`（而非`search`/`autocomplete`） |
| `/api/v1/locations/hot-spots` | GET | 获取热门景点 | 使用`hot-spots`（而非`popular`/`recommended`） |
| `/api/v1/locations/reverse-geocode` | GET | 逆地理编码 | 标准GIS术语 |

**请求参数术语**：
- `keyword`: 搜索关键词（而非`query`/`search`/`q`）
- `type`: 地点类型（`departure`/`destination`，而非`location_type`）
- `province`: 省份名称（而非`province_name`）
- `limit`: 返回数量限制（而非`count`/`size`）

**响应字段术语**：
- `suggestions`: 搜索建议列表（而非`results`/`items`）
- `hot_spots`: 热门景点列表（而非`recommendations`/`popular_spots`）

#### 3.2.6 前端组件命名

| 组件名 | 用途 | Props术语 | Events术语 |
|--------|------|----------|-----------|
| `location-picker` | 地点选择组件 | `type`, `province`, `value`, `placeholder` | `change` |
| ❌ `place-picker` | - | - | 避免使用place |
| ❌ `poi-selector` | - | - | 避免使用selector |

**组件内部状态术语**：
```javascript
// ✅ 推荐
data: {
  keyword: '',              // 搜索关键词
  suggestions: [],          // 搜索建议列表
  hotSpots: [],            // 热门景点列表
  recentLocations: [],     // 最近使用地点列表
  showResults: false,      // 是否显示搜索结果
  loading: false           // 是否加载中
}

// ❌ 避免
data: {
  searchText: '',          // 使用keyword
  results: [],             // 使用suggestions
  popularPlaces: [],       // 使用hotSpots
  history: [],             // 使用recentLocations
  isResultsVisible: false  // 使用showResults
}
```

#### 3.2.7 用户界面文案规范

**标签文本**：
| 场景 | 统一文案 | ❌ 避免使用 |
|------|---------|-----------|
| 出发地标签 | "出发地点" | "出发城市"、"起点" |
| 目的地标签 | "目的地景点" | "目的地"、"终点"、"目标地点" |
| 搜索框占位符（出发地） | "请输入出发地点（景点/地标/酒店）" | "请输入位置"、"搜索出发地" |
| 搜索框占位符（目的地） | "搜索景点、酒店或地标" | "请输入目的地"、"搜索位置" |
| 当前位置按钮 | "我的位置" | "当前位置"、"获取定位" |
| 地图选点按钮 | "在地图上选" | "地图选择"、"打开地图" |
| 最近使用区域标题 | "最近使用" | "历史记录"、"最近选择" |
| 热门景点区域标题 | "热门景点" | "推荐地点"、"热门目的地" |
| 无搜索结果提示 | "无搜索结果，试试热门景点" | "未找到"、"暂无数据" |

**错误提示文案**：
| 场景 | 统一文案 | ❌ 避免使用 |
|------|---------|-----------|
| 搜索失败 | "搜索失败，请稍后重试" | "网络错误"、"加载失败" |
| 定位权限拒绝 | "需要定位权限才能使用此功能" | "无法获取位置"、"授权失败" |
| 必填验证 | "请选择出发地点" / "请选择目的地景点" | "出发地不能为空"、"请输入目的地" |

#### 3.2.8 代码注释规范

**Java注释**：
```java
// ✅ 推荐
/**
 * 搜索地点建议（POI搜索自动补全）
 * 策略：优先查询本地hot_destinations表，不足时调用高德API补充
 *
 * @param keyword 搜索关键词（至少2个字符）
 * @param type 地点类型：departure（出发地）或destination（目的地）
 * @param province 省份名称（可选，用于限定搜索范围）
 * @param limit 返回数量限制（默认10）
 * @return 搜索建议列表
 */
public SuggestionResponse suggest(String keyword, String type, String province, int limit)

// ❌ 避免
/**
 * 搜索位置推荐
 * @param query 查询文本
 * @param locationType 位置类型
 */
```

**JavaScript注释**：
```javascript
// ✅ 推荐
/**
 * 处理地点选择变更
 * @param {Event} e - 微信事件对象
 * @param {LocationValue} e.detail.value - 选中的地点值
 */
handleRegionalDepartureChange(e) {}

// 从地址文本中提取城市名
// 示例: "浙江省湖州市德清县" → "湖州市"
extractCityName(address) {}

// ❌ 避免
// 处理位置改变
// 提取城市
```

#### 3.2.9 日志输出规范

**统一日志格式**：
```java
// ✅ 推荐
log.info("POI搜索: keyword={}, type={}, province={}, resultCount={}, costMs={}",
  keyword, type, province, suggestions.size(), costMs);

log.info("热门景点加载: province={}, limit={}, resultCount={}",
  province, limit, hotSpots.size());

log.warn("高德API失败，降级到静态表: keyword={}, error={}",
  keyword, e.getMessage());

log.debug("Redis缓存命中: key={}, ttl={}s",
  cacheKey, ttl);

// ❌ 避免
log.info("地点查询: ...");           // 使用"POI搜索"
log.info("推荐位置加载: ...");        // 使用"热门景点加载"
log.warn("API调用失败: ...");        // 明确指出"高德API失败"
```

#### 3.2.10 高德地图API术语映射

| 高德API术语 | 我们的术语 | 说明 |
|-----------|-----------|------|
| `pois` | `suggestions` | 搜索结果列表 |
| `location` (字符串) | `longitude,latitude` | 高德返回"经度,纬度"字符串，我们拆分为两个字段 |
| `adcode` | `province_code` / `city_code` | 行政区划代码 |
| `name` | `poi_name` | POI名称 |
| `address` | `address` | 详细地址 |
| `typecode` | `poi_type` | 类型代码（需转换为我们的枚举） |

**坐标系说明**：
- 高德地图使用**GCJ-02坐标系**（国测局坐标）
- 微信小程序`wx.getLocation({type: 'gcj02'})`也返回GCJ-02坐标
- 统一使用GCJ-02，无需坐标转换

### 3.4 方案类型 (Plan Type)

| 类型值 | 中文名 | 核心价值主张 | 定位说明 | 预算占比 |
|--------|--------|-------------|----------|----------|
| `budget` | 经济型 | 极致性价比，确保核心体验 | 最低预算方案，满足基本需求 | ≈ budget_min |
| `standard` | 平衡型 | 平衡之选，兼顾舒适与趣味 | 性价比方案，推荐选择 | ≈ (budget_min + budget_max) / 2 |
| `premium` | 品质型 | 尊享体验，打造团队高光时刻 | 最高预算方案，追求体验 | ≈ budget_max |

### 3.5 方案状态 (Plan Status)

| 状态值 | 中文名 | 说明 | 后续动作 |
|--------|--------|------|----------|
| `generating` | 生成中 | AI正在生成方案 | 等待完成 |
| `failed` | 生成失败 | AI生成过程出错 | 重新生成 |
| `draft` | 制定完成 | 方案已生成，待用户通晒 | 可通晒、可删除 |
| `reviewing` | 通晒中 | 方案已提交通晒，团队审阅中 | 可确认、可撤回 |
| `confirmed` | 已确认 | 用户已采纳此方案 | 纳入北极星指标、可归档 |
| `archived` | 已归档 | 方案已归档，不再展示 | 可恢复 |

**状态流转图**:
```
generating → failed (生成出错)
generating → draft (生成完成)
draft → reviewing (通晒此方案)
reviewing → draft (撤回通晒)
reviewing → confirmed (确认此方案)
confirmed → archived (归档)
```

### 3.6 请求状态 (Request Status)

| 状态值 | 中文名 | 说明 |
|--------|--------|------|
| `CREATING` | 创建中 | 请求刚创建 |
| `GENERATING` | 生成中 | AI正在生成方案 |
| `COMPLETED` | 已完成 | 3套方案已生成 |
| `FAILED` | 失败 | 生成过程出错 |

### 3.7 地图服务 (Map Service) ⭐ v1.5新增

#### 3.7.1 核心术语定义

| 中文术语 | 英文术语 | 代码标识 | 说明 | ❌ 避免使用 |
|---------|---------|---------|------|-----------|
| **标注** | **Marker** | `marker` | 地图上的标记点（如起点/终点/途经点） | 标记、图钉、pin |
| **路径** | **Path** | `path` / `polyline` | 连接多个坐标点的线条（表示行程路线） | 线路、轨迹、路线线条 |
| **折线** | **Polyline** | `polyline` | 由多个坐标点组成的折线（高德API术语） | 路径点列表、坐标串 |
| **缩放级别** | **Zoom Level** | `zoom` | 地图显示精度（3-18，数字越大越详细） | 缩放比例、zoom比例 |
| **地图尺寸** | **Map Size** | `size` | 静态地图图片的宽高（如750x520） | 图片大小、地图大小 |
| **静态地图** | **Static Map** | `staticMap` | 服务端生成的地图图片URL（用于展示） | 地图图片、地图快照 |
| **交互地图** | **Interactive Map** | `interactiveMap` | 小程序原生地图组件（用户可操作） | 动态地图、可交互地图 |
| **降级策略** | **Degradation** | `degradation` | API失败时的兜底方案（简化→占位图） | 回退、fallback、备选方案 |
| **占位图** | **Placeholder** | `placeholder` | API完全失败时显示的默认图片 | 默认图、兜底图 |
| **缓存键** | **Cache Key** | `cacheKey` | 基于请求参数生成的MD5哈希（32字符） | 缓存ID、key |

#### 3.7.2 标注类型枚举

| 标注类型 | 中文名 | 样式参数 | 说明 |
|---------|--------|---------|------|
| `START` | 起点 | 绿色大标，标签"S" | 行程的第一个地点 |
| `END` | 终点 | 红色大标，标签"E" | 行程的最后一个地点 |
| `WAYPOINT` | 途经点 | 蓝色中标，无标签 | 起终点之间的中间地点 |
| `SUPPLIER` | 供应商地点 | 橙色小标，标签"$" | 供应商POI（非MVP） |

#### 3.7.3 路径样式枚举（按交通方式）

| 交通方式 | 英文术语 | 路径样式 | 说明 |
|---------|---------|---------|------|
| 驾车 | `driving` | 蓝色粗线（宽度6，透明度1.0） | 自驾或包车路线 |
| 步行 | `walking` | 绿色中线（宽度4，透明度0.8） | 景点间步行路线 |
| 骑行 | `cycling` | 橙色中线（宽度5，透明度0.9） | 骑行路线（非MVP） |
| 公交 | `transit` | 紫色中线（宽度5，透明度0.9） | 公共交通路线 |

#### 3.7.4 地图尺寸预设

| 预设名称 | 英文标识 | 尺寸（宽x高） | 使用场景 |
|---------|---------|-------------|----------|
| 详情页主地图 | `DETAIL` | 750x520 | 方案详情页展示完整路线 |
| 列表缩略图 | `THUMBNAIL` | 375x200 | 方案列表页快速预览 |
| 分享图 | `SHARE` | 1200x800 | 社交媒体分享（适配微信朋友圈） |
| 供应商地点图 | `SUPPLIER` | 600x400 | 供应商详情页（非MVP） |

#### 3.7.5 缩放级别映射

| Zoom级别 | 跨度范围 | 视图类型 | 典型场景 |
|---------|---------|---------|----------|
| 3 | >5度（>500km） | 全球/跨省 | 北京→上海、上海→广州 |
| 8 | 1-5度（100-500km） | 省级/跨市 | 杭州→宁波 |
| 12 | 0.1-1度（10-100km） | 城市 | 杭州市内跨区 |
| 15 | 0.01-0.1度（1-10km） | 街区 | 西湖周边景点 |
| 17 | <0.01度（<1km） | 建筑 | 相邻建筑物 |

#### 3.7.6 降级策略层级

| 降级级别 | 策略名称 | 触发条件 | 应对措施 |
|---------|---------|---------|----------|
| Level 1 | 重试 | API超时/限流 | 指数退避重试（1s→2s→4s，最多3次） |
| Level 2 | 简化地图 | 重试失败 | 降低zoom、缩小尺寸、移除路径、改用JPEG |
| Level 3 | 占位图 | 简化失败 | 返回CDN占位图URL |
| Level 4 | 熔断器 | 持续失败 | 熔断器打开，快速失败，不调用API |

#### 3.7.7 缓存架构

| 缓存层级 | 存储介质 | 容量 | TTL | 用途 |
|---------|---------|------|-----|------|
| L1 | Caffeine内存 | 1000条 | 7天 | 快速访问（<10ms） |
| L2 | Redis | 无限制 | 30天 | 跨实例共享 |
| L3 | MySQL | 无限制 | 永久 | 防缓存穿透、热度统计 |

#### 3.7.8 数据库表设计

**表名**: `static_map_url_cache` （静态地图URL缓存表）

| 数据库字段 | Java字段 | 类型 | 说明 |
|-----------|---------|------|------|
| `cache_key` | `cacheKey` | VARCHAR(32) | MD5缓存键（UNIQUE） |
| `url` | `url` | TEXT | 静态地图URL |
| `request` | `request` | JSON | 原始请求参数（用于调试） |
| `hit_count` | `hitCount` | INT | 缓存命中次数（热度统计） |
| `created_at` | `createdAt` | TIMESTAMP | 创建时间 |
| `last_hit_at` | `lastHitAt` | TIMESTAMP | 最后命中时间 |

#### 3.7.9 API响应字段

**路线API响应结构** (`GET /api/v1/plans/{planId}/route?day={dayNum}`):

| API字段 | Java字段 | 类型 | 说明 |
|---------|---------|------|------|
| `markers` | `markers` | Array | 标注点列表（起点/终点/途经点） |
| `polyline` | `polyline` | Array | 折线数据（包含points数组和样式） |
| `include_points` | `includePoints` | Array | 路径细化点（高德API返回） |
| `segments` | `segments` | Array | 路线段详情（from/to/distance/duration/mode） |
| `summary` | `summary` | Object | 路线摘要（总距离/总时长） |
| `unresolved` | `unresolved` | Array | 未解析的地点名称 |
| `mapType` | `mapType` | String | 地图类型：static/interactive |
| `staticMapUrl` | `staticMapUrl` | String/null | 静态地图URL（跨市路线为null） |

#### 3.7.10 日志输出规范

**统一日志格式**：
```java
// ✅ 推荐
log.debug("L1 cache hit: {}", cacheKey);
log.debug("L2 cache hit: {}", cacheKey);
log.debug("L3 cache hit: {}", cacheKey);
log.info("Cache miss, generating new URL: {}", cacheKey);
log.warn("L1 memory cache cleared");
log.warn("Redis get failed: {}", e.getMessage());
log.error("Database save failed: {}", e.getMessage());

// ❌ 避免
log.info("内存缓存命中");              // 使用"L1 cache hit"明确层级
log.info("缓存未命中，调用API");       // 使用"Cache miss, generating new URL"
```

---

## 4. 命名一致性检查清单

### 4.1 ✅ 已统一的字段

| 字段 | 状态 | 说明 |
|------|------|------|
| `departure_city` | ✅ | 数据库/Java/Python/API 全链路一致 |
| `destination` | ✅ | 数据库/Java/Python/API 全链路一致 |
| `destination_city` | ✅ | 数据库/Java/Python/API 全链路一致（可选字段） |
| `plan_name` | ✅ | 数据库/Java/Python/API 全链路一致（非 title） |
| `supplier_snapshots` | ✅ | DB/Java/Python 一致（MVP 不对外输出） |
| `budget_breakdown` | ✅ | DB/Java/Python 一致（MVP 不对外输出） |
| `review_count` | ✅ | DB/Java/API 一致（通晒反馈指标） |
| `average_score` | ✅ | DB/Java/API 一致（通晒反馈指标） |

### 4.2 ⚠️ 需注意的映射

| 前端字段 | API字段 | 说明 |
|----------|---------|------|
| `departureLocation` | `departure_city` | 前端变量名保留，UI文案统一为“出发城市” |
| `create_time` | `created_at` | DB字段为 `create_time`，API 列表统一输出 `created_at` |
| `accommodation` | `preferences.accommodation_level` | 旧字段名，需迁移/兼容 |

### 4.3 📋 跨团队术语映射

| 产品/业务术语 | 技术术语 | 数据库字段 | API字段 | 前端展示 |
|-------------|---------|-----------|---------|---------|
| 团建方案 | Plan | `plans` 表 | `plan` | "方案" |
| 方案类型（经济/平衡/品质） | PlanType | `plan_type` | `plan_type` | "经济型"/"平衡型"/"品质型" |
| **通晒方案** | **SubmitReview** | `status='reviewing'` | `PUT /plans/{id}/submit-review` | **"通晒此方案"** |
| 确认方案 | ConfirmPlan | `status='confirmed'` | `PUT /plans/{id}/confirm` | "确认此方案" |
| 供应商快照（非MVP） | SupplierSnapshot | `supplier_snapshots` | `supplier_snapshots` | - |
| 生成时间 | GenerationDuration | `generation_time_ms` | `generation_time_ms` | "已为您生成方案（耗时45秒）" |
| 出发城市 | DepartureCity | `departure_city` | `departure_city` | "出发城市" |
| 目的地 | Destination | `destination` | `destination` | "目的地" |
| 目的地城市 | DestinationCity | `destination_city` | `destination_city` | - |

---

## 4.4 UI组件与交互术语

| 中文术语 | 英文术语 | 组件名 | 事件处理 | 说明 |
|---------|---------|--------|----------|------|
| 自定义导航栏 | Custom Navigation Bar | `custom-navbar` | - | 替代系统默认导航栏，支持自定义右侧内容 |
| 状态栏占位 | Status Bar Placeholder | `status-bar` | - | 适配不同机型的状态栏高度 |
| 用户状态显示 | User Status Display | `navbar-user` | `handleUserAvatar` | 导航栏右上角显示登录状态 |
| 用户信息胶囊 | User Info Capsule | `user-info-mini` | - | 已登录时显示头像+昵称的胶囊组件 |
| 登录入口按钮 | Login Entry Button | `login-btn-mini` | - | 未登录时显示的"登录"按钮 |
| 切换账号 | Switch Account | `relogin-entry` | `handleReLogin` | 登录页清除当前登录状态的入口 |
| 继续使用 | Continue | `btn-continue` | `handleContinue` | 已登录时验证token后进入主功能 |
| Token刷新 | Token Refresh | - | `refreshTokenIfNeeded` | 自动检测token即将过期并刷新 |

---

## 5. 领域事件命名

| 事件类型 | 聚合根 | 触发时机 | Payload字段 |
|---------|--------|---------|-------------|
| `PlanRequestCreated` | PlanRequest | 用户提交生成需求后 | `{plan_request_id}` |
| `PlanGenerationRequested` | PlanRequest | 用户请求生成（更明确） | `{plan_request_id}` |
| `PlanGenerated` | Plan | AI服务回调生成方案后 | `{plan_id}` |
| `PlanGenerationSucceeded` | Plan | 生成成功（更明确） | `{plan_id}` |
| `PlanSubmittedForReview` | Plan | 用户通晒方案后 | `{plan_id}` |
| `PlanConfirmed` | Plan | 用户确认方案后 | `{plan_id}` |
| `PlanAdoptionConfirmed` | Plan | 用户采纳确认（更明确） | `{plan_id}` |
| `SupplierContacted`（非MVP） | SupplierContactLog | 用户联系供应商后 | `{plan_id, supplier_id, channel}` |

---

## 6. 反模式与禁用术语

| ❌ 禁用术语 | ✅ 应使用 | 原因 |
|-----------|---------|------|
| "订单" | Plan（方案） | 一期不涉及支付/履约 |
| "预订" | Confirm（确认） | 确认≠预订 |
| "出发地" | departure_city（出发城市）或 departure（出发地点） | 统一术语，避免歧义 |
| "title" | plan_name（方案名称） | 代码已统一使用 plan_name |
| "suppliers" (单数形式) | supplier_snapshots（供应商快照） | 非MVP：如保留该字段，也应强调是快照而非引用 |
| **"位置"** ⭐ | **Location（地点）** | 统一使用"地点"而非"位置" |
| **"地方"** ⭐ | **Location（地点）** | 统一使用"地点" |
| **"place"** ⭐ | **location** | 代码中统一使用location |
| **"search"** ⭐ | **suggest（搜索建议）** | API接口使用suggest明确语义 |
| **"results"** ⭐ | **suggestions（建议列表）** | 前端变量使用suggestions |
| **"popular"** ⭐ | **hot-spots（热门景点）** | API和前端统一使用hot-spots/hotSpots |
| **"lat/lng"** ⭐ | **latitude/longitude** | 使用完整单词，避免缩写 |
| **"poi_name"单独使用** ⭐ | **name（在POI上下文）或 poi_name（跨域）** | 同一领域内可简化，跨域需明确 |

---

## 7. 前端UI状态管理

### 7.1 全局状态 (app.globalData)

| 状态字段 | 类型 | 初始值 | 说明 |
|---------|------|--------|------|
| `isLogin` | Boolean | `false` | 用户是否已登录 |
| `userInfo` | Object/null | `null` | 用户信息（userId, nickname, avatar等） |
| `isGuestMode` | Boolean | `false` | 是否游客模式 |

### 7.2 本地存储 (Storage Keys)

| 存储键 | 值类型 | 说明 |
|--------|--------|------|
| `STORAGE_KEYS.SESSION_TOKEN` | String | JWT会话令牌 |
| `STORAGE_KEYS.USER_INFO` | Object | 用户信息JSON |

### 7.3 页面导航与路由

| 页面路径 | 页面名称 | 导航栏类型 | 说明 |
|---------|---------|-----------|------|
| `/pages/login/login` | 登录页 | 系统默认 | 微信登录入口 |
| `/pages/home/home` | 首页 | 自定义 | 发现页，显示热门目的地和推荐方案 |
| `/pages/index/index` | 生成方案页 | 系统默认 | AI方案生成主流程 |
| `/pages/myplans/myplans` | 我的方案 | 系统默认 | 历史方案列表 |

---

## 8. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-01-06 | 初始版本，整合全链路字段定义 |
| v1.1 | 2026-01-07 | 补充"通晒"工作流：Section 4.3 添加"通晒方案"术语映射，Section 5 添加 `PlanSubmittedForReview` 领域事件 |
| v1.2 | 2026-01-08 | 补充UI组件术语：添加Section 4.4（自定义导航栏、用户状态显示等），添加Section 7（前端状态管理、路由） |
| v1.3 | 2026-01-09 | 强化出发城市/目的地/目的地城市区分；补充通晒反馈指标；补充更明确的领域事件命名；PlanType补充价值主张 |
| v1.4 | 2026-01-14 | 新增地点选择（LocationPicker）模块完整术语体系：<br>• Section 3.2：地点选择与POI核心术语（11个术语定义）<br>• Section 3.2.2：LocationValue标准数据结构<br>• Section 3.2.3：POI类型枚举（7种类型）<br>• Section 3.2.4：hot_destinations表字段规范<br>• Section 3.2.5：API接口命名规范（suggest/hot-spots/reverse-geocode）<br>• Section 3.2.6：前端组件命名规范<br>• Section 3.2.7：用户界面文案规范（10+条文案标准）<br>• Section 3.2.8：代码注释规范（Java/JavaScript）<br>• Section 3.2.9：日志输出规范<br>• Section 3.2.10：高德地图API术语映射<br>• Section 6：扩充反模式禁用术语（新增8条） |
| **v1.5** | **2026-01-14** | **新增地图服务（MapService）模块术语体系**：<br>• Section 3.7：地图服务核心术语（10个术语定义）<br>• Section 3.7.2：标注类型枚举（START/END/WAYPOINT/SUPPLIER）<br>• Section 3.7.3：路径样式枚举（driving/walking/cycling/transit）<br>• Section 3.7.4：地图尺寸预设（DETAIL/THUMBNAIL/SHARE/SUPPLIER）<br>• Section 3.7.5：缩放级别映射（zoom 3-17对应不同跨度范围）<br>• Section 3.7.6：降级策略层级（Level 1-4）<br>• Section 3.7.7：三级缓存架构（L1/L2/L3）<br>• Section 3.7.8：static_map_url_cache表字段规范<br>• Section 3.7.9：路线API响应字段<br>• Section 3.7.10：日志输出规范<br>• **术语修正**：代码中"位置"→"地点"（2处） |
