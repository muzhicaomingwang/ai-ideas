package com.teamventure.app.service;

import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.teamventure.adapter.web.plans.PlanController.GenerateRequest;
import com.teamventure.adapter.web.plans.PlanController.GenerateResponse;
import com.teamventure.adapter.web.plans.PlanController.SupplierContactRequest;
import com.teamventure.app.service.dto.BatchPlanCallbackRequest;
import com.teamventure.app.support.BizException;
import com.teamventure.app.support.IdGenerator;
import com.teamventure.app.support.ItineraryMarkdownParser;
import com.teamventure.app.support.ItineraryMarkdownSanitizer;
import com.teamventure.app.support.ItineraryMarkdownValidator;
import com.teamventure.infrastructure.persistence.mapper.DomainEventMapper;
import com.teamventure.infrastructure.persistence.mapper.PlanMapper;
import com.teamventure.infrastructure.persistence.mapper.PlanRequestMapper;
import com.teamventure.infrastructure.persistence.mapper.SupplierContactLogMapper;
import com.teamventure.infrastructure.persistence.po.DomainEventPO;
import com.teamventure.infrastructure.persistence.po.PlanPO;
import com.teamventure.infrastructure.persistence.po.PlanRequestPO;
import com.teamventure.infrastructure.persistence.po.SupplierContactLogPO;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Value;

@Service
public class PlanCommandService {
    private final PlanRequestMapper planRequestMapper;
    private final PlanMapper planMapper;
    private final SupplierContactLogMapper contactLogMapper;
    private final DomainEventMapper eventMapper;
    private final RabbitTemplate rabbitTemplate;
    private final String exchange;
    private final String routingKey;
    private final HttpClient httpClient;
    private final InternalPlanCallbackService callbackService;
    private final String aiServiceUrl;
    private final OssService ossService;
    private final PlanAuthorizationService planAuthorizationService;
    private final PlanCollaborationCommandService planCollaborationCommandService;

    public PlanCommandService(
            PlanRequestMapper planRequestMapper,
            PlanMapper planMapper,
            SupplierContactLogMapper contactLogMapper,
            DomainEventMapper eventMapper,
            RabbitTemplate rabbitTemplate,
            @Value("${teamventure.mq.exchange.plan-generation}") String exchange,
            @Value("${teamventure.mq.routing-key.plan-request}") String routingKey,
            InternalPlanCallbackService callbackService,
            OssService ossService,
            @Value("${teamventure.ai-service.url:}") String aiServiceUrl,
            PlanAuthorizationService planAuthorizationService,
            PlanCollaborationCommandService planCollaborationCommandService
    ) {
        this.planRequestMapper = planRequestMapper;
        this.planMapper = planMapper;
        this.contactLogMapper = contactLogMapper;
        this.eventMapper = eventMapper;
        this.rabbitTemplate = rabbitTemplate;
        this.exchange = exchange;
        this.routingKey = routingKey;
        this.callbackService = callbackService;
        this.ossService = ossService;
        this.aiServiceUrl = aiServiceUrl == null ? "" : aiServiceUrl.trim();
        this.planAuthorizationService = planAuthorizationService;
        this.planCollaborationCommandService = planCollaborationCommandService;
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(java.time.Duration.ofSeconds(3))
                .build();
    }

