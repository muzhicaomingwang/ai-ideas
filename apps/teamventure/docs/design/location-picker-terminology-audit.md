# LocationPicker模块术语使用审计报告

**创建日期**: 2026-01-14
**审计范围**: TeamVenture 现有代码库（前端小程序 + 后端Java服务）
**审计目的**: 梳理现有术语使用情况，为LocationPicker模块开发提供一致性基准

---

## 执行摘要

**审计结果**：✅ 核心术语已基本统一，新增LocationPicker模块需遵循现有规范

**关键发现**：
1. ✅ `departure_city`、`destination`、`destination_city` 全链路一致
2. ✅ 前端使用`departureLocation`映射到`departure_city`（已有明确注释）
3. ⚠️ 现有代码中"地点"概念尚未细化到景点维度（需扩展）
4. ✅ 后端已有地理编码能力（`resolveLngLat()`方法）

---

## 1. 现有术语使用情况

### 1.1 前端术语映射（pages/index/index.js）

**✅ 已统一的字段**：

```javascript
// 前端变量 → API字段（已有注释说明，第13-16行）
formData.departureLocation → API: departure_city   // 出发城市
formData.destination       → API: destination      // 目的地

// 数据结构（第199-202行）
location: {
  regional: {
    departureCity: '',           // 出发城市（文本输入）
    destinationProvince: '',     // 目的地省份（picker选择）
    destinationCity: '',         // 目的地城市（picker选择）
    destinationLocation: ''      // 目的地区县/景点（picker选择，可选）
  },
  domestic: {
    departureCity: '',           // 出发城市
    destinationCity: ''          // 目的地城市
  },
  international: {
    departureCity: '',           // 出发城市
    destinationCountry: '',      // 目的地国家
    destinationCity: ''          // 目的地城市
  },
  activity: {
    departureCity: ''            // 出发城市
  }
}
```

**映射逻辑**（第548-564行）：
```javascript
switch (tripType) {
  case 'regional':
    formData.departureLocation = location.regional.departureCity
    formData.destination = location.regional.destinationLocation || location.regional.destinationCity
    break
  case 'domestic':
    formData.departureLocation = location.domestic.departureCity
    formData.destination = location.domestic.destinationCity
    break
  // ...
}
```

**观察结论**：
- ✅ 术语一致性良好（都使用`departure`/`destination`前缀）
- ✅ 有清晰的映射注释
- ⚠️ `destinationLocation`语义模糊（既可以是区县，也可以是景点）
- 💡 建议：LocationPicker模块使用`departure`/`destination`作为LocationValue对象字段名

### 1.2 后端术语使用（Java）

**✅ 已统一的字段**（PlanService.java, PlanController.java, PO类）：

```java
// PO字段（数据库映射）
private String departureCity;     // 出发城市
private String destination;       // 目的地
private String destinationCity;   // 目的地城市（可选）

// API字段（完全一致）
public record GenerateRequest(
  String departure_city,
  String destination,
  String destination_city
) {}
```

**观察结论**：
- ✅ 数据库字段、Java字段、API字段完全一致（snake_case）
- ✅ 无歧义术语
- 💡 新增字段建议：`departure_location`/`destination_location`（GeoJSON格式存储经纬度）

### 1.3 地理编码相关术语（PlanService.java 705-749行）

**现有实现**：
```java
// 方法名：resolveLngLat（解析经纬度）
private Optional<double[]> resolveLngLat(String keyword, String cityHint) {
  // 调用高德API: /v3/place/text
  // 解析响应中的location字段（格式："经度,纬度"）
  String location = asString(firstMap.get("location")).orElse("");
  String[] parts = location.split(",", 2);
  double lng = Double.parseDouble(parts[0]);
  double lat = Double.parseDouble(parts[1]);
  return Optional.of(new double[]{lng, lat});
}
```

**术语观察**：
- ✅ 使用`lngLat`（经纬度）缩写，清晰明确
- ⚠️ 变量名`location`与高德API返回字段同名（上下文清晰，可接受）
- ⚠️ 使用`lng/lat`缩写（高德API规范），与我们建议的`longitude/latitude`完整形式不同
- 💡 建议：LocationService新代码使用完整形式`longitude/latitude`，与高德API交互时再转换

