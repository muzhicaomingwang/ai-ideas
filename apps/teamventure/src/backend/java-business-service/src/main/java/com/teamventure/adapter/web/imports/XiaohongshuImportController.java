package com.teamventure.adapter.web.imports;

import com.teamventure.adapter.web.common.ApiResponse;
import com.teamventure.app.service.AuthService;
import com.teamventure.app.service.XiaohongshuImportService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/import/xiaohongshu")
public class XiaohongshuImportController {

    private final AuthService authService;
    private final XiaohongshuImportService importService;

    public XiaohongshuImportController(AuthService authService, XiaohongshuImportService importService) {
        this.authService = authService;
        this.importService = importService;
    }

    @PostMapping("/parse")
    public ApiResponse<ParseResponse> parse(@RequestHeader(value = "Authorization", required = false) String authorization,
                                            @Valid @RequestBody ParseRequest req) {
        // Require login (consistent with other APIs)
        authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(importService.parse(req.link));
    }

    public static class ParseRequest {
        @NotBlank
        public String link;
    }

    public static class ParseResponse {
        public boolean is_itinerary;
        public String title;
        public String destination;
        public Integer days;
        public String source_url;
        public String raw_content;
        public String generatedMarkdown;
    }
}

