# TeamVenture 单元测试配置指南

**创建日期**: 2026-01-08
**目标**: 前后端单元测试100%覆盖率
**工具栈**:
- 后端: JUnit 5 + Mockito + JaCoCo
- 前端: ESLint + Jest (规划中)

---

## 1. 后端测试配置 (Java)

### 1.1 已完成配置

#### Maven依赖
```xml
<!-- 已添加到 pom.xml -->

<!-- 测试框架 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>  <!-- 包含 JUnit 5 + Mockito -->
    <scope>test</scope>
</dependency>

<!-- Mock final类支持 -->
<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-inline</artifactId>
    <version>5.2.0</version>
    <scope>test</scope>
</dependency>

<!-- 内存数据库（测试用） -->
<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>test</scope>
</dependency>
```

#### JaCoCo代码覆盖率插件
```xml
<!-- 已配置覆盖率目标: 行覆盖率80%, 分支覆盖率75% -->
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.12</version>
    <!-- 配置详见 pom.xml line 236-284 -->
</plugin>
```

#### 测试配置文件
- `src/test/resources/application-test.yml` - 测试环境配置
  - 使用H2内存数据库
  - Redis/RabbitMQ指向本地测试环境
  - 日志级别设为DEBUG

### 1.2 已完成的测试

#### ✅ JwtSupportTest (10个测试用例，100%通过)
**测试覆盖**:
- Token生成
- Token解析（正常/无效/篡改）
- 过期时间获取
- 即将过期判断（有效期充足/即将过期/已过期）
- Token完整性（多次生成不同）
- Token安全（不同密钥无法解析）

**运行命令**:
```bash
cd /Users/qitmac001395/workspace/QAL/ideas/apps/teamventure/src/backend/java-business-service
mvn test -Dtest=JwtSupportTest
```

**测试结果**:
```
[INFO] Tests run: 10, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

**文件位置**: `src/test/java/com/teamventure/app/support/JwtSupportTest.java`

#### 🔄 AuthServiceIntegrationTest (开发中)
**测试覆盖**（计划）:
- 新用户注册
- 老用户登录（无更新/更新昵称/更新头像）
- 默认昵称处理
- Redis降级处理
- getUserIdFromAuthorization（正常/异常）
- refreshTokenIfNeeded（刷新/不刷新/异常）

**当前状态**: 编译通过，待运行验证

**文件位置**:
- `src/test/java/com/teamventure/app/service/AuthServiceTest.java` (纯单元测试，有mock问题)
- `src/test/java/com/teamventure/app/service/AuthServiceIntegrationTest.java` (集成测试，推荐)

### 1.3 遇到的问题与解决方案

#### 问题1: Mockito无法mock StringRedisTemplate
**现象**:
```
Mockito cannot mock this class: class org.springframework.data.redis.core.StringRedisTemplate
```

**原因**: Java 23上Mockito默认无法mock final类

**解决方案**:
- ✅ 已添加 `mockito-inline` 依赖
- ✅ 改用 `@SpringBootTest + @MockBean` 进行集成测试

#### 问题2: JaCoCo与Java 23兼容性
**现象**:
```
Unsupported class file major version 67
```

**原因**:
- Maven使用Java 23编译 (version 67 = Java 23)
- pom.xml配置的是Java 17
- JaCoCo 0.8.11不支持Java 23

**解决方案**:
- ✅ 升级JaCoCo到0.8.12（已支持Java 21+）
- ⚠️ Maven仍使用Java 23，与pom.xml配置不一致

**临时方案**: 跳过JaCoCo运行测试
```bash
mvn test -Djacoco.skip=true
```

**长期方案**: 统一Java版本
```bash
# 方案A: 配置Maven使用Java 17
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
mvn test