---

## 2. 术语不一致问题清单

### 2.1 发现的问题

| 问题 | 位置 | 现状 | 影响 | 建议 |
|------|------|------|------|------|
| ⚠️ "位置"混用 | app.json, detail.js | 微信API使用"位置"（wx.getLocation, wx.openLocation） | 低 | 业务代码统一用"地点"，微信API保持原生术语 |
| ⚠️ lng/lat vs longitude/latitude | PlanService.java | 现有代码使用缩写`lng/lat` | 低 | 新代码使用完整形式，兼容现有代码 |
| ⚠️ destinationLocation语义模糊 | index.js | 既表示区县又表示景点 | 中 | 用LocationValue对象替代，明确语义 |

### 2.2 无需修改的合理使用

**微信API原生术语**（保持不变）：
- `wx.getLocation()` - "获取位置"（微信官方术语）
- `wx.chooseLocation()` - "选择位置"（微信官方术语）
- `wx.openLocation()` - "打开位置"（微信官方术语）
- `app.json` permission: "scope.userLocation"（微信官方术语）

**原因**：这些是微信小程序框架的原生API，不应修改。在注释中说明映射关系即可。

**CSS/样式相关**：
- `position: absolute/relative/fixed` - CSS属性，保持不变
- `.placeholder` - 占位符样式类，保持不变

---

## 3. LocationPicker模块术语规范

### 3.1 必须遵守的命名规范

**组件命名**：
| 层级 | 命名规范 | 示例 | ❌ 反例 |
|------|---------|------|--------|
| 文件/目录 | `location-picker` | `components/location-picker/` | `place-picker`, `poi-selector` |
| 组件JS类 | `location-picker` | `Component({...})` in location-picker.js | - |
| Java类 | `Location`前缀 | `LocationService`, `LocationController` | `PlaceService`, `PoiService` |
| 数据库表 | `snake_case` | `hot_destinations` | `hot_locations`, `popular_pois` |
| API路径 | `/locations` | `/api/v1/locations/suggest` | `/places`, `/pois` |

**字段命名**：
| 场景 | 命名规范 | 示例 | ❌ 反例 |
|------|---------|------|--------|
| 数据库字段 | `snake_case` | `poi_id`, `poi_name`, `short_name` | `poiId`, `location_id` |
| Java字段 | `camelCase` | `poiId`, `poiName`, `shortName` | `poi_id`, `locationId` |
| API字段 | `snake_case` | `poi_id`, `poi_name`, `hot_spots` | `poiId`, `hotSpots` |
| 前端JS | `camelCase` | `poiId`, `poiName`, `hotSpots` | `poi_id`, `hot_spots` |

### 3.2 LocationValue对象字段规范

**标准格式**（必须严格遵守）：
```typescript
interface LocationValue {
  name: string;              // ✅ 使用name（而非poi_name或location_name）
  address: string;           // ✅ 使用address（完整地址）
  location?: {               // ✅ 使用location嵌套对象
    longitude: number;       // ✅ 完整单词longitude（而非lng）
    latitude: number;        // ✅ 完整单词latitude（而非lat）
  };
  poi_id?: string;          // ✅ snake_case（与API一致）
  poi_type?: string;        // ✅ snake_case（与API一致）
}
```

**字段语义**：
- `name`: 用户看到的显示名称（如"莫干山风景名胜区"）
- `address`: 行政区划完整地址（如"浙江省湖州市德清县"）
- `location`: 精确坐标（用于地图展示、距离计算）
- `poi_id`: 高德POI唯一标识（用于获取详情、评分等）
- `poi_type`: POI分类（用于图标显示、筛选）

### 3.3 API接口术语规范

**接口1：搜索建议**
```
GET /api/v1/locations/suggest

✅ 使用术语：
- 路径: /locations（而非/places或/pois）
- 方法名: suggest（而非search/autocomplete/query）
- 参数: keyword（而非query/q/search）
- 参数: type（而非location_type/point_type）
- 响应: suggestions（而非results/items/pois）

❌ 避免：
GET /api/v1/places/search
GET /api/v1/pois/autocomplete
```

