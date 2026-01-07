package com.teamventure.adapter.web.plans;

import com.teamventure.adapter.web.common.ApiResponse;
import com.teamventure.app.service.AuthService;
import com.teamventure.app.service.PlanService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.math.BigDecimal;
import java.util.Map;
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
                                          @PathVariable String planId) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        planService.submitReview(userId, planId);
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

    /**
     * 方案生成请求 DTO
     *
     * 字段语义说明：
     * - departure_city: 出发城市，团队从哪里出发（如公司所在地：上海市）
     * - destination: 目的地，团建活动举办地点（如：杭州千岛湖）
     *
     * 前端显示格式："{departure_city} → {destination}"
     * 示例：上海市 → 杭州千岛湖
     */
    public static class GenerateRequest {
        /** 参与人数 */
        @NotNull public Integer people_count;
        /** 最低预算（元） */
        @NotNull public BigDecimal budget_min;
        /** 最高预算（元） */
        @NotNull public BigDecimal budget_max;
        /** 开始日期（YYYY-MM-DD） */
        @NotBlank public String start_date;
        /** 结束日期（YYYY-MM-DD） */
        @NotBlank public String end_date;
        /** 出发城市（团队从哪里出发，如公司所在地：上海市） */
        @NotBlank public String departure_city;
        /** 目的地（团建活动举办地点，如：杭州千岛湖，可选） */
        public String destination;
        /** 偏好设置（活动类型、住宿标准、餐饮偏好等） */
        public Map<String, Object> preferences;
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
}
