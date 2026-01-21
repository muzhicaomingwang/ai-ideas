package com.teamventure.infrastructure.persistence.po;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.teamventure.app.support.BizException;
import com.teamventure.app.support.IdGenerator;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.Map;

/**
 * 方案实体（plans 表）
 *
 * 字段语义说明：
 * - departure_city: 出发城市，团队从哪里出发（如公司所在地：上海市）
 * - destination: 目的地，团建活动举办地点（如：杭州千岛湖）
 * - destination_city: 目的地所属行政城市（如：杭州）
 *
 * 前端显示格式："{departure_city} → {destination}"
 * 示例：上海市 → 杭州千岛湖
 */
@TableName("plans")
public class PlanPO {
    @TableId
    private String plan_id;
    private String plan_request_id;
    private String user_id;
    private String plan_type;
    private String plan_name;
    private String summary;
    private String highlights;
    private String logo_url;
    private String logo_storage;
    private String itinerary;
    private Integer itinerary_version;
    private String budget_breakdown;
    private String supplier_snapshots;
    private BigDecimal budget_total;
    private BigDecimal budget_per_person;
    private Integer duration_days;
    /** 出发城市（团队从哪里出发，如公司所在地：上海市） */
    private String departure_city;
    /** 目的地（团建活动举办地点，如：杭州千岛湖） */
    private String destination;
    /** 目的地所属行政城市（如：杭州） */
    private String destination_city;
    private String status;
    private Instant create_time;
    private Instant confirmed_time;
    private Instant deleted_at;
    private Instant archived_at;
    /** 通晒开始时间（draft → reviewing 时设置） */
    private Instant review_started_at;
    /** 通晒评价数（reviewing/confirmed 期间累加） */
    private Integer review_count;
    /** 通晒平均分（0-5，可为空） */
    private java.math.BigDecimal average_score;

    public static PlanPO fromMap(Map<String, Object> m) {
        PlanPO po = new PlanPO();
        po.plan_id = (String) m.getOrDefault("plan_id", IdGenerator.newId("plan"));
        po.plan_type = (String) m.getOrDefault("plan_type", "standard");
        po.plan_name = (String) m.getOrDefault("plan_name", "");
        po.summary = (String) m.getOrDefault("summary", "");
        po.highlights = JsonHelper.safeJson(m.get("highlights"));
        po.logo_url = (String) m.getOrDefault("logo_url", null);
        po.logo_storage = (String) m.getOrDefault("logo_storage", null);
        po.itinerary = JsonHelper.safeJson(m.get("itinerary"));
        po.itinerary_version = 1;
        po.budget_breakdown = JsonHelper.safeJson(m.get("budget_breakdown"));
        po.supplier_snapshots = JsonHelper.safeJson(m.get("supplier_snapshots"));
        po.budget_total = JsonHelper.safeDecimal(m.get("budget_total"));
        po.budget_per_person = JsonHelper.safeDecimal(m.get("budget_per_person"));
        po.duration_days = JsonHelper.safeInt(m.get("duration_days"));
        po.departure_city = (String) m.getOrDefault("departure_city", "");
        po.destination = (String) m.getOrDefault("destination", "");
        po.destination_city = (String) m.getOrDefault("destination_city", "");
        po.review_count = JsonHelper.safeInt(m.getOrDefault("review_count", 0));
        po.average_score = JsonHelper.safeDecimal(m.get("average_score"));
        po.status = (String) m.getOrDefault("status", "draft");
        return po;
    }

    public String getPlanId() { return plan_id; }
    public void setPlanId(String v) { this.plan_id = v; }
    public String getPlanRequestId() { return plan_request_id; }
    public void setPlanRequestId(String v) { this.plan_request_id = v; }
    public String getUserId() { return user_id; }
    public void setUserId(String v) { this.user_id = v; }
    public String getPlanName() { return plan_name; }
    public void setPlanName(String v) { this.plan_name = v; }
    public String getPlanType() { return plan_type; }
    public void setPlanType(String v) { this.plan_type = v; }
    public String getStatus() { return status; }
    public void setStatus(String v) { this.status = v; }
    public Instant getCreateTime() { return create_time; }
    public void setCreateTime(Instant v) { this.create_time = v; }
    public Instant getConfirmedTime() { return confirmed_time; }
    public void setConfirmedTime(Instant v) { this.confirmed_time = v; }
    public java.math.BigDecimal getBudgetTotal() { return budget_total; }
    public void setBudgetTotal(java.math.BigDecimal v) { this.budget_total = v; }
    public Integer getDurationDays() { return duration_days; }
    public void setDurationDays(Integer v) { this.duration_days = v; }

    // 以下是详情页所需的完整字段 getter/setter
    public String getSummary() { return summary; }
    public void setSummary(String v) { this.summary = v; }

    public String getHighlights() { return highlights; }
    public void setHighlights(String v) { this.highlights = v; }

    public String getLogoUrl() { return logo_url; }
    public void setLogoUrl(String v) { this.logo_url = v; }

    public String getLogoStorage() { return logo_storage; }
    public void setLogoStorage(String v) { this.logo_storage = v; }

    public String getItinerary() { return itinerary; }
    public void setItinerary(String v) { this.itinerary = v; }

    public Integer getItineraryVersion() { return itinerary_version; }
    public void setItineraryVersion(Integer v) { this.itinerary_version = v; }

    public String getBudgetBreakdown() { return budget_breakdown; }
    public void setBudgetBreakdown(String v) { this.budget_breakdown = v; }

    public String getSupplierSnapshots() { return supplier_snapshots; }
    public void setSupplierSnapshots(String v) { this.supplier_snapshots = v; }

    public BigDecimal getBudgetPerPerson() { return budget_per_person; }
    public void setBudgetPerPerson(BigDecimal v) { this.budget_per_person = v; }

    public String getDepartureCity() { return departure_city; }
    public void setDepartureCity(String v) { this.departure_city = v; }

    public String getDestination() { return destination; }
    public void setDestination(String v) { this.destination = v; }

    public String getDestinationCity() { return destination_city; }
    public void setDestinationCity(String v) { this.destination_city = v; }

    public Instant getDeletedAt() { return deleted_at; }
    public void setDeletedAt(Instant v) { this.deleted_at = v; }

    public Instant getArchivedAt() { return archived_at; }
    public void setArchivedAt(Instant v) { this.archived_at = v; }

    public Instant getReviewStartedAt() { return review_started_at; }
    public void setReviewStartedAt(Instant v) { this.review_started_at = v; }

    public Integer getReviewCount() { return review_count; }
    public void setReviewCount(Integer v) { this.review_count = v; }

    public java.math.BigDecimal getAverageScore() { return average_score; }
    public void setAverageScore(java.math.BigDecimal v) { this.average_score = v; }
}