**接口2：热门景点**
```
GET /api/v1/locations/hot-spots

✅ 使用术语：
- 路径: /hot-spots（而非/popular/recommended/trending）
- 响应: hot_spots（而非popular_spots/recommendations）

❌ 避免：
GET /api/v1/locations/popular
GET /api/v1/locations/recommended
```

**接口3：逆地理编码**
```
GET /api/v1/locations/reverse-geocode

✅ 使用术语：
- 方法名: reverse-geocode（GIS标准术语）
- 参数: longitude/latitude（完整单词）
- 响应: formatted_address（而非address_text）

❌ 避免：
GET /api/v1/locations/decode
GET /api/v1/locations/coord-to-address
参数: lng/lat
```

### 3.4 前端UI文案规范

**表单标签**：
```xml
<!-- ✅ 推荐 -->
<view class="form-label">出发地点</view>
<view class="form-label">目的地景点</view>

<!-- ❌ 避免 -->
<view class="form-label">出发城市</view>  <!-- 太宽泛，不体现景点级精度 -->
<view class="form-label">目的地</view>     <!-- 不明确 -->
<view class="form-label">目标地点</view>   <!-- 术语不统一 -->
```

**占位符文案**：
```javascript
// ✅ 推荐
placeholder: "请输入出发地点（景点/地标/酒店）"
placeholder: "搜索景点、酒店或地标"

// ❌ 避免
placeholder: "请输入位置"              // 太宽泛
placeholder: "搜索目的地"              // 不明确
placeholder: "输入您要去的地方"        // 口语化，不统一
```

**区域标题**：
```xml
<!-- ✅ 推荐 -->
<view class="section-title">🕐 最近使用</view>
<view class="section-title">🏷️ 热门景点</view>
<view class="section-title">🔍 搜索结果</view>

<!-- ❌ 避免 -->
<view class="section-title">历史记录</view>    <!-- 使用"最近使用" -->
<view class="section-title">推荐地点</view>    <!-- 使用"热门景点" -->
<view class="section-title">找到的结果</view>  <!-- 使用"搜索结果" -->
```

### 3.5 日志输出规范

**Java日志**：
```java
// ✅ 推荐
log.info("POI搜索: keyword={}, type={}, province={}, resultCount={}, costMs={}",
  keyword, type, province, suggestions.size(), costMs);

log.info("热门景点加载: province={}, limit={}, count={}",
  province, limit, hotSpots.size());

log.warn("高德API调用失败，降级到静态表: keyword={}, error={}",
  keyword, e.getMessage());

log.debug("Redis缓存命中: key={}, ttl={}s", cacheKey, ttl);

// ❌ 避免
log.info("地点搜索: ...");          // 使用"POI搜索"更明确
log.info("推荐景点加载: ...");       // 使用"热门景点加载"
log.warn("API失败: ...");           // 明确指出"高德API调用失败"
log.debug("缓存hit: ...");          // 使用"缓存命中"
```

**前端日志**：
```javascript
// ✅ 推荐
console.log('[LocationPicker] 搜索关键词:', keyword)
console.log('[LocationPicker] 搜索建议数量:', suggestions.length)
console.warn('[LocationPicker] 搜索失败:', error)

// ❌ 避免
console.log('搜索:', keyword)        // 缺少模块标识
console.log('结果数:', count)        // 使用"搜索建议数量"
```

---

## 4. 现有代码兼容性分析

### 4.1 前端兼容性

**现有字段（必须保留）**：
```javascript
// 旧版formData结构（第199-202行）
formData.location.regional = {
  departureCity: '',           // ← 保留，作为兼容字段
  destinationProvince: '',     // ← 保留，用于热门推荐province参数
  destinationCity: '',         // ← 保留，作为兼容字段
  destinationLocation: ''      // ← 保留，作为兼容字段
}
```

**新增字段（LocationPicker模块）**：
```javascript
// 新版formData结构（扩展）
formData.location.regional = {
  // 旧字段（保留）
  departureCity: '',
  destinationProvince: '',
  destinationCity: '',
  destinationLocation: '',

  // 新增字段
  departure: LocationValue,      // 出发地点（LocationValue对象）
  destination: LocationValue     // 目的地点（LocationValue对象）
}
```

