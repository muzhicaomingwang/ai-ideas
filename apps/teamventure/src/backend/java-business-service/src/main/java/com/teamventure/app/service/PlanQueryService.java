package com.teamventure.app.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.teamventure.app.support.BizException;
import com.teamventure.infrastructure.persistence.mapper.PlanMapper;
import com.teamventure.infrastructure.persistence.mapper.PlanRequestMapper;
import com.teamventure.infrastructure.persistence.po.PlanPO;
import com.teamventure.infrastructure.persistence.po.PlanRequestPO;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.stereotype.Service;

@Service
public class PlanQueryService {
    private static final int GENERATION_TIMEOUT_MINUTES = 5;

    private final PlanRequestMapper planRequestMapper;
    private final PlanMapper planMapper;
    private final PlanAuthorizationService planAuthorizationService;
    private final OssService ossService;
    private final PlanRouteQueryService planRouteQueryService;

    public PlanQueryService(
            PlanRequestMapper planRequestMapper,
            PlanMapper planMapper,
            PlanAuthorizationService planAuthorizationService,
            OssService ossService,
            PlanRouteQueryService planRouteQueryService
    ) {
        this.planRequestMapper = planRequestMapper;
        this.planMapper = planMapper;
        this.planAuthorizationService = planAuthorizationService;
        this.ossService = ossService;
        this.planRouteQueryService = planRouteQueryService;
    }

