package com.teamventure.infrastructure.persistence.po;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.math.BigDecimal;
import java.time.Instant;

@TableName("plan_requests")
public class PlanRequestPO {
    @TableId
    private String plan_request_id;
    private String user_id;
    private Integer people_count;
    private BigDecimal budget_min;
    private BigDecimal budget_max;
    private String start_date;
    private String end_date;
    private String departure_city;
    private String preferences;
    private String status;
    private Instant generation_started_at;
    private Instant generation_completed_at;

    public String getPlanRequestId() { return plan_request_id; }
    public void setPlanRequestId(String v) { this.plan_request_id = v; }
    public String getUserId() { return user_id; }
    public void setUserId(String v) { this.user_id = v; }
    public Integer getPeopleCount() { return people_count; }
    public void setPeopleCount(Integer v) { this.people_count = v; }
    public BigDecimal getBudgetMin() { return budget_min; }
    public void setBudgetMin(BigDecimal v) { this.budget_min = v; }
    public BigDecimal getBudgetMax() { return budget_max; }
    public void setBudgetMax(BigDecimal v) { this.budget_max = v; }
    public String getStartDate() { return start_date; }
    public void setStartDate(String v) { this.start_date = v; }
    public String getEndDate() { return end_date; }
    public void setEndDate(String v) { this.end_date = v; }
    public String getDepartureCity() { return departure_city; }
    public void setDepartureCity(String v) { this.departure_city = v; }
    public String getPreferencesJson() { return preferences; }
    public void setPreferencesJson(String v) { this.preferences = v; }
    public String getStatus() { return status; }
    public void setStatus(String v) { this.status = v; }
    public Instant getGenerationStartedAt() { return generation_started_at; }
    public void setGenerationStartedAt(Instant v) { this.generation_started_at = v; }
    public Instant getGenerationCompletedAt() { return generation_completed_at; }
    public void setGenerationCompletedAt(Instant v) { this.generation_completed_at = v; }
}