**映射策略**（向后兼容）：
```javascript
mapFormDataToAPIRequest() {
  // 新版优先，旧版fallback
  const departure = location.regional.departure?.name || location.regional.departureCity
  const destination = location.regional.destination?.name
    || location.regional.destinationLocation
    || location.regional.destinationCity

  return {
    departure_city: departure,
    destination: destination,
    // 新增可选字段
    departure_location: location.regional.departure?.location,
    destination_location: location.regional.destination?.location
  }
}
```

### 4.2 后端兼容性

**现有数据库字段（必须保留）**：
```sql
-- plan_requests 表
departure_city VARCHAR(64) NOT NULL,
destination VARCHAR(255) NOT NULL,
destination_city VARCHAR(64),

-- plans 表
departure_city VARCHAR(64) NOT NULL,
destination VARCHAR(255) NOT NULL,
destination_city VARCHAR(64),
```

**建议新增字段（可选）**：
```sql
-- 可选：存储精确坐标（用于距离计算、路线规划）
departure_longitude DECIMAL(10, 6),
departure_latitude DECIMAL(10, 6),
destination_longitude DECIMAL(10, 6),
destination_latitude DECIMAL(10, 6),

-- 或使用POINT类型（MySQL 5.7+）
departure_location POINT,
destination_location POINT,
SPATIAL INDEX idx_destination_location (destination_location)
```

**注意**：新增字段都是可选的，不影响现有数据和API。

---

## 5. 术语一致性检查清单

### 5.1 开发阶段检查

**代码Review检查项**（每个PR必查）：

- [ ] **文件命名**：是否使用`location-picker`（而非place/poi）
- [ ] **类名**：Java类是否使用`Location`前缀
- [ ] **方法名**：是否使用`suggest`/`hotSpots`（而非search/popular）
- [ ] **变量名**：前端是否使用`camelCase`，后端是否使用`snake_case`
- [ ] **API字段**：是否全部使用`snake_case`
- [ ] **数据库字段**：是否使用`snake_case`，POI相关是否有`poi_`前缀
- [ ] **注释**：是否使用统一术语（地点/景点/POI/搜索建议）
- [ ] **日志**：是否使用规范格式和统一术语
- [ ] **UI文案**：是否符合文案规范（出发地点/目的地景点）
- [ ] **错误提示**：是否使用规范文案

### 5.2 测试阶段检查

**API测试检查项**：
- [ ] 请求参数命名是否符合规范（keyword, type, province, limit）
- [ ] 响应字段命名是否符合规范（suggestions, hot_spots）
- [ ] 错误响应文案是否规范

**前端测试检查项**：
- [ ] 组件props命名是否规范
- [ ] 组件events命名是否规范
- [ ] UI文案显示是否符合规范
- [ ] console日志是否使用规范术语

### 5.3 文档更新检查

**需同步更新的文档**：
- [ ] `docs/design/api-design.md` - API接口文档
- [ ] `docs/design/database-design.md` - 数据库设计文档（如新增字段）
- [ ] `docs/design/ubiquitous-language-glossary.md` - 术语表（已更新✅）
- [ ] `README.md` - 项目README（如有必要）

---

## 6. 建议的术语迁移路径

### 阶段1：新代码采用新规范（当前）
- LocationPicker模块所有新代码严格遵循术语规范
- 不修改现有代码（避免大规模重构）
- 在交互边界做映射和兼容

### 阶段2：文档先行（后续）
- 更新所有设计文档，明确术语定义
- 在Code Review时引用术语表
- 新增代码必须符合术语规范

### 阶段3：渐进式重构（可选，长期）
- 在修改现有模块时，顺便统一术语
- 优先级：注释 > 变量名 > 字段名（数据库最后）
- 保持向后兼容，不破坏现有API

---

## 7. 术语统一的价值

### 7.1 减少沟通成本
- **产品-开发**：产品说"目的地景点"，开发直接对应`destination`字段
- **前端-后端**：前端`suggestions`对应后端`SuggestionResponse`，无歧义
- **代码-文档**：代码中看到`hot_spots`，文档中也是同样术语

### 7.2 提升代码可读性
```java
// ❌ 不统一的代码
List<PoiResult> results = searchPlaces(query);
List<Location> popular = getRecommendedLocations();

// ✅ 统一术语的代码
List<PoiSuggestion> suggestions = suggest(keyword);
List<HotSpot> hotSpots = getHotSpots();
```