# 方案B: 升级项目到Java 21
# 修改 pom.xml: <java.version>21</java.version>
```

### 1.4 待完成的测试

| Service类 | 优先级 | 预估用例数 | 状态 |
|----------|--------|-----------|------|
| AuthService | P0 | 12个 | 🔄 开发中 |
| JwtSupport | P0 | 10个 | ✅ 已完成 |
| PlanService | P0 | 15个 | ⏸️ 待开发 |
| SupplierService | P1 | 8个 | ⏸️ 待开发 |
| OssService | P1 | 6个 | ⏸️ 待开发 |
| IdGenerator | P2 | 5个 | ⏸️ 待开发 |
| Jsons (工具类) | P2 | 4个 | ⏸️ 待开发 |

| Controller类 | 优先级 | 预估用例数 | 状态 |
|------------|--------|-----------|------|
| AuthController | P0 | 8个 | ⏸️ 待开发 |
| UserController | P0 | 6个 | ⏸️ 待开发 |
| PlanController | P0 | 12个 | ⏸️ 待开发 |
| SupplierController | P1 | 6个 | ⏸️ 待开发 |

**预估总用例数**: ~92个测试用例

### 1.5 运行测试命令

```bash
cd /Users/qitmac001395/workspace/QAL/ideas/apps/teamventure/src/backend/java-business-service

# 运行所有测试
mvn test

# 运行特定测试类
mvn test -Dtest=JwtSupportTest

# 生成覆盖率报告
mvn test jacoco:report

# 查看覆盖率报告
open target/site/jacoco/index.html

# 检查覆盖率是否达标（80%行覆盖率，75%分支覆盖率）
mvn verify
```

---

## 2. 前端测试配置 (小程序)

### 2.1 已完成配置

#### ESLint配置
**文件**: `.eslintrc.json`

**规则说明**:
- 基于 `eslint-config-standard`
- 允许使用console（小程序调试需要）
- 支持微信小程序全局对象（wx, getApp, Page等）
- 字段命名规则：允许snake_case（与API对齐）

**全局对象**:
```json
{
  "globals": {
    "wx": "readonly",          // 微信API
    "getApp": "readonly",      // 获取App实例
    "getCurrentPages": "readonly",
    "Page": "readonly",        // 页面注册
    "Component": "readonly",   // 组件注册
    "App": "readonly"          // App注册
  }
}
```

**运行命令**:
```bash
cd /Users/qitmac001395/workspace/QAL/ideas/apps/teamventure/src/frontend/miniapp

# 安装依赖
npm install

# 运行Lint检查
npm run lint

# 自动修复
npm run lint:fix
```

#### 忽略文件配置
**文件**: `.eslintignore`

忽略以下目录：
- `node_modules/`
- `dist/`
- `.miniprogram/`
- `miniprogram_npm/`
- `*.min.js`

### 2.2 单元测试框架（规划中）

#### 方案选择

**选项1: miniprogram-simulate（官方推荐）**
- 优点：官方维护，API完整，适配小程序特性
- 缺点：配置复杂，文档较少
- 适用：需要测试wx API的场景

**选项2: Jest + jsdom（社区方案）**
- 优点：生态成熟，文档丰富，易于上手
- 缺点：需要mock所有wx API
- 适用：工具函数、纯逻辑测试

**推荐方案**: 结合使用
- utils层（纯JS逻辑）: Jest
- pages层（wx API依赖）: miniprogram-simulate

#### Jest配置（已添加到package.json）
```json
{
  "scripts": {
    "test": "jest",
    "test:coverage": "jest --coverage",
    "test:watch": "jest --watch"
  }
}
```

### 2.3 待创建的测试文件

| 文件 | 测试类型 | 优先级 | 预估用例数 |
|------|---------|--------|-----------|
| utils/config.js | 单元测试 | P0 | 5个 |
| utils/request.js | 单元测试 | P0 | 12个 |
| utils/format.js | 单元测试 | P1 | 8个 |
| pages/login/login.js | 集成测试 | P0 | 10个 |
| pages/home/home.js | 集成测试 | P1 | 8个 |
| pages/index/index.js | 集成测试 | P0 | 15个 |
| pages/myplans/myplans.js | 集成测试 | P1 | 10个 |

**预估总用例数**: ~68个测试用例

### 2.4 示例测试文件结构

```javascript
// tests/utils/config.test.js
import { API_BASE_URL, STORAGE_KEYS, ERROR_CODES } from '../../utils/config.js'

describe('Config - API_BASE_URL', () => {
  test('local环境返回localhost地址', () => {
    expect(API_BASE_URL).toContain('localhost')
  })
})

describe('Config - STORAGE_KEYS', () => {
  test('SESSION_TOKEN常量定义正确', () => {
    expect(STORAGE_KEYS.SESSION_TOKEN).toBe('sessionToken')
  })

  test('USER_INFO常量定义正确', () => {
    expect(STORAGE_KEYS.USER_INFO).toBe('userInfo')
  })
})

