# 功能设计：我的方案页 Tab 状态筛选

**版本**: v1.0
**创建日期**: 2026-01-06
**状态**: 待评审

---

## 1. 需求概述

### 1.1 背景
当前"我的方案"页面以时间倒序展示所有方案，用户无法快速筛选不同状态的方案。

### 1.2 目标
- 在页面顶部添加 Tab 筛选器，支持按状态快速筛选
- 默认展示"制定完成"的方案（草稿状态，待确认）
- "已确认"的方案置顶显示
- 保持现有的下拉刷新和触底加载更多功能

---

## 2. 领域统一语言确认

### 2.1 方案状态定义

| 状态值 | 中文名 | Tab展示名 | 说明 | 是否独立Tab |
|--------|--------|-----------|------|------------|
| `draft` | 草稿 | **制定完成** | 方案已生成，待用户确认 | ✅ 是（默认Tab） |
| `confirmed` | 已确认 | **已确认** | 用户已采纳此方案 | ✅ 是 |
| `generating` | 生成中 | **生成中** | AI正在生成方案 | ✅ 是 |
| `failed` | 生成失败 | - | 方案生成失败 | ❌ 混在"全部"中 |

### 2.2 Tab 结构

```
┌────────┬────────────┬──────────┬──────────┐
│  全部  │  制定完成   │   已确认  │  生成中   │
│        │  (默认)    │          │          │
└────────┴────────────┴──────────┴──────────┘
```

### 2.3 排序规则

| Tab | 排序逻辑 |
|-----|---------|
| 全部 | `confirmed` 置顶，然后按 `create_time DESC` |
| 制定完成 | 按 `create_time DESC` |
| 已确认 | 按 `confirmed_time DESC` |
| 生成中 | 按 `create_time DESC` |

---

## 3. API 设计变更

### 3.1 查询方案列表 API（变更）

#### Endpoint
```
GET /api/v1/plans?page=1&pageSize=10&status=draft
```

#### 请求参数（新增 status）

| 字段 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | Integer | ❌ | 1 | 页码（从1开始） |
| pageSize | Integer | ❌ | 10 | 每页大小（最大100） |
| **status** | String | ❌ | - | 状态筛选：`draft`/`confirmed`/`generating`/`failed`，不传则返回全部 |

#### 请求示例

**筛选"制定完成"的方案**:
```bash
curl -X GET "http://localhost/api/v1/plans?page=1&pageSize=10&status=draft" \
  -H "Authorization: Bearer <token>"
```

**查询全部方案（已确认置顶）**:
```bash
curl -X GET "http://localhost/api/v1/plans?page=1&pageSize=10" \
  -H "Authorization: Bearer <token>"
```

#### 响应格式（不变）

```json
{
  "success": true,
  "data": {
    "records": [
      {
        "plan_id": "plan_01ke3d123",
        "plan_type": "standard",
        "plan_name": "千岛湖团建3日游方案A",
        "status": "draft",
        "departure_city": "上海市",
        "destination": "杭州千岛湖",
        "budget_total": 12000,
        "duration_days": 3,
        "create_time": "2026-01-04T15:30:00",
        "confirmed_time": null
      }
    ],
    "total": 15,
    "size": 10,
    "current": 1,
    "pages": 2
  },
  "error": null
}
```

---

## 4. 前端设计

### 4.1 页面结构

```
┌─────────────────────────────────────────┐
│              我的方案（标题栏）            │
├─────────────────────────────────────────┤
│  [全部] [制定完成] [已确认] [生成中]      │  ← Tab 栏（固定）
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  方案卡片 1                      │   │
│  │  状态标签 | 路线 | 预算 | 天数   │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │  ← 可滚动区域
│  │  方案卡片 2                      │   │
│  │  ...                            │   │
│  └─────────────────────────────────┘   │
│                                         │
│          加载更多 / 没有更多了           │
│                                         │
└─────────────────────────────────────────┘
```

### 4.2 数据结构变更

```javascript
// pages/myplans/myplans.js
Page({
  data: {
    // 新增：Tab 相关
    tabs: [
      { key: '',           name: '全部' },
      { key: 'draft',      name: '制定完成' },
      { key: 'confirmed',  name: '已确认' },
      { key: 'generating', name: '生成中' }
    ],
    currentTab: 'draft',  // 默认选中"制定完成"

    // 原有字段
    plans: [],
    loading: true,
    loadingMore: false,
    hasMore: true,
    page: 1,
    pageSize: 10
  }
})
```

