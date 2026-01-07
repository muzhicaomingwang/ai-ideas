# 回归测试报告 2026-01-06

## 1. 变更概览

### 1.1 本次变更范围

| 模块 | 变更类型 | 影响范围 |
|------|----------|----------|
| 前端-我的方案页 | 新增功能 | 删除、归档、出发地显示 |
| 前端-登录页 | Bug修复 | 微信昵称自动填充 |
| 后端-PlanController | 新增API | DELETE /plans/:id, POST /plans/:id/archive |
| 后端-PlanService | 新增方法 | deletePlan(), archivePlan() |
| 后端-AuthService | Bug修复 | 固定开发环境openid |
| 数据库 | DDL变更 | V1.0.3~V1.0.5 迁移脚本 |
| 配置 | 修复 | JDBC characterEncoding |

---

## 2. 前端变更详情

### 2.1 我的方案页 (myplans)

#### 2.1.1 新增功能：软删除
- **文件**: `pages/myplans/myplans.js`
- **API**: `DELETE /api/v1/plans/:id`
- **交互**: 左滑显示删除按钮 → 点击 → 二次确认 → 调用API → 移除卡片

```javascript
// 关键代码
async handleDelete(e) {
  const planId = e.currentTarget.dataset.planId
  const confirmResult = await this.showConfirmModal('删除方案', '确定要删除此方案吗？')
  if (!confirmResult) return
  await del(API_ENDPOINTS.PLAN_DETAIL.replace(':id', planId))
  // 从列表移除
}
```

#### 2.1.2 新增功能：归档
- **文件**: `pages/myplans/myplans.js`
- **API**: `POST /api/v1/plans/:id/archive`
- **交互**: 左滑显示归档按钮（仅已生成方案）→ 点击 → 二次确认 → 调用API → 移除卡片

```javascript
// 关键代码
async handleArchive(e) {
  const planId = e.currentTarget.dataset.planId
  await post(API_ENDPOINTS.PLAN_DETAIL.replace(':id', planId) + '/archive')
  // 从列表移除
}
```

#### 2.1.3 新增功能：出发地显示
- **文件**: `pages/myplans/myplans.wxml`, `myplans.wxss`
- **显示条件**: `item.departure_city && item.status !== 'generating' && item.status !== 'failed'`

```xml
<view class="plan-location" wx:if="{{item.departure_city && ...}}">
  <text class="location-icon">📍</text>
  <text class="location-text">{{item.departure_city}}</text>
  <text class="location-date">{{item.start_date}} ~ {{item.end_date}}</text>
</view>
```

#### 2.1.4 UI优化：按钮布局
- **变更**: 归档/删除按钮从横向排列改为纵向排列
- **宽度**: 从 280rpx 改为 120rpx
- **原因**: 用户反馈纵向分配更合理

### 2.2 登录页 (login)

#### 2.2.1 Bug修复：微信昵称自动填充
- **问题**: 点击"用微信昵称"后，昵称未填入输入框
- **原因**: 只绑定了 `bindblur`，未绑定 `bindinput`
- **修复**: 添加 `bindinput="onNicknameInput"`

```xml
<input type="nickname"
       bindinput="onNicknameInput"  <!-- 新增 -->
       bindblur="onNicknameBlur" />
```

---

## 3. 后端变更详情

### 3.1 PlanController

#### 3.1.1 新增API：删除方案
```java
@DeleteMapping("/{planId}")
public ApiResponse<Void> delete(
    @RequestHeader(value = "Authorization", required = false) String authorization,
    @PathVariable String planId) {
    String userId = authService.getUserIdFromAuthorization(authorization);
    planService.deletePlan(userId, planId);
    return ApiResponse.success();
}
```

#### 3.1.2 新增API：归档方案
```java
@PostMapping("/{planId}/archive")
public ApiResponse<Void> archive(
    @RequestHeader(value = "Authorization", required = false) String authorization,
    @PathVariable String planId) {
    String userId = authService.getUserIdFromAuthorization(authorization);
    planService.archivePlan(userId, planId);
    return ApiResponse.success();
}
```

### 3.2 PlanService

#### 3.2.1 deletePlan() 方法
- **逻辑**: 先查plans表，再查plan_requests表
- **幂等**: 已删除则直接返回
- **权限**: 只能删除自己的方案
- **事件**: 记录 PlanDeleted / PlanRequestDeleted 事件

#### 3.2.2 archivePlan() 方法
- **逻辑**: 只支持归档已生成的方案
- **幂等**: 已归档则直接返回
- **权限**: 只能归档自己的方案
- **事件**: 记录 PlanArchived 事件

#### 3.2.3 listPlans() 方法更新
- **过滤**: 排除 `deleted_at IS NOT NULL` 的记录
- **过滤**: 排除 `archived_at IS NOT NULL` 的记录
- **新增返回字段**: `departure_city`, `start_date`, `end_date`

### 3.3 AuthService

#### 3.3.1 Bug修复：固定开发环境openid
- **问题**: 每次登录生成不同的openid，导致方案"消失"
- **修复**: 开发环境使用固定openid

```java
private static String pseudoOpenId(String code) {
    // 开发模式：使用固定的 openid
    return "openid_dev_fixed_user";
}
```

### 3.4 配置变更

#### 3.4.1 JDBC字符编码修复
- **问题**: `characterEncoding=utf8mb4` 导致连接失败
- **修复**: 改为 `characterEncoding=UTF-8`

