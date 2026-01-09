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
import java.util.Locale;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

@Service
public class AuthService {
    private static final Logger log = LoggerFactory.getLogger(AuthService.class);
    private static final long EXPIRES_SECONDS = 604800L; // 7 days
    private static final long REFRESH_THRESHOLD_SECONDS = 43200L; // Refresh when < 12 hours remaining

    private final UserMapper userMapper;
    private final StringRedisTemplate redis;
    private final JwtSupport jwt;
    private final OssService ossService;

    public AuthService(
            UserMapper userMapper,
            StringRedisTemplate redis,
            @Value("${teamventure.jwt.secret:change-me-change-me-change-me-change-me}") String jwtSecret,
            OssService ossService
    ) {
        this.userMapper = userMapper;
        this.redis = redis;
        this.jwt = new JwtSupport(jwtSecret);
        this.ossService = ossService;
    }

    public LoginResponse loginWithWeChat(String code, String nickname, String avatarUrl) {
        String openid = pseudoOpenId(code);

        UserPO user = userMapper.selectOne(new QueryWrapper<UserPO>().eq("wechat_openid", openid));
        if (user == null) {
            // 创建新用户
            user = new UserPO();
            user.setUserId(IdGenerator.newId("user"));
            user.setWechatOpenid(openid);
            // 使用传入的nickname，如果为空则使用默认值
            user.setNickname(hasText(nickname) ? nickname.trim() : "微信用户");
            user.setAvatarUrl(hasText(avatarUrl) && !isExampleDotComAvatar(avatarUrl) ? avatarUrl : "");
            user.setRole("HR");
            user.setStatus("ACTIVE");
            userMapper.insert(user);
        } else {
            // 更新现有用户信息（如果提供了新的nickname或avatarUrl）
            boolean needUpdate = false;

            if (hasText(nickname) && !nickname.trim().equals(user.getNickname())) {
                user.setNickname(nickname.trim());
                needUpdate = true;
            }

            if (hasText(avatarUrl)) {
                if (!isExampleDotComAvatar(avatarUrl) && !avatarUrl.equals(user.getAvatarUrl())) {
                    user.setAvatarUrl(avatarUrl);
                    needUpdate = true;
                }
            } else if (isExampleDotComAvatar(user.getAvatarUrl())) {
                // 自动清理历史测试数据里遗留的 example.com 外链头像，避免前端持续 404
                user.setAvatarUrl("");
                needUpdate = true;
            }

            if (needUpdate) {
                userMapper.updateById(user);
            }
        }

        String token = jwt.issueToken(user.getUserId(), EXPIRES_SECONDS);
        try {
            redis.opsForValue().set("session:" + token, user.getUserId(), Duration.ofSeconds(EXPIRES_SECONDS));
        } catch (Exception e) {
            // Redis 不可用时仍允许登录，后续请求可回退到 JWT 解析
            log.warn("redis unavailable when setting session token, fallback to stateless jwt: userId={}", user.getUserId(), e);
        }

        // 构建包含完整userInfo的响应
        String avatar = ossService.resolveAvatarUrl(user.getUserId(), user.getAvatarUrl());
        LoginResponse.UserInfo userInfo = new LoginResponse.UserInfo(
            user.getUserId(),
            user.getNickname(),
            avatar,
            user.getPhone(),
            user.getCompany(),
            user.getRole()
        );

        return new LoginResponse(token, userInfo);
    }

    // 辅助方法：检查字符串是否有内容
    private boolean hasText(String str) {
        return str != null && !str.trim().isEmpty();
    }

    private boolean isExampleDotComAvatar(String avatarUrl) {
        if (avatarUrl == null) return false;
        String s = avatarUrl.trim().toLowerCase(Locale.ROOT);
        return s.startsWith("http://example.com/") || s.startsWith("https://example.com/");
    }

    public String getUserIdFromAuthorization(String authorization) {
        if (authorization == null || !authorization.startsWith("Bearer ")) {
            throw new BizException("UNAUTHENTICATED", "missing bearer token");
        }
        String token = authorization.substring("Bearer ".length()).trim();
        String userId = null;
        try {
            userId = redis.opsForValue().get("session:" + token);
        } catch (Exception e) {
            // 本地联调常见：Redis 未启动/密码不一致/网络不可达，避免直接 500
            log.warn("redis unavailable when reading session token, fallback to stateless jwt", e);
        }
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

    /**
     * Refresh token if it's close to expiration.
     * Returns new token and user info, or null if token doesn't need refresh.
     */
    public LoginResponse refreshTokenIfNeeded(String authorization) {
        if (authorization == null || !authorization.startsWith("Bearer ")) {
            throw new BizException("UNAUTHENTICATED", "missing bearer token");
        }
        String token = authorization.substring("Bearer ".length()).trim();

        // Validate and extract userId
        String userId;
        try {
            userId = jwt.parseUserId(token);
        } catch (Exception e) {
            throw new BizException("UNAUTHENTICATED", "invalid token");
        }

        // Check if token needs refresh
        boolean needsRefresh;
        try {
            needsRefresh = jwt.willExpireSoon(token, REFRESH_THRESHOLD_SECONDS);
        } catch (Exception e) {
            throw new BizException("UNAUTHENTICATED", "invalid token");
        }

        if (!needsRefresh) {
            return null; // Token is still fresh, no refresh needed
        }

        // Issue new token
        String newToken = jwt.issueToken(userId, EXPIRES_SECONDS);

        // Update Redis session
        try {
            // Delete old session
            redis.delete("session:" + token);
            // Create new session
            redis.opsForValue().set("session:" + newToken, userId, Duration.ofSeconds(EXPIRES_SECONDS));
        } catch (Exception e) {
            log.warn("redis unavailable when refreshing token, fallback to stateless jwt: userId={}", userId, e);
        }

        // Load user info
        UserPO user = userMapper.selectOne(new QueryWrapper<UserPO>().eq("user_id", userId));
        if (user == null) {
            throw new BizException("UNAUTHENTICATED", "user not found");
        }

        String avatar = ossService.resolveAvatarUrl(user.getUserId(), user.getAvatarUrl());
        LoginResponse.UserInfo userInfo = new LoginResponse.UserInfo(
            user.getUserId(),
            user.getNickname(),
            avatar,
            user.getPhone(),
            user.getCompany(),
            user.getRole()
        );

        log.info("Token refreshed for user: {}", userId);
        return new LoginResponse(newToken, userInfo);
    }

    private static String pseudoOpenId(String code) {
        // 开发模式：使用固定的 openid，确保同一设备登录到同一账号
        // TODO: 生产环境需调用微信 API (jscode2session) 获取真实 openid
        // 暂时使用固定 openid 方便测试，所有用户登录到同一账号
        return "openid_dev_fixed_user";
    }
}
