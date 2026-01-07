package com.teamventure.adapter.web.media;

import com.teamventure.adapter.web.common.ApiResponse;
import com.teamventure.app.service.AuthService;
import com.teamventure.app.service.OssService;
import com.teamventure.app.service.OssService.Category;
import com.teamventure.app.support.BizException;
import jakarta.validation.constraints.NotBlank;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/v1/media")
public class MediaController {

    private final AuthService authService;
    private final OssService ossService;

    public MediaController(AuthService authService, OssService ossService) {
        this.authService = authService;
        this.ossService = ossService;
    }

    @PostMapping("/upload")
    public ApiResponse<UploadResponse> upload(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @RequestParam(defaultValue = "itinerary") String category,
            @RequestParam(required = false) String scope,
            @RequestPart("file") MultipartFile file
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        Category c = parseCategory(category);
        var r = ossService.uploadImage(userId, c, file, scope);
        return ApiResponse.success(new UploadResponse(r.bucket(), r.objectKey(), r.url(), r.publicReadable()));
    }

    @GetMapping("/presign")
    public ApiResponse<PresignResponse> presign(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @RequestParam @NotBlank String bucket,
            @RequestParam @NotBlank String key
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        // Basic guard for private avatar objects: must be under the current user's prefix.
        if ("avatars".equals(bucket) && !key.startsWith("users/" + userId + "/")) {
            throw new BizException("FORBIDDEN", "invalid key scope");
        }
        String url = ossService.presignGet(bucket, key);
        return ApiResponse.success(new PresignResponse(url));
    }

    private static Category parseCategory(String v) {
        String s = v == null ? "" : v.trim().toLowerCase();
        return switch (s) {
            case "avatar", "avatars" -> Category.AVATAR;
            case "itinerary", "itineraries" -> Category.ITINERARY;
            default -> Category.ITINERARY;
        };
    }

    public record UploadResponse(String bucket, String key, String url, boolean publicReadable) {}

    public record PresignResponse(String url) {}
}
