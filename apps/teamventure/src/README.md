# TeamVenture 开发环境配置指南

> **目标**: 在30分钟内搭建完整的本地开发环境
>
> **前置要求**: Docker、Java 17、Python 3.11、Maven、Poetry

---

## 📋 环境检查清单

### 必需工具

在开始之前，请确保已安装以下工具：

```bash
# Java环境
java -version
# 需要: openjdk version "17.0.x" 或更高

# Maven
mvn -version
# 需要: Apache Maven 3.8+

# Python环境
python3 --version
# 需要: Python 3.11+

# Poetry（Python包管理）
poetry --version
# 如未安装: curl -sSL https://install.python-poetry.org | python3 -

# Docker
docker --version
docker-compose --version
# 需要: Docker 20.10+、Docker Compose 2.0+

# Node.js（微信开发者工具依赖）
node --version
# 需要: Node.js 16+
```

---

## 🚀 快速启动（30分钟）

### Step 1: 启动基础设施（10分钟）

#### 1.1 创建 Docker Compose 配置

在 `src/` 目录下创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  # MySQL 主库
  mysql-master:
    image: mysql:8.0
    container_name: teamventure-mysql-master
    environment:
      MYSQL_ROOT_PASSWORD: root123456
      MYSQL_DATABASE: teamventure_main
      MYSQL_CHARACTER_SET_SERVER: utf8mb4
      MYSQL_COLLATION_SERVER: utf8mb4_unicode_ci
    ports:
      - "3306:3306"
    volumes:
      - mysql-master-data:/var/lib/mysql
      - ./database/schema:/docker-entrypoint-initdb.d
    command: --server-id=1 --log-bin=mysql-bin --binlog-format=ROW

  # MySQL 从库
  mysql-slave:
    image: mysql:8.0
    container_name: teamventure-mysql-slave
    environment:
      MYSQL_ROOT_PASSWORD: root123456
      MYSQL_DATABASE: teamventure_main
    ports:
      - "3307:3306"
    volumes:
      - mysql-slave-data:/var/lib/mysql
    command: --server-id=2 --relay-log=mysql-relay-bin

  # Redis
  redis:
    image: redis:7.0-alpine
    container_name: teamventure-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes

  # RabbitMQ
  rabbitmq:
    image: rabbitmq:3.12-management
    container_name: teamventure-rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: admin123456
    ports:
      - "5672:5672"    # AMQP端口
      - "15672:15672"  # 管理界面
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq

volumes:
  mysql-master-data:
  mysql-slave-data:
  redis-data:
  rabbitmq-data:
```

#### 1.2 启动所有服务

```bash
# 在 src/ 目录下执行
docker-compose up -d

# 查看服务状态
docker-compose ps

# 预期输出：
# NAME                       STATUS    PORTS
# teamventure-mysql-master   Up        0.0.0.0:3306->3306/tcp
# teamventure-mysql-slave    Up        0.0.0.0:3307->3306/tcp
# teamventure-redis          Up        0.0.0.0:6379->6379/tcp
# teamventure-rabbitmq       Up        0.0.0.0:5672->5672/tcp, 0.0.0.0:15672->15672/tcp
```

#### 1.3 验证服务

```bash
# 验证MySQL
mysql -h 127.0.0.1 -P 3306 -u root -proot123456 -e "SELECT VERSION();"

# 验证Redis
redis-cli ping
# 预期输出: PONG

# 验证RabbitMQ（浏览器访问）
# http://localhost:15672
# 用户名: admin, 密码: admin123456
```

---

### Step 2: 初始化数据库（5分钟）

#### 2.1 执行DDL脚本

```bash
# 连接MySQL主库
mysql -h 127.0.0.1 -P 3306 -u root -proot123456 teamventure_main

# 执行初始化脚本
mysql> source database/schema/V1.0.0__init.sql;

# 执行供应商种子数据（如果有）
mysql> source database/schema/V1.0.1__seed_suppliers.sql;

# 验证表结构
mysql> SHOW TABLES;
# 预期输出：
# +---------------------------+
# | Tables_in_teamventure_main|
# +---------------------------+
# | users                     |
# | sessions                  |
# | plan_requests             |
# | plans                     |
# | suppliers                 |
# | supplier_contact_logs     |
# | domain_events             |
# +---------------------------+
```

#### 2.2 配置主从复制（可选）

```bash
# 在主库创建复制用户
mysql -h 127.0.0.1 -P 3306 -u root -proot123456 -e "
CREATE USER 'repl'@'%' IDENTIFIED WITH mysql_native_password BY 'repl123456';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';
FLUSH PRIVILEGES;
SHOW MASTER STATUS;
"

