package com.teamventure.app.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
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
        po.setDestination(req.destination);
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
        mq.put("destination", req.destination);
        mq.put("preferences", req.preferences == null ? Map.of() : req.preferences);
        mq.put("trace_id", IdGenerator.newId("trace"));

        rabbitTemplate.convertAndSend(exchange, routingKey, Jsons.toJson(mq));
        return new GenerateResponse(planRequestId, "generating");
    }

    private static final int GENERATION_TIMEOUT_MINUTES = 5;

    /**
     * 查询方案列表，支持按状态筛选
     *
     * @param userId   用户ID
     * @param page     页码
     * @param pageSize 每页大小
     * @param status   状态筛选：draft/confirmed/generating/failed，null表示全部
     * @return 分页结果
     */
    public Map<String, Object> listPlans(String userId, int page, int pageSize, String status) {
        List<Map<String, Object>> mergedList = new ArrayList<>();
        long totalPending = 0;

        // 1. 处理 generating/failed 状态（来自 plan_requests 表）
        boolean needPendingRequests = status == null || "generating".equalsIgnoreCase(status) || "failed".equalsIgnoreCase(status);
        if (needPendingRequests) {
            QueryWrapper<PlanRequestPO> pendingQuery = new QueryWrapper<PlanRequestPO>()
                    .eq("user_id", userId)
                    .isNull("deleted_at")
                    .orderByDesc("create_time");

            // 根据 status 筛选
            if ("generating".equalsIgnoreCase(status)) {
                pendingQuery.eq("status", "GENERATING");
            } else if ("failed".equalsIgnoreCase(status)) {
                pendingQuery.eq("status", "FAILED");
            } else {
                // 全部：包含 GENERATING 和 FAILED
                pendingQuery.in("status", List.of("GENERATING", "FAILED"));
            }

            List<PlanRequestPO> pendingRequests = planRequestMapper.selectList(pendingQuery);

            // 自动标记超时的 GENERATING 请求为 FAILED
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

            // 转换为统一格式
            for (PlanRequestPO req : pendingRequests) {
                Map<String, Object> item = new HashMap<>();
                item.put("plan_id", req.getPlanRequestId());
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
            totalPending = pendingRequests.size();
        }

        // 2. 处理 draft/reviewing/confirmed 状态（来自 plans 表）
        boolean needPlans = status == null || "draft".equalsIgnoreCase(status)
                || "reviewing".equalsIgnoreCase(status) || "confirmed".equalsIgnoreCase(status);
        Page<PlanPO> plansPage = new Page<>(page, pageSize);
        if (needPlans) {
            QueryWrapper<PlanPO> planQuery = new QueryWrapper<PlanPO>()
                    .eq("user_id", userId)
                    .isNull("deleted_at")
                    .isNull("archived_at");

            // 根据 status 筛选
            if ("draft".equalsIgnoreCase(status)) {
                planQuery.eq("status", "draft");
                planQuery.orderByDesc("create_time");
            } else if ("reviewing".equalsIgnoreCase(status)) {
                planQuery.eq("status", "reviewing");
                planQuery.orderByDesc("review_started_at");
            } else if ("confirmed".equalsIgnoreCase(status)) {
                planQuery.eq("status", "confirmed");
                planQuery.orderByDesc("confirmed_time");
            } else {
                // 全部：confirmed 置顶，reviewing 次之，然后按 create_time 倒序
                // 注意：MyBatis-Plus 的 orderByAsc/orderByDesc 仅支持列名；传入表达式可能触发 SQL 注入校验或生成非法 SQL，导致 500。
                // 这里用 last() 追加固定的 ORDER BY 片段（无用户输入），保证“全部”列表也稳定可用。
                planQuery.last("ORDER BY CASE WHEN status = 'confirmed' THEN 0 WHEN status = 'reviewing' THEN 1 ELSE 2 END ASC, create_time DESC");
            }

            plansPage = planMapper.selectPage(new Page<>(page, pageSize), planQuery);

            // 批量查询关联的 plan_request 信息
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

            // 转换为统一格式
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
                item.put("confirmed_time", plan.getConfirmedTime());
                item.put("review_started_at", plan.getReviewStartedAt());
                item.put("create_time", plan.getCreateTime());
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
        }

        // 3. 返回结果
        Map<String, Object> result = new HashMap<>();
        result.put("plans", mergedList);
        result.put("total", plansPage.getTotal() + totalPending);
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

    /**
     * 确认方案：reviewing → confirmed
     * 只允许从"通晒中"状态确认方案
     */
    public void confirmPlan(String userId, String planId) {
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
        if ("confirmed".equalsIgnoreCase(plan.getStatus())) {
            return; // 幂等：已确认则直接返回
        }
        if (!"reviewing".equalsIgnoreCase(plan.getStatus())) {
            throw new BizException("INVALID_STATUS", "只有通晒中状态的方案才能确认");
        }
        plan.setStatus("confirmed");
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
     * 归档方案：confirmed → archived
     * 只有已确认的方案才能归档
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
        if (!"confirmed".equalsIgnoreCase(plan.getStatus())) {
            throw new BizException("INVALID_STATUS", "只有已确认状态的方案才能归档");
        }
        plan.setArchivedAt(Instant.now());
        plan.setStatus("archived");
        planMapper.updateById(plan);
        recordEvent("PlanArchived", "Plan", planId, userId, Map.of("plan_id", planId));
    }

    /**
     * 提交通晒：draft → reviewing
     * 将方案从"制定完成"状态提交到"通晒中"状态
     */
    public void submitReview(String userId, String planId) {
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
        if (!"draft".equalsIgnoreCase(plan.getStatus())) {
            throw new BizException("INVALID_STATUS", "只有制定完成状态的方案才能提交通晒");
        }
        plan.setStatus("reviewing");
        plan.setReviewStartedAt(Instant.now());
        planMapper.updateById(plan);
        recordEvent("PlanSubmittedForReview", "Plan", planId, userId, Map.of("plan_id", planId));
    }

    /**
     * 回退通晒：confirmed → reviewing
     * 将已确认的方案回退到通晒中状态（允许重新修改）
     */
    public void revertReview(String userId, String planId) {
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
        if (!"confirmed".equalsIgnoreCase(plan.getStatus())) {
            throw new BizException("INVALID_STATUS", "只有已确认状态的方案才能回退通晒");
        }
        // 使用 UpdateWrapper 显式将 confirmed_time 设为 null
        UpdateWrapper<PlanPO> updateWrapper = new UpdateWrapper<>();
        updateWrapper.eq("plan_id", planId)
                .set("status", "reviewing")
                .set("confirmed_time", null);
        planMapper.update(null, updateWrapper);
        recordEvent("PlanRevertedToReview", "Plan", planId, userId, Map.of("plan_id", planId));
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
        result.put("destination", plan.getDestination());
        result.put("confirmed_time", plan.getConfirmedTime());
        result.put("review_started_at", plan.getReviewStartedAt());

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
