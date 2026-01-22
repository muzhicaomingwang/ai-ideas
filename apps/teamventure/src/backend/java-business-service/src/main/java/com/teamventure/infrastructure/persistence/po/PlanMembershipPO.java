package com.teamventure.infrastructure.persistence.po;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.Instant;

@TableName("plan_memberships")
public class PlanMembershipPO {
    @TableId
    private String membership_id;
    private String plan_id;
    private String user_id;
    private String role;
    private String status;

    private String apply_reason;
    private String last_decision;
    private String decided_by;
    private Instant decided_at;

    private String removed_by;
    private Instant removed_at;

    private Instant create_time;
    private Instant update_time;

    public String getMembershipId() { return membership_id; }
    public void setMembershipId(String v) { this.membership_id = v; }
    public String getPlanId() { return plan_id; }
    public void setPlanId(String v) { this.plan_id = v; }
    public String getUserId() { return user_id; }
    public void setUserId(String v) { this.user_id = v; }
    public String getRole() { return role; }
    public void setRole(String v) { this.role = v; }
    public String getStatus() { return status; }
    public void setStatus(String v) { this.status = v; }
    public String getApplyReason() { return apply_reason; }
    public void setApplyReason(String v) { this.apply_reason = v; }
    public String getLastDecision() { return last_decision; }
    public void setLastDecision(String v) { this.last_decision = v; }
    public String getDecidedBy() { return decided_by; }
    public void setDecidedBy(String v) { this.decided_by = v; }
    public Instant getDecidedAt() { return decided_at; }
    public void setDecidedAt(Instant v) { this.decided_at = v; }
    public String getRemovedBy() { return removed_by; }
    public void setRemovedBy(String v) { this.removed_by = v; }
    public Instant getRemovedAt() { return removed_at; }
    public void setRemovedAt(Instant v) { this.removed_at = v; }
    public Instant getCreateTime() { return create_time; }
    public void setCreateTime(Instant v) { this.create_time = v; }
    public Instant getUpdateTime() { return update_time; }
    public void setUpdateTime(Instant v) { this.update_time = v; }
}

