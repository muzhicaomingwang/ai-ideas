package com.teamventure.adapter.web.plans;

import com.teamventure.adapter.web.common.ApiResponse;
import com.teamventure.app.service.AuthService;
import com.teamventure.app.service.PlanCommandService;
import com.teamventure.app.service.PlanQueryService;
import com.fasterxml.jackson.annotation.JsonAlias;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.util.HashMap;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/plans")
public class PlanController {

    private final AuthService authService;
    private final PlanCommandService planCommandService;
    private final PlanQueryService planQueryService;

    public PlanController(AuthService authService, PlanCommandService planCommandService, PlanQueryService planQueryService) {
        this.authService = authService;
        this.planCommandService = planCommandService;
        this.planQueryService = planQueryService;
    }

    @PostMapping("/generate")
    public ApiResponse<GenerateResponse> generate(@RequestHeader(value = "Authorization", required = false) String authorization,
                                                 @Valid @RequestBody GenerateRequest req) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(planCommandService.createPlanRequestAndPublish(userId, req));
    }

    @PostMapping("/save")
    public ApiResponse<Map<String, Object>> save(@RequestHeader(value = "Authorization", required = false) String authorization,
                                                 @Valid @RequestBody SaveRequest req) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(planCommandService.saveDraftPlanFromMarkdown(userId, req.markdown_content, req.plan_name, req.logo_storage, req.logo_url));
    }

    @GetMapping
    public ApiResponse<?> list(@RequestHeader(value = "Authorization", required = false) String authorization,
                               @RequestParam(defaultValue = "1") int page,
                               @RequestParam(defaultValue = "10") int pageSize,
                               @RequestParam(required = false) String status) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(planQueryService.listPlans(userId, page, pageSize, status));
    }

    @GetMapping("/{planId}")
    public ApiResponse<?> detail(@RequestHeader(value = "Authorization", required = false) String authorization, @PathVariable String planId) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(planQueryService.getPlanDetail(userId, planId));
    }

    @GetMapping("/{planId}/route")
    public ApiResponse<Map<String, Object>> route(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable String planId,
            @RequestParam(required = false) Integer day
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(planQueryService.getPlanRoute(userId, planId, day));
    }

    @PostMapping("/{planId}/confirm")
    public ApiResponse<Void> confirm(@RequestHeader(value = "Authorization", required = false) String authorization, @PathVariable String planId) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        planCommandService.confirmPlan(userId, planId);
        return ApiResponse.success();
    }

    @PostMapping("/{planId}/supplier-contacts")
    public ApiResponse<Void> contact(@RequestHeader(value = "Authorization", required = false) String authorization,
                                     @PathVariable String planId,
                                     @Valid @RequestBody SupplierContactRequest req) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        planCommandService.logSupplierContact(userId, planId, req);
        return ApiResponse.success();
    }

    @PostMapping("/{planId}/archive")
    public ApiResponse<Void> archive(@RequestHeader(value = "Authorization", required = false) String authorization,
                                     @PathVariable String planId) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        planCommandService.archivePlan(userId, planId);
        return ApiResponse.success();
    }

    @PutMapping("/{planId}/submit-review")
    public ApiResponse<Void> submitReview(@RequestHeader(value = "Authorization", required = false) String authorization,
                                          @PathVariable String planId,
                                          @RequestBody(required = false) SubmitReviewRequest req) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        planCommandService.submitReview(userId, planId, req);
        return ApiResponse.success();
    }

    @PostMapping("/{planId}/revert-review")
    public ApiResponse<Void> revertReview(@RequestHeader(value = "Authorization", required = false) String authorization,
                                          @PathVariable String planId) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        planCommandService.revertReview(userId, planId);
        return ApiResponse.success();
    }

    @DeleteMapping("/{planId}")
    public ApiResponse<Void> delete(@RequestHeader(value = "Authorization", required = false) String authorization,
                                    @PathVariable String planId) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        planCommandService.deletePlan(userId, planId);
        return ApiResponse.success();
    }

    @PutMapping("/{planId}/itinerary")
    public ResponseEntity<ApiResponse<Map<String, Object>>> updateItinerary(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable String planId,
            @Valid @RequestBody UpdateItineraryRequest req
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        Map<String, Object> result = planCommandService.updateItineraryWithCas(userId, planId, req.base_version, req.itinerary);

        if (Boolean.TRUE.equals(result.get("conflict"))) {
            Map<String, Object> payload = new HashMap<>();
            payload.put("itinerary_version", result.get("itinerary_version"));
            payload.put("itinerary", result.get("itinerary"));
            return ResponseEntity.status(HttpStatus.CONFLICT)
                    .body(ApiResponse.failure("CONFLICT", "itinerary_version mismatch", payload));
        }

        Map<String, Object> payload = new HashMap<>();
        payload.put("itinerary_version", result.get("itinerary_version"));
        payload.put("itinerary", result.get("itinerary"));
        return ResponseEntity.ok(ApiResponse.success(payload));
    }

    /**
     * 方案生成请求 DTO - Markdown格式
     *
     * 用户通过Markdown格式描述团建需求，包括：
     * - 基本信息（天数、人数、预算）
     * - 行程路线（出发地、到达地、途径地）
     * - 交通安排（航班/高铁班次）
     * - 住宿安排（每日出发/入住酒店）
     * - 活动偏好、特殊要求等
     *
     * AI Agent将直接解析Markdown内容，生成1套定制化方案
     */
    public static class GenerateRequest {
        /** Markdown格式的行程需求描述 */
        @NotBlank
        public String markdown_content;

        /** 可选：用户指定的方案名称（用于覆盖AI生成名称） */
        public String plan_name;
    }

    public static class SaveRequest {
        /** Markdown格式的行程内容（直接保存为制定完成 draft 方案） */
        @NotBlank
        public String markdown_content;

        /** 用户指定的方案名称 */
        @NotBlank
        public String plan_name;

        /** 可选：方案 Logo 对象引用（minio://bucket/key，用于列表展示） */
        @JsonAlias({"logoStorage", "logo_storage"})
        public String logo_storage;

        /** 兼容：旧字段（历史实现） */
        @JsonAlias({"logoUrl", "logo_url", "plan_logo", "planLogo"})
        public String logo_url;
    }

    public static class GenerateResponse {
        public String plan_request_id;
        public String status;

        public GenerateResponse(String planRequestId, String status) {
            this.plan_request_id = planRequestId;
            this.status = status;
        }
    }

    public static class SupplierContactRequest {
        @NotBlank public String supplier_id;
        @NotBlank public String channel; // PHONE/WECHAT/EMAIL
        public String notes;
    }

    public static class UpdateItineraryRequest {
        @NotNull public Map<String, Object> itinerary;
        @NotNull
        @JsonAlias({"base_version", "baseVersion", "expected_itinerary_version", "expectedItineraryVersion"})
        public Integer base_version;
    }

    public static class SubmitReviewRequest {
        /** 用户确认的出发日期（YYYY-MM-DD） */
        @JsonAlias({"start_date", "startDate"})
        public String start_date;
    }
}
