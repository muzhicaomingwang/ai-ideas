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