    @Transactional(readOnly = true)
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
            Instant timeoutThreshold = Instant.now().minusSeconds((long) GENERATION_TIMEOUT_MINUTES * 60);
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
                item.put("plan_type", "standard");
                item.put("plan_name", "GENERATING".equals(req.getStatus()) ? "方案生成中..." : "生成失败");
                item.put("summary", "");
                item.put("budget_total", null);
                item.put("budget_per_person", null);
                item.put("duration_days", null);
                item.put("departure_city", req.getDepartureCity());
                item.put("destination", req.getDestination());
                item.put("destination_city", req.getDestinationCity());
                item.put("status", req.getStatus().toLowerCase());
                item.put("create_time", req.getGenerationStartedAt());
                item.put("confirmed_time", null);
                item.put("review_started_at", null);
                item.put("created_at", req.getGenerationStartedAt());
                item.put("people_count", req.getPeopleCount());
                item.put("group_size", req.getPeopleCount()); // UL v1.3 alias (non-breaking)
                item.put("start_date", req.getStartDate());
                item.put("end_date", req.getEndDate());
                item.put("is_generating", "GENERATING".equals(req.getStatus()));
                mergedList.add(item);
            }

            totalPending = pendingRequests.size();
        }

        // 2. 处理 draft/confirmed/reviewing/archived 状态（来自 plans 表）
        boolean needPlans = status == null || (!"generating".equalsIgnoreCase(status) && !"failed".equalsIgnoreCase(status));
        Page<PlanPO> plansPage = new Page<>(page, pageSize);
        List<PlanPO> plans;
        if (needPlans) {
            QueryWrapper<PlanPO> planQuery = new QueryWrapper<PlanPO>()
                    .eq("user_id", userId)
                    .isNull("deleted_at")
                    .orderByDesc("create_time");

            if (status != null && !status.isBlank()) {
                planQuery.eq("status", status.toLowerCase());
            }

            plansPage = planMapper.selectPage(plansPage, planQuery);
            plans = plansPage.getRecords();

            // 批量加载 plan_requests（用于 people_count/start_date/end_date）
            Map<String, PlanRequestPO> requestMap = new HashMap<>();
            if (plans != null && !plans.isEmpty()) {
                List<String> requestIds = plans.stream()
                        .map(PlanPO::getPlanRequestId)
                        .filter(id -> id != null && !id.isBlank())
                        .distinct()
                        .toList();
                if (!requestIds.isEmpty()) {
                    List<PlanRequestPO> reqs = planRequestMapper.selectList(new QueryWrapper<PlanRequestPO>()
                            .in("plan_request_id", requestIds));
                    for (PlanRequestPO r : reqs) {
                        requestMap.put(r.getPlanRequestId(), r);
                    }
                }
            }

            // 转换为 Map
            List<Map<String, Object>> planMaps = new ArrayList<>();
            if (plans != null) {
                for (PlanPO plan : plans) {
                    Map<String, Object> item = new HashMap<>();
                    item.put("plan_id", plan.getPlanId());
                    item.put("plan_request_id", plan.getPlanRequestId());
                    item.put("plan_type", plan.getPlanType());
                    item.put("plan_name", plan.getPlanName());
                    item.put("summary", plan.getSummary());
                    item.put("budget_total", plan.getBudgetTotal());
                    item.put("budget_per_person", plan.getBudgetPerPerson());
                    item.put("duration_days", plan.getDurationDays());
                    item.put("departure_city", plan.getDepartureCity());
                    item.put("destination", plan.getDestination());
                    item.put("destination_city", plan.getDestinationCity());
                    item.put("status", plan.getStatus());
                    item.put("create_time", plan.getCreateTime());
                    item.put("confirmed_time", plan.getConfirmedTime());
                    item.put("review_started_at", plan.getReviewStartedAt());
                    item.put("created_at", plan.getCreateTime());

                    PlanRequestPO req = requestMap.get(plan.getPlanRequestId());
                    if (req != null) {
                        item.put("people_count", req.getPeopleCount());
                        item.put("group_size", req.getPeopleCount()); // UL v1.3 alias (non-breaking)
                        item.put("start_date", req.getStartDate());
                        item.put("end_date", req.getEndDate());
                    } else {
                        item.put("people_count", null);
                        item.put("group_size", null);
                    }
                    item.put("is_generating", false);
                    planMaps.add(item);
                }
            }

            // 已确认置顶，其余按创建时间倒序
            planMaps.sort(Comparator.<Map<String, Object>, Integer>comparing(m -> "confirmed".equalsIgnoreCase(String.valueOf(m.get("status"))) ? 0 : 1)
                    .thenComparing(m -> (Instant) m.getOrDefault("create_time", Instant.EPOCH), Comparator.reverseOrder()));

            mergedList.addAll(planMaps);
        }

        Map<String, Object> result = new HashMap<>();
        result.put("plans", mergedList);
        result.put("total", plansPage.getTotal() + totalPending);
        result.put("page", page);
        result.put("pageSize", pageSize);
        result.put("hasMore", plansPage.hasNext());
        return result;
    }

    @Transactional(readOnly = true)
    public Object getPlanDetail(String userId, String planId) {
        PlanPO plan = planMapper.selectById(planId);
        if (plan != null) {
            if (plan.getDeletedAt() != null) {
                throw new BizException("NOT_FOUND", "plan not found");
            }
            planAuthorizationService.requireMemberForCurrent(planId, userId);
            return convertPlanToDetailMap(plan);
        }

        PlanRequestPO req = planRequestMapper.selectById(planId);
        if (req != null) {
            if (req.getDeletedAt() != null) {
                throw new BizException("NOT_FOUND", "plan not found");
            }
            if (!userId.equals(req.getUserId())) {
                throw new BizException("UNAUTHORIZED", "not owner");
            }
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
            result.put("destination", req.getDestination());
            result.put("destination_city", req.getDestinationCity());
            result.put("created_at", req.getGenerationStartedAt());
            result.put("is_generating", isGenerating);
            result.put("group_size", req.getPeopleCount());
            result.put("trip_duration", null);
            return result;
        }

        throw new BizException("NOT_FOUND", "plan not found");
    }

    public Map<String, Object> getPlanRoute(String userId, String planId, Integer day) {
        return planRouteQueryService.getPlanRoute(userId, planId, day);
    }

    private Map<String, Object> convertPlanToDetailMap(PlanPO plan) {
        Map<String, Object> result = new HashMap<>();
        result.put("plan_id", plan.getPlanId());
        result.put("plan_request_id", plan.getPlanRequestId());
        result.put("user_id", plan.getUserId());
        result.put("plan_type", plan.getPlanType());
        result.put("plan_name", plan.getPlanName());
        result.put("summary", plan.getSummary());
        result.put("status", plan.getStatus());
        result.put("logo_url", resolveLogoUrl(plan));
        result.put("budget_total", plan.getBudgetTotal());
        result.put("budget_per_person", plan.getBudgetPerPerson());
        result.put("duration_days", plan.getDurationDays());
        result.put("trip_duration", plan.getDurationDays()); // UL v1.3 alias (non-breaking)
        result.put("departure_city", plan.getDepartureCity());
        result.put("destination", plan.getDestination());
        result.put("destination_city", plan.getDestinationCity());
        result.put("review_count", plan.getReviewCount());
        result.put("average_score", plan.getAverageScore());
        result.put("confirmed_time", plan.getConfirmedTime());
        result.put("review_started_at", plan.getReviewStartedAt());
        result.put("itinerary_version", plan.getItineraryVersion() == null ? 1 : plan.getItineraryVersion());
        PlanRequestPO req = plan.getPlanRequestId() == null ? null : planRequestMapper.selectById(plan.getPlanRequestId());
        result.put("people_count", req == null ? null : req.getPeopleCount());
        result.put("group_size", req == null ? null : req.getPeopleCount()); // UL v1.3 alias (non-breaking)

        result.put("highlights", Jsons.toStringList(plan.getHighlights()));
        result.put("itinerary", Jsons.toMap(plan.getItinerary()));

        result.put("is_generating", false);
        return result;
    }

    private String resolveLogoUrl(PlanPO plan) {
        String url = ossService.resolveItineraryUrl(plan.getLogoStorage());
        if (url != null && !url.isBlank()) return url;
        return ossService.resolveItineraryUrl(plan.getLogoUrl());
    }
}
