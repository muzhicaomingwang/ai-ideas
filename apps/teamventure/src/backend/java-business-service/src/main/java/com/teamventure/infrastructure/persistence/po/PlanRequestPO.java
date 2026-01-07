package com.teamventure.infrastructure.persistence.po;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.math.BigDecimal;
import java.time.Instant;

/**
 * 方案请求实体（plan_requests 表）
 *
 * 字段语义说明：
 * - departure_city: 出发城市，团队从哪里出发（如公司所在地：上海市）
 * - destination: 目的地，团建活动举办地点（如：杭州千岛湖）
 *
 * 前端显示格式："{departure_city} → {destination}"
 * 示例：上海市 → 杭州千岛湖
 */
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
    /** 出发城市（团队从哪里出发，如公司所在地：上海市） */
    private String departure_city;
    /** 目的地（团建活动举办地点，如：杭州千岛湖） */
    private String destination;
    private String preferences;
    private String status;
    private Instant generation_started_at;
    private Instant generation_completed_at;
    private String error_code;
    private String error_message;
    private Instant deleted_at;

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
    public String getDestination() { return destination; }
    public void setDestination(String v) { this.destination = v; }
    public String getPreferencesJson() { return preferences; }
    public void setPreferencesJson(String v) { this.preferences = v; }
    public String getStatus() { return status; }
    public void setStatus(String v) { this.status = v; }
    public Instant getGenerationStartedAt() { return generation_started_at; }
    public void setGenerationStartedAt(Instant v) { this.generation_started_at = v; }
    public Instant getGenerationCompletedAt() { return generation_completed_at; }
    public void setGenerationCompletedAt(Instant v) { this.generation_completed_at = v; }
    public String getErrorCode() { return error_code; }
    public void setErrorCode(String v) { this.error_code = v; }
    public String getErrorMessage() { return error_message; }
    public void setErrorMessage(String v) { this.error_message = v; }
    public Instant getDeletedAt() { return deleted_at; }
    public void setDeletedAt(Instant v) { this.deleted_at = v; }
}