    public GenerateResponse createPlanRequestAndPublish(String userId, GenerateRequest req) {
        String markdown = req.markdown_content == null ? "" : req.markdown_content.trim();
        if (markdown.contains("## Day")) {
            String sanitized = ItineraryMarkdownSanitizer.sanitizeDraftItineraryMarkdown(markdown).trim();
            var res = ItineraryMarkdownValidator.validate(sanitized);
            if (!res.valid) {
                throw new BizException("VALIDATION_ERROR",
                        "Markdown 格式不合规：\n" + String.join("\n", res.errors.stream().limit(10).toList()));
            }
            markdown = sanitized;
        }

        String planRequestId = IdGenerator.newId("plan_req");
        PlanRequestPO po = new PlanRequestPO();
        po.setPlanRequestId(planRequestId);
        po.setUserId(userId);
        po.setMarkdownContent(markdown); // 保存Markdown内容（对行程类内容做清洗+校验）
        po.setStatus("GENERATING");
        po.setGenerationStartedAt(Instant.now());
        planRequestMapper.insert(po);

        recordEvent("PlanRequestCreated", "PlanRequest", planRequestId, userId, Map.of("plan_request_id", planRequestId));
        recordEvent("PlanGenerationRequested", "PlanRequest", planRequestId, userId, Map.of("plan_request_id", planRequestId));

        // 同步调用 Python AI 服务生成方案，生成完成后再返回（前端可在本页等待完成后跳转）
        if (aiServiceUrl.isBlank()) {
            markPlanRequestFailed(planRequestId, "AI_SERVICE_NOT_CONFIGURED", "AI 服务未配置（teamventure.ai-service.url）");
            throw new BizException("AI_SERVICE_NOT_CONFIGURED", "AI service is not configured");
        }

        String endpoint = aiServiceUrl.endsWith("/")
                ? (aiServiceUrl.substring(0, aiServiceUrl.length() - 1) + "/api/v1/plans/generate")
                : (aiServiceUrl + "/api/v1/plans/generate");

        Map<String, Object> payload = new HashMap<>();
        payload.put("plan_request_id", planRequestId);
        payload.put("user_id", userId);
        payload.put("markdown_content", markdown);
        if (req.plan_name != null && !req.plan_name.isBlank()) {
            payload.put("plan_name", req.plan_name.trim());
        }
        payload.put("trace_id", IdGenerator.newId("trace"));

        try {
            byte[] body = Jsons.toJson(payload).getBytes(StandardCharsets.UTF_8);
            HttpRequest httpReq = HttpRequest.newBuilder(URI.create(endpoint))
                    .timeout(Duration.ofSeconds(180))
                    .header("Content-Type", "application/json")
                    .header("Accept", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofByteArray(body))
                    .build();

            HttpResponse<byte[]> httpRes = httpClient.send(httpReq, HttpResponse.BodyHandlers.ofByteArray());
            if (httpRes.statusCode() < 200 || httpRes.statusCode() >= 300) {
                String details = new String(httpRes.body() == null ? new byte[0] : httpRes.body(), StandardCharsets.UTF_8);
                if (details.length() > 500) details = details.substring(0, 500) + "...";
                markPlanRequestFailed(planRequestId, "AI_HTTP_ERROR", "AI 服务请求失败：" + httpRes.statusCode());
                throw new BizException("GENERATION_FAILED", "AI service failed: " + details);
            }

            String text = new String(httpRes.body() == null ? new byte[0] : httpRes.body(), StandardCharsets.UTF_8);
            Map<String, Object> res = Jsons.toMap(text);
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> plans = (List<Map<String, Object>>) res.get("plans");
            if (plans == null) plans = List.of();

            BatchPlanCallbackRequest cb = new BatchPlanCallbackRequest();
            cb.plan_request_id = planRequestId;
            cb.user_id = userId;
            cb.plans = plans;
            cb.trace_id = (String) res.getOrDefault("trace_id", payload.get("trace_id"));
            callbackService.handleGeneratedPlans(cb);

            return new GenerateResponse(planRequestId, "completed");
        } catch (BizException e) {
            throw e;
        } catch (Exception e) {
            markPlanRequestFailed(planRequestId, "GENERATION_FAILED", "方案生成失败");
            throw new BizException("GENERATION_FAILED", "方案生成失败，请稍后重试");
        }
    }