### 7.3 降低维护成本
- 新人接手时：查术语表即可理解业务概念
- Bug调试时：日志中的术语与代码一致，快速定位
- 重构时：搜索统一术语，一次性找到所有相关代码

### 7.4 支持国际化
- 统一的英文术语，方便未来扩展多语言
- `location` / `destination` / `suggestion` 都是通用英文术语
- 避免中式英语（如 `place-choosing`）

---

## 8. 快速参考卡（开发时核对）

### 核心术语速查

| 概念 | 英文 | 数据库 | Java | API | 前端JS | UI文案 |
|------|------|--------|------|-----|--------|--------|
| 地点 | Location | - | `Location` | - | `location` | "地点" |
| 景点/POI | POI | `poi_id` | `poiId` | `poi_id` | `poiId` | "景点" |
| 出发地点 | Departure | `departure_city` | `departureCity` | `departure_city` | `departure` | "出发地点" |
| 目的地点 | Destination | `destination` | `destination` | `destination` | `destination` | "目的地景点" |
| 搜索建议 | Suggestion | - | `SuggestionResponse` | `suggestions` | `suggestions` | "搜索结果" |
| 热门景点 | Hot Spot | `hot_destinations表` | `HotSpot` | `hot_spots` | `hotSpots` | "热门景点" |
| 最近使用 | Recent | - | - | - | `recentLocations` | "最近使用" |
| 经度 | Longitude | `longitude` | `longitude` | `longitude` | `longitude` | - |
| 纬度 | Latitude | `latitude` | `latitude` | `latitude` | `latitude` | - |

### 禁用术语速查

| ❌ 禁用 | ✅ 替换为 | 适用范围 |
|--------|---------|---------|
| 位置 | 地点 | 业务代码（微信API除外） |
| 地方 | 地点 | 所有场景 |
| place | location | 所有代码 |
| search | suggest | API接口名 |
| results | suggestions | 搜索结果变量 |
| popular | hot-spots | 热门景点 |
| lat/lng | latitude/longitude | 新代码（现有代码可保留） |
| 起点/终点 | 出发地点/目的地点 | UI文案 |

---

## 9. 审计结论

### 现状评估
- ✅ **优秀**：departure_city、destination、destination_city 全链路一致
- ✅ **良好**：前端有清晰的映射注释和文档
- ✅ **可用**：后端地理编码能力已具备，可直接复用
- ⚠️ **需改进**：地点概念需细化到景点维度（当前只到城市/区县）

### 建议行动
1. ✅ **已完成**：扩展ubiquitous-language-glossary.md（v1.4）
2. 🔄 **进行中**：创建本审计报告
3. ⏭️ **下一步**：更新api-design.md，添加LocationPicker相关接口
4. ⏭️ **后续**：Code Review时严格执行术语检查清单

### 风险提示
- **低风险**：新增LocationPicker模块，不修改现有代码，兼容性风险低
- **需注意**：前端formData新增字段（departure/destination LocationValue），需确保向后兼容
- **建议**：保留旧字段作为fallback，双写新旧字段

---

## 附录：术语对照快速索引

**中英文对照**：
- 地点 = Location
- 景点 = Attraction / POI
- 出发地点 = Departure Location
- 目的地点 = Destination Location
- 搜索建议 = Suggestion
- 热门景点 = Hot Spot
- 最近使用 = Recent Location

**命名风格对照**：
- 数据库：`snake_case` (poi_id, hot_destinations)
- Java：`camelCase` (poiId, hotSpots) + `PascalCase` (类名)
- API：`snake_case` (poi_id, hot_spots)
- 前端JS：`camelCase` (poiId, hotSpots)
- 组件名：`kebab-case` (location-picker)

**关键原则**：
1. 统一优先于习惯（即使现有代码用了缩写，新代码也用完整形式）
2. 业务术语优先于技术术语（"地点"优于"位置"，"景点"优于"POI"）
3. 跨层传递时保持一致（前端suggestions → API suggestions → Java SuggestionResponse）
4. 微信原生API保持不变（wx.getLocation的"位置"术语可接受）