# 记下 File 和 Position 的值（例如: mysql-bin.000003, 157）

# 在从库配置复制
mysql -h 127.0.0.1 -P 3307 -u root -proot123456 -e "
CHANGE MASTER TO
  MASTER_HOST='mysql-master',
  MASTER_USER='repl',
  MASTER_PASSWORD='repl123456',
  MASTER_LOG_FILE='mysql-bin.000003',
  MASTER_LOG_POS=157;
START SLAVE;
SHOW SLAVE STATUS\G
"

# 确认 Slave_IO_Running 和 Slave_SQL_Running 都是 Yes
```

---

### Step 3: 启动Java服务（10分钟）

#### 3.1 配置Java项目

```bash
cd backend/java-business-service

# 创建项目骨架（如果还没创建）
mvn archetype:generate \
  -DgroupId=com.teamventure \
  -DartifactId=teamventure-business \
  -DarchetypeArtifactId=maven-archetype-quickstart \
  -DinteractiveMode=false
```

#### 3.2 配置 application.yml

在 `src/main/resources/application.yml` 中配置：

```yaml
spring:
  application:
    name: teamventure-business

  # 数据源（主库）
  datasource:
    master:
      jdbc-url: jdbc:mysql://localhost:3306/teamventure_main?useSSL=false&serverTimezone=Asia/Shanghai&characterEncoding=utf8mb4
      username: root
      password: root123456
      driver-class-name: com.mysql.cj.jdbc.Driver

    # 数据源（从库）
    slave:
      jdbc-url: jdbc:mysql://localhost:3307/teamventure_main?useSSL=false&serverTimezone=Asia/Shanghai&characterEncoding=utf8mb4
      username: root
      password: root123456
      driver-class-name: com.mysql.cj.jdbc.Driver

  # Redis配置
  redis:
    host: localhost
    port: 6379
    timeout: 3000ms

  # RabbitMQ配置
  rabbitmq:
    host: localhost
    port: 5672
    username: admin
    password: admin123456

# MyBatis配置
mybatis-plus:
  mapper-locations: classpath*:/mapper/**/*.xml
  type-aliases-package: com.teamventure.domain
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.slf4j.Slf4jImpl

# 服务端口
server:
  port: 8080
```

#### 3.3 启动Java服务

```bash
# 安装依赖
mvn clean install

# 启动服务
mvn spring-boot:run

# 验证服务
curl http://localhost:8080/actuator/health
# 预期输出: {"status":"UP"}
```

---

### Step 4: 启动Python AI服务（5分钟）

#### 4.1 配置Python项目

```bash
cd backend/python-ai-service

# 初始化项目（如果还没初始化）
poetry init

# 添加依赖
poetry add fastapi uvicorn langgraph openai redis httpx pydantic python-dotenv
poetry add --group dev pytest pytest-asyncio black ruff
```

#### 4.2 配置环境变量

创建 `.env` 文件（或使用 `.env.local`）：

```bash
# OpenAI API
OPENAI_API_KEY=sk-xxx  # 替换为真实的API Key（Mock模式下可不填）
OPENAI_MODEL=gpt-4-0125-preview

# ⚠️ AI Mock模式（开发测试时建议开启以节省token）
# true=使用mock数据（不调用OpenAI），false=调用真实AI
ENABLE_AI_MOCK=true

# AI缓存配置（相同输入24小时内复用结果，减少token消耗）
AI_CACHE_ENABLED=true
AI_CACHE_TTL_SECONDS=86400

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis123456

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=admin123456

# Java服务回调地址
JAVA_CALLBACK_URL=http://localhost:8080/internal/plans/batch
JAVA_INTERNAL_SECRET=change-this-in-production

# 日志级别
LOG_LEVEL=INFO
```

**💡 Token优化建议**：
- 开发阶段设置 `ENABLE_AI_MOCK=true`（完全不消耗token）
- 需要测试AI质量时临时改为 `false`
- 详细说明见：`backend/python-ai-service/docs/AI_TOKEN_OPTIMIZATION.md`

#### 4.3 启动Python服务

```bash
# 安装依赖
poetry install

