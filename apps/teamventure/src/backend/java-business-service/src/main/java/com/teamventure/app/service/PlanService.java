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
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
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
    private final String amapApiKey;
    private final HttpClient httpClient;

    // 新增：地图相关组件
    private final com.teamventure.infrastructure.map.ZoomCalculator zoomCalculator;
    private final com.teamventure.infrastructure.cache.StaticMapUrlCache staticMapUrlCache;
    private final com.teamventure.infrastructure.map.MarkerStyleConfig markerStyleConfig;
    private final com.teamventure.infrastructure.map.PathStyleConfig pathStyleConfig;
    private final com.teamventure.infrastructure.map.MapDegradationHandler mapDegradationHandler;

    private static final Map<String, double[]> GEO_CACHE = new LinkedHashMap<>(256, 0.75f, true) {
        @Override
        protected boolean removeEldestEntry(Map.Entry<String, double[]> eldest) {
            return size() > 300;
        }
    };

    /**
     * 路线规划结果缓存（LRU淘汰策略）
     * Key格式: "origin_lng,lat|dest_lng,lat|mode"
     */
    private static final Map<String, RouteSegment> ROUTE_CACHE = new LinkedHashMap<>(128, 0.75f, true) {
        @Override
        protected boolean removeEldestEntry(Map.Entry<String, RouteSegment> eldest) {
            return size() > 200;
        }
    };

    public PlanService(
            PlanRequestMapper planRequestMapper,
            PlanMapper planMapper,
            SupplierContactLogMapper contactLogMapper,
            DomainEventMapper eventMapper,
            RabbitTemplate rabbitTemplate,
            @Value("${teamventure.mq.exchange.plan-generation}") String exchange,
            @Value("${teamventure.mq.routing-key.plan-request}") String routingKey,
            @Value("${AMAP_API_KEY:}") String amapApiKey,
            com.teamventure.infrastructure.map.ZoomCalculator zoomCalculator,
            com.teamventure.infrastructure.cache.StaticMapUrlCache staticMapUrlCache,
            com.teamventure.infrastructure.map.MarkerStyleConfig markerStyleConfig,
            com.teamventure.infrastructure.map.PathStyleConfig pathStyleConfig,
            com.teamventure.infrastructure.map.MapDegradationHandler mapDegradationHandler
    ) {
        this.planRequestMapper = planRequestMapper;
        this.planMapper = planMapper;
        this.contactLogMapper = contactLogMapper;
        this.eventMapper = eventMapper;
        this.rabbitTemplate = rabbitTemplate;
        this.exchange = exchange;
        this.routingKey = routingKey;
        this.amapApiKey = amapApiKey == null ? "" : amapApiKey;
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(java.time.Duration.ofSeconds(3))
                .build();

        // 新增组件
        this.zoomCalculator = zoomCalculator;
        this.staticMapUrlCache = staticMapUrlCache;
        this.markerStyleConfig = markerStyleConfig;
        this.pathStyleConfig = pathStyleConfig;
        this.mapDegradationHandler = mapDegradationHandler;
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
        po.setDestinationCity(req.destination_city);
        po.setPreferencesJson(req.preferences == null ? "{}" : Jsons.toJson(req.preferences));
        po.setStatus("GENERATING");
        po.setGenerationStartedAt(Instant.now());
        planRequestMapper.insert(po);

        recordEvent("PlanRequestCreated", "PlanRequest", planRequestId, userId, Map.of("plan_request_id", planRequestId));
        // UL v1.3+ (backward compatible): more explicit event name.
        recordEvent("PlanGenerationRequested", "PlanRequest", planRequestId, userId, Map.of("plan_request_id", planRequestId));

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
        mq.put("destination_city", req.destination_city);
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
                item.put("group_size", req.getPeopleCount()); // UL v1.3 alias (non-breaking)
                item.put("budget_total", req.getBudgetMax());
                item.put("start_date", req.getStartDate());
                item.put("end_date", req.getEndDate());
                item.put("trip_duration", null); // UL v1.3 alias (unknown for pending requests)
                item.put("departure_city", req.getDepartureCity());
                item.put("destination", req.getDestination());
                item.put("destination_city", req.getDestinationCity());
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
                item.put("trip_duration", plan.getDurationDays()); // UL v1.3 alias (non-breaking)
                item.put("departure_city", plan.getDepartureCity());
                item.put("destination", plan.getDestination());
                item.put("destination_city", plan.getDestinationCity());
                item.put("confirmed_time", plan.getConfirmedTime());
                item.put("review_started_at", plan.getReviewStartedAt());
                // API 统一输出 created_at（前端列表使用该字段）；create_time 为数据库字段命名
                item.put("created_at", plan.getCreateTime());
                // 从 plan_request 获取额外信息
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
            result.put("destination", req.getDestination());
            result.put("destination_city", req.getDestinationCity());
            result.put("created_at", req.getGenerationStartedAt());
            result.put("is_generating", isGenerating);
            // UL v1.3 alias fields (non-breaking)
            result.put("group_size", req.getPeopleCount());
            result.put("trip_duration", null);
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
        // UL v1.3+ (backward compatible): more explicit event name.
        recordEvent("PlanAdoptionConfirmed", "Plan", planId, userId, Map.of("plan_id", planId));
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

    public Map<String, Object> getPlanRoute(String userId, String planId, Integer day) {
        PlanPO plan = planMapper.selectById(planId);
        if (plan == null || plan.getDeletedAt() != null) {
            throw new BizException("NOT_FOUND", "plan not found");
        }
        if (!userId.equals(plan.getUserId())) {
            throw new BizException("UNAUTHORIZED", "not owner");
        }

        Map<String, Object> itinerary = Jsons.toMap(plan.getItinerary());
        Object daysObj = itinerary.get("days");
        if (!(daysObj instanceof List<?> daysListRaw) || daysListRaw.isEmpty()) {
            return Map.of(
                    "markers", List.of(),
                    "polyline", List.of(),
                    "include_points", List.of(),
                    "unresolved", List.of()
            );
        }

        String cityHint = plan.getDestinationCity() == null || plan.getDestinationCity().isBlank()
                ? (plan.getDestination() == null ? "" : plan.getDestination())
                : plan.getDestinationCity();
        List<Map<String, Object>> markers = new ArrayList<>();
        List<Map<String, Object>> points = new ArrayList<>();
        List<Map<String, Object>> unresolved = new ArrayList<>();

        int markerId = 1;
        for (Object d : daysListRaw) {
            if (!(d instanceof Map<?, ?> dayMapRaw)) continue;
            Map<String, Object> dayMap = castMap(dayMapRaw);
            Integer dayNo = asInt(dayMap.get("day")).orElse(null);
            if (day != null && dayNo != null && !day.equals(dayNo)) continue;
            if (day != null && dayNo == null) continue;

            Object itemsObj = dayMap.get("items");
            if (!(itemsObj instanceof List<?> itemsRaw)) continue;
            for (Object it : itemsRaw) {
                if (!(it instanceof Map<?, ?> itemRaw)) continue;
                Map<String, Object> item = castMap(itemRaw);
                String activity = asString(item.get("activity")).orElse("");
                String location = asString(item.get("location")).orElse("");

                String keyword = !location.isBlank() ? location : activity;
                if (keyword.isBlank()) continue;

                Optional<double[]> lngLat = resolveLngLat(keyword, cityHint);
                if (lngLat.isEmpty()) {
                    unresolved.add(Map.of(
                            "day", dayNo == null ? 0 : dayNo,
                            "keyword", keyword
                    ));
                    continue;
                }
                double lng = lngLat.get()[0];
                double lat = lngLat.get()[1];

                markers.add(Map.of(
                        "id", markerId,
                        "latitude", lat,
                        "longitude", lng,
                        "title", keyword.length() > 18 ? keyword.substring(0, 18) : keyword
                ));
                points.add(Map.of("latitude", lat, "longitude", lng));
                markerId++;
            }
        }

        // === 路线规划逻辑 ===
        List<Map<String, Object>> allRoutePoints = new ArrayList<>();
        List<Map<String, Object>> segmentInfos = new ArrayList<>();
        int totalDistance = 0;
        int totalDuration = 0;

        // 遍历相邻地点对，规划每段路线
        for (int i = 0; i < markers.size() - 1; i++) {
            Map<String, Object> origin = markers.get(i);
            Map<String, Object> dest = markers.get(i + 1);

            double[] originLngLat = {
                    (double) origin.get("longitude"),
                    (double) origin.get("latitude")
            };
            double[] destLngLat = {
                    (double) dest.get("longitude"),
                    (double) dest.get("latitude")
            };

            // 计算直线距离
            double distanceKm = calculateDistance(originLngLat, destLngLat);

            // 选择交通方式
            String mode = selectTransportMode(distanceKm);

            // 尝试路线规划
            Optional<RouteSegment> segment = resolveRouteSegment(originLngLat, destLngLat, mode);

            if (segment.isPresent()) {
                // 成功：使用规划的路径点
                RouteSegment seg = segment.get();
                allRoutePoints.addAll(seg.points);

                totalDistance += seg.distanceMeters;
                totalDuration += seg.durationSeconds;

                segmentInfos.add(Map.of(
                        "from", origin.get("title"),
                        "to", dest.get("title"),
                        "distance", seg.distanceMeters,
                        "duration", seg.durationSeconds,
                        "mode", seg.mode
                ));
            } else {
                // 降级：使用起点和终点的直线连接
                allRoutePoints.add(Map.of(
                        "latitude", origin.get("latitude"),
                        "longitude", origin.get("longitude")
                ));
                allRoutePoints.add(Map.of(
                        "latitude", dest.get("latitude"),
                        "longitude", dest.get("longitude")
                ));

                int estimatedDistance = (int) (distanceKm * 1000);
                totalDistance += estimatedDistance;

                segmentInfos.add(Map.of(
                        "from", origin.get("title"),
                        "to", dest.get("title"),
                        "distance", estimatedDistance,
                        "duration", 0,
                        "mode", "direct",
                        "warning", "路线规划失败，显示为直线连接"
                ));
            }
        }

        // 构建polyline（使用规划的路径点）
        List<Map<String, Object>> polyline = List.of(
                Map.of(
                        "points", allRoutePoints,
                        "color", "#1890FF",
                        "width", 6,
                        "borderColor", "#ffffff",
                        "borderWidth", 2
                )
        );

        // Determine route type and generate static map URL for same-city routes
        String mapType = "interactive";
        String staticMapUrl = "";

        if (!points.isEmpty() && !amapApiKey.isBlank()) {
            // Calculate geographic bounding box
            double minLat = points.stream().mapToDouble(p -> (double) p.get("latitude")).min().orElse(0);
            double maxLat = points.stream().mapToDouble(p -> (double) p.get("latitude")).max().orElse(0);
            double minLng = points.stream().mapToDouble(p -> (double) p.get("longitude")).min().orElse(0);
            double maxLng = points.stream().mapToDouble(p -> (double) p.get("longitude")).max().orElse(0);

            double latSpan = maxLat - minLat;
            double lngSpan = maxLng - minLng;
            double maxSpan = Math.max(latSpan, lngSpan);

            // Same-city route: span < 0.5 degrees (≈50km radius) - 修改阈值
            if (maxSpan < 0.5) {
                mapType = "static";

                // 转换为Point对象列表
                List<com.teamventure.domain.valueobject.MapRequest.Point> routePoints = new ArrayList<>();
                for (Map<String, Object> point : points) {
                    routePoints.add(
                        com.teamventure.domain.valueobject.MapRequest.Point.of(
                            (double) point.get("longitude"),
                            (double) point.get("latitude")
                        )
                    );
                }

                // 计算中心点
                double centerLat = (minLat + maxLat) / 2.0;
                double centerLng = (minLng + maxLng) / 2.0;
                com.teamventure.domain.valueobject.MapRequest.Point center =
                    com.teamventure.domain.valueobject.MapRequest.Point.of(centerLng, centerLat);

                // 使用智能zoom计算器
                int zoom = zoomCalculator.calculateOptimalZoom(
                    routePoints,
                    com.teamventure.domain.valueobject.MapSizePreset.DETAIL
                );

                // 使用样式配置生成markers和paths参数
                String markersParam = markerStyleConfig.generateMarkersParam(routePoints);
                String pathsParam = pathStyleConfig.generatePathsParam(routePoints);

                // 构建MapRequest对象
                com.teamventure.domain.valueobject.MapRequest mapRequest =
                    com.teamventure.domain.valueobject.MapRequest.builder()
                        .size(com.teamventure.domain.valueobject.MapSizePreset.DETAIL)
                        .zoom(zoom)
                        .center(center)
                        .markers(markersParam)
                        .paths(pathsParam)
                        .style("normal")
                        .format("png")
                        .build();

                // 使用缓存获取URL（带降级处理）
                staticMapUrl = staticMapUrlCache.getOrGenerate(
                    mapRequest,
                    () -> mapDegradationHandler.callWithFallback(
                        mapRequest,
                        () -> buildAmapStaticMapUrl(mapRequest)
                    )
                );
            }
        }

        // 构建summary
        Map<String, Object> summary = Map.of(
                "totalDistance", totalDistance,
                "totalDuration", totalDuration
        );

        Map<String, Object> result = new HashMap<>();
        result.put("markers", markers);
        result.put("polyline", polyline);
        result.put("include_points", allRoutePoints);  // 改为allRoutePoints
        result.put("unresolved", unresolved);
        result.put("mapType", mapType);
        result.put("staticMapUrl", staticMapUrl);
        result.put("segments", segmentInfos);  // 新增
        result.put("summary", summary);        // 新增

        return result;
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

        // 解析 JSON 字符串字段
        result.put("highlights", Jsons.toStringList(plan.getHighlights())); // highlights 是字符串数组
        result.put("itinerary", Jsons.toMap(plan.getItinerary()));

        result.put("is_generating", false);
        return result;
    }

    private static Map<String, Object> castMap(Map<?, ?> raw) {
        Map<String, Object> m = new HashMap<>();
        for (Map.Entry<?, ?> e : raw.entrySet()) {
            if (e.getKey() == null) continue;
            m.put(String.valueOf(e.getKey()), e.getValue());
        }
        return m;
    }

    private static Optional<String> asString(Object v) {
        if (v == null) return Optional.empty();
        if (v instanceof String s) return Optional.of(s);
        return Optional.of(String.valueOf(v));
    }

    private static Optional<Integer> asInt(Object v) {
        if (v == null) return Optional.empty();
        if (v instanceof Integer i) return Optional.of(i);
        if (v instanceof Number n) return Optional.of(n.intValue());
        try {
            return Optional.of(Integer.parseInt(String.valueOf(v)));
        } catch (Exception ignore) {
            return Optional.empty();
        }
    }

    /**
     * 构建高德静态地图URL
     *
     * @param request 地图请求参数
     * @return 静态地图URL
     */
    private String buildAmapStaticMapUrl(com.teamventure.domain.valueobject.MapRequest request) {
        return "https://restapi.amap.com/v3/staticmap"
                + "?key=" + enc(amapApiKey)
                + "&center=" + enc(String.format("%.6f,%.6f",
                    request.getCenter().getLongitude(),
                    request.getCenter().getLatitude()))
                + "&zoom=" + request.getZoom()
                + "&size=" + request.getSize().toApiParam()
                + "&markers=" + enc(request.getMarkers())
                + "&paths=" + enc(request.getPaths())
                + "&scale=2";  // 高清输出（2倍像素密度）
    }

    private Optional<double[]> resolveLngLat(String keyword, String cityHint) {
        if (this.amapApiKey.isBlank()) return Optional.empty();
        String cacheKey = keyword + "|" + cityHint;
        synchronized (GEO_CACHE) {
            double[] cached = GEO_CACHE.get(cacheKey);
            if (cached != null) return Optional.of(cached);
        }

        try {
            String url = "https://restapi.amap.com/v3/place/text"
                    + "?key=" + enc(amapApiKey)
                    + "&keywords=" + enc(keyword)
                    + "&offset=1&page=1&extensions=base&output=JSON"
                    + (cityHint == null || cityHint.isBlank() ? "" : "&city=" + enc(cityHint));

            HttpRequest req = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .timeout(java.time.Duration.ofSeconds(6))
                    .GET()
                    .build();

            HttpResponse<String> resp = httpClient.send(req, HttpResponse.BodyHandlers.ofString());
            if (resp.statusCode() != 200) return Optional.empty();

            Map<String, Object> body = Jsons.toMap(resp.body());
            Object poisObj = body.get("pois");
            if (!(poisObj instanceof List<?> pois) || pois.isEmpty()) return Optional.empty();
            Object first = pois.get(0);
            if (!(first instanceof Map<?, ?> firstMapRaw)) return Optional.empty();
            Map<String, Object> firstMap = castMap(firstMapRaw);
            String location = asString(firstMap.get("location")).orElse("");
            if (location.isBlank() || !location.contains(",")) return Optional.empty();
            String[] parts = location.split(",", 2);
            double lng = Double.parseDouble(parts[0]);
            double lat = Double.parseDouble(parts[1]);

            double[] lngLat = new double[]{lng, lat};
            synchronized (GEO_CACHE) {
                GEO_CACHE.put(cacheKey, lngLat);
            }
            return Optional.of(lngLat);
        } catch (Exception ignore) {
            return Optional.empty();
        }
    }

    private static String enc(String s) {
        return URLEncoder.encode(s == null ? "" : s, StandardCharsets.UTF_8);
    }

    public Map<String, Object> updateItineraryWithCas(String userId, String planId, int baseVersion, Map<String, Object> itinerary) {
        if (baseVersion < 1) {
            throw new BizException("BAD_REQUEST", "invalid base_version");
        }

        PlanPO plan = planMapper.selectById(planId);
        if (plan == null || plan.getDeletedAt() != null) {
            throw new BizException("NOT_FOUND", "plan not found");
        }
        if (!userId.equals(plan.getUserId())) {
            throw new BizException("UNAUTHORIZED", "not owner");
        }

        // 兼容历史数据：早期记录可能 itinerary_version 为空，导致 CAS 永远冲突
        if (plan.getItineraryVersion() == null) {
            UpdateWrapper<PlanPO> initVersion = new UpdateWrapper<>();
            initVersion.eq("plan_id", planId)
                    .eq("user_id", userId)
                    .isNull("itinerary_version")
                    .set("itinerary_version", 1);
            planMapper.update(null, initVersion);
        }

        UpdateWrapper<PlanPO> uw = new UpdateWrapper<>();
        uw.eq("plan_id", planId)
          .eq("user_id", userId)
          .eq("itinerary_version", baseVersion)
          .set("itinerary", Jsons.toJson(itinerary))
          .set("itinerary_version", baseVersion + 1);

        int rows = planMapper.update(null, uw);
        if (rows == 0) {
            PlanPO latest = planMapper.selectById(planId);
            int latestVersion = latest == null || latest.getItineraryVersion() == null ? 1 : latest.getItineraryVersion();
            return Map.of(
                    "conflict", true,
                    "itinerary_version", latestVersion,
                    "itinerary", latest == null ? Map.of("days", List.of()) : Jsons.toMap(latest.getItinerary())
            );
        }

        return Map.of(
                "conflict", false,
                "itinerary_version", baseVersion + 1,
                "itinerary", itinerary
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

    // ==================== 路线规划相关方法 ====================

    /**
     * 规划两点间的路线（调用高德路线规划API）
     *
     * @param originLngLat 起点经纬度 [lng, lat]
     * @param destLngLat 终点经纬度 [lng, lat]
     * @param mode 交通方式: "walking" | "driving"
     * @return RouteSegment对象，包含polyline、distance、duration
     */
    private Optional<RouteSegment> resolveRouteSegment(
            double[] originLngLat,
            double[] destLngLat,
            String mode
    ) {
        if (this.amapApiKey.isBlank()) return Optional.empty();

        // 1. 检查缓存
        String cacheKey = buildRouteCacheKey(originLngLat, destLngLat, mode);
        synchronized (ROUTE_CACHE) {
            RouteSegment cached = ROUTE_CACHE.get(cacheKey);
            if (cached != null) return Optional.of(cached);
        }

        // 2. 选择API端点
        String apiPath = mode.equals("walking")
                ? "/v3/direction/walking"
                : "/v3/direction/driving";

        try {
            // 3. 构建请求URL
            String origin = originLngLat[0] + "," + originLngLat[1];
            String destination = destLngLat[0] + "," + destLngLat[1];
            String url = "https://restapi.amap.com" + apiPath
                    + "?key=" + enc(amapApiKey)
                    + "&origin=" + enc(origin)
                    + "&destination=" + enc(destination);

            // 4. 发送HTTP请求
            HttpRequest req = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .timeout(java.time.Duration.ofSeconds(6))
                    .GET()
                    .build();

            HttpResponse<String> resp = httpClient.send(req, HttpResponse.BodyHandlers.ofString());
            if (resp.statusCode() != 200) return Optional.empty();

            // 5. 解析响应
            Map<String, Object> body = Jsons.toMap(resp.body());
            String status = asString(body.get("status")).orElse("");
            if (!"1".equals(status)) return Optional.empty();

            Object routeObj = body.get("route");
            if (!(routeObj instanceof Map<?, ?> routeMapRaw)) return Optional.empty();

            Map<String, Object> routeMap = castMap(routeMapRaw);
            Object pathsObj = routeMap.get("paths");
            if (!(pathsObj instanceof List<?> paths) || paths.isEmpty()) {
                return Optional.empty();
            }

            Object firstPath = paths.get(0);
            if (!(firstPath instanceof Map<?, ?> pathMapRaw)) return Optional.empty();
            Map<String, Object> pathMap = castMap(pathMapRaw);

            // 6. 提取polyline（优先使用path级别，否则拼接steps）
            String polylineStr = asString(pathMap.get("polyline")).orElse("");

            if (polylineStr.isBlank()) {
                // 降级：拼接steps中的polyline
                Object stepsObj = pathMap.get("steps");
                if (stepsObj instanceof List<?> steps) {
                    StringBuilder combined = new StringBuilder();
                    for (Object step : steps) {
                        if (step instanceof Map<?, ?> stepMap) {
                            String stepPoly = asString(castMap(stepMap).get("polyline")).orElse("");
                            if (!stepPoly.isBlank()) {
                                if (combined.length() > 0) combined.append(";");
                                combined.append(stepPoly);
                            }
                        }
                    }
                    polylineStr = combined.toString();
                }
            }

            int distance = asInt(pathMap.get("distance")).orElse(0);
            int duration = asInt(pathMap.get("duration")).orElse(0);

            if (polylineStr.isBlank()) return Optional.empty();

            // 7. 解析polyline字符串为坐标点列表
            List<Map<String, Object>> points = parsePolyline(polylineStr);
            if (points.isEmpty()) return Optional.empty();

            // 8. 构建结果并缓存
            RouteSegment segment = new RouteSegment(points, distance, duration, mode);
            synchronized (ROUTE_CACHE) {
                ROUTE_CACHE.put(cacheKey, segment);
            }

            return Optional.of(segment);

        } catch (Exception e) {
            System.err.println("Route planning failed: " + e.getMessage());
            return Optional.empty();
        }
    }

    /**
     * 解析高德polyline字符串为坐标点列表
     *
     * 输入格式: "120.1,30.2;120.11,30.21;120.12,30.22"
     * 输出格式: [{"latitude":30.2,"longitude":120.1}, ...]
     *
     * @param polylineStr 高德返回的polyline字符串（分号分隔，格式为"经度,纬度"）
     * @return 坐标点列表
     */
    private List<Map<String, Object>> parsePolyline(String polylineStr) {
        List<Map<String, Object>> points = new ArrayList<>();

        if (polylineStr == null || polylineStr.isBlank()) {
            return points;
        }

        String[] pairs = polylineStr.split(";");
        for (String pair : pairs) {
            if (pair.isBlank() || !pair.contains(",")) continue;

            String[] parts = pair.split(",", 2);
            try {
                double lng = Double.parseDouble(parts[0].trim());
                double lat = Double.parseDouble(parts[1].trim());

                points.add(Map.of(
                        "latitude", lat,
                        "longitude", lng
                ));
            } catch (NumberFormatException ignore) {
                // 跳过无效坐标点
            }
        }

        return points;
    }

    /**
     * 计算两点间的haversine距离（千米）
     *
     * @param lngLat1 点1 [lng, lat]
     * @param lngLat2 点2 [lng, lat]
     * @return 距离（千米）
     */
    private double calculateDistance(double[] lngLat1, double[] lngLat2) {
        final double EARTH_RADIUS_KM = 6371.0;

        double lat1 = Math.toRadians(lngLat1[1]);
        double lat2 = Math.toRadians(lngLat2[1]);
        double deltaLat = Math.toRadians(lngLat2[1] - lngLat1[1]);
        double deltaLng = Math.toRadians(lngLat2[0] - lngLat1[0]);

        double a = Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2) +
                Math.cos(lat1) * Math.cos(lat2) *
                        Math.sin(deltaLng / 2) * Math.sin(deltaLng / 2);

        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

        return EARTH_RADIUS_KM * c;
    }

    /**
     * 根据两点距离选择交通方式
     *
     * @param distanceKm 两点间直线距离（千米）
     * @return "walking" | "driving"
     */
    private String selectTransportMode(double distanceKm) {
        final double WALKING_THRESHOLD_KM = 3.0;
        return distanceKm < WALKING_THRESHOLD_KM ? "walking" : "driving";
    }

    /**
     * 构建路线缓存键
     *
     * @param origin 起点 [lng, lat]
     * @param dest 终点 [lng, lat]
     * @param mode 交通方式
     * @return 缓存键（保留4位小数，精度约11米）
     */
    private String buildRouteCacheKey(double[] origin, double[] dest, String mode) {
        return String.format("%.4f,%.4f|%.4f,%.4f|%s",
                origin[0], origin[1],
                dest[0], dest[1],
                mode
        );
    }

    // ==================== 内部类 ====================

    /**
     * 路线段数据结构
     */
    private static class RouteSegment {
        public final List<Map<String, Object>> points;  // 路径点列表
        public final int distanceMeters;                // 距离（米）
        public final int durationSeconds;               // 时长（秒）
        public final String mode;                       // walking|driving

        public RouteSegment(
                List<Map<String, Object>> points,
                int distanceMeters,
                int durationSeconds,
                String mode
        ) {
            this.points = points;
            this.distanceMeters = distanceMeters;
            this.durationSeconds = durationSeconds;
            this.mode = mode;
        }
    }
}
