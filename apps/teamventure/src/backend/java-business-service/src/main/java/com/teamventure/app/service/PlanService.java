package com.teamventure.app.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.teamventure.adapter.web.plans.PlanController.GenerateRequest;
import com.teamventure.adapter.web.plans.PlanController.GenerateResponse;
import com.teamventure.adapter.web.plans.PlanController.SupplierContactRequest;
import com.teamventure.app.support.BizException;
import com.teamventure.app.support.IdGenerator;
import com.teamventure.infrastructure.persistence.mapper.DomainEventMapper;
import com.teamventure.infrastructure.persistence.mapper.PlanMapper;
import com.teamventure.infrastructure.persistence.mapper.PlanRequestMapper;
import com.teamventure.infrastructure.persistence.mapper.SupplierContactLogMapper;
import com.teamventure.infrastructure.persistence.po.DomainEventPO;
import com.teamventure.infrastructure.persistence.po.PlanPO;
import com.teamventure.infrastructure.persistence.po.PlanRequestPO;
import com.teamventure.infrastructure.persistence.po.SupplierContactLogPO;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class PlanService {
    private final PlanRequestMapper planRequestMapper;
    private final PlanMapper planMapper;
    private final SupplierContactLogMapper contactLogMapper;
    private final DomainEventMapper eventMapper;
    private final RabbitTemplate rabbitTemplate;
    private final String exchange;
    private final String routingKey;

    public PlanService(
            PlanRequestMapper planRequestMapper,
            PlanMapper planMapper,
            SupplierContactLogMapper contactLogMapper,
            DomainEventMapper eventMapper,
            RabbitTemplate rabbitTemplate,
            @Value("${teamventure.mq.exchange.plan-generation}") String exchange,
            @Value("${teamventure.mq.routing-key.plan-request}") String routingKey
    ) {
        this.planRequestMapper = planRequestMapper;
        this.planMapper = planMapper;
        this.contactLogMapper = contactLogMapper;
        this.eventMapper = eventMapper;
        this.rabbitTemplate = rabbitTemplate;
        this.exchange = exchange;
        this.routingKey = routingKey;
    }

    public GenerateResponse createPlanRequestAndPublish(String userId, GenerateRequest req) {
        String planRequestId = IdGenerator.newId("plan_req");
        PlanRequestPO po = new PlanRequestPO();
        po.setPlanRequestId(planRequestId);
        po.setUserId(userId);
        po.setPeopleCount(req.people_count);
        po.setBudgetMin(req.budget_min);
        po.setBudgetMax(req.budget_max);
        po.setStartDate(req.start_date);
        po.setEndDate(req.end_date);
        po.setDepartureCity(req.departure_city);
        po.setPreferencesJson(req.preferences == null ? "{}" : Jsons.toJson(req.preferences));
        po.setStatus("GENERATING");
        po.setGenerationStartedAt(Instant.now());
        planRequestMapper.insert(po);

        recordEvent("PlanRequestCreated", "PlanRequest", planRequestId, userId, Map.of("plan_request_id", planRequestId));

        Map<String, Object> mq = new HashMap<>();
        mq.put("plan_request_id", planRequestId);
        mq.put("user_id", userId);
        mq.put("people_count", req.people_count);
        mq.put("budget_min", req.budget_min);
        mq.put("budget_max", req.budget_max);
        mq.put("start_date", req.start_date);
        mq.put("end_date", req.end_date);
        mq.put("departure_city", req.departure_city);
        mq.put("preferences", req.preferences == null ? Map.of() : req.preferences);
        mq.put("trace_id", IdGenerator.newId("trace"));

        rabbitTemplate.convertAndSend(exchange, routingKey, Jsons.toJson(mq));
        return new GenerateResponse(planRequestId, "generating");
    }

    public Object listPlans(String userId, int page, int pageSize) {
        Page<PlanPO> p = new Page<>(page, pageSize);
        Page<PlanPO> res = planMapper.selectPage(
                p,
                new QueryWrapper<PlanPO>().eq("user_id", userId).orderByDesc("create_time")
        );
        return res;
    }

    public Object getPlanDetail(String userId, String planId) {
        PlanPO plan = planMapper.selectById(planId);
        if (plan == null) {
            throw new BizException("NOT_FOUND", "plan not found");
        }
        if (!userId.equals(plan.getUserId())) {
            throw new BizException("UNAUTHORIZED", "not owner");
        }
        return plan;
    }

    public void confirmPlan(String userId, String planId) {
        PlanPO plan = planMapper.selectById(planId);
        if (plan == null) {
            throw new BizException("NOT_FOUND", "plan not found");
        }
        if (!userId.equals(plan.getUserId())) {
            throw new BizException("UNAUTHORIZED", "not owner");
        }
        if ("CONFIRMED".equalsIgnoreCase(plan.getStatus())) {
            return;
        }
        plan.setStatus("CONFIRMED");
        plan.setConfirmedTime(Instant.now());
        planMapper.updateById(plan);
        recordEvent("PlanConfirmed", "Plan", planId, userId, Map.of("plan_id", planId));
    }

    public void logSupplierContact(String userId, String planId, SupplierContactRequest req) {
        SupplierContactLogPO po = new SupplierContactLogPO();
        po.setContactId(IdGenerator.newId("contact"));
        po.setPlanId(planId);
        po.setSupplierId(req.supplier_id);
        po.setUserId(userId);
        po.setChannel(req.channel);
        po.setNotes(req.notes);
        contactLogMapper.insert(po);
        recordEvent(
                "SupplierContacted",
                "SupplierContactLog",
                po.getContactId(),
                userId,
                Map.of("plan_id", planId, "supplier_id", req.supplier_id, "channel", req.channel)
        );
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

