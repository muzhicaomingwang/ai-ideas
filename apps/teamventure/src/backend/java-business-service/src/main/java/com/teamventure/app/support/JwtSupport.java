package com.teamventure.app.support;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Date;
import javax.crypto.SecretKey;

public class JwtSupport {
    private final SecretKey key;

    public JwtSupport(String secret) {
        this.key = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
    }

    public String issueToken(String userId, long expiresInSeconds) {
        Instant now = Instant.now();
        return Jwts.builder()
                .subject(userId)
                .issuedAt(Date.from(now))
                .expiration(Date.from(now.plusSeconds(expiresInSeconds)))
                .signWith(key)
                .compact();
    }

    public String parseUserId(String token) {
        return parseClaims(token).getSubject();
    }

    /**
     * 获取token过期时间（秒级时间戳）
     * Get token expiration time in seconds since epoch
     */
    public long getExpirationTime(String token) {
        return parseClaims(token).getExpiration().getTime() / 1000;
    }

    /**
     * 检查token是否即将过期
     * Check if token will expire within given seconds
     *
     * 用途: 实现自动Token刷新（Token Refresh）
     * 参考: AuthService.REFRESH_THRESHOLD_SECONDS = 12小时
     * 术语对照: ubiquitous-language-glossary.md Section 4.4 "Token刷新"
     */
    public boolean willExpireSoon(String token, long thresholdSeconds) {
        long expirationTime = getExpirationTime(token);
        long currentTime = Instant.now().getEpochSecond();
        return (expirationTime - currentTime) < thresholdSeconds;
    }

    private Claims parseClaims(String token) {
        return Jwts.parser()
                .verifyWith(key)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }
}

