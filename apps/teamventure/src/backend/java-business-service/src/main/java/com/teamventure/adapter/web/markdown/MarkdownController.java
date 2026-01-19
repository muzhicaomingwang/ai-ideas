package com.teamventure.adapter.web.markdown;

import com.teamventure.adapter.web.common.ApiResponse;
import com.teamventure.app.service.AuthService;
import com.teamventure.app.service.MarkdownOptimizeService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/markdown")
public class MarkdownController {
    private final AuthService authService;
    private final MarkdownOptimizeService markdownOptimizeService;

    public MarkdownController(AuthService authService, MarkdownOptimizeService markdownOptimizeService) {
        this.authService = authService;
        this.markdownOptimizeService = markdownOptimizeService;
    }

    @PostMapping("/optimize")
    public ApiResponse<OptimizeResponse> optimize(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @Valid @RequestBody OptimizeRequest req
    ) {
        authService.getUserIdFromAuthorization(authorization);
        String content = markdownOptimizeService.optimize(req.markdown_content);
        return ApiResponse.success(new OptimizeResponse(content));
    }

    @PostMapping("/convert")
    public ApiResponse<OptimizeResponse> convert(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @Valid @RequestBody ConvertRequest req
    ) {
        authService.getUserIdFromAuthorization(authorization);
        String content = markdownOptimizeService.convertFromParsed(req.parsed_content);
        return ApiResponse.success(new OptimizeResponse(content));
    }

    public static class OptimizeRequest {
        @NotBlank
        public String markdown_content;
    }

    public static class ConvertRequest {
        @NotBlank
        public String parsed_content;
    }

    public static class OptimizeResponse {
        public String markdown_content;

        public OptimizeResponse(String markdownContent) {
            this.markdown_content = markdownContent;
        }
    }
}
