# 小程序本地开发环境问题排查指南

**创建日期**: 2026-01-14
**适用场景**: 本地开发时遇到ERR_CONNECTION_REFUSED错误

---

## 问题症状

```
POST http://localhost/api/v1/auth/wechat/refresh net::ERR_CONNECTION_REFUSED
GET http://localhost/api/v1/users/me net::ERR_CONNECTION_REFUSED
Failed to load image http://api.teamventure.com/avatars/... net::ERR_CONNECTION_REFUSED
```

---

## 快速修复步骤

### 步骤1：启动Docker服务（如果未运行）

```bash
# 检查Docker Desktop是否运行
pgrep -fl "Docker Desktop"

# 如果未运行，启动Docker Desktop
open -a "Docker"

# 等待Docker完全启动（约30秒）
sleep 30

# 验证Docker可用
docker ps
```

### 步骤2：启动TeamVenture后端服务

```bash
cd /Users/qitmac001395/workspace/QAL/ideas/apps/teamventure

# 重启所有服务（使新配置生效）
make restart

# 检查服务健康状态
make health
```

**预期输出**：
```
Java 服务: {"status":"UP",...}
Python 服务: {"status":"healthy",...}
MySQL: mysqld is alive
Redis: PONG
```

### 步骤3：清除微信开发者工具缓存

**在微信开发者工具中**：
1. 点击顶部菜单：**工具** → **清除缓存**
2. 勾选：**清除所有缓存数据**（包括编译缓存、文件缓存、登录状态）
3. 点击"**确定**"
4. 点击"**编译**"按钮重新编译项目

**重要**：必须清除缓存，否则旧的config.js会继续使用！

### 步骤4：验证修复效果

**在微信开发者工具控制台中**：
```javascript
// 应该看到：
检查登录状态: {token: "...", userInfo: {...}}

// 而不是：
[API GET] /users/me 失败: {error: {code: "NETWORK_ERROR"}}
```

**成功标志**：
- ✅ 不再有`ERR_CONNECTION_REFUSED`错误
- ✅ 头像正常加载
- ✅ 方案列表正常加载

---

## 配置说明

### 当前本地开发配置（v1.7）

**前端配置** (`src/frontend/miniapp/utils/config.js`):
```javascript
const API_BASE_URLS = {
  local: 'http://localhost:8080/api/v1',  // 直接访问Java服务
  ...
}
```

**后端配置** (`src/.env.local`):
```properties
# Java服务端口
JAVA_SERVICE_PORT=8080

# OSS公共访问地址（MinIO）
TEAMVENTURE_OSS_PUBLIC_BASE_URL=http://localhost:9000
TEAMVENTURE_OSS_PRESIGN_ENDPOINT=http://localhost:9000
```

**服务端口映射**：
| 服务 | 容器内端口 | 宿主机端口 | 前端访问地址 |
|------|-----------|-----------|-------------|
| Java业务服务 | 8082 | 8080 | http://localhost:8080/api/v1 |
| MinIO对象存储 | 9000 | 9000 | http://localhost:9000 |
| Python AI服务 | 8000 | 8000 | http://localhost:8000 |

---

## 常见问题

### Q1: 清除缓存后仍然报错？

**检查配置文件是否生效**：
```javascript
// 在微信开发者工具控制台运行：
console.log(getApp().globalData.apiBaseUrl || '未设置')
```

**预期输出**：`http://localhost:8080/api/v1`

**如果不是**，检查是否有`wx.getStorageSync('apiBaseUrl')`覆盖。

### Q2: Java服务未启动？

**检查Java容器状态**：
```bash
docker ps | grep teamventure-java
```

**如果未运行**：
```bash
make up      # 启动所有服务
make logs-java  # 查看Java服务日志
```

### Q3: MinIO服务未启动？

**检查MinIO容器状态**：
```bash
docker ps | grep teamventure-minio
```

**验证MinIO可访问**：
```bash
curl http://localhost:9000/minio/health/live
```

预期输出：空响应（200 OK）

### Q4: 端口被占用？

**检查端口占用**：
```bash
lsof -i :8080  # Java服务端口
lsof -i :9000  # MinIO端口
```

**如果被占用**，停止占用进程或修改端口。

---

## 生产环境配置（通过Nginx）

**生产环境应使用Nginx反向代理**，统一入口：

**前端配置**：
```javascript
const API_BASE_URLS = {
  prod: 'https://api.teamventure.com/api/v1'
}
```

**Nginx配置** (`src/nginx/nginx.conf`):
```nginx
location /api/v1/ {
    proxy_pass http://java-business-service:8082/api/v1/;
}

location /avatars/ {
    proxy_pass http://minio:9000/avatars/;
}
```

**hosts配置** (`/etc/hosts`):
```
127.0.0.1 api.teamventure.com
```

**优点**：
- 统一域名，避免跨域问题
- 简化前端配置
- 支持HTTPS和负载均衡

---

## 调试技巧

### 查看小程序请求日志

**在微信开发者工具控制台**：
```javascript
// 查看当前环境
console.log(require('./utils/config.js').CURRENT_ENV)

// 查看当前API地址
console.log(require('./utils/config.js').API_BASE_URL)
```

### 手动测试API

**使用curl测试**：
```bash
# 测试健康检查
curl http://localhost:8080/actuator/health

# 测试方案列表（需要token）
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8080/api/v1/plans?page=1&pageSize=10
```

### 查看Java服务日志

```bash
make logs-java | tail -100
```

**关键日志标识**：
```
Started TeamVentureApplication  # 启动成功
Tomcat started on port 8082     # 端口监听
```

---

## 配置修改历史

| 版本 | 日期 | 变更 | Commit |
|-----|------|------|--------|
| v1.0 | 2026-01-14 | 初始配置（使用Nginx） | - |
| v1.1 | 2026-01-14 | 简化本地开发（直接访问端口） | 28c34ea |
| v1.2 | 2026-01-14 | 修复OSS地址配置 | (当前) |

---

## 总结

**本地开发环境配置要点**：
1. ✅ 前端：`http://localhost:8080/api/v1`
2. ✅ OSS：`http://localhost:9000`
3. ✅ Docker服务：必须运行
4. ✅ 清除缓存：每次修改配置后必须清除
5. ⚠️ 生产环境：必须使用Nginx统一代理

遇到问题先检查：Docker运行 → 服务健康 → 清除缓存 → 重新编译
