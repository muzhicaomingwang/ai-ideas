# 前端小程序本地测试指南

> **版本**: v1.2
> **更新日期**: 2025-01-03
> **适用范围**: TeamVenture 小程序前后端联调测试

---

## 1. 环境准备

### 1.1 必要工具

- **微信开发者工具**: 版本 ≥ 1.06.2307260
- **Node.js**: 版本 ≥ 16.x
- **Docker Desktop**: 用于运行后端服务

### 1.2 后端服务准备

确保以下服务已启动并正常运行：

```bash
cd /Users/qitmac001395/workspace/QAL/ideas/apps/teamventure/src

# 启动所有服务
docker-compose up -d

# 检查服务状态
docker-compose ps

# 预期结果：所有服务状态为 Up (healthy)
# - teamventure-nginx
# - teamventure-java
# - teamventure-mysql-master
# - teamventure-redis
# - teamventure-rabbitmq
```

### 1.3 验证后端服务

```bash
# 测试 Nginx 网关
curl http://localhost
# 预期输出: {"message":"TeamVenture API Gateway","version":"1.0.0"}

# 测试 Java 服务健康检查
curl http://localhost/actuator/health
# 预期输出: {"status":"UP"}

# 测试 MySQL 连接
docker exec teamventure-mysql-master mysql -u root -proot123456 -e "SHOW DATABASES;"
# 预期输出: 包含 teamventure_main 数据库
```

---

## 2. 前端配置

### 2.1 配置文件检查

**文件位置**: `src/frontend/miniapp/utils/config.js`

**关键配置项**:

```javascript
// 1. 关闭 Mock 模式
export const USE_MOCK_DATA = false

// 2. 确认环境为 local
const ENV = 'local'

// 3. 确认本地 API 地址
const API_BASE_URLS = {
  local: 'http://localhost/api/v1',  // 通过 Docker Nginx 网关
  // ...
}

// 4. 确认登录端点路径
export const API_ENDPOINTS = {
  USER_LOGIN: '/auth/wechat/login',  // 注意：不是 /users/login
  // ...
}
```

**完整 API URL**: `http://localhost/api/v1/auth/wechat/login`

### 2.2 微信开发者工具配置

#### 步骤 1: 打开项目

1. 启动微信开发者工具
2. 选择"导入项目"
3. 项目目录: `src/frontend/miniapp`
4. AppID: 使用测试号或真实 AppID

#### 步骤 2: 配置本地服务器

**⚠️ 重要**: 必须配置以下选项，否则无法访问 localhost API

1. 点击右上角"详情"按钮
2. 切换到"本地设置" tab
3. **必须勾选**以下选项：
   - ✅ **不校验合法域名、web-view（业务域名）、TLS版本以及HTTPS证书**
   - ✅ **不校验安全域名、TLS版本以及HTTPS证书**
   - ✅ **启用调试**

4. 可选勾选（推荐）：
   - ✅ **ES6 转 ES5**
   - ✅ **样式自动补全**
   - ✅ **上传代码时样式自动补全**

#### 步骤 3: 配置网络代理（如需要）

如果开发环境使用了代理，需要在"代理设置"中配置：

1. 点击"详情" → "代理设置"
2. 选择"不使用代理"或根据实际情况配置

---

## 3. 功能测试流程

### 3.1 登录功能测试

#### 测试步骤

1. **启动小程序**
   - 编译并运行小程序
   - 点击底部 Tab "我的"

2. **触发登录**
   - 点击"点击登录"按钮
   - 观察控制台输出

3. **填写用户信息**
   - 点击"微信一键登录"按钮（获取 code）
   - 点击头像选择按钮，选择一张图片
   - 在昵称输入框输入昵称（如"测试用户123"）
   - 点击"完成登录"按钮

4. **观察网络请求**（开发者工具 → 调试器 → Network）
   ```
   请求 URL: http://localhost/api/v1/auth/wechat/login
   请求方法: POST
   请求体: {
     "code": "WECHAT_CODE",
     "nickname": "测试用户123",
     "avatarUrl": "https://thirdwx.qlogo.cn/..."
   }

   响应: {
     "success": true,
     "data": {
       "sessionToken": "eyJhbGc...",
       "userInfo": {
         "user_id": "user_xxx",
         "nickname": "测试用户123",
         "avatar": "https://...",
         "phone": "",
         "company": "",
         "role": "HR"
       }
     }
   }
   ```

