package com.teamventure.app.support;

import io.jsonwebtoken.JwtException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.*;

/**
 * JwtSupport 单元测试
 *
 * 测试覆盖:
 *   - Token生成
 *   - Token解析
 *   - Token过期时间获取
 *   - Token即将过期判断
 *   - 无效token处理
 *
 * 术语对照: ubiquitous-language-glossary.md Section 4.4 "Token刷新"
 */
@DisplayName("JwtSupport 单元测试")
class JwtSupportTest {

    private JwtSupport jwtSupport;

    private static final String TEST_SECRET = "test-secret-key-must-be-at-least-256-bits-long-for-hs256-algorithm";
    private static final String TEST_USER_ID = "user_01ke123abc456";

    @BeforeEach
    void setUp() {
        jwtSupport = new JwtSupport(TEST_SECRET);
    }

    @Test
    @DisplayName("生成Token - 正常流程")
    void testIssueToken() {
        // When
        String token = jwtSupport.issueToken(TEST_USER_ID, 3600);

        // Then
        assertThat(token).isNotEmpty();
        assertThat(token.split("\\.")).hasSize(3); // JWT格式: header.payload.signature
    }

    @Test
    @DisplayName("解析Token - 获取userId")
    void testParseUserId() {
        // Given
        String token = jwtSupport.issueToken(TEST_USER_ID, 3600);

        // When
        String userId = jwtSupport.parseUserId(token);

        // Then
        assertThat(userId).isEqualTo(TEST_USER_ID);
    }

    @Test
    @DisplayName("解析Token - 无效token抛异常")
    void testParseUserId_InvalidToken() {
        // When & Then
        assertThatThrownBy(() -> jwtSupport.parseUserId("invalid.token.here"))
            .isInstanceOf(JwtException.class);
    }

    @Test
    @DisplayName("解析Token - 篡改的token抛异常")
    void testParseUserId_TamperedToken() {
        // Given: 生成有效token然后篡改
        String token = jwtSupport.issueToken(TEST_USER_ID, 3600);
        String tamperedToken = token.substring(0, token.length() - 5) + "XXXXX";

        // When & Then
        assertThatThrownBy(() -> jwtSupport.parseUserId(tamperedToken))
            .isInstanceOf(JwtException.class);
    }

    @Test
    @DisplayName("获取过期时间 - 正常流程")
    void testGetExpirationTime() {
        // Given
        long expiresInSeconds = 3600;
        long beforeIssue = System.currentTimeMillis() / 1000;
        String token = jwtSupport.issueToken(TEST_USER_ID, expiresInSeconds);
        long afterIssue = System.currentTimeMillis() / 1000;

        // When
        long expirationTime = jwtSupport.getExpirationTime(token);

        // Then: 过期时间应该在 beforeIssue+3600 到 afterIssue+3600 之间
        assertThat(expirationTime).isBetween(beforeIssue + expiresInSeconds, afterIssue + expiresInSeconds);
    }

    @Test
    @DisplayName("检查即将过期 - token有效期充足")
    void testWillExpireSoon_NotExpiringSoon() {
        // Given: token有效期7天
        String token = jwtSupport.issueToken(TEST_USER_ID, 604800); // 7 days
        long thresholdSeconds = 43200; // 12 hours

        // When
        boolean willExpire = jwtSupport.willExpireSoon(token, thresholdSeconds);

        // Then: 7天内不会过期，应返回false
        assertThat(willExpire).isFalse();
    }

    @Test
    @DisplayName("检查即将过期 - token即将过期")
    void testWillExpireSoon_ExpiringSoon() {
        // Given: token有效期仅10小时
        String token = jwtSupport.issueToken(TEST_USER_ID, 36000); // 10 hours
        long thresholdSeconds = 43200; // 12 hours

        // When
        boolean willExpire = jwtSupport.willExpireSoon(token, thresholdSeconds);

        // Then: 10小时 < 12小时阈值，应返回true
        assertThat(willExpire).isTrue();
    }

    @Test
    @DisplayName("检查即将过期 - token已经过期（抛异常）")
    void testWillExpireSoon_AlreadyExpired() {
        // Given: token有效期1秒
        String token = jwtSupport.issueToken(TEST_USER_ID, 1);

        // When: 等待2秒让token过期
        try {
            Thread.sleep(2000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        long thresholdSeconds = 3600;

        // When & Then: 已过期的token解析时会抛出异常
        assertThatThrownBy(() -> jwtSupport.willExpireSoon(token, thresholdSeconds))
            .isInstanceOf(io.jsonwebtoken.ExpiredJwtException.class);
    }

    @Test
    @DisplayName("Token完整性 - 同一用户ID多次生成token（间隔后）不同")
    void testIssueToken_DifferentTokensForSameUser() throws InterruptedException {
        // When: 生成第一个token
        String token1 = jwtSupport.issueToken(TEST_USER_ID, 3600);

        // When: 等待1秒确保iat（签发时间）不同
        Thread.sleep(1100);

        // When: 生成第二个token
        String token2 = jwtSupport.issueToken(TEST_USER_ID, 3600);

        // Then: token应该不同（因为签发时间不同）
        assertThat(token1).isNotEqualTo(token2);

        // But: 解析出的userId应该相同
        assertThat(jwtSupport.parseUserId(token1)).isEqualTo(TEST_USER_ID);
        assertThat(jwtSupport.parseUserId(token2)).isEqualTo(TEST_USER_ID);
    }

    @Test
    @DisplayName("Token安全 - 不同密钥无法解析")
    void testParseUserId_DifferentSecret() {
        // Given: 使用密钥A生成token
        String token = jwtSupport.issueToken(TEST_USER_ID, 3600);

        // When: 使用密钥B尝试解析
        JwtSupport differentJwtSupport = new JwtSupport("different-secret-key-must-be-at-least-256-bits-long-for-algorithm");

        // Then: 应该抛异常
        assertThatThrownBy(() -> differentJwtSupport.parseUserId(token))
            .isInstanceOf(JwtException.class);
    }
}
