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
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
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

    private static final int GENERATION_TIMEOUT_MINUTES = 5;

    public Map<String, Object> listPlans(String userId, int page, int pageSize) {
        // 1. 查询 GENERATING 和 FAILED 状态的请求（排除已删除）
        List<PlanRequestPO> pendingRequests = planRequestMapper.selectList(
                new QueryWrapper<PlanRequestPO>()
                        .eq("user_id", userId)
                        .in("status", List.of("GENERATING", "FAILED"))
                        .isNull("deleted_at")
                        .orderByDesc("create_time")
        );

        // 1.1 自动标记超时的 GENERATING 请求为 FAILED
        Instant timeoutThreshold = Instant.now().minusSeconds(GENERATION_TIMEOUT_MINUTES * 60);
        for (PlanRequestPO req : pendingRequests) {
            if ("GENERATING".equals(req.getStatus()) && req.getGenerationStartedAt() != null
                    && req.getGenerationStartedAt().isBefore(timeoutThreshold)) {
                req.setStatus("FAILED");
                req.setErrorCode("GENERATION_TIMEOUT");
                req.setErrorMessage("方案生成超时，请重新提交");
                planRequestMapper.updateById(req);
            }
        }

        // 2. 查询已生成的方案（排除已删除和已归档）
        Page<PlanPO> p = new Page<>(page, pageSize);
        Page<PlanPO> plansPage = planMapper.selectPage(
                p,
                new QueryWrapper<PlanPO>()
                        .eq("user_id", userId)
                        .isNull("deleted_at")
                        .isNull("archived_at")
                        .orderByDesc("create_time")
        );

        // 3. 合并结果（生成中的排在前面）
        List<Map<String, Object>> mergedList = new ArrayList<>();

        // 添加生成中/失败的请求（转换为统一格式）
        for (PlanRequestPO req : pendingRequests) {
            Map<String, Object> item = new HashMap<>();
            item.put("plan_id", req.getPlanRequestId()); // 用 plan_request_id 作为 plan_id
            item.put("plan_request_id", req.getPlanRequestId());
            boolean isGenerating = "GENERATING".equals(req.getStatus());
            item.put("plan_name", isGenerating ? "方案生成中..." : "生成失败");
            item.put("status", req.getStatus().toLowerCase());
            item.put("people_count", req.getPeopleCount());
            item.put("budget_total", req.getBudgetMax());
            item.put("start_date", req.getStartDate());
            item.put("end_date", req.getEndDate());
            item.put("departure_city", req.getDepartureCity());
            item.put("destination", req.getDestination());
            item.put("created_at", req.getGenerationStartedAt());
            item.put("is_generating", isGenerating);
            mergedList.add(item);
        }

        // 添加已生成的方案
        // 先收集所有 plan_request_id，批量查询关联信息
        List<String> planRequestIds = plansPage.getRecords().stream()
                .map(PlanPO::getPlanRequestId)
                .filter(id -> id != null)
                .toList();
        Map<String, PlanRequestPO> requestMap = new HashMap<>();
        if (!planRequestIds.isEmpty()) {
            List<PlanRequestPO> requests = planRequestMapper.selectList(
                    new QueryWrapper<PlanRequestPO>().in("plan_request_id", planRequestIds)
            );
            for (PlanRequestPO req : requests) {
                requestMap.put(req.getPlanRequestId(), req);
            }
        }

        for (PlanPO plan : plansPage.getRecords()) {
            Map<String, Object> item = new HashMap<>();
            item.put("plan_id", plan.getPlanId());
            item.put("plan_request_id", plan.getPlanRequestId());
            item.put("plan_name", plan.getPlanName());
            item.put("status", plan.getStatus());
            item.put("plan_type", plan.getPlanType());
            item.put("budget_total", plan.getBudgetTotal());
            item.put("duration_days", plan.getDurationDays());
            item.put("departure_city", plan.getDepartureCity());
            item.put("destination", plan.getDestination());
            // 从 plan_request 获取额外信息
            PlanRequestPO req = requestMap.get(plan.getPlanRequestId());
            if (req != null) {
                item.put("people_count", req.getPeopleCount());
                item.put("start_date", req.getStartDate());
                item.put("end_date", req.getEndDate());
            } else {
                item.put("people_count", null);
            }
            item.put("is_generating", false);
            mergedList.add(item);
        }

        // 4. 返回结果
        Map<String, Object> result = new HashMap<>();
        result.put("plans", mergedList);
        result.put("total", plansPage.getTotal() + pendingRequests.size());
        result.put("page", page);
        result.put("pageSize", pageSize);
        result.put("hasMore", plansPage.hasNext());
        return result;
    }

    public Object getPlanDetail(String userId, String planId) {
        // 先尝试查询 plans 表
        PlanPO plan = planMapper.selectById(planId);
        if (plan != null) {
            // 检查是否已删除
            if (plan.getDeletedAt() != null) {
                throw new BizException("NOT_FOUND", "plan not found");
            }
            if (!userId.equals(plan.getUserId())) {
                throw new BizException("UNAUTHORIZED", "not owner");
            }
            // 转换为 Map 并解析 JSON 字段，供前端使用
            return convertPlanToDetailMap(plan);
        }

        // 如果 plans 表没找到，查询 plan_requests 表（可能是生成中的）
        PlanRequestPO req = planRequestMapper.selectById(planId);
        if (req != null) {
            // 检查是否已删除
            if (req.getDeletedAt() != null) {
                throw new BizException("NOT_FOUND", "plan not found");
            }
            if (!userId.equals(req.getUserId())) {
                throw new BizException("UNAUTHORIZED", "not owner");
            }
            // 返回生成中/失败的状态信息
            boolean isGenerating = "GENERATING".equals(req.getStatus());
            Map<String, Object> result = new HashMap<>();
            result.put("plan_id", req.getPlanRequestId());
            result.put("plan_request_id", req.getPlanRequestId());
            result.put("plan_name", isGenerating ? "方案生成中..." : "生成失败");
            result.put("status", req.getStatus().toLowerCase());
            result.put("people_count", req.getPeopleCount());
            result.put("budget_min", req.getBudgetMin());
            result.put("budget_max", req.getBudgetMax());
            result.put("start_date", req.getStartDate());
            result.put("end_date", req.getEndDate());
            result.put("departure_city", req.getDepartureCity());
            result.put("created_at", req.getGenerationStartedAt());
            result.put("is_generating", isGenerating);
            return result;
        }

        throw new BizException("NOT_FOUND", "plan not found");
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

    /**
     * 删除方案（软删除）
     * 支持删除已生成的方案和生成中/失败的请求
     */
    public void deletePlan(String userId, String planId) {
        // 1. 先查 plans 表
        PlanPO plan = planMapper.selectById(planId);
        if (plan != null) {
            if (!userId.equals(plan.getUserId())) {
                throw new BizException("UNAUTHORIZED", "not owner");
            }
            if (plan.getDeletedAt() != null) {
                return; // 幂等：已删除则直接返回
            }
            plan.setDeletedAt(Instant.now());
            planMapper.updateById(plan);
            recordEvent("PlanDeleted", "Plan", planId, userId, Map.of("plan_id", planId));
            return;
        }

        // 2. 再查 plan_requests 表（处理生成中/失败的）
        PlanRequestPO req = planRequestMapper.selectById(planId);
        if (req != null) {
            if (!userId.equals(req.getUserId())) {
                throw new BizException("UNAUTHORIZED", "not owner");
            }
            if (req.getDeletedAt() != null) {
                return; // 幂等：已删除则直接返回
            }
            req.setDeletedAt(Instant.now());
            planRequestMapper.updateById(req);
            recordEvent("PlanRequestDeleted", "PlanRequest", planId, userId, Map.of("plan_request_id", planId));
            return;
        }

        throw new BizException("NOT_FOUND", "plan not found");
    }

    /**
     * 归档方案
     * 只能归档已生成的方案（不能归档生成中/失败的请求）
     */
    public void archivePlan(String userId, String planId) {
        PlanPO plan = planMapper.selectById(planId);
        if (plan == null) {
            throw new BizException("NOT_FOUND", "plan not found");
        }
        if (!userId.equals(plan.getUserId())) {
            throw new BizException("UNAUTHORIZED", "not owner");
        }
        if (plan.getDeletedAt() != null) {
            throw new BizException("NOT_FOUND", "plan not found");
        }
        if (plan.getArchivedAt() != null) {
            return; // 幂等：已归档则直接返回
        }
        plan.setArchivedAt(Instant.now());
        planMapper.updateById(plan);
        recordEvent("PlanArchived", "Plan", planId, userId, Map.of("plan_id", planId));
    }

    /**
     * 将 PlanPO 转换为详情 Map，解析 JSON 字符串字段
     */
    private Map<String, Object> convertPlanToDetailMap(PlanPO plan) {
        Map<String, Object> result = new HashMap<>();
        result.put("plan_id", plan.getPlanId());
        result.put("plan_request_id", plan.getPlanRequestId());
        result.put("user_id", plan.getUserId());
        result.put("plan_type", plan.getPlanType());
        result.put("plan_name", plan.getPlanName());
        result.put("summary", plan.getSummary());
        result.put("status", plan.getStatus());
        result.put("budget_total", plan.getBudgetTotal());
        result.put("budget_per_person", plan.getBudgetPerPerson());
        result.put("duration_days", plan.getDurationDays());
        result.put("departure_city", plan.getDepartureCity());
        result.put("confirmed_time", plan.getConfirmedTime());

        // 解析 JSON 字符串字段
        result.put("highlights", Jsons.toStringList(plan.getHighlights())); // highlights 是字符串数组
        result.put("itinerary", Jsons.toMap(plan.getItinerary()));
        result.put("budget_breakdown", Jsons.toMap(plan.getBudgetBreakdown()));
        // 前端期望 suppliers 而不是 supplier_snapshots
        result.put("suppliers", Jsons.toList(plan.getSupplierSnapshots()));

        result.put("is_generating", false);
        return result;
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