5. **验证本地存储**（开发者工具 → 调试器 → Storage → Storage）
   ```javascript
   // 检查 sessionToken
   wx.getStorageSync('sessionToken')
   // 应返回 JWT token

   // 检查 userInfo
   wx.getStorageSync('userInfo')
   // 应返回完整的用户信息对象
   ```

6. **验证页面显示**
   - 登录成功后自动跳转首页
   - 点击底部 Tab "我的"
   - 验证用户头像和昵称正确显示

#### 验证后端数据存储

```bash
# 查询 MySQL users 表
docker exec teamventure-mysql-master mysql -u root -proot123456 -D teamventure_main -e \
  "SELECT user_id, wechat_openid, nickname, avatar_url, role, status, create_time FROM users ORDER BY create_time DESC LIMIT 1;"

# 预期结果：
# - nickname 为 "测试用户123"
# - avatar_url 包含微信临时 URL
# - role 为 "HR"
# - status 为 "ACTIVE"

# 查询 Redis session
docker exec teamventure-redis redis-cli -a redis123456 KEYS "session:*"
# 应返回 session key

docker exec teamventure-redis redis-cli -a redis123456 GET "session:{JWT_TOKEN}"
# 应返回 user_id
```

### 3.2 方案生成功能测试

#### 测试步骤

1. **进入生成方案页**
   - 点击底部 Tab "生成方案"
   - 或从首页点击"立即体验"

2. **填写基础信息**（第1步）
   - 人数: 50
   - 预算: 最低 10000，最高 15000
   - 出发城市: 北京
   - 目的地: 密云（或从首页点击热门目的地预填）
   - 开始日期: 选择未来日期
   - 结束日期: 选择未来日期（比开始日期晚）
   - 点击"下一步"

3. **选择偏好**（第2步）
   - 活动类型: 团队协作
   - 住宿标准: 舒适型
   - 餐饮偏好: 农家菜
   - 特殊需求: （可选填写）
   - 点击"生成方案"

4. **观察生成过程**
   - 应显示 Loading 动画
   - 预期 60 秒内返回结果

5. **查看对比页**
   - 应展示 3 套方案（经济型、平衡型、品质型）
   - 每个方案显示总预算、人均、天数、亮点

6. **进入详情页**
   - 点击任意方案"查看详情"
   - 验证行程、预算、供应商信息完整显示

7. **观察网络请求**
   ```
   请求 URL: http://localhost/api/v1/plans/generate
   请求方法: POST
   请求头: Authorization: Bearer {JWT_TOKEN}
   请求体: {
     "peopleCount": 50,
     "budgetMin": 10000,
     "budgetMax": 15000,
     "startDate": "2025-02-01",
     "endDate": "2025-02-03",
     "departureCity": "北京",
     "destination": "密云",
     "preferences": {
       "activityTypes": ["team_building"],
       "accommodation": "standard",
       "dining": ["local"],
       "specialRequests": ""
     }
   }
   ```

#### 验证后端数据存储

```bash
# 查询 plan_requests 表
docker exec teamventure-mysql-master mysql -u root -proot123456 -D teamventure_main -e \
  "SELECT plan_request_id, user_id, people_count, budget_min, budget_max, departure_city, status FROM plan_requests ORDER BY create_time DESC LIMIT 1;"

# 查询 plans 表
docker exec teamventure-mysql-master mysql -u root -proot123456 -D teamventure_main -e \
  "SELECT plan_id, plan_type, plan_name, budget_total, duration_days, status FROM plans ORDER BY create_time DESC LIMIT 3;"

# 验证 user_id 关联正确
```

### 3.3 我的方案列表测试

#### 测试步骤

1. **进入我的方案页**
   - 点击底部 Tab "我的方案"

2. **验证列表显示**
   - 应显示刚才生成的方案
   - 方案卡片显示标题、目的地、预算、日期、状态

3. **测试左滑删除**
   - 左滑任意方案卡片
   - 点击"删除"按钮
   - 确认删除后方案消失

4. **测试下拉刷新**
   - 下拉列表
   - 应重新加载数据

5. **测试上拉加载更多**（如有超过 10 条方案）
   - 滚动到底部
   - 自动加载下一页

6. **点击方案卡片**
   - 进入详情页
   - 验证数据与对比页一致

### 3.4 退出登录测试

#### 测试步骤