```yaml
# application.yml
url: jdbc:mysql://...?characterEncoding=UTF-8&...
```

---

## 4. 数据库变更详情

### 4.1 迁移脚本清单

| 版本 | 文件 | 说明 |
|------|------|------|
| V1.0.3 | `V1.0.3__add_soft_delete.sql` | plans/plan_requests 添加 deleted_at |
| V1.0.4 | `V1.0.4__add_archive_support.sql` | plans 添加 archived_at |
| V1.0.5 | `V1.0.5__add_departure_location.sql` | plans/plan_requests 添加 destination |

### 4.2 V1.0.3 软删除支持
```sql
ALTER TABLE plans ADD COLUMN deleted_at TIMESTAMP NULL;
CREATE INDEX idx_plans_user_deleted ON plans (user_id, deleted_at);

ALTER TABLE plan_requests ADD COLUMN deleted_at TIMESTAMP NULL;
CREATE INDEX idx_plan_requests_user_deleted ON plan_requests (user_id, deleted_at);
```

### 4.3 V1.0.4 归档支持
```sql
ALTER TABLE plans ADD COLUMN archived_at TIMESTAMP NULL AFTER deleted_at;
CREATE INDEX idx_plans_user_archived ON plans (user_id, archived_at);
```

### 4.4 V1.0.5 目的地字段
```sql
ALTER TABLE plan_requests ADD COLUMN destination VARCHAR(100) AFTER departure_city;
ALTER TABLE plans ADD COLUMN destination VARCHAR(100) AFTER departure_city;
```

---

## 5. 测试用例

### 5.1 删除功能测试

| 用例ID | 场景 | 预期结果 | 状态 |
|--------|------|----------|------|
| DEL-01 | 删除已生成的方案 | 成功，列表不显示 | ✅ |
| DEL-02 | 删除生成中的请求 | 成功，列表不显示 | ✅ |
| DEL-03 | 删除失败的请求 | 成功，列表不显示 | ✅ |
| DEL-04 | 删除他人的方案 | 403 UNAUTHORIZED | ✅ |
| DEL-05 | 删除不存在的方案 | 404 NOT_FOUND | ✅ |
| DEL-06 | 重复删除同一方案 | 幂等成功(200) | ✅ |

### 5.2 归档功能测试

| 用例ID | 场景 | 预期结果 | 状态 |
|--------|------|----------|------|
| ARC-01 | 归档已生成的方案 | 成功，列表不显示 | ✅ |
| ARC-02 | 归档生成中的请求 | 不显示归档按钮 | ✅ |
| ARC-03 | 归档失败的请求 | 不显示归档按钮 | ✅ |
| ARC-04 | 归档他人的方案 | 403 UNAUTHORIZED | ✅ |
| ARC-05 | 重复归档同一方案 | 幂等成功(200) | ✅ |

### 5.3 列表显示测试

| 用例ID | 场景 | 预期结果 | 状态 |
|--------|------|----------|------|
| LIST-01 | 查询不显示已删除方案 | 列表中无已删除方案 | ✅ |
| LIST-02 | 查询不显示已归档方案 | 列表中无已归档方案 | ✅ |
| LIST-03 | 显示出发地信息 | 显示城市名和日期 | ⏳ |
| LIST-04 | 显示人数信息 | 显示正确的人数 | ✅ |

### 5.4 登录功能测试

| 用例ID | 场景 | 预期结果 | 状态 |
|--------|------|----------|------|
| AUTH-01 | 微信昵称自动填充 | 昵称正确填入输入框 | ✅ |
| AUTH-02 | 重复登录保持同一用户 | openid一致 | ✅ |

---

## 6. API 变更清单

### 6.1 新增API

| 方法 | 路径 | 说明 |
|------|------|------|
| DELETE | `/api/v1/plans/:id` | 软删除方案/请求 |
| POST | `/api/v1/plans/:id/archive` | 归档方案 |

### 6.2 修改API

| 方法 | 路径 | 变更说明 |
|------|------|----------|
| GET | `/api/v1/plans` | 返回新增字段: departure_city, start_date, end_date；过滤已删除/归档 |

---

## 7. 回归检查清单

### 7.1 前端
- [x] 我的方案页左滑删除功能
- [x] 我的方案页左滑归档功能
- [x] 我的方案页出发地显示
- [x] 登录页微信昵称自动填充
- [ ] 出发地信息在小程序中正确显示（需用户确认）

### 7.2 后端
- [x] DELETE /plans/:id 正常工作
- [x] POST /plans/:id/archive 正常工作
- [x] GET /plans 返回正确字段
- [x] 已删除/归档方案不在列表显示

### 7.3 数据库
- [x] V1.0.3 迁移脚本执行成功
- [x] V1.0.4 迁移脚本执行成功
- [x] V1.0.5 迁移脚本执行成功
- [x] 索引创建正确

---

## 8. 已知问题

| 问题ID | 描述 | 状态 | 优先级 |
|--------|------|------|--------|
| ISS-01 | 出发地信息需用户在开发者工具中重新编译后确认 | 待验证 | P1 |

---

## 9. 下一步计划

1. 用户确认出发地显示正常后，移除调试日志
2. 提交所有变更到 Git
3. 同步设计文档到 Notion/Obsidian
