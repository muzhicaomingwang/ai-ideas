package com.teamventure.adapter.web.auth;

import com.teamventure.adapter.web.common.ApiResponse;
import com.teamventure.app.service.AuthService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/auth/wechat")
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    /**
     * 微信登录 API
     * Endpoint: POST /api/v1/auth/wechat/login
     * 参考文档: docs/design/api-design.md Section 2.2
     */
    @PostMapping("/login")
    public ApiResponse<LoginResponse> login(@Valid @RequestBody LoginRequest req) {
        return ApiResponse.success(authService.loginWithWeChat(req.code, req.nickname, req.avatarUrl));
    }

    /**
     * 刷新Token API (Token Refresh)
     * Endpoint: POST /api/v1/auth/wechat/refresh
     * 用途: 当token剩余有效期 < 12小时时自动刷新，实现无感续期
     * 参考文档: docs/design/api-design.md Section 2.4
     *
     * @return 如果token仍有效无需刷新，返回null；否则返回新token和用户信息
     */
    @PostMapping("/refresh")
    public ApiResponse<LoginResponse> refresh(@RequestHeader("Authorization") String authorization) {
        LoginResponse response = authService.refreshTokenIfNeeded(authorization);
        if (response == null) {
            // Token仍然有效，无需刷新 (Token still valid, no refresh needed)
            return ApiResponse.success(null);
        }
        return ApiResponse.success(response);
    }

    public static class LoginRequest {
        @NotBlank public String code;
        public String nickname;     // 可选：用户昵称
        public String avatarUrl;    // 可选：用户头像URL
    }

    public static class LoginResponse {
        public String sessionToken;
        public UserInfo userInfo;

        public LoginResponse(String sessionToken, UserInfo userInfo) {
            this.sessionToken = sessionToken;
            this.userInfo = userInfo;
        }

        public static class UserInfo {
            public String user_id;
            public String nickname;
            public String avatar;
            public String phone;
            public String company;
            public String role;

            public UserInfo(String userId, String nickname, String avatar, String phone, String company, String role) {
                this.user_id = userId;
                this.nickname = nickname;
                this.avatar = avatar;
                this.phone = phone;
                this.company = company;
                this.role = role;
            }
        }
    }
}

