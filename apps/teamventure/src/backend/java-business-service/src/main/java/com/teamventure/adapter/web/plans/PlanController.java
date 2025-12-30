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
    public ApiResponse<GenerateResponse> generate(@RequestHeader("Authorization") String authorization,
                                                 @Valid @RequestBody GenerateRequest req) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(planService.createPlanRequestAndPublish(userId, req));
    }

    @GetMapping
    public ApiResponse<?> list(@RequestHeader("Authorization") String authorization,
                               @RequestParam(defaultValue = "1") int page,
                               @RequestParam(defaultValue = "10") int pageSize) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(planService.listPlans(userId, page, pageSize));
    }

    @GetMapping("/{planId}")
    public ApiResponse<?> detail(@RequestHeader("Authorization") String authorization, @PathVariable String planId) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(planService.getPlanDetail(userId, planId));
    }

    @PostMapping("/{planId}/confirm")
    public ApiResponse<Void> confirm(@RequestHeader("Authorization") String authorization, @PathVariable String planId) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        planService.confirmPlan(userId, planId);
        return ApiResponse.success();
    }

    @PostMapping("/{planId}/supplier-contacts")
    public ApiResponse<Void> contact(@RequestHeader("Authorization") String authorization,
                                     @PathVariable String planId,
                                     @Valid @RequestBody SupplierContactRequest req) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        planService.logSupplierContact(userId, planId, req);
        return ApiResponse.success();
    }

    public static class GenerateRequest {
        @NotNull public Integer people_count;
        @NotNull public BigDecimal budget_min;
        @NotNull public BigDecimal budget_max;
        @NotBlank public String start_date;
        @NotBlank public String end_date;
        @NotBlank public String departure_city;
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