### 4.3 交互流程

```
用户点击Tab
    │
    ▼
重置 page=1, plans=[]
    │
    ▼
调用 API（带 status 参数）
    │
    ▼
渲染方案列表
    │
    ▼
用户下拉/触底
    │
    ▼
加载更多（保持 status 参数）
```

### 4.4 WXML 结构

```html
<!-- Tab 栏 -->
<view class="tabs-container">
  <view
    wx:for="{{tabs}}"
    wx:key="key"
    class="tab-item {{currentTab === item.key ? 'active' : ''}}"
    bindtap="handleTabChange"
    data-key="{{item.key}}"
  >
    {{item.name}}
  </view>
</view>

<!-- 方案列表 -->
<scroll-view
  scroll-y
  refresher-enabled
  bindrefresherrefresh="onPullDownRefresh"
  bindscrolltolower="onReachBottom"
>
  <!-- 方案卡片列表 -->
</scroll-view>
```

### 4.5 WXSS 样式

```css
/* Tab 栏样式 */
.tabs-container {
  display: flex;
  background: #fff;
  padding: 16rpx 24rpx;
  border-bottom: 1rpx solid #f0f0f0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 16rpx 0;
  font-size: 28rpx;
  color: #666;
  position: relative;
}

.tab-item.active {
  color: #1890ff;
  font-weight: 500;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 48rpx;
  height: 4rpx;
  background: #1890ff;
  border-radius: 2rpx;
}
```

---

## 5. 后端设计

### 5.1 Java Service 变更

**文件**: `PlanController.java`

```java
@GetMapping
public ApiResponse<?> list(
    @RequestHeader(value = "Authorization", required = false) String authorization,
    @RequestParam(defaultValue = "1") int page,
    @RequestParam(defaultValue = "10") int pageSize,
    @RequestParam(required = false) String status  // 新增参数
) {
    String userId = authService.getUserIdFromAuthorization(authorization);
    return ApiResponse.success(planService.listPlans(userId, page, pageSize, status));
}
```

**文件**: `PlanService.java`

```java
public IPage<PlanPO> listPlans(String userId, int page, int pageSize, String status) {
    Page<PlanPO> pageReq = new Page<>(page, pageSize);

    LambdaQueryWrapper<PlanPO> query = new LambdaQueryWrapper<PlanPO>()
        .eq(PlanPO::getUserId, userId)
        .isNull(PlanPO::getDeletedAt)
        .isNull(PlanPO::getArchivedAt);

    // 状态筛选
    if (StringUtils.hasText(status)) {
        query.eq(PlanPO::getStatus, status);
        // 有状态筛选时，按创建时间倒序
        query.orderByDesc(PlanPO::getCreateTime);
    } else {
        // 无状态筛选时，confirmed 置顶，然后按创建时间倒序
        query.orderByDesc(PlanPO::getStatus)  // confirmed > draft（字母序）
             .orderByDesc(PlanPO::getCreateTime);
    }

    return planMapper.selectPage(pageReq, query);
}
```

### 5.2 排序逻辑说明

**"全部"Tab 的置顶逻辑**:
- 方案 1（推荐）：使用 `CASE WHEN` SQL 表达式
  ```sql
  ORDER BY
    CASE WHEN status = 'confirmed' THEN 0 ELSE 1 END ASC,
    create_time DESC
  ```
- 方案 2（简化）：利用字母序（`confirmed` < `draft` < `generating`）
  ```sql
  ORDER BY status ASC, create_time DESC
  ```

> 注意：字母序方案需要确保 `confirmed` 排在最前，当前字母序为 `confirmed` > `draft` > `generating`，需要用 DESC。

---

## 6. 修改范围汇总

### 6.1 前端（小程序）

| 文件 | 修改内容 |
|------|---------|
| `pages/myplans/myplans.js` | 添加 Tab 状态管理、切换逻辑、API 参数传递 |
| `pages/myplans/myplans.wxml` | 添加 Tab 栏 UI 结构 |
| `pages/myplans/myplans.wxss` | 添加 Tab 栏样式 |

### 6.2 后端（Java）

| 文件 | 修改内容 |
|------|---------|
| `PlanController.java` | 添加 `status` 请求参数 |
| `PlanService.java` | 修改 `listPlans` 方法，支持状态筛选和置顶排序 |

### 6.3 文档