# 启动服务
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 验证服务
curl http://localhost:8000/health
# 预期输出: {"status":"healthy"}
```

---

### Step 5: 配置微信开发者工具（可选）

#### 5.1 下载安装

访问 [微信开发者工具官网](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html) 下载安装。

#### 5.2 导入项目

1. 打开微信开发者工具
2. 选择"导入项目"
3. 项目目录: `apps/teamventure/src/frontend/miniapp`
4. AppID: 使用测试号或真实AppID
5. 点击"导入"

#### 5.3 配置后端地址

在 `miniapp/utils/config.js` 中配置：

```javascript
export const API_BASE_URL = 'http://localhost:8080/api/v1'
```

---

## 🔧 开发工作流

### 日常开发

```bash
# 启动所有基础设施
cd apps/teamventure/src
docker-compose up -d

# Terminal 1: 启动Java服务
cd backend/java-business-service
mvn spring-boot:run

# Terminal 2: 启动Python服务
cd backend/python-ai-service
poetry run uvicorn src.main:app --reload

# Terminal 3: 启动小程序（微信开发者工具）
# 手动点击"编译"
```

### 停止服务

```bash
# 停止Java服务: Ctrl+C

# 停止Python服务: Ctrl+C

# 停止基础设施
docker-compose down

# 停止并清除数据卷（危险操作！）
docker-compose down -v
```

---

## 📊 服务端口清单

| 服务 | 端口 | 访问地址 | 用途 |
|------|------|---------|------|
| **Java业务服务** | 8080 | http://localhost:8080 | REST API |
| **Python AI服务** | 8000 | http://localhost:8000 | AI生成服务 |
| **MySQL主库** | 3306 | localhost:3306 | 写操作 |
| **MySQL从库** | 3307 | localhost:3307 | 读操作 |
| **Redis** | 6379 | localhost:6379 | 缓存+Session |
| **RabbitMQ** | 5672 | localhost:5672 | 消息队列 |
| **RabbitMQ管理界面** | 15672 | http://localhost:15672 | 队列管理 |

---

## 🧪 测试环境

### 单元测试

```bash
# Java单元测试
cd backend/java-business-service
mvn test

# Python单元测试
cd backend/python-ai-service
poetry run pytest tests/unit/

# 查看覆盖率
poetry run pytest --cov=src tests/
```

### 集成测试

```bash
# Java集成测试
mvn verify

# Python集成测试
poetry run pytest tests/integration/
```

---

## 🐛 常见问题

### MySQL连接失败

```bash
# 问题: Can't connect to MySQL server on 'localhost'
# 解决: 确认Docker容器正在运行
docker-compose ps

# 如果状态不是Up，重启容器
docker-compose restart mysql-master
```

### RabbitMQ连接超时

```bash
# 问题: Connection refused on localhost:5672
# 解决: 检查RabbitMQ日志
docker-compose logs rabbitmq

# 确认用户名密码正确
docker exec teamventure-rabbitmq rabbitmqctl list_users
```

### 端口冲突

```bash
# 问题: Bind for 0.0.0.0:3306 failed: port is already allocated
# 解决: 修改docker-compose.yml中的端口映射
# 例如: "3316:3306" 代替 "3306:3306"
```

### OpenAI API调用失败

```bash
# 问题: openai.error.AuthenticationError: Incorrect API key
# 解决: 检查.env文件中的OPENAI_API_KEY是否正确
cat backend/python-ai-service/.env | grep OPENAI_API_KEY

# 验证API Key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer sk-xxx"
```

---

## 📚 参考文档

### 开发规范
- [详细设计文档](../docs/design/detailed-design.md) - 架构、代码规范、Git提交规范
- [数据库设计](../docs/design/database-design.md) - 表结构、索引、分表策略
- [API设计](../docs/design/api-design.md) - 接口规范、错误码

### 技术文档
- [COLA架构官方文档](https://github.com/alibaba/COLA)
- [LangGraph文档](https://langchain-ai.github.io/langgraph/)
- [微信小程序开发文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)

---

## 🤝 贡献指南

### 提交代码

```bash
# 1. 创建功能分支
git checkout -b feature/user-login

# 2. 开发功能

# 3. 提交代码（遵循规范）
git commit -m "feat(auth): 实现微信登录功能

- 添加微信登录API
- 实现session管理
- 添加单元测试

Closes #123
"

# 4. 推送分支
git push origin feature/user-login

# 5. 创建Pull Request
```

### Code Review清单

- [ ] 代码遵循COLA架构规范
- [ ] 写操作使用主库，读操作使用从库
- [ ] 添加了充分的单元测试（覆盖率 > 80%）
- [ ] 添加了必要的注释
- [ ] 通过了所有CI检查
- [ ] API文档已更新

---

**最后更新**: 2025-12-30
**维护者**: TeamVenture开发团队
