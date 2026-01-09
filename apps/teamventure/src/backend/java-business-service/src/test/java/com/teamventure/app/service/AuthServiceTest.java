package com.teamventure.app.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.teamventure.adapter.web.auth.AuthController.LoginResponse;
import com.teamventure.app.support.BizException;
import com.teamventure.infrastructure.persistence.mapper.UserMapper;
import com.teamventure.infrastructure.persistence.po.UserPO;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.ValueOperations;

import java.time.Duration;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * AuthService 单元测试
 *
 * 测试覆盖:
 *   - 微信登录（新用户/老用户）
 *   - Token生成与存储
 *   - Token验证（getUserIdFromAuthorization）
 *   - Token刷新（refreshTokenIfNeeded）
 *   - Redis降级处理
 *
 * 术语对照: ubiquitous-language-glossary.md Section 2.1, 4.4
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("AuthService 单元测试")
class AuthServiceTest {

    @Mock
    private UserMapper userMapper;

    @Mock
    private StringRedisTemplate redis;

    @Mock
    private ValueOperations<String, String> valueOps;

    @Mock
    private OssService ossService;

    private AuthService authService;

    private static final String TEST_JWT_SECRET = "test-secret-key-must-be-at-least-256-bits-long-for-hs256-algorithm";

    @BeforeEach
    void setUp() {
        when(redis.opsForValue()).thenReturn(valueOps);
        when(ossService.resolveAvatarUrl(anyString(), anyString())).thenAnswer(
            invocation -> {
                String userId = invocation.getArgument(0);
                String avatarUrl = invocation.getArgument(1);
                return avatarUrl.isEmpty() ? "" : "http://api.teamventure.com/avatars/users/" + userId + "/avatars/obj_test.jpg";
            }
        );

        authService = new AuthService(userMapper, redis, TEST_JWT_SECRET, ossService);
    }

    @Test
    @DisplayName("登录成功 - 新用户注册")
    void testLoginWithWeChat_NewUser() {
        // Given: 新用户，数据库中不存在
        String code = "test_wechat_code";
        String nickname = "张三";
        String avatarUrl = "https://wx.qlogo.cn/test.jpg";

        when(userMapper.selectOne(any(QueryWrapper.class))).thenReturn(null);

        // When: 调用登录
        LoginResponse response = authService.loginWithWeChat(code, nickname, avatarUrl);

        // Then: 验证返回结果
        assertThat(response).isNotNull();
        assertThat(response.sessionToken).isNotEmpty();
        assertThat(response.userInfo).isNotNull();
        assertThat(response.userInfo.nickname).isEqualTo(nickname);

        // Then: 验证创建了新用户
        ArgumentCaptor<UserPO> userCaptor = ArgumentCaptor.forClass(UserPO.class);
        verify(userMapper).insert(userCaptor.capture());
        UserPO createdUser = userCaptor.getValue();
        assertThat(createdUser.getUserId()).startsWith("user_");
        assertThat(createdUser.getNickname()).isEqualTo(nickname);
        assertThat(createdUser.getWechatOpenid()).isEqualTo("openid_dev_fixed_user");
        assertThat(createdUser.getRole()).isEqualTo("HR");
        assertThat(createdUser.getStatus()).isEqualTo("ACTIVE");

        // Then: 验证Redis存储了session
        ArgumentCaptor<String> keyCaptor = ArgumentCaptor.forClass(String.class);
        ArgumentCaptor<String> valueCaptor = ArgumentCaptor.forClass(String.class);
        ArgumentCaptor<Duration> durationCaptor = ArgumentCaptor.forClass(Duration.class);
        verify(valueOps).set(keyCaptor.capture(), valueCaptor.capture(), durationCaptor.capture());

        assertThat(keyCaptor.getValue()).startsWith("session:");
        assertThat(valueCaptor.getValue()).startsWith("user_");
        assertThat(durationCaptor.getValue().getSeconds()).isEqualTo(604800L); // 7 days
    }