| 文件 | 修改内容 |
|------|---------|
| `api-design.md` | 更新 3.2 查询方案列表 API，添加 status 参数说明 |
| `teamventure-phase1-miniapp-design.md` | 更新 3.3 我的方案页设计 |
| `ubiquitous-language-glossary.md` | 确认状态术语映射 |

### 6.4 数据库

**无变更** - 现有 `plans.status` 字段已支持所需状态值

---

## 7. 测试用例

### 7.1 API 测试用例

| 用例ID | 场景 | 请求 | 预期结果 |
|--------|------|------|---------|
| TC-API-01 | 默认查询（无status） | `GET /plans?page=1` | 返回全部方案，confirmed置顶 |
| TC-API-02 | 筛选制定完成 | `GET /plans?status=draft` | 仅返回 status=draft 的方案 |
| TC-API-03 | 筛选已确认 | `GET /plans?status=confirmed` | 仅返回 status=confirmed 的方案 |
| TC-API-04 | 筛选生成中 | `GET /plans?status=generating` | 仅返回 status=generating 的方案 |
| TC-API-05 | 无效状态值 | `GET /plans?status=invalid` | 返回空列表或忽略参数 |
| TC-API-06 | 分页+状态筛选 | `GET /plans?status=draft&page=2` | 正确分页，保持状态筛选 |

### 7.2 前端测试用例

| 用例ID | 场景 | 操作 | 预期结果 |
|--------|------|------|---------|
| TC-FE-01 | 页面加载 | 进入"我的方案"页 | 默认选中"制定完成"Tab，显示 draft 方案 |
| TC-FE-02 | 切换Tab | 点击"已确认"Tab | 列表刷新，仅显示 confirmed 方案 |
| TC-FE-03 | 切换到全部 | 点击"全部"Tab | 显示所有方案，confirmed 置顶 |
| TC-FE-04 | 下拉刷新 | 下拉刷新 | 重新加载当前Tab的数据 |
| TC-FE-05 | 触底加载 | 滚动到底部 | 加载下一页，保持当前Tab筛选 |
| TC-FE-06 | 空状态 | 切换到无数据的Tab | 显示空状态提示 |
| TC-FE-07 | Tab切换重置分页 | 切换Tab | page重置为1，从头加载 |

### 7.3 边界条件

| 用例ID | 场景 | 预期结果 |
|--------|------|---------|
| TC-BC-01 | 只有1条confirmed方案 | 全部Tab中该方案置顶 |
| TC-BC-02 | 无任何方案 | 所有Tab都显示空状态 |
| TC-BC-03 | 100+方案分页 | 分页正常，Tab切换不影响 |

---

## 8. Checklist

### 8.1 开发 Checklist

- [ ] 后端：PlanController 添加 status 参数
- [ ] 后端：PlanService 实现状态筛选和置顶排序
- [ ] 后端：单元测试通过
- [ ] 前端：myplans.js 添加 Tab 状态管理
- [ ] 前端：myplans.wxml 添加 Tab UI
- [ ] 前端：myplans.wxss 添加 Tab 样式
- [ ] 前端：Tab 切换时重置分页
- [ ] 前端：下拉刷新/触底加载保持状态筛选

### 8.2 测试 Checklist

- [ ] API 测试：6 个用例全部通过
- [ ] 前端测试：7 个用例全部通过
- [ ] 边界条件：3 个用例全部通过
- [ ] 回归测试：现有功能不受影响

### 8.3 文档 Checklist

- [ ] api-design.md 已更新
- [ ] teamventure-phase1-miniapp-design.md 已更新
- [ ] ubiquitous-language-glossary.md 已确认

---

## 9. 评审确认

| 角色 | 姓名 | 确认日期 | 签名 |
|------|------|---------|------|
| 产品 | | | |
| 开发 | | | |
| 测试 | | | |

---

## 附录：状态流转图

```
                    ┌─────────────┐
                    │  generating │ ← 提交生成请求
                    │   (生成中)   │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               │               ▼
    ┌─────────────┐        │        ┌─────────────┐
    │    draft    │        │        │   failed    │
    │  (制定完成)  │        │        │  (生成失败)  │
    └──────┬──────┘        │        └─────────────┘
           │               │
           ▼               │
    ┌─────────────┐        │
    │  confirmed  │        │
    │   (已确认)   │        │
    └─────────────┘        │
                           │
    状态不可回退 ◄──────────┘
```
