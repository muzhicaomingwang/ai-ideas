package com.teamventure.app.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.teamventure.infrastructure.persistence.po.PlanItineraryRevisionPO;
import com.teamventure.infrastructure.persistence.po.PlanItinerarySuggestionPO;
import com.teamventure.infrastructure.persistence.po.PlanMembershipPO;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import com.teamventure.app.support.BizException;
import com.teamventure.infrastructure.persistence.mapper.PlanItineraryRevisionMapper;
import com.teamventure.infrastructure.persistence.mapper.PlanItinerarySuggestionMapper;
import com.teamventure.infrastructure.persistence.mapper.PlanMembershipMapper;

@Service
public class PlanCollaborationQueryService {
    private final PlanMembershipMapper membershipMapper;
    private final PlanItineraryRevisionMapper revisionMapper;
    private final PlanItinerarySuggestionMapper suggestionMapper;
    private final PlanAuthorizationService authz;

    public PlanCollaborationQueryService(
            PlanMembershipMapper membershipMapper,
            PlanItineraryRevisionMapper revisionMapper,
            PlanItinerarySuggestionMapper suggestionMapper,
            PlanAuthorizationService authz
    ) {
        this.membershipMapper = membershipMapper;
        this.revisionMapper = revisionMapper;
        this.suggestionMapper = suggestionMapper;
        this.authz = authz;
    }

    @Transactional(readOnly = true)
    public List<PlanMembershipPO> listPendingApplications(String ownerId, String planId) {
        authz.requireOwner(planId, ownerId);
        return membershipMapper.selectList(new QueryWrapper<PlanMembershipPO>()
                .eq("plan_id", planId)
                .eq("role", "PARTICIPANT")
                .eq("status", "PENDING")
                .orderByDesc("create_time"));
    }

    @Transactional(readOnly = true)
    public List<PlanMembershipPO> listMembers(String userId, String planId) {
        authz.requireOwnerOrParticipantActive(planId, userId);
        return membershipMapper.selectList(new QueryWrapper<PlanMembershipPO>()
                .eq("plan_id", planId)
                .eq("status", "ACTIVE")
                .in("role", List.of("OWNER", "PARTICIPANT"))
                .orderByAsc("role")
                .orderByAsc("create_time"));
    }

    @Transactional(readOnly = true)
    public List<PlanItineraryRevisionPO> listItineraryVersions(String userId, String planId) {
        authz.requireOwnerOrParticipantActive(planId, userId);
        return revisionMapper.selectList(new QueryWrapper<PlanItineraryRevisionPO>()
                .eq("plan_id", planId)
                .orderByDesc("version"));
    }

    @Transactional(readOnly = true)
    public Map<String, Object> getItineraryVersionDetail(String userId, String planId, int version) {
        authz.requireOwnerOrParticipantActive(planId, userId);
        PlanItineraryRevisionPO r = revisionMapper.selectOne(new QueryWrapper<PlanItineraryRevisionPO>()
                .eq("plan_id", planId)
                .eq("version", version)
                .last("LIMIT 1"));
        if (r == null) throw new BizException("NOT_FOUND", "version not found");
        return Map.of(
                "plan_id", planId,
                "version", version,
                "itinerary", Jsons.toMap(r.getItinerary()),
                "created_by", r.getCreatedBy(),
                "create_time", r.getCreateTime()
        );
    }

    @Transactional(readOnly = true)
    public List<PlanItinerarySuggestionPO> listSuggestions(String userId, String planId, Integer targetVersion) {
        authz.requireOwnerOrParticipantActive(planId, userId);
        QueryWrapper<PlanItinerarySuggestionPO> qw = new QueryWrapper<PlanItinerarySuggestionPO>()
                .eq("plan_id", planId)
                .orderByDesc("create_time");
        if (targetVersion != null) qw.eq("target_version", targetVersion);
        return suggestionMapper.selectList(qw);
    }
}