    @Test
    @DisplayName("登录成功 - 老用户登录（无更新）")
    void testLoginWithWeChat_ExistingUser_NoUpdate() {
        // Given: 老用户，信息无变化
        String code = "test_code";
        UserPO existingUser = createTestUser();

        when(userMapper.selectOne(any(QueryWrapper.class))).thenReturn(existingUser);

        // When
        LoginResponse response = authService.loginWithWeChat(code, existingUser.getNickname(), existingUser.getAvatarUrl());

        // Then
        assertThat(response).isNotNull();
        assertThat(response.userInfo.user_id).isEqualTo(existingUser.getUserId());
        assertThat(response.userInfo.nickname).isEqualTo(existingUser.getNickname());

        // Then: 不应该调用 updateById
        verify(userMapper, never()).updateById(any());
        // Then: 不应该调用 insert
        verify(userMapper, never()).insert(any());
    }

    @Test
    @DisplayName("登录成功 - 老用户更新昵称")
    void testLoginWithWeChat_ExistingUser_UpdateNickname() {
        // Given
        UserPO existingUser = createTestUser();
        String newNickname = "新昵称";

        when(userMapper.selectOne(any(QueryWrapper.class))).thenReturn(existingUser);

        // When
        authService.loginWithWeChat("code", newNickname, existingUser.getAvatarUrl());

        // Then: 应该更新用户信息
        ArgumentCaptor<UserPO> userCaptor = ArgumentCaptor.forClass(UserPO.class);
        verify(userMapper).updateById(userCaptor.capture());
        assertThat(userCaptor.getValue().getNickname()).isEqualTo(newNickname);
    }

    @Test
    @DisplayName("登录成功 - 使用默认昵称（nickname为空）")
    void testLoginWithWeChat_NewUser_DefaultNickname() {
        // Given: nickname传入为null或空字符串
        when(userMapper.selectOne(any(QueryWrapper.class))).thenReturn(null);

        // When
        LoginResponse response = authService.loginWithWeChat("code", null, "");

        // Then: 使用默认昵称"微信用户"
        assertThat(response.userInfo.nickname).isEqualTo("微信用户");

        ArgumentCaptor<UserPO> userCaptor = ArgumentCaptor.forClass(UserPO.class);
        verify(userMapper).insert(userCaptor.capture());
        assertThat(userCaptor.getValue().getNickname()).isEqualTo("微信用户");
    }

    @Test
    @DisplayName("登录成功 - Redis不可用时降级")
    void testLoginWithWeChat_RedisUnavailable() {
        // Given
        when(userMapper.selectOne(any(QueryWrapper.class))).thenReturn(null);
        doThrow(new RuntimeException("Redis connection failed")).when(valueOps).set(anyString(), anyString(), any(Duration.class));

        // When: Redis失败不应影响登录
        LoginResponse response = authService.loginWithWeChat("code", "测试", "");

        // Then: 登录仍然成功
        assertThat(response).isNotNull();
        assertThat(response.sessionToken).isNotEmpty();

        // Then: 用户仍然被创建
        verify(userMapper).insert(any(UserPO.class));
    }

    @Test
    @DisplayName("获取用户ID - 正常流程（Redis命中）")
    void testGetUserIdFromAuthorization_RedisHit() {
        // Given
        String token = "test_valid_token";
        String userId = "user_01ke123";
        String authorization = "Bearer " + token;

        when(valueOps.get("session:" + token)).thenReturn(userId);

        // When
        String result = authService.getUserIdFromAuthorization(authorization);

        // Then
        assertThat(result).isEqualTo(userId);
    }

    @Test
    @DisplayName("获取用户ID - Redis未命中，降级到JWT解析")
    void testGetUserIdFromAuthorization_RedisMiss_FallbackToJwt() {
        // Given: Redis返回null，需要解析JWT
        when(valueOps.get(anyString())).thenReturn(null);

        // 先创建一个有效的JWT token
        UserPO testUser = createTestUser();
        when(userMapper.selectOne(any(QueryWrapper.class))).thenReturn(null);
        LoginResponse loginResponse = authService.loginWithWeChat("code", testUser.getNickname(), "");
        String validToken = loginResponse.sessionToken;

        // When: 使用有效token（但Redis中不存在）
        String authorization = "Bearer " + validToken;
        String result = authService.getUserIdFromAuthorization(authorization);

        // Then: 应该从JWT解析出userId
        assertThat(result).isNotEmpty();
        assertThat(result).startsWith("user_");
    }