    public Map<String, Object> saveDraftPlanFromMarkdown(String userId, String markdownContent, String planName, String logoStorage, String legacyLogoUrl) {
        String markdown = markdownContent == null ? "" : markdownContent;
        String name = planName == null ? "" : planName.trim();
        if (name.isBlank()) throw new BizException("VALIDATION_ERROR", "plan_name is empty");
        if (markdown.trim().isEmpty()) throw new BizException("VALIDATION_ERROR", "markdown_content is empty");

        // Align with miniapp "line-based validation" behavior:
        // keep only Day headings and time rows, then validate with the shared v2 validator.
        String sanitized = ItineraryMarkdownSanitizer.sanitizeDraftItineraryMarkdown(markdown);
        String filtered = ItineraryMarkdownSanitizer.filterDayAndTimeLines(sanitized);

        var check = ItineraryMarkdownValidator.validate(filtered);
        if (!check.valid) {
            throw new BizException("VALIDATION_ERROR",
                    "Markdown 格式不合规：\n" + String.join("\n", check.errors.stream().limit(10).toList()));
        }

        Map<String, Object> itinerary = ItineraryMarkdownParser.parseToItinerary(filtered);
        int durationDays = 0;
        Object daysObj = itinerary.get("days");
        if (daysObj instanceof List<?> list) durationDays = list.size();

        PlanPO plan = new PlanPO();
        plan.setPlanId(IdGenerator.newId("plan"));
        plan.setPlanRequestId(IdGenerator.newId("plan_req"));
        plan.setUserId(userId);
        plan.setPlanType("standard");
        plan.setPlanName(name);
        plan.setSummary("");
        plan.setHighlights(Jsons.toJson(List.of()));
        String normalizedStorage = normalizeLogoStorageValue(logoStorage);
        String normalizedLegacy = normalizeLegacyLogoUrl(legacyLogoUrl);
        // 兼容：如果历史字段传了 minio://...，且符合 itinerary bucket，则也写入 logo_storage
        if ((normalizedStorage == null || normalizedStorage.isBlank()) && normalizedLegacy != null && normalizedLegacy.startsWith("minio://")) {
            String resolved = ossService.resolveItineraryUrl(normalizedLegacy);
            if (resolved != null && !resolved.isBlank()) {
                normalizedStorage = normalizedLegacy;
                normalizedLegacy = null;
            }
        }
        plan.setLogoStorage((normalizedStorage == null || normalizedStorage.isBlank()) ? null : normalizedStorage);
        plan.setLogoUrl((normalizedLegacy == null || normalizedLegacy.isBlank()) ? null : normalizedLegacy);
        plan.setItinerary(Jsons.toJson(itinerary));
        plan.setItineraryVersion(1);
        plan.setBudgetBreakdown(Jsons.toJson(Map.of()));
        plan.setSupplierSnapshots(Jsons.toJson(List.of()));
        plan.setBudgetTotal(java.math.BigDecimal.ZERO);
        plan.setBudgetPerPerson(java.math.BigDecimal.ZERO);
        plan.setDurationDays(durationDays <= 0 ? 1 : durationDays);
        plan.setDepartureCity("");
        plan.setDestination("");
        plan.setDestinationCity("");
        plan.setStatus("draft");
        planMapper.insert(plan);
        planCollaborationCommandService.ensureOwnerMembershipAndCurrentRevision(plan);

        recordEvent("PlanSaved", "Plan", plan.getPlanId(), userId, Map.of("plan_id", plan.getPlanId()));

        return Map.of(
                "plan_id", plan.getPlanId(),
                "status", "draft"
        );
    }