1. **触发退出登录**
   - 点击底部 Tab "我的"
   - 点击"退出登录"按钮
   - 确认退出

2. **验证本地数据清除**
   ```javascript
   wx.getStorageSync('sessionToken')  // 应返回空
   wx.getStorageSync('userInfo')       // 应返回空
   ```

3. **验证页面状态**
   - "我的"页面应显示"点击登录"按钮
   - 不显示用户头像和昵称
   - 不显示统计数据卡片
   - 功能菜单仅显示部分项（设置、帮助、关于）

4. **验证访问控制**
   - 尝试访问"我的方案"
   - 应跳转到登录页或显示"请先登录"提示

---

## 4. 常见问题排查

### 4.1 网络请求失败

**症状**: 控制台报错 `request:fail`

**可能原因**:
1. 后端服务未启动
2. 微信开发者工具未勾选"不校验合法域名"
3. Docker 容器网络问题

**解决方法**:
```bash
# 1. 检查 Docker 服务状态
docker-compose ps

# 2. 检查 Nginx 日志
docker-compose logs nginx

# 3. 检查 Java 服务日志
docker-compose logs java-business-service

# 4. 测试 API 连通性
curl http://localhost/actuator/health

# 5. 重启开发者工具并重新勾选配置
```

### 4.2 登录失败：返回 401

**症状**: 登录请求返回 401 Unauthorized

**可能原因**:
1. 后端 JWT 配置问题
2. Redis 连接失败

**解决方法**:
```bash
# 检查 Redis 连接
docker exec teamventure-redis redis-cli -a redis123456 PING
# 应返回 PONG

# 检查 Java 服务环境变量
docker exec teamventure-java env | grep JWT

# 查看 Java 服务日志
docker-compose logs java-business-service | grep -i error
```

### 4.3 登录成功但用户信息未显示

**症状**: 登录返回成功，但"我的"页面未显示头像和昵称

**可能原因**:
1. 本地存储未正确写入
2. userInfo 数据结构不匹配

**解决方法**:
```javascript
// 在开发者工具控制台检查
console.log(wx.getStorageSync('userInfo'))

// 检查响应数据结构
// 应包含: user_id, nickname, avatar, phone, company, role
```

### 4.4 头像不显示

**症状**: 用户昵称显示正常，但头像显示占位符

**可能原因**:
1. 微信临时 URL 已过期（48小时）
2. 图片加载失败

**解决方法**:
- 重新登录以获取新的临时 URL
- 检查 avatar_url 字段是否为空
- 查看开发者工具 Network 是否有图片加载失败

### 4.5 方案生成超时

**症状**: 点击"生成方案"后一直 Loading，最终超时

**可能原因**:
1. Python AI 服务未启动或异常
2. RabbitMQ 连接失败
3. LLM API 调用超时

**解决方法**:
```bash
# 检查 Python 服务状态
docker-compose ps python-ai-service

# 检查 Python 服务日志
docker-compose logs python-ai-service

# 检查 RabbitMQ 状态
docker-compose ps rabbitmq

# 访问 RabbitMQ 管理界面
open http://localhost:15672
# 用户名: admin, 密码: admin123456
```

### 4.6 数据库连接失败

**症状**: 后端服务日志显示数据库连接错误

**解决方法**:
```bash
# 检查 MySQL 容器状态
docker-compose ps mysql-master

# 检查 MySQL 日志
docker-compose logs mysql-master

# 测试连接
docker exec teamventure-mysql-master mysql -u root -proot123456 -e "SELECT 1;"

# 如果连接失败，重启 MySQL
docker-compose restart mysql-master
```

---

## 5. 测试检查清单

### 5.1 环境配置检查

- [ ] Docker 所有服务已启动（docker-compose ps）
- [ ] Nginx 网关可访问（curl http://localhost）
- [ ] Java 服务健康检查通过（curl http://localhost/actuator/health）
- [ ] MySQL 数据库已初始化（7 个表已创建）
- [ ] Redis 连接正常（redis-cli PING）
- [ ] 前端 config.js 中 USE_MOCK_DATA = false
- [ ] 前端 API_BASE_URL = 'http://localhost/api/v1'
- [ ] 微信开发者工具已勾选"不校验合法域名"

### 5.2 登录功能检查

**术语对照**: 参考 ubiquitous-language-glossary.md Section 2.1, 4.4, 7.1

