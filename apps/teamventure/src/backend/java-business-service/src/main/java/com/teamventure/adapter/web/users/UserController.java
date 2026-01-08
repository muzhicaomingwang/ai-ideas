package com.teamventure.adapter.web.users;

import com.teamventure.adapter.web.common.ApiResponse;
import com.teamventure.app.service.AuthService;
import com.teamventure.app.service.OssService;
import com.teamventure.infrastructure.persistence.mapper.UserMapper;
import com.teamventure.infrastructure.persistence.po.UserPO;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/users")
public class UserController {

    private final AuthService authService;
    private final UserMapper userMapper;
    private final OssService ossService;

    public UserController(AuthService authService, UserMapper userMapper, OssService ossService) {
        this.authService = authService;
        this.userMapper = userMapper;
        this.ossService = ossService;
    }

    /**
     * 获取当前用户信息 API (Get Current User)
     * Endpoint: GET /api/v1/users/me
     * 用途:
     *   - Token验证：在用户"继续使用"时验证token有效性
     *   - 数据刷新：获取最新的用户信息（如昵称、头像变更）
     *   - 登录状态检查：前端页面初始化时验证登录状态
     * 参考文档: docs/design/api-design.md Section 2.3
     * 术语对照: 参考 ubiquitous-language-glossary.md Section 2.1
     */
    @GetMapping("/me")
    public ApiResponse<UserInfo> me(@RequestHeader(value = "Authorization", required = false) String authorization) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        UserPO user = userMapper.selectById(userId);
        if (user == null) {
            return ApiResponse.success(new UserInfo(userId, "", "", null, null, "HR"));
        }
        String avatar = ossService.resolveAvatarUrl(userId, user.getAvatarUrl());
        return ApiResponse.success(new UserInfo(
                user.getUserId(),
                user.getNickname(),
                avatar,
                user.getPhone(),
                user.getCompany(),
                user.getRole()
        ));
    }

    @PutMapping("/me/avatar")
    public ApiResponse<Void> updateAvatar(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @Valid @RequestBody UpdateAvatarRequest req
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        UserPO user = userMapper.selectById(userId);
        if (user == null) {
            return ApiResponse.failure("NOT_FOUND", "user not found");
        }
        String stored = ossService.toAvatarStorageValue(userId, req.avatarKey);
        user.setAvatarUrl(stored);
        userMapper.updateById(user);
        return ApiResponse.success();
    }

    public record UpdateAvatarRequest(@NotBlank String avatarKey) {}

    public record UserInfo(
            String user_id,
            String nickname,
            String avatar,
            String phone,
            String company,
            String role
    ) {}
}