describe('Config - ERROR_CODES', () => {
  test('包含所有必需的错误码', () => {
    expect(ERROR_CODES.UNAUTHORIZED).toBe('UNAUTHORIZED')
    expect(ERROR_CODES.NETWORK_ERROR).toBe('NETWORK_ERROR')
    expect(ERROR_CODES.TIMEOUT).toBe('TIMEOUT')
  })
})
```

```javascript
// tests/utils/request.test.js
/**
 * request.js 单元测试
 *
 * 注意: 需要mock wx API
 */

// Mock wx全局对象
global.wx = {
  request: jest.fn(),
  getStorageSync: jest.fn(),
  setStorageSync: jest.fn(),
  removeStorageSync: jest.fn(),
  showLoading: jest.fn(),
  hideLoading: jest.fn(),
  showToast: jest.fn(),
  reLaunch: jest.fn(),
  switchTab: jest.fn()
}

import { get, post } from '../../utils/request.js'

describe('Request - refreshTokenIfNeeded', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('token不存在时返回false', async () => {
    wx.getStorageSync.mockReturnValue(null)
    // 测试逻辑...
  })

  test('token有效期充足时不刷新', async () => {
    // 测试逻辑...
  })

  test('token即将过期时自动刷新', async () => {
    // 测试逻辑...
  })
})
```

### 2.5 miniprogram-simulate 配置（待实施）

```bash
# 安装官方测试工具
npm install --save-dev miniprogram-simulate

# 创建测试文件
mkdir -p tests/pages
```

**示例测试**:
```javascript
// tests/pages/login.test.js
const simulate = require('miniprogram-simulate')

describe('Login Page', () => {
  let page

  beforeAll(() => {
    page = simulate.load('/pages/login/login')
  })

  test('未登录时显示微信登录按钮', () => {
    const button = page.querySelector('.btn-wechat-login')
    expect(button).not.toBeNull()
  })

  test('已登录时显示继续使用按钮', () => {
    page.setData({ isLogin: true })
    const button = page.querySelector('.btn-continue')
    expect(button).not.toBeNull()
  })

  test('点击继续使用触发token验证', async () => {
    page.setData({ isLogin: true })
    const button = page.querySelector('.btn-continue')

    // Mock API调用
    global.wx.request = jest.fn((options) => {
      options.success({ statusCode: 200, data: { success: true } })
    })

    button.dispatchEvent('tap')

    // 验证调用了 GET /users/me
    expect(global.wx.request).toHaveBeenCalledWith(
      expect.objectContaining({
        url: expect.stringContaining('/users/me'),
        method: 'GET'
      })
    )
  })
})
```

---

## 3. 当前测试覆盖率

### 3.1 后端（Java）

| 模块 | 类数 | 测试文件 | 用例数 | 覆盖率 | 状态 |
|------|------|---------|--------|--------|------|
| app.support.JwtSupport | 1 | JwtSupportTest | 10 | ~95% | ✅ 已完成 |
| app.service.AuthService | 1 | AuthServiceIntegrationTest | 4 | ~40% | 🔄 开发中 |
| app.service.PlanService | 1 | - | 0 | 0% | ⏸️ 待开发 |
| app.service.SupplierService | 1 | - | 0 | 0% | ⏸️ 待开发 |
| app.service.OssService | 1 | - | 0 | 0% | ⏸️ 待开发 |
| **整体** | **~20类** | **2个** | **14个** | **~15%** | 🔄 进行中 |

### 3.2 前端（JavaScript）

| 模块 | 文件数 | 测试文件 | 用例数 | 覆盖率 | 状态 |
|------|--------|---------|--------|--------|------|
| utils/ | 4 | 0 | 0 | 0% | ⏸️ 待开发 |
| pages/ | 6 | 0 | 0 | 0% | ⏸️ 待开发 |
| components/ | 2 | 0 | 0 | 0% | ⏸️ 待开发 |
| **整体** | **12个** | **0个** | **0个** | **0%** | ⏸️ 待开发 |

---

## 4. 测试编写规范

### 4.1 命名约定

**测试类命名**:
- 单元测试: `{ClassName}Test.java`（如 `JwtSupportTest.java`）
- 集成测试: `{ClassName}IntegrationTest.java`（如 `AuthServiceIntegrationTest.java`）
- 控制器测试: `{ClassName}ControllerTest.java`

**测试方法命名**:
```java
@Test
@DisplayName("功能描述 - 测试场景")
void test{Method}_{Scenario}() {
    // 例如: testLoginWithWeChat_NewUser()
}
```

### 4.2 测试结构（Given-When-Then）

```java
@Test
@DisplayName("登录成功 - 新用户注册")
void testLoginWithWeChat_NewUser() {
    // Given: 准备测试数据和mock行为
    when(userMapper.selectOne(any())).thenReturn(null);

    // When: 执行被测方法
    LoginResponse response = authService.loginWithWeChat("code", "张三", "");

    // Then: 验证结果和行为
    assertThat(response).isNotNull();
    verify(userMapper).insert(any());
}
```

### 4.3 断言库

**推荐使用 AssertJ**（已包含在 spring-boot-starter-test）:
```java
// 更清晰的断言
assertThat(response.sessionToken).isNotEmpty();
assertThat(user.getUserId()).startsWith("user_");
assertThatThrownBy(() -> service.doSomething())
    .isInstanceOf(BizException.class)
    .hasFieldOrPropertyWithValue("code", "INVALID_ARGUMENT");
