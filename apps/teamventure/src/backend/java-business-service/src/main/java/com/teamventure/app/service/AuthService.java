package com.teamventure.app.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.teamventure.adapter.web.auth.AuthController.LoginResponse;
import com.teamventure.app.support.BizException;
import com.teamventure.app.support.IdGenerator;
import com.teamventure.app.support.JwtSupport;
import com.teamventure.infrastructure.persistence.mapper.UserMapper;
import com.teamventure.infrastructure.persistence.po.UserPO;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Duration;
import java.util.HexFormat;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

@Service
public class AuthService {
    private static final long EXPIRES_SECONDS = 86400L;

    private final UserMapper userMapper;
    private final StringRedisTemplate redis;
    private final JwtSupport jwt;

    public AuthService(
            UserMapper userMapper,
            StringRedisTemplate redis,
            @Value("${teamventure.jwt.secret:change-me-change-me-change-me-change-me}") String jwtSecret
    ) {
        this.userMapper = userMapper;
        this.redis = redis;
        this.jwt = new JwtSupport(jwtSecret);
    }

    public LoginResponse loginWithWeChat(String code) {
        String openid = pseudoOpenId(code);

        UserPO user = userMapper.selectOne(new QueryWrapper<UserPO>().eq("wechat_openid", openid));
        if (user == null) {
            user = new UserPO();
            user.setUserId(IdGenerator.newId("user"));
            user.setWechatOpenid(openid);
            user.setNickname("新用户");
            user.setRole("HR");
            user.setStatus("ACTIVE");
            userMapper.insert(user);
        }

        String token = jwt.issueToken(user.getUserId(), EXPIRES_SECONDS);
        redis.opsForValue().set("session:" + token, user.getUserId(), Duration.ofSeconds(EXPIRES_SECONDS));
        return new LoginResponse(user.getUserId(), token, EXPIRES_SECONDS);
    }

    public String getUserIdFromAuthorization(String authorization) {
        if (authorization == null || !authorization.startsWith("Bearer ")) {
            throw new BizException("UNAUTHENTICATED", "missing bearer token");
        }
        String token = authorization.substring("Bearer ".length()).trim();
        String userId = redis.opsForValue().get("session:" + token);
        if (userId == null) {
            // fallback: parse jwt (stateless); still requires that token is valid
            try {
                userId = jwt.parseUserId(token);
            } catch (Exception e) {
                throw new BizException("UNAUTHENTICATED", "invalid token");
            }
        }
        return userId;
    }

    private static String pseudoOpenId(String code) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(code.getBytes(StandardCharsets.UTF_8));
            return "openid_" + HexFormat.of().formatHex(hash).substring(0, 16);
        } catch (Exception e) {
            throw new BizException("INTERNAL_ERROR", "openid generation failed");
        }
    }
}

