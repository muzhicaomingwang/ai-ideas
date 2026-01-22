package com.teamventure.infrastructure.persistence.po;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.Instant;

@TableName("plan_itinerary_revisions")
public class PlanItineraryRevisionPO {
    @TableId
    private String revision_id;
    private String plan_id;
    private Integer version;
    private String itinerary;
    private String created_by;
    private Instant create_time;

    public String getRevisionId() { return revision_id; }
    public void setRevisionId(String v) { this.revision_id = v; }
    public String getPlanId() { return plan_id; }
    public void setPlanId(String v) { this.plan_id = v; }
    public Integer getVersion() { return version; }
    public void setVersion(Integer v) { this.version = v; }
    public String getItinerary() { return itinerary; }
    public void setItinerary(String v) { this.itinerary = v; }
    public String getCreatedBy() { return created_by; }
    public void setCreatedBy(String v) { this.created_by = v; }
    public Instant getCreateTime() { return create_time; }
    public void setCreateTime(Instant v) { this.create_time = v; }
}