```

### 4.4 Mock策略

**优先级**:
1. **真实对象**: 如果依赖简单（如POJO、工具类），直接使用真实对象
2. **@MockBean**: Spring管理的Bean（如Repository、Service）
3. **@Mock**: 非Spring管理的对象（如第三方API client）

**示例**:
```java
@SpringBootTest
class ServiceTest {
    @Autowired
    private ServiceUnderTest serviceUnderTest;  // 真实对象

    @MockBean
    private UserMapper userMapper;  // Mock Repository

    @Mock
    private ExternalApiClient apiClient;  // Mock 外部依赖
}
```

---

## 5. 前端测试规范（待实施）

### 5.1 utils层测试（纯逻辑）

**策略**: 使用Jest，不依赖wx API

**示例**:
```javascript
// tests/utils/format.test.js
describe('Format Utils', () => {
  test('formatPrice - 格式化价格', () => {
    expect(formatPrice(10000)).toBe('¥10,000')
    expect(formatPrice(0)).toBe('¥0')
    expect(formatPrice(null)).toBe('-')
  })

  test('formatDate - 格式化日期', () => {
    expect(formatDate('2026-01-08')).toBe('2026年1月8日')
  })
})
```

### 5.2 pages层测试（wx API依赖）

**策略**: Mock wx API

**示例**:
```javascript
// tests/pages/login.test.js
describe('Login Page - handleContinue', () => {
  beforeEach(() => {
    // Mock wx API
    global.wx = {
      showLoading: jest.fn(),
      hideLoading: jest.fn(),
      switchTab: jest.fn(),
      showToast: jest.fn(),
      getStorageSync: jest.fn(),
      removeStorageSync: jest.fn()
    }
  })

  test('token有效时跳转首页', async () => {
    // Mock successful API call
    const mockGet = jest.fn().mockResolvedValue({ user_id: 'test' })

    // 执行测试...
  })

  test('token无效时触发重新登录', async () => {
    // Mock API failure
    const mockGet = jest.fn().mockRejectedValue(new Error('invalid token'))

    // 执行测试，验证调用了 handleReLogin
  })
})
```

---

## 6. 代码覆盖率目标

### 6.1 后端目标

| 层级 | 目标覆盖率 | 当前覆盖率 | 优先级 |
|------|-----------|-----------|--------|
| **Service层** | 90%+ | ~15% | P0 |
| **Controller层** | 85%+ | 0% | P0 |
| **Support工具类** | 95%+ | ~95% | ✅ |
| **Domain实体** | 60%+ | 0% | P2 |
| **整体** | **80%+** | **~15%** | **P0** |

### 6.2 前端目标

| 层级 | 目标覆盖率 | 当前覆盖率 | 优先级 |
|------|-----------|-----------|--------|
| **utils层** | 95%+ | 0% | P0 |
| **pages层** | 70%+ | 0% | P1 |
| **components层** | 80%+ | 0% | P2 |
| **整体** | **75%+** | **0%** | **P0** |

---

## 7. 已知问题与待办事项

### 7.1 ⚠️ 阻塞问题

| 问题 | 影响范围 | 状态 | 解决方案 |
|------|---------|------|---------|
| Java版本不一致（Maven用23，pom.xml配17） | 后端测试运行 | 🔴 阻塞 | 统一Java版本或配置JAVA_HOME |
| Mockito无法mock StringRedisTemplate | AuthService测试 | 🟡 已缓解 | 改用@SpringBootTest |
| 小程序测试框架未配置 | 前端测试 | 🟡 计划中 | 安装miniprogram-simulate |

### 7.2 📋 待办清单

**后端（高优先级）**:
- [ ] 解决Java版本问题（配置Maven使用Java 17）
- [ ] 完成AuthService集成测试（当前4个用例，目标12个）
- [ ] 编写PlanService单元测试（15个用例）
- [ ] 编写Controller集成测试（26个用例）
- [ ] 运行完整测试套件，生成覆盖率报告
- [ ] 补充测试用例直到达到80%+覆盖率

**前端（高优先级）**:
- [ ] 安装npm依赖（eslint, jest）
- [ ] 运行ESLint检查并修复问题
- [ ] 配置Jest（创建jest.config.js）
- [ ] 编写utils层测试（config, request, format）
- [ ] 配置miniprogram-simulate
- [ ] 编写pages层测试（login, home, index）
- [ ] 生成前端覆盖率报告

---

## 8. 快速开始指南

### 8.1 后端测试快速开始

```bash
# Step 1: 进入后端项目目录
cd /Users/qitmac001395/workspace/QAL/ideas/apps/teamventure/src/backend/java-business-service

