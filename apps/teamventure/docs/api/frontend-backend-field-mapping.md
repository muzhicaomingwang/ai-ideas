# TeamVenture 前后端字段映射文档

**版本**: v1.0
**创建日期**: 2026-01-04
**用途**: 确保前后端API字段完全对齐，避免集成问题

---

## 1. 登录 API

### Endpoint
```
POST /api/v1/auth/wechat/login
```

### 字段映射

| 字段名 | 类型 | 必需 | 前端 | 后端 | 状态 | 备注 |
|-------|------|------|------|------|------|------|
| code | String | ✅ | ✅ | ✅ | ✅ | 微信登录code |
| nickname | String | ❌ | ✅ | ✅ | ✅ | 用户昵称（可选） |
| avatarUrl | String | ❌ | ✅ | ✅ | ✅ | 头像URL（可选） |

### 请求示例

**前端发送**:
```javascript
{
  code: "081vXS0w3qE5Rq2bCe2w3lv...",
  nickname: "张三",
  avatarUrl: "https://thirdwx.qlogo.cn/..."
}
```

**后端期望**:
```java
public class LoginRequest {
    @NotBlank public String code;       // 必需
    public String nickname;              // 可选
    public String avatarUrl;             // 可选
}
```

### 响应示例

**后端返回**:
```json
{
  "success": true,
  "data": {
    "sessionToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "userInfo": {
      "user_id": "user_01ke3abc123",
      "nickname": "张三",
      "avatar": "https://thirdwx.qlogo.cn/...",
      "phone": "",
      "company": "",
      "role": "user"
    }
  },
  "error": null
}
```

**前端处理**:
```javascript
// 存储
wx.setStorageSync('sessionToken', data.sessionToken)
wx.setStorageSync('userInfo', data.userInfo)

// 使用
const token = data.sessionToken
const userId = data.userInfo.user_id
```

---

## 2. 方案生成 API

### Endpoint
```
POST /api/v1/plans/generate
```

### 字段映射

| 字段名 | 类型 | 必需 | 前端 | 后端 | 状态 | 备注 |
|-------|------|------|------|------|------|------|
| people_count | Integer | ✅ | ✅ | ✅ | ✅ | 参与人数 |
| budget_min | Number | ✅ | ✅ | ✅ | ✅ | 最低预算 |
| budget_max | Number | ✅ | ✅ | ✅ | ✅ | 最高预算 |
| start_date | String | ✅ | ✅ | ✅ | ✅ | 开始日期 YYYY-MM-DD |
| end_date | String | ✅ | ✅ | ✅ | ✅ | 结束日期 YYYY-MM-DD |
| departure_city | String | ✅ | ✅ | ✅ | ✅ | 出发城市 |
| preferences | Object | ❌ | ✅ | ✅ | ✅ | 偏好设置（JSON对象） |
| destination | String | ❌ | ✅ | ❌ | ⚠️ | **前端发送，后端忽略** |

### ⚠️ 问题说明

**destination 字段不匹配**:
- **前端**: 发送 `destination` 字段（UI上有"目的地(可选)"输入框）
- **后端**: DTO中没有定义此字段
- **影响**: Spring Boot 会忽略未定义的字段，不会报错
- **建议**:
  1. **短期**: 保持现状（后端忽略此字段）
  2. **长期**: 要么在后端添加此字段，要么在前端移除

### 请求示例

**前端发送**:
```javascript
{
  people_count: 50,
  budget_min: 10000,
  budget_max: 15000,
  start_date: "2026-02-01",
  end_date: "2026-02-03",
  departure_city: "Beijing",      // ✅ 已修复（之前是 departure_location）
  destination: "Huairou",          // ⚠️ 后端会忽略
  preferences: {
    activity_types: ["team_building", "leisure"],
    accommodation_level: "standard",
    dining_style: ["bbq", "hotpot"],
    special_requirements: "有老人，需要无障碍设施"
  }
}
```

**后端期望**:
```java
public class GenerateRequest {
    @NotNull public Integer people_count;        // 必需
    @NotNull public BigDecimal budget_min;       // 必需
    @NotNull public BigDecimal budget_max;       // 必需
    @NotBlank public String start_date;          // 必需
    @NotBlank public String end_date;            // 必需
    @NotBlank public String departure_city;      // 必需
    public Map<String, Object> preferences;      // 可选
    // 注意：没有 destination 字段！
}
```

### preferences 结构

**前端定义** (frontend/miniapp/pages/index/index.js):
```javascript
preferences: {
  activity_types: [],           // 数组：活动类型
  accommodation_level: '',      // 字符串：住宿标准
  dining_style: [],             // 数组：餐饮偏好
  special_requirements: ''      // 字符串：特殊需求
}
```

**后端处理** (Map<String, Object>):
```java
// 后端将其作为 JSON 存储到数据库的 preferences 字段（JSON类型）
// Python AI 服务会读取这个 JSON 并生成方案
```

### 响应示例

**后端返回**:
```json
{
  "success": true,
  "data": {
    "plan_request_id": "plan_req_01ke3cnw4t5dvp8jhjvfdafq1v",
    "status": "generating"
  },
  "error": null
}
```

---

## 3. 方案列表 API

### Endpoint
```
GET /api/v1/plans?page=1&pageSize=10
```

### 请求头
```
Authorization: Bearer {sessionToken}
```

### 响应示例

