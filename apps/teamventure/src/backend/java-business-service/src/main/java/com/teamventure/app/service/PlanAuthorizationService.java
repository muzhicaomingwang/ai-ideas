package com.teamventure.app.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.teamventure.app.support.BizException;
import com.teamventure.infrastructure.persistence.mapper.PlanMembershipMapper;
import com.teamventure.infrastructure.persistence.po.PlanMembershipPO;
import java.util.Set;
import org.springframework.stereotype.Service;

@Service
public class PlanAuthorizationService {
    private static final Set<String> VISIBLE_STATUSES = Set.of("ACTIVE", "PENDING");

    private final PlanMembershipMapper membershipMapper;

    public PlanAuthorizationService(PlanMembershipMapper membershipMapper) {
        this.membershipMapper = membershipMapper;
    }

    public PlanMembershipPO getMembership(String planId, String userId) {
        return membershipMapper.selectOne(new QueryWrapper<PlanMembershipPO>()
                .eq("plan_id", planId)
                .eq("user_id", userId)
                .last("LIMIT 1"));
    }

    public void requireMemberForCurrent(String planId, String userId) {
        PlanMembershipPO m = getMembership(planId, userId);
        if (m == null || m.getStatus() == null || !VISIBLE_STATUSES.contains(m.getStatus().toUpperCase())) {
            throw new BizException("UNAUTHORIZED", "not member");
        }
    }

    public void requireOwner(String planId, String userId) {
        PlanMembershipPO m = getMembership(planId, userId);
        if (m == null) throw new BizException("UNAUTHORIZED", "not owner");
        if (!"OWNER".equalsIgnoreCase(m.getRole()) || !"ACTIVE".equalsIgnoreCase(m.getStatus())) {
            throw new BizException("UNAUTHORIZED", "not owner");
        }
    }

    public void requireParticipantActive(String planId, String userId) {
        PlanMembershipPO m = getMembership(planId, userId);
        if (m == null) throw new BizException("UNAUTHORIZED", "not participant");
        if (!"PARTICIPANT".equalsIgnoreCase(m.getRole()) || !"ACTIVE".equalsIgnoreCase(m.getStatus())) {
            throw new BizException("UNAUTHORIZED", "not participant");
        }
    }

    public void requireOwnerOrParticipantActive(String planId, String userId) {
        PlanMembershipPO m = getMembership(planId, userId);
        if (m == null) throw new BizException("UNAUTHORIZED", "not member");
        boolean ok = ("OWNER".equalsIgnoreCase(m.getRole()) && "ACTIVE".equalsIgnoreCase(m.getStatus()))
                || ("PARTICIPANT".equalsIgnoreCase(m.getRole()) && "ACTIVE".equalsIgnoreCase(m.getStatus()));
        if (!ok) throw new BizException("UNAUTHORIZED", "not allowed");
    }
}