# Step 2: 运行现有测试
mvn test -Djacoco.skip=true

# Step 3: 查看测试结果
cat target/surefire-reports/*.txt

# Step 4: 如果有失败，查看详细日志
mvn test -Dtest=JwtSupportTest -X
```

### 8.2 前端测试快速开始

```bash
# Step 1: 进入前端项目目录
cd /Users/qitmac001395/workspace/QAL/ideas/apps/teamventure/src/frontend/miniapp

# Step 2: 安装依赖
npm install

# Step 3: 运行ESLint检查
npm run lint

# Step 4: 自动修复简单问题
npm run lint:fix

# Step 5: (待实施) 运行单元测试
npm test

# Step 6: (待实施) 生成覆盖率报告
npm run test:coverage
```

---

## 9. 参考文档

- **领域统一语言**: `docs/design/ubiquitous-language-glossary.md`
- **API设计**: `docs/design/api-design.md`
- **后端测试用例矩阵**: `docs/qa/backend-api-testcases-full.md`
- **前端测试用例**: `FRONTEND_TEST_CASES.md`
- **JUnit 5文档**: https://junit.org/junit5/docs/current/user-guide/
- **Mockito文档**: https://javadoc.io/doc/org.mockito/mockito-core/latest/org/mockito/Mockito.html
- **Jest文档**: https://jestjs.io/
- **miniprogram-simulate**: https://github.com/wechat-miniprogram/miniprogram-simulate

---

## 10. 术语对照

**测试术语** (参考 ubiquitous-language-glossary.md):

| 中文 | 英文 | 说明 |
|------|------|------|
| 单元测试 | Unit Test | 测试单个类/方法，mock所有依赖 |
| 集成测试 | Integration Test | 测试多个组件协作，使用真实依赖或@MockBean |
| 代码覆盖率 | Code Coverage | 测试执行过的代码比例 |
| 行覆盖率 | Line Coverage | 执行过的代码行比例 |
| 分支覆盖率 | Branch Coverage | 执行过的条件分支比例 |
| Mock | Mock | 模拟对象，替代真实依赖 |
| Stub | Stub | 预设行为的假对象 |

---

## 11. 下一步行动

### 立即执行（本周）:
1. ✅ 配置JaCoCo（已完成）
2. ✅ 配置ESLint（已完成）
3. ✅ 编写JwtSupport测试（已完成，10个用例全部通过）
4. 🔄 解决Java版本问题
5. 🔄 完成AuthService测试
6. 安装前端npm依赖并运行ESLint

### 短期目标（本月）:
- 后端：Service层测试覆盖率达到80%+
- 前端：utils层测试覆盖率达到90%+
- 建立CI/CD自动化测试流程

### 长期目标（本季度）:
- 后端：整体覆盖率达到85%+
- 前端：整体覆盖率达到75%+
- 所有核心功能100%测试覆盖

---

**最后更新**: 2026-01-08
**维护者**: 开发团队 + QA团队
