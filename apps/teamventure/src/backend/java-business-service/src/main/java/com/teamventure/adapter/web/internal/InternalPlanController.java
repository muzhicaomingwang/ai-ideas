package com.teamventure.adapter.web.internal;

import com.teamventure.adapter.web.common.ApiResponse;
import com.teamventure.app.service.InternalPlanCallbackService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/internal")
public class InternalPlanController {

    private final InternalPlanCallbackService callbackService;
    private final String internalSecret;

    public InternalPlanController(
            InternalPlanCallbackService callbackService,
            @Value("${teamventure.ai-service.callback-secret}") String internalSecret
    ) {
        this.callbackService = callbackService;
        this.internalSecret = internalSecret;
    }

    @PostMapping("/plans/batch")
    public ApiResponse<Void> createPlans(@RequestHeader("X-Internal-Secret") String secret,
                                         @Valid @RequestBody BatchPlanRequest req) {
        if (!internalSecret.equals(secret)) {
            return ApiResponse.failure("UNAUTHORIZED", "invalid internal secret");
        }
        callbackService.handleGeneratedPlans(req);
        return ApiResponse.success();
    }

    public static class BatchPlanRequest {
        @NotBlank public String plan_request_id;
        @NotBlank public String user_id;
        public List<Map<String, Object>> plans;
        public String trace_id;
    }
}

