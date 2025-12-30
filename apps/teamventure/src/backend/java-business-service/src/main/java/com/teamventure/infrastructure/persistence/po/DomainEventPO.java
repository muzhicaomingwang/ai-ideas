package com.teamventure.infrastructure.persistence.po;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.Instant;

@TableName("domain_events")
public class DomainEventPO {
    @TableId
    private String event_id;
    private String event_type;
    private String aggregate_type;
    private String aggregate_id;
    private String user_id;
    private String payload;
    private Instant occurred_at;
    private Boolean processed;

    public String getEventId() { return event_id; }
    public void setEventId(String id) { this.event_id = id; }
    public String getEventType() { return event_type; }
    public void setEventType(String v) { this.event_type = v; }
    public String getAggregateType() { return aggregate_type; }
    public void setAggregateType(String v) { this.aggregate_type = v; }
    public String getAggregateId() { return aggregate_id; }
    public void setAggregateId(String v) { this.aggregate_id = v; }
    public String getUserId() { return user_id; }
    public void setUserId(String v) { this.user_id = v; }
    public String getPayloadJson() { return payload; }
    public void setPayloadJson(String v) { this.payload = v; }
    public Instant getOccurredAt() { return occurred_at; }
    public void setOccurredAt(Instant v) { this.occurred_at = v; }
    public Boolean getProcessed() { return processed; }
    public void setProcessed(Boolean v) { this.processed = v; }
}

