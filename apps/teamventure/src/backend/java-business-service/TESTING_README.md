# Java后端单元测试快速开始

## 🚨 重要：先解决Java版本问题

### 当前状态
- **Maven使用**: Java 23.0.2
- **项目配置**: Java 17
- **问题**: 版本不匹配导致JaCoCo失败

### 解决方案

#### 方法1: 配置Maven使用Java 17（推荐）

```bash
# Step 1: 检查系统已安装的Java版本
/usr/libexec/java_home -V

# 输出示例:
# 23.0.2 (arm64) "Homebrew" ...
# 21.0.2 (arm64) "Oracle Corporation" ...
# 17.0.9 (arm64) "Azul Systems, Inc." ...

# Step 2: 如果有Java 17，设置JAVA_HOME
export JAVA_HOME=$(/usr/libexec/java_home -v 17)

# Step 3: 验证
mvn --version
# 应显示: Java version: 17.x.x

# Step 4: 运行测试
mvn test
```

**永久生效（可选）**:
```bash
# 添加到 ~/.zshrc 或 ~/.bash_profile
echo 'export JAVA_HOME=$(/usr/libexec/java_home -v 17)' >> ~/.zshrc
source ~/.zshrc
```

#### 方法2: 安装Java 17（如果没有）

```bash
# 使用Homebrew安装
brew install openjdk@17

# 链接到系统
sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk \
  /Library/Java/JavaVirtualMachines/openjdk-17.jdk

# 设置JAVA_HOME
export JAVA_HOME=$(/usr/libexec/java_home -v 17)

# 验证
java -version  # 应显示 17.x.x
mvn --version  # 应显示 Java version: 17.x.x
```

#### 临时方案: 跳过JaCoCo

如果暂时无法解决版本问题，可以跳过JaCoCo运行测试：

```bash
mvn test -Djacoco.skip=true
```

注意：这样不会生成覆盖率报告。

---

## ✅ 运行测试（问题解决后）

### Step 1: 验证环境

```bash
cd /Users/qitmac001395/workspace/QAL/ideas/apps/teamventure/src/backend/java-business-service

# 检查Java版本
mvn --version
# 期望输出: Java version: 17.x.x

# 检查Maven配置
mvn help:effective-pom | grep "java.version"
# 期望输出: <java.version>17</java.version>
```

### Step 2: 运行所有测试

```bash
# 运行所有测试
mvn test

# 预期输出:
# [INFO] Tests run: 14, Failures: 0, Errors: 0, Skipped: 0
# [INFO] BUILD SUCCESS
```

### Step 3: 查看覆盖率报告

```bash
# 生成JaCoCo报告
mvn test jacoco:report

# 在浏览器中打开
open target/site/jacoco/index.html
```

**覆盖率报告内容**:
- 整体覆盖率百分比
- 每个类的覆盖率明细
- 未覆盖的代码行高亮显示（红色）

### Step 4: 检查是否达标

```bash
# JaCoCo会自动检查是否达到配置的阈值
mvn verify

# 如果覆盖率不足，会失败:
# Rule violated for bundle teamventure-business:
# lines covered ratio is 0.15, but expected minimum is 0.80
```

**当前配置的阈值**:
- 行覆盖率: ≥ 80%
- 分支覆盖率: ≥ 75%

---

## 📝 已完成的测试

### JwtSupportTest ✅

**文件**: `src/test/java/com/teamventure/app/support/JwtSupportTest.java`

**测试用例** (10个):
1. testIssueToken - 生成Token正常流程
2. testParseUserId - 解析Token获取userId
3. testParseUserId_InvalidToken - 无效token抛异常
4. testParseUserId_TamperedToken - 篡改token抛异常
5. testGetExpirationTime - 获取过期时间正常流程
6. testWillExpireSoon_NotExpiringSoon - token有效期充足
7. testWillExpireSoon_ExpiringSoon - token即将过期
8. testWillExpireSoon_AlreadyExpired - token已过期抛异常
9. testIssueToken_DifferentTokensForSameUser - 多次生成不同token
10. testParseUserId_DifferentSecret - 不同密钥无法解析