    public void confirmPlan(String userId, String planId) {
        PlanPO plan = planMapper.selectById(planId);
        if (plan == null) {
            throw new BizException("NOT_FOUND", "plan not found");
        }
        planAuthorizationService.requireOwner(planId, userId);
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

    public void archivePlan(String userId, String planId) {
        PlanPO plan = planMapper.selectById(planId);
        if (plan == null) {
            throw new BizException("NOT_FOUND", "plan not found");
        }
        planAuthorizationService.requireOwner(planId, userId);
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

    public void submitReview(String userId, String planId, com.teamventure.adapter.web.plans.PlanController.SubmitReviewRequest req) {
        PlanPO plan = planMapper.selectById(planId);
        if (plan == null) {
            throw new BizException("NOT_FOUND", "plan not found");
        }
        planAuthorizationService.requireOwner(planId, userId);
        if (plan.getDeletedAt() != null) {
            throw new BizException("NOT_FOUND", "plan not found");
        }
        if (!"draft".equalsIgnoreCase(plan.getStatus())) {
            throw new BizException("INVALID_STATUS", "只有制定完成状态的方案才能提交通晒");
        }

        String startDate = req == null ? null : req.start_date;
        if (startDate == null || startDate.isBlank()) {
            throw new BizException("VALIDATION_ERROR", "start_date is required");
        }

        // Persist confirmed dates onto plan_request (plans table doesn't store dates)
        String planRequestId = plan.getPlanRequestId();
        if (planRequestId != null && !planRequestId.isBlank()) {
            int durationDays = plan.getDurationDays() == null || plan.getDurationDays() <= 0 ? 1 : plan.getDurationDays();
            String endDate = addDays(startDate.trim(), durationDays - 1);
            UpdateWrapper<PlanRequestPO> uw = new UpdateWrapper<PlanRequestPO>()
                    .eq("plan_request_id", planRequestId)
                    .set("start_date", startDate.trim())
                    .set("end_date", endDate);
            planRequestMapper.update(null, uw);
        }

        plan.setStatus("reviewing");
        plan.setReviewStartedAt(Instant.now());
        planMapper.updateById(plan);
        recordEvent("PlanSubmittedForReview", "Plan", planId, userId, Map.of("plan_id", planId));
    }

    public void revertReview(String userId, String planId) {
        PlanPO plan = planMapper.selectById(planId);
        if (plan == null) {
            throw new BizException("NOT_FOUND", "plan not found");
        }
        planAuthorizationService.requireOwner(planId, userId);
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

    public void deletePlan(String userId, String planId) {
        // 1. 先查 plans 表
        PlanPO plan = planMapper.selectById(planId);
        if (plan != null) {
            planAuthorizationService.requireOwner(planId, userId);
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

    public Map<String, Object> updateItineraryWithCas(String userId, String planId, int baseVersion, Map<String, Object> itinerary) {
        if (baseVersion < 1) {
            throw new BizException("BAD_REQUEST", "invalid base_version");
        }

        PlanPO plan = planMapper.selectById(planId);
        if (plan == null || plan.getDeletedAt() != null) {
            throw new BizException("NOT_FOUND", "plan not found");
        }
        planAuthorizationService.requireOwner(planId, userId);
        if (!"reviewing".equalsIgnoreCase(plan.getStatus())) {
            throw new BizException("INVALID_STATUS", "only reviewing can update itinerary");
        }

        // 兼容历史数据：早期记录可能 itinerary_version 为空，导致 CAS 永远冲突
        if (plan.getItineraryVersion() == null) {
            UpdateWrapper<PlanPO> initVersion = new UpdateWrapper<>();
            initVersion.eq("plan_id", planId)
                    .isNull("itinerary_version")
                    .set("itinerary_version", 1);
            planMapper.update(null, initVersion);
        }

        UpdateWrapper<PlanPO> uw = new UpdateWrapper<>();
        uw.eq("plan_id", planId)
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

        PlanPO latest = planMapper.selectById(planId);
        if (latest != null) {
            planCollaborationCommandService.ensureOwnerMembershipAndCurrentRevision(latest);
        }

        return Map.of(
                "conflict", false,
                "itinerary_version", baseVersion + 1,
                "itinerary", itinerary
        );
    }

    private void markPlanRequestFailed(String planRequestId, String code, String message) {
        PlanRequestPO po = planRequestMapper.selectById(planRequestId);
        if (po == null) return;
        po.setStatus("FAILED");
        po.setErrorCode(code);
        po.setErrorMessage(message);
        po.setGenerationCompletedAt(Instant.now());
        planRequestMapper.updateById(po);
        recordEvent("PlanGenerationFailed", "PlanRequest", planRequestId, po.getUserId(), Map.of(
                "plan_request_id", planRequestId,
                "error_code", code,
                "error_message", message
        ));
    }

    private static String addDays(String startDate, int plusDays) {
        try {
            java.time.LocalDate d = java.time.LocalDate.parse(startDate);
            return d.plusDays(Math.max(0, plusDays)).toString();
        } catch (Exception e) {
            return startDate;
        }
    }

    private String normalizeLogoStorageValue(String logoStorage) {
        String v = logoStorage == null ? "" : logoStorage.trim();
        if (v.isBlank()) return null;
        if (!v.startsWith("minio://")) {
            throw new BizException("VALIDATION_ERROR", "logo_storage must be minio://bucket/key");
        }
        if (v.length() > 512) {
            throw new BizException("VALIDATION_ERROR", "logo_storage too long");
        }
        String resolved = ossService.resolveItineraryUrl(v);
        if (resolved == null || resolved.isBlank()) {
            throw new BizException("VALIDATION_ERROR", "invalid logo_storage");
        }
        return v;
    }

    private String normalizeLegacyLogoUrl(String legacyLogoUrl) {
        String legacy = legacyLogoUrl == null ? "" : legacyLogoUrl.trim();
        if (legacy.isBlank()) return null;
        if (legacy.length() > 512) {
            throw new BizException("VALIDATION_ERROR", "logo_url too long");
        }
        if (!(legacy.startsWith("http://") || legacy.startsWith("https://") || legacy.startsWith("minio://"))) {
            throw new BizException("VALIDATION_ERROR", "invalid logo_url");
        }
        return legacy;
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
