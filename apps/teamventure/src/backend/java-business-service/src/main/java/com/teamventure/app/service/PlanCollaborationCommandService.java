package com.teamventure.app.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.teamventure.app.support.BizException;
import com.teamventure.app.support.IdGenerator;
import com.teamventure.infrastructure.persistence.mapper.PlanItineraryRevisionMapper;
import com.teamventure.infrastructure.persistence.mapper.PlanItinerarySuggestionMapper;
import com.teamventure.infrastructure.persistence.mapper.PlanMembershipMapper;
import com.teamventure.infrastructure.persistence.mapper.PlanMapper;
import com.teamventure.infrastructure.persistence.po.PlanItineraryRevisionPO;
import com.teamventure.infrastructure.persistence.po.PlanItinerarySuggestionPO;
import com.teamventure.infrastructure.persistence.po.PlanMembershipPO;
import com.teamventure.infrastructure.persistence.po.PlanPO;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
public class PlanCollaborationCommandService {
    private final PlanMapper planMapper;
    private final PlanMembershipMapper membershipMapper;
    private final PlanItineraryRevisionMapper revisionMapper;
    private final PlanItinerarySuggestionMapper suggestionMapper;
    private final PlanAuthorizationService authz;

    public PlanCollaborationCommandService(
            PlanMapper planMapper,
            PlanMembershipMapper membershipMapper,
            PlanItineraryRevisionMapper revisionMapper,
            PlanItinerarySuggestionMapper suggestionMapper,
            PlanAuthorizationService authz
    ) {
        this.planMapper = planMapper;
        this.membershipMapper = membershipMapper;
        this.revisionMapper = revisionMapper;
        this.suggestionMapper = suggestionMapper;
        this.authz = authz;
    }

    public void ensureOwnerMembershipAndCurrentRevision(PlanPO plan) {
        if (plan == null) return;
        if (plan.getPlanId() == null || plan.getUserId() == null) return;

        PlanMembershipPO existing = membershipMapper.selectOne(new QueryWrapper<PlanMembershipPO>()
                .eq("plan_id", plan.getPlanId())
                .eq("user_id", plan.getUserId())
                .last("LIMIT 1"));
        if (existing == null) {
            PlanMembershipPO m = new PlanMembershipPO();
            m.setMembershipId(IdGenerator.newId("pm"));
            m.setPlanId(plan.getPlanId());
            m.setUserId(plan.getUserId());
            m.setRole("OWNER");
            m.setStatus("ACTIVE");
            membershipMapper.insert(m);
        }

        Integer v = plan.getItineraryVersion() == null ? 1 : plan.getItineraryVersion();
        long cnt = revisionMapper.selectCount(new QueryWrapper<PlanItineraryRevisionPO>()
                .eq("plan_id", plan.getPlanId())
                .eq("version", v));
        if (cnt == 0) {
            PlanItineraryRevisionPO r = new PlanItineraryRevisionPO();
            r.setRevisionId(IdGenerator.newId("rev"));
            r.setPlanId(plan.getPlanId());
            r.setVersion(v);
            r.setItinerary(plan.getItinerary());
            r.setCreatedBy(plan.getUserId());
            r.setCreateTime(Instant.now());
            revisionMapper.insert(r);
        }
    }

    public void bookmark(String userId, String planId) {
        PlanPO plan = planMapper.selectById(planId);
        if (plan == null || plan.getDeletedAt() != null) throw new BizException("NOT_FOUND", "plan not found");

        PlanMembershipPO m = authz.getMembership(planId, userId);
        if (m != null) return; // idempotent (if already OWNER/PARTICIPANT/WATCHER/PENDING)

        PlanMembershipPO nw = new PlanMembershipPO();
        nw.setMembershipId(IdGenerator.newId("pm"));
        nw.setPlanId(planId);
        nw.setUserId(userId);
        nw.setRole("WATCHER");
        nw.setStatus("ACTIVE");
        membershipMapper.insert(nw);
    }

    public void unbookmark(String userId, String planId) {
        PlanMembershipPO m = authz.getMembership(planId, userId);
        if (m == null) return; // idempotent
        if ("OWNER".equalsIgnoreCase(m.getRole()) || "PARTICIPANT".equalsIgnoreCase(m.getRole())) {
            throw new BizException("INVALID_STATE", "cannot unbookmark while owner/participant");
        }
        membershipMapper.delete(new QueryWrapper<PlanMembershipPO>()
                .eq("plan_id", planId)
                .eq("user_id", userId));
    }

    public void applyToParticipate(String userId, String planId, String applyReason) {
        PlanPO plan = planMapper.selectById(planId);
        if (plan == null || plan.getDeletedAt() != null) throw new BizException("NOT_FOUND", "plan not found");

        PlanMembershipPO m = authz.getMembership(planId, userId);
        if (m == null) throw new BizException("INVALID_STATE", "must bookmark before apply");
        if (!"WATCHER".equalsIgnoreCase(m.getRole()) || !"ACTIVE".equalsIgnoreCase(m.getStatus())) {
            throw new BizException("INVALID_STATE", "must bookmark before apply");
        }

        UpdateWrapper<PlanMembershipPO> uw = new UpdateWrapper<>();
        uw.eq("plan_id", planId)
                .eq("user_id", userId)
                .set("role", "PARTICIPANT")
                .set("status", "PENDING")
                .set("apply_reason", applyReason);
        membershipMapper.update(null, uw);
    }

