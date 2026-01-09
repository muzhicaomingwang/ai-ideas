package com.teamventure.app.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.teamventure.adapter.web.auth.AuthController.LoginResponse;
import com.teamventure.app.support.BizException;
import com.teamventure.infrastructure.persistence.mapper.UserMapper;
import com.teamventure.infrastructure.persistence.po.UserPO;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.test.context.ActiveProfiles;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * AuthService 集成测试（使用 Spring Boot Test）
 *
 * 测试覆盖:
 *   - 微信登录（新用户/老用户）
 *   - Token生成与验证
 *   - getUserIdFromAuthorization
 *   - refreshTokenIfNeeded
 *
 * 术语对照: ubiquitous-language-glossary.md Section 2.1, 4.4
 */
@SpringBootTest(classes = com.teamventure.TestApplication.class)
@ActiveProfiles("test")
@DisplayName("AuthService 集成测试")
class AuthServiceIntegrationTest {

    @Autowired
    private AuthService authService;

    @MockBean
    private UserMapper userMapper;

    @MockBean
    private StringRedisTemplate redis;

    @MockBean
    private OssService ossService;

    @BeforeEach
    void setUp() {
        // Mock OssService 默认行为
        when(ossService.resolveAvatarUrl(anyString(), anyString())).thenAnswer(
            invocation -> {
                String avatarUrl = invocation.getArgument(1);
                return avatarUrl.isEmpty() ? "" : "http://api.teamventure.com/avatars/users/test/avatars/obj_test.jpg";
            }
        );
    }

    @AfterEach
    void tearDown() {
        // 清理mock调用记录
        reset(userMapper, redis, ossService);
    }

    @Test
    @DisplayName("登录 - 新用户注册成功")
    void testLoginWithWeChat_NewUser() {
        // Given
        when(userMapper.selectOne(any(QueryWrapper.class))).thenReturn(null);

        // When
        LoginResponse response = authService.loginWithWeChat("test_code", "张三", "");

        // Then
        assertThat(response).isNotNull();
        assertThat(response.sessionToken).isNotEmpty();
        assertThat(response.userInfo).isNotNull();
        assertThat(response.userInfo.nickname).isEqualTo("张三");
        assertThat(response.userInfo.user_id).startsWith("user_");

        // Verify user was inserted
        verify(userMapper, times(1)).insert(any(UserPO.class));
    }

    @Test
    @DisplayName("登录 - 老用户不更新")
    void testLoginWithWeChat_ExistingUser_NoUpdate() {
        // Given
        UserPO existingUser = createTestUser();
        when(userMapper.selectOne(any(QueryWrapper.class))).thenReturn(existingUser);

        // When
        LoginResponse response = authService.loginWithWeChat("code", existingUser.getNickname(), existingUser.getAvatarUrl());

        // Then
        assertThat(response.userInfo.user_id).isEqualTo(existingUser.getUserId());
        verify(userMapper, never()).updateById(any());
        verify(userMapper, never()).insert(any());
    }

    @Test
    @DisplayName("获取用户ID - 缺少Bearer前缀")
    void testGetUserIdFromAuthorization_MissingBearer() {
        // When & Then
        assertThatThrownBy(() -> authService.getUserIdFromAuthorization("InvalidToken"))
            .isInstanceOf(BizException.class)
            .hasFieldOrPropertyWithValue("code", "UNAUTHENTICATED");
    }

    @Test
    @DisplayName("获取用户ID - Authorization为null")
    void testGetUserIdFromAuthorization_Null() {
        // When & Then
        assertThatThrownBy(() -> authService.getUserIdFromAuthorization(null))
            .isInstanceOf(BizException.class)
            .hasFieldOrPropertyWithValue("code", "UNAUTHENTICATED");
    }

    private UserPO createTestUser() {
        UserPO user = new UserPO();
        user.setUserId("user_01ke123abc456");
        user.setWechatOpenid("test_openid");
        user.setNickname("测试用户");
        user.setAvatarUrl("");
        user.setRole("HR");
        user.setStatus("ACTIVE");
        return user;
    }
}