#### 首次登录流程
- [ ] wx.login() 成功获取 code
- [ ] 头像选择器正常弹出并返回临时路径
- [ ] 昵称输入框支持输入
- [ ] 登录请求发送到 http://localhost/api/v1/auth/wechat/login
- [ ] 后端返回 sessionToken 和 userInfo
- [ ] sessionToken 存储到本地 storage
- [ ] userInfo 存储到本地 storage
- [ ] MySQL users 表创建新记录
- [ ] Redis 存储 session
- [ ] 登录成功后跳转首页

#### 继续使用（Token验证）
**术语**: `继续使用 = Continue = handleContinue`
**参考**: api-design.md Section 2.3

- [ ] 已登录状态下显示"继续使用"按钮
- [ ] 点击按钮显示"验证中..."加载提示
- [ ] 发送 GET /users/me 请求验证token
- [ ] Token有效：隐藏加载，跳转首页
- [ ] Token无效：显示"请重新登录"提示，清除登录状态

**测试Token验证失败场景**:
```bash
# 手动删除 Redis session 模拟token失效
docker exec teamventure-redis redis-cli -a redis123456 DEL "session:{{token}}"
# 然后点击"继续使用"，应提示重新登录
```

#### 切换账号功能
**术语**: `切换账号 = Switch Account = handleReLogin`
**参考**: ubiquitous-language-glossary.md Section 4.4

- [ ] 已登录状态下显示"切换账号"入口
- [ ] 点击后显示"请重新登录"提示
- [ ] 清除本地 sessionToken
- [ ] 清除本地 userInfo
- [ ] 清除全局 app.globalData.isLogin 和 userInfo
- [ ] 页面状态重置为未登录（显示微信登录按钮）

#### 退出登录（从其他页面）
- [ ] "我的"页面显示用户头像和昵称
- [ ] 首页导航栏显示用户头像和昵称
- [ ] 退出登录清除所有本地数据
- [ ] 退出后再次进入登录页显示未登录状态

### 5.3 方案生成检查

- [ ] 填写表单数据正确提交
- [ ] 请求携带 Authorization header
- [ ] 后端验证 token 成功
- [ ] 60 秒内返回 3 套方案
- [ ] 对比页正确显示方案信息
- [ ] 详情页行程、预算、供应商信息完整
- [ ] MySQL plan_requests 表创建记录
- [ ] MySQL plans 表创建 3 条记录
- [ ] user_id 关联正确

### 5.4 我的方案检查

- [ ] 列表正确显示当前用户方案
- [ ] 不显示其他用户方案
- [ ] 左滑删除功能正常
- [ ] 下拉刷新功能正常
- [ ] 上拉加载更多功能正常（如适用）
- [ ] 点击方案卡片进入详情

### 5.5 首页功能检查

**术语对照**: 参考 ubiquitous-language-glossary.md Section 4.4, 7.3

#### 自定义导航栏（Custom Navigation Bar）
**参考**: miniapp-ux-ui-specification.md Section 4.6 "自定义导航栏设计"

**未登录状态**:
- [ ] 导航栏显示"首页"标题（居中）
- [ ] 右上角显示"登录"按钮（半透明边框样式）
- [ ] 点击登录按钮跳转到登录页
- [ ] 状态栏高度自动适配（不同机型）
- [ ] Banner不被导航栏遮挡（padding-top动态计算）

**已登录状态**:
- [ ] 导航栏显示"首页"标题（居中）
- [ ] 右上角显示用户信息胶囊（User Info Capsule）
  - [ ] 头像显示正确（圆形，带边框）
  - [ ] 昵称显示正确（最多显示6个字符，超出省略）
  - [ ] 胶囊背景为半透明白色
- [ ] 点击用户信息胶囊弹出ActionSheet
  - [ ] 显示"个人中心"和"退出登录"选项
  - [ ] 点击"个人中心"显示"功能开发中"提示
  - [ ] 点击"退出登录"弹出确认对话框
  - [ ] 确认退出后清除登录状态

**头像占位符测试**:
- [ ] 用户未上传头像时显示 emoji 👤
- [ ] 头像占位符居中显示
- [ ] 占位符颜色为灰色（#999）

#### 页面内容
- [ ] Banner 正确显示（TeamVenture + 副标题）
- [ ] 快捷操作按钮正常跳转（生成方案、我的方案）
- [ ] 热门目的地横向滚动流畅
- [ ] 点击目的地正确预填到生成方案页
- [ ] 推荐方案列表正确显示
- [ ] 活动类型网格正确显示（3列×2行）