    public void cancelApplication(String userId, String planId) {
        PlanMembershipPO m = authz.getMembership(planId, userId);
        if (m == null) throw new BizException("NOT_FOUND", "application not found");
        if (!"PARTICIPANT".equalsIgnoreCase(m.getRole()) || !"PENDING".equalsIgnoreCase(m.getStatus())) {
            throw new BizException("INVALID_STATE", "not pending");
        }

        UpdateWrapper<PlanMembershipPO> uw = new UpdateWrapper<>();
        uw.eq("plan_id", planId)
                .eq("user_id", userId)
                .set("role", "WATCHER")
                .set("status", "ACTIVE");
        membershipMapper.update(null, uw);
    }

    public void approveApplication(String ownerId, String planId, String userId) {
        authz.requireOwner(planId, ownerId);
        PlanMembershipPO m = authz.getMembership(planId, userId);
        if (m == null) throw new BizException("NOT_FOUND", "application not found");
        if (!"PARTICIPANT".equalsIgnoreCase(m.getRole()) || !"PENDING".equalsIgnoreCase(m.getStatus())) {
            throw new BizException("INVALID_STATE", "not pending");
        }

        UpdateWrapper<PlanMembershipPO> uw = new UpdateWrapper<>();
        uw.eq("plan_id", planId)
                .eq("user_id", userId)
                .set("status", "ACTIVE")
                .set("last_decision", "APPROVED")
                .set("decided_by", ownerId)
                .set("decided_at", Instant.now());
        membershipMapper.update(null, uw);
    }

    public void rejectApplication(String ownerId, String planId, String userId) {
        authz.requireOwner(planId, ownerId);
        PlanMembershipPO m = authz.getMembership(planId, userId);
        if (m == null) throw new BizException("NOT_FOUND", "application not found");
        if (!"PARTICIPANT".equalsIgnoreCase(m.getRole()) || !"PENDING".equalsIgnoreCase(m.getStatus())) {
            throw new BizException("INVALID_STATE", "not pending");
        }

        UpdateWrapper<PlanMembershipPO> uw = new UpdateWrapper<>();
        uw.eq("plan_id", planId)
                .eq("user_id", userId)
                .set("role", "WATCHER")
                .set("status", "ACTIVE")
                .set("last_decision", "REJECTED")
                .set("decided_by", ownerId)
                .set("decided_at", Instant.now());
        membershipMapper.update(null, uw);
    }

    public void removeParticipant(String ownerId, String planId, String userId) {
        authz.requireOwner(planId, ownerId);
        PlanMembershipPO m = authz.getMembership(planId, userId);
        if (m == null) throw new BizException("NOT_FOUND", "membership not found");
        if (!"PARTICIPANT".equalsIgnoreCase(m.getRole()) || !"ACTIVE".equalsIgnoreCase(m.getStatus())) {
            throw new BizException("INVALID_STATE", "not active participant");
        }

        UpdateWrapper<PlanMembershipPO> uw = new UpdateWrapper<>();
        uw.eq("plan_id", planId)
                .eq("user_id", userId)
                .set("role", "WATCHER")
                .set("status", "ACTIVE")
                .set("removed_by", ownerId)
                .set("removed_at", Instant.now());
        membershipMapper.update(null, uw);
    }

    public Map<String, Object> createSuggestion(String userId, String planId, int targetVersion, String content) {
        authz.requireParticipantActive(planId, userId);
        long cnt = revisionMapper.selectCount(new QueryWrapper<PlanItineraryRevisionPO>()
                .eq("plan_id", planId)
                .eq("version", targetVersion));
        if (cnt == 0) throw new BizException("NOT_FOUND", "target version not found");

        PlanItinerarySuggestionPO po = new PlanItinerarySuggestionPO();
        po.setSuggestionId(IdGenerator.newId("sug"));
        po.setPlanId(planId);
        po.setTargetVersion(targetVersion);
        po.setUserId(userId);
        po.setContent(content == null ? "" : content);
        po.setStatus("OPEN");
        suggestionMapper.insert(po);
        return Map.of("suggestion_id", po.getSuggestionId());
    }

    public void updateOwnSuggestion(String userId, String suggestionId, String content) {
        PlanItinerarySuggestionPO po = suggestionMapper.selectById(suggestionId);
        if (po == null) throw new BizException("NOT_FOUND", "suggestion not found");
        if (!userId.equals(po.getUserId())) throw new BizException("UNAUTHORIZED", "not owner");
        authz.requireOwnerOrParticipantActive(po.getPlanId(), userId);

        UpdateWrapper<PlanItinerarySuggestionPO> uw = new UpdateWrapper<>();
        uw.eq("suggestion_id", suggestionId)
                .set("content", content == null ? "" : content);
        suggestionMapper.update(null, uw);
    }

    public void deleteOwnSuggestion(String userId, String suggestionId) {
        PlanItinerarySuggestionPO po = suggestionMapper.selectById(suggestionId);
        if (po == null) return;
        if (!userId.equals(po.getUserId())) throw new BizException("UNAUTHORIZED", "not owner");
        authz.requireOwnerOrParticipantActive(po.getPlanId(), userId);
        suggestionMapper.deleteById(suggestionId);
    }
}