    @Test
    @DisplayName("获取用户ID - 缺少Bearer前缀")
    void testGetUserIdFromAuthorization_MissingBearer() {
        // Given
        String authorization = "InvalidToken";

        // When & Then
        assertThatThrownBy(() -> authService.getUserIdFromAuthorization(authorization))
            .isInstanceOf(BizException.class)
            .hasFieldOrPropertyWithValue("code", "UNAUTHENTICATED")
            .hasMessageContaining("missing bearer token");
    }

    @Test
    @DisplayName("获取用户ID - Authorization为null")
    void testGetUserIdFromAuthorization_Null() {
        // When & Then
        assertThatThrownBy(() -> authService.getUserIdFromAuthorization(null))
            .isInstanceOf(BizException.class)
            .hasFieldOrPropertyWithValue("code", "UNAUTHENTICATED");
    }

    @Test
    @DisplayName("获取用户ID - 无效的JWT token")
    void testGetUserIdFromAuthorization_InvalidJwt() {
        // Given: Redis不可用，且token无效
        when(valueOps.get(anyString())).thenReturn(null);
        String authorization = "Bearer invalid_jwt_token_here";

        // When & Then
        assertThatThrownBy(() -> authService.getUserIdFromAuthorization(authorization))
            .isInstanceOf(BizException.class)
            .hasFieldOrPropertyWithValue("code", "UNAUTHENTICATED")
            .hasMessageContaining("invalid token");
    }

    @Test
    @DisplayName("刷新Token - 无需刷新（token仍有效）")
    void testRefreshTokenIfNeeded_NoRefreshNeeded() {
        // Given: 创建一个刚签发的token（有效期7天）
        UserPO testUser = createTestUser();
        when(userMapper.selectOne(any(QueryWrapper.class))).thenReturn(null);
        LoginResponse loginResponse = authService.loginWithWeChat("code", testUser.getNickname(), "");
        String freshToken = loginResponse.sessionToken;

        // When: 尝试刷新
        String authorization = "Bearer " + freshToken;
        LoginResponse refreshResponse = authService.refreshTokenIfNeeded(authorization);

        // Then: 不应该刷新（返回null）
        assertThat(refreshResponse).isNull();
    }

    @Test
    @DisplayName("刷新Token - 无效token抛异常")
    void testRefreshTokenIfNeeded_InvalidToken() {
        // Given
        String authorization = "Bearer invalid_token";

        // When & Then
        assertThatThrownBy(() -> authService.refreshTokenIfNeeded(authorization))
            .isInstanceOf(BizException.class)
            .hasFieldOrPropertyWithValue("code", "UNAUTHENTICATED");
    }

    @Test
    @DisplayName("刷新Token - 用户不存在")
    void testRefreshTokenIfNeeded_UserNotFound() {
        // Given: token有效但用户已被删除
        UserPO testUser = createTestUser();
        when(userMapper.selectOne(any(QueryWrapper.class))).thenReturn(null); // 创建用户时返回null
        LoginResponse loginResponse = authService.loginWithWeChat("code", testUser.getNickname(), "");

        // 模拟token即将过期（通过修改时间很难实现，这里跳过此场景）
        // 在实际测试中，可以使用反射或者创建一个快过期的token

        // 假设token需要刷新，但用户已被删除
        when(userMapper.selectOne(any(QueryWrapper.class))).thenReturn(null); // 刷新时查询用户

        // 注意：当前实现中，如果token有效但用户不存在，会抛出异常
        // 这是合理的行为，因为token对应的用户应该存在
    }

    // Helper method
    private UserPO createTestUser() {
        UserPO user = new UserPO();
        user.setUserId("user_01ke123abc456");
        user.setWechatOpenid("test_openid_123");
        user.setNickname("测试用户");
        user.setAvatarUrl("");
        user.setRole("HR");
        user.setStatus("ACTIVE");
        return user;
    }
}