### 5.6 我的页面检查

- [ ] 未登录状态显示"点击登录"按钮
- [ ] 已登录状态显示用户头像和昵称
- [ ] 头像失效时显示占位符
- [ ] 统计数据正确加载（总方案、收藏、已完成）
- [ ] 功能菜单正常跳转
- [ ] 退出登录功能正常

---

## 6. 性能测试（可选）

### 6.1 并发登录测试

使用工具（如 JMeter、Apache Bench）模拟多用户同时登录：

```bash
# 使用 ab 工具测试
ab -n 100 -c 10 -T 'application/json' -p login.json http://localhost/api/v1/auth/wechat/login
```

**预期结果**:
- 100 个请求全部成功
- 平均响应时间 < 500ms
- 无数据库死锁或重复记录

### 6.2 方案生成压力测试

模拟多用户同时生成方案：

```bash
# 使用 ab 工具测试
ab -n 50 -c 5 -H "Authorization: Bearer {JWT_TOKEN}" -T 'application/json' -p generate.json http://localhost/api/v1/plans/generate
```

**预期结果**:
- 所有请求在 60 秒内完成
- 无 500 错误
- 数据库记录正确创建

---

## 7. 调试技巧

### 7.1 启用详细日志

**微信开发者工具**:
- 点击"详情" → "本地设置" → 勾选"显示调试信息"
- 查看 Console、Network、Storage 面板

**后端日志**:
```bash
# 实时查看 Java 服务日志
docker-compose logs -f java-business-service

# 实时查看 Nginx 日志
docker-compose logs -f nginx

# 实时查看所有服务日志
docker-compose logs -f
```

### 7.2 使用 Postman 测试后端 API

**登录 API 测试**:
```
POST http://localhost/api/v1/auth/wechat/login
Content-Type: application/json

{
  "code": "TEST_CODE",
  "nickname": "测试用户",
  "avatarUrl": "https://example.com/avatar.jpg"
}
```

**方案生成 API 测试**:
```
POST http://localhost/api/v1/plans/generate
Content-Type: application/json
Authorization: Bearer {JWT_TOKEN}

{
  "peopleCount": 50,
  "budgetMin": 10000,
  "budgetMax": 15000,
  "startDate": "2025-02-01",
  "endDate": "2025-02-03",
  "departureCity": "北京",
  "destination": "密云",
  "preferences": {
    "activityTypes": ["team_building"],
    "accommodation": "standard",
    "dining": ["local"],
    "specialRequests": ""
  }
}
```

### 7.3 数据库查询技巧

```bash
# 进入 MySQL 容器
docker exec -it teamventure-mysql-master mysql -u root -proot123456 -D teamventure_main

# 查询最新用户
SELECT * FROM users ORDER BY create_time DESC LIMIT 5;

# 查询最新方案请求
SELECT * FROM plan_requests ORDER BY create_time DESC LIMIT 5;

# 查询最新方案
SELECT * FROM plans ORDER BY create_time DESC LIMIT 10;

# 按用户查询方案
SELECT p.plan_id, p.plan_name, p.budget_total, pr.user_id
FROM plans p
JOIN plan_requests pr ON p.plan_request_id = pr.plan_request_id
WHERE pr.user_id = 'user_xxx'
ORDER BY p.create_time DESC;
```

---

## 8. 下一步

完成本地测试后，可以：

1. **执行完整 E2E 测试**
   - 参考: `docs/qa/checklist-and-testcases.md`
   - 执行: `docs/qa/scripts/run_backend_api_full_coverage.sh`

2. **修复发现的 Bug**
   - 记录在: `docs/qa/buglist.md`
   - 优先修复 P0、P1 级别 Bug

3. **准备测试环境部署**
   - 配置 dev 环境 API 地址
   - 配置微信小程序合法域名
   - 上传代码到微信后台

4. **性能优化**
   - 根据性能测试结果调优
   - 优化数据库查询
   - 优化前端渲染性能

---

## 9. 联系支持

如遇到无法解决的问题，请：

1. 检查本文档的"常见问题排查"部分
2. 查看后端服务日志
3. 查看微信开发者工具控制台
4. 提交 Issue 到项目 GitHub 仓库

---

**文档维护**: 请在每次功能更新后同步更新本文档。
