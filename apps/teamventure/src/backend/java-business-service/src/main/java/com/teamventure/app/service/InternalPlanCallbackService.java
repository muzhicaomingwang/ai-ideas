package com.teamventure.app.service;

import com.teamventure.adapter.web.internal.InternalPlanController.BatchPlanRequest;
import com.teamventure.app.support.BizException;
import com.teamventure.app.support.IdGenerator;
import com.teamventure.infrastructure.persistence.mapper.DomainEventMapper;
import com.teamventure.infrastructure.persistence.mapper.PlanMapper;
import com.teamventure.infrastructure.persistence.mapper.PlanRequestMapper;
import com.teamventure.infrastructure.persistence.po.DomainEventPO;
import com.teamventure.infrastructure.persistence.po.PlanPO;
import com.teamventure.infrastructure.persistence.po.PlanRequestPO;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class InternalPlanCallbackService {
    private final PlanRequestMapper planRequestMapper;
    private final PlanMapper planMapper;
    private final DomainEventMapper eventMapper;

    public InternalPlanCallbackService(PlanRequestMapper planRequestMapper, PlanMapper planMapper, DomainEventMapper eventMapper) {
        this.planRequestMapper = planRequestMapper;
        this.planMapper = planMapper;
        this.eventMapper = eventMapper;
    }

    @Transactional
    public void handleGeneratedPlans(BatchPlanRequest req) {
        PlanRequestPO planRequest = planRequestMapper.selectById(req.plan_request_id);
        if (planRequest == null) {
            throw new BizException("NOT_FOUND", "plan request not found");
        }

        List<Map<String, Object>> plans = req.plans == null ? List.of() : req.plans;
        for (Map<String, Object> planMap : plans) {
            PlanPO plan = PlanPO.fromMap(planMap);
            plan.setPlanRequestId(req.plan_request_id);
            plan.setUserId(req.user_id);
            planMapper.insert(plan);
            recordEvent("PlanGenerated", "Plan", plan.getPlanId(), req.user_id, Map.of("plan_id", plan.getPlanId()));
        }

        planRequest.setStatus("COMPLETED");
        planRequest.setGenerationCompletedAt(Instant.now());
        planRequestMapper.updateById(planRequest);
    }

    private void recordEvent(String eventType, String aggregateType, String aggregateId, String userId, Map<String, Object> payload) {
        DomainEventPO evt = new DomainEventPO();
        evt.setEventId(IdGenerator.newId("evt"));
        evt.setEventType(eventType);
        evt.setAggregateType(aggregateType);
        evt.setAggregateId(aggregateId);
        evt.setUserId(userId);
        evt.setPayloadJson(Jsons.toJson(payload));
        evt.setOccurredAt(Instant.now());
        evt.setProcessed(false);
        eventMapper.insert(evt);
    }
}

