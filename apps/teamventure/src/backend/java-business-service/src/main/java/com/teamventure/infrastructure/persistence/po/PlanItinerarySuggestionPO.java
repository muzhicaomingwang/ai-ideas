package com.teamventure.infrastructure.persistence.po;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.Instant;

@TableName("plan_itinerary_suggestions")
public class PlanItinerarySuggestionPO {
    @TableId
    private String suggestion_id;
    private String plan_id;
    private Integer target_version;
    private String user_id;
    private String content;
    private String status;
    private Instant create_time;
    private Instant update_time;

    public String getSuggestionId() { return suggestion_id; }
    public void setSuggestionId(String v) { this.suggestion_id = v; }
    public String getPlanId() { return plan_id; }
    public void setPlanId(String v) { this.plan_id = v; }
    public Integer getTargetVersion() { return target_version; }
    public void setTargetVersion(Integer v) { this.target_version = v; }
    public String getUserId() { return user_id; }
    public void setUserId(String v) { this.user_id = v; }
    public String getContent() { return content; }
    public void setContent(String v) { this.content = v; }
    public String getStatus() { return status; }
    public void setStatus(String v) { this.status = v; }
    public Instant getCreateTime() { return create_time; }
    public void setCreateTime(Instant v) { this.create_time = v; }
    public Instant getUpdateTime() { return update_time; }
    public void setUpdateTime(Instant v) { this.update_time = v; }
}