**后端返回** (MyBatis Plus 分页对象):
```json
{
  "success": true,
  "data": {
    "records": [
      {
        "plan_id": "plan_01ke3d123",
        "title": "北京团建3日游方案A",
        "destination": "Beijing",
        "days": 3,
        "budget": 12000,
        "status": "generated",
        "create_time": "2026-01-04T15:30:00"
      }
    ],
    "total": 1,
    "size": 10,
    "current": 1,
    "pages": 1
  },
  "error": null
}
```

---

## 4. 方案详情 API

### Endpoint
```
GET /api/v1/plans/{planId}
```

### 请求头
```
Authorization: Bearer {sessionToken}
```

### 响应示例

**后端返回**:
```json
{
  "success": true,
  "data": {
    "plan_id": "plan_01ke3d123",
    "title": "北京团建3日游方案A",
    "destination": "Beijing",
    "days": 3,
    "budget": 12000,
    "itinerary": {
      "day1": {
        "date": "2026-02-01",
        "activities": [...]
      },
      "day2": {...},
      "day3": {...}
    },
    "status": "generated",
    "created_at": "2026-01-04T15:30:00"
  },
  "error": null
}
```

---

## 5. 确认方案 API

### Endpoint
```
POST /api/v1/plans/{planId}/confirm
```

### 请求头
```
Authorization: Bearer {sessionToken}
```

### 请求体
```
空（无需请求体）
```

### 响应示例

**后端返回**:
```json
{
  "success": true,
  "data": null,
  "error": null
}
```

---

## 6. 记录供应商联系 API

### Endpoint
```
POST /api/v1/plans/{planId}/supplier-contacts
```

### 字段映射

| 字段名 | 类型 | 必需 | 前端 | 后端 | 状态 | 备注 |
|-------|------|------|------|------|------|------|
| supplier_id | String | ✅ | ✅ | ✅ | ✅ | 供应商ID |
| channel | String | ✅ | ✅ | ✅ | ✅ | 联系渠道（PHONE/WECHAT/EMAIL） |
| notes | String | ❌ | ✅ | ✅ | ✅ | 备注信息 |

### 请求示例

**前端发送**:
```javascript
{
  supplier_id: "sup_hotel_001",
  channel: "PHONE",
  notes: "致电酒店预订部，确认50人会议室和住宿"
}
```

**后端期望**:
```java
public class SupplierContactRequest {
    @NotBlank public String supplier_id;     // 必需
    @NotBlank public String channel;         // 必需
    public String notes;                     // 可选
}
```

---

## 7. 统一响应格式

所有API都使用统一的响应包装器：

### 成功响应
```json
{
  "success": true,
  "data": {...},
  "error": null
}
```

### 错误响应
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述信息"
  }
}
```

### 常见错误码

| 错误码 | HTTP状态 | 说明 | 前端处理 |
|-------|---------|------|---------|
| UNAUTHORIZED | 401 | 未登录或token过期 | 跳转登录页 |
| FORBIDDEN | 403 | 无权访问 | 提示无权限 |
| VALIDATION_ERROR | 400 | 参数验证失败 | 显示错误信息 |
| NOT_FOUND | 404 | 资源不存在 | 提示资源不存在 |
| INTERNAL_ERROR | 500 | 服务器内部错误 | 提示稍后重试 |

---

## 8. 已知问题和解决方案

### ✅ 已修复

1. **departure_location → departure_city**
   - **问题**: 前端发送 `departure_location`，后端期望 `departure_city`
   - **修复**: 前端已改为 `departure_city`
   - **文件**: `frontend/miniapp/pages/index/index.js` 第339行

### ⚠️ 待处理

1. **destination 字段**
   - **问题**: 前端发送 `destination`，后端DTO没有定义
   - **影响**: 无（Spring Boot自动忽略）
   - **建议**:
     - 方案A: 前端移除此字段（如果不需要）
     - 方案B: 后端添加此字段到DTO和数据库（如果需要）
     - 方案C: 保持现状（后端忽略）

---

## 9. 测试检查清单

### 登录流程
- [ ] 微信登录成功返回 sessionToken
- [ ] userInfo 包含所有必要字段
- [ ] token 正确存储到本地storage
- [ ] 后续请求携带正确的 Authorization header

### 方案生成
- [ ] 所有必需字段都已填写
- [ ] 请求成功返回 plan_request_id
- [ ] departure_city 字段正确发送
- [ ] preferences 对象结构正确

### 方案查询
- [ ] 列表查询返回正确的分页数据
- [ ] 详情查询返回完整方案信息
- [ ] 权限验证正确（不能访问其他用户的方案）

### 错误处理
- [ ] 401错误自动跳转登录页
- [ ] 400错误显示验证错误信息
- [ ] 500错误显示友好提示并支持重试

---

## 10. 开发建议

### 前端开发
1. **严格按照后端DTO定义构建请求对象**
2. **使用TypeScript定义接口类型**（如果项目支持）
3. **在发送请求前打印请求数据到控制台**（开发环境）
4. **统一封装API调用函数**，避免字段名硬编码

### 后端开发
1. **所有DTO使用`@Valid`注解**，确保参数验证
2. **使用清晰的字段命名**（snake_case for JSON, camelCase for Java）
3. **API文档与代码同步**（OpenAPI/Swagger）
4. **提供清晰的错误信息**，帮助前端快速定位问题

### 协作建议
1. **接口变更前后端同步讨论**
2. **使用Postman Collection共享API测试用例**
3. **集成测试覆盖关键业务流程**
4. **定期review前后端字段映射文档**

---

**最后更新**: 2026-01-04
**维护者**: Claude Code
