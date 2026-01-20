package com.teamventure.app.service.dto;

import jakarta.validation.constraints.NotBlank;
import java.util.List;
import java.util.Map;

public class BatchPlanCallbackRequest {
    @NotBlank public String plan_request_id;
    @NotBlank public String user_id;
    public List<Map<String, Object>> plans;
    public String trace_id;
}

