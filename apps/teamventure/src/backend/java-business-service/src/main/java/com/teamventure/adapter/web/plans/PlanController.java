package com.teamventure.adapter.web.plans;

import com.teamventure.adapter.web.common.ApiResponse;
import com.teamventure.app.service.AuthService;
import com.teamventure.app.service.PlanService;
import com.fasterxml.jackson.annotation.JsonAlias;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/plans")
public class PlanController {

    private final AuthService authService;
    private final PlanService planService;

    public PlanController(AuthService authService, PlanService planService) {
        this.authService = authService;
        this.planService = planService;
    }

    @PostMapping("/generate")
    public ApiResponse<GenerateResponse> generate(@RequestHeader(value = "Authorization", required = false) String authorization,
                                                 @Valid @RequestBody GenerateRequest req) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(planService.createPlanRequestAndPublish(userId, req));
    }

    @GetMapping
    public ApiResponse<?> list(@RequestHeader(value = "Authorization", required = false) String authorization,
                               @RequestParam(defaultValue = "1") int page,
                               @RequestParam(defaultValue = "10") int pageSize,
                               @RequestParam(required = false) String status) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(planService.listPlans(userId, page, pageSize, status));
    }

    @GetMapping("/{planId}")
    public ApiResponse<?> detail(@RequestHeader(value = "Authorization", required = false) String authorization, @PathVariable String planId) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(planService.getPlanDetail(userId, planId));
    }

    @GetMapping("/{planId}/route")
    public ApiResponse<Map<String, Object>> route(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable String planId,
            @RequestParam(required = false) Integer day
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(planService.getPlanRoute(userId, planId, day));
    }

    @PostMapping("/{planId}/confirm")
    public ApiResponse<Void> confirm(@RequestHeader(value = "Authorization", required = false) String authorization, @PathVariable String planId) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        planService.confirmPlan(userId, planId);
        return ApiResponse.success();
    }

    @PostMapping("/{planId}/supplier-contacts")
    public ApiResponse<Void> contact(@RequestHeader(value = "Authorization", required = false) String authorization,
                                     @PathVariable String planId,
                                     @Valid @RequestBody SupplierContactRequest req) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        planService.logSupplierContact(userId, planId, req);
        return ApiResponse.success();
    }

    @PostMapping("/{planId}/archive")
    public ApiResponse<Void> archive(@RequestHeader(value = "Authorization", required = false) String authorization,
                                     @PathVariable String planId) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        planService.archivePlan(userId, planId);
        return ApiResponse.success();
    }

    @PutMapping("/{planId}/submit-review")
    public ApiResponse<Void> submitReview(@RequestHeader(value = "Authorization", required = false) String authorization,
                                          @PathVariable String planId,
                                          @RequestBody(required = false) SubmitReviewRequest req) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        planService.submitReview(userId, planId, req);
        return ApiResponse.success();
    }

    @PostMapping("/{planId}/revert-review")
    public ApiResponse<Void> revertReview(@RequestHeader(value = "Authorization", required = false) String authorization,
                                          @PathVariable String planId) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        planService.revertReview(userId, planId);
        return ApiResponse.success();
    }

    @DeleteMapping("/{planId}")
    public ApiResponse<Void> delete(@RequestHeader(value = "Authorization", required = false) String authorization,
                                    @PathVariable String planId) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        planService.deletePlan(userId, planId);
        return ApiResponse.success();
    }

    @PutMapping("/{planId}/itinerary")
    public ResponseEntity<ApiResponse<Map<String, Object>>> updateItinerary(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable String planId,
            @Valid @RequestBody UpdateItineraryRequest req
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        Map<String, Object> result = planService.updateItineraryWithCas(userId, planId, req.base_version, req.itinerary);

        if (Boolean.TRUE.equals(result.get("conflict"))) {
            Map<String, Object> payload = new HashMap<>();
            payload.put("itinerary_version", result.get("itinerary_version"));
            payload.put("itinerary", result.get("itinerary"));
            return ResponseEntity.status(HttpStatus.CONFLICT)
                    .body(ApiResponse.failure("CAS_CONFLICT", "itinerary has changed", payload));
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
        @NotNull public Integer base_version;
    }

    public static class SubmitReviewRequest {
        /** 用户确认的出发日期（YYYY-MM-DD） */
        @JsonAlias({"start_date", "startDate"})
        public String start_date;
    }
}