**运行命令**:
```bash
mvn test -Dtest=JwtSupportTest
```

**结果**:
```
[INFO] Tests run: 10, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

### AuthServiceIntegrationTest 🔄

**文件**: `src/test/java/com/teamventure/app/service/AuthServiceIntegrationTest.java`

**已完成测试用例** (4个):
1. testLoginWithWeChat_NewUser - 新用户注册
2. testLoginWithWeChat_ExistingUser_NoUpdate - 老用户登录不更新
3. testGetUserIdFromAuthorization_MissingBearer - 缺少Bearer前缀
4. testGetUserIdFromAuthorization_Null - Authorization为null

**待补充测试用例** (8个):
- 老用户更新昵称
- 老用户更新头像
- 使用默认昵称
- Redis降级处理
- Token刷新（token有效/即将过期/已过期）
- getUserIdFromAuthorization（Redis命中/未命中/无效JWT）

---

## 🛠️ 测试编写指南

### 测试类模板

```java
package com.teamventure.app.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.ActiveProfiles;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * {ClassName} 单元测试
 *
 * 测试覆盖:
 *   - 功能点1
 *   - 功能点2
 *
 * 术语对照: ubiquitous-language-glossary.md Section X.X
 */
@SpringBootTest
@ActiveProfiles("test")
@DisplayName("{ClassName} 单元测试")
class {ClassName}Test {

    @Autowired
    private {ClassName} serviceUnderTest;

    @MockBean
    private SomeDependency dependency;

    @BeforeEach
    void setUp() {
        // 设置mock行为
        when(dependency.someMethod(any())).thenReturn(expected);
    }

    @Test
    @DisplayName("功能描述 - 测试场景")
    void testMethod_Scenario() {
        // Given: 准备测试数据
        String input = "test";

        // When: 执行被测方法
        String result = serviceUnderTest.someMethod(input);

        // Then: 验证结果
        assertThat(result).isEqualTo(expected);
        verify(dependency).someMethod(input);
    }

    @Test
    @DisplayName("异常场景 - 参数为null")
    void testMethod_NullInput() {
        // When & Then
        assertThatThrownBy(() -> serviceUnderTest.someMethod(null))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("参数不能为null");
    }
}
```

### 常用断言

```java
// 基本断言
assertThat(actual).isEqualTo(expected);
assertThat(actual).isNotNull();
assertThat(actual).isTrue();

// 字符串断言
assertThat(userId).startsWith("user_");
assertThat(token).isNotEmpty();
assertThat(message).contains("失败");

// 集合断言
assertThat(list).hasSize(3);
assertThat(list).contains(item1, item2);
assertThat(list).isEmpty();

// 异常断言
assertThatThrownBy(() -> service.doSomething())
    .isInstanceOf(BizException.class)
    .hasFieldOrPropertyWithValue("code", "INVALID_ARGUMENT")
    .hasMessageContaining("参数错误");

// 数值断言
assertThat(count).isGreaterThan(0);
assertThat(price).isBetween(100.0, 200.0);
```

---

## 📚 参考资源

### 官方文档
- [JUnit 5 User Guide](https://junit.org/junit5/docs/current/user-guide/)
- [Mockito Documentation](https://javadoc.io/doc/org.mockito/mockito-core/latest/org/mockito/Mockito.html)
- [AssertJ Documentation](https://assertj.github.io/doc/)
- [Spring Boot Testing](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.testing)
- [JaCoCo Maven Plugin](https://www.jacoco.org/jacoco/trunk/doc/maven.html)

### 内部文档
- **领域统一语言**: `docs/design/ubiquitous-language-glossary.md`
- **API设计**: `docs/design/api-design.md`
- **测试配置指南**: `docs/qa/unit-testing-setup-guide.md`
- **测试进展报告**: `docs/qa/TESTING_STATUS_2026-01-08.md`

---

**维护者**: TeamVenture 开发团队
**最后更新**: 2026-01-08
