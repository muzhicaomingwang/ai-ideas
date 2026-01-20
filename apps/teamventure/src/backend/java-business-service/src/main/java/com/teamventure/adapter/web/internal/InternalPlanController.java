package com.teamventure.adapter.web.internal;

import com.teamventure.adapter.web.common.ApiResponse;
import com.teamventure.app.service.InternalPlanCallbackService;
import com.teamventure.app.service.dto.BatchPlanCallbackRequest;
import jakarta.validation.Valid;
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
                                         @Valid @RequestBody BatchPlanCallbackRequest req) {
        if (!internalSecret.equals(secret)) {
            return ApiResponse.failure("UNAUTHORIZED", "invalid internal secret");
        }
        callbackService.handleGeneratedPlans(req);
        return ApiResponse.success();
    }
}
