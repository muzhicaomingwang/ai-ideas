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

    @PostMapping("/login")
    public ApiResponse<LoginResponse> login(@Valid @RequestBody LoginRequest req) {
        return ApiResponse.success(authService.loginWithWeChat(req.code));
    }

    public static class LoginRequest {
        @NotBlank public String code;
    }

    public static class LoginResponse {
        public String user_id;
        public String session_token;
        public long expires_in_seconds;

        public LoginResponse(String userId, String token, long expiresInSeconds) {
            this.user_id = userId;
            this.session_token = token;
            this.expires_in_seconds = expiresInSeconds;
        }
    }
}

