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
     * Get token expiration time in seconds since epoch
     */
    public long getExpirationTime(String token) {
        return parseClaims(token).getExpiration().getTime() / 1000;
    }

    /**
     * Check if token will expire within given seconds
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

