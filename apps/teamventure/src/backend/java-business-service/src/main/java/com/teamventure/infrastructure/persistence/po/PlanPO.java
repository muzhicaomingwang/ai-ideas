package com.teamventure.infrastructure.persistence.po;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.teamventure.app.support.BizException;
import com.teamventure.app.support.IdGenerator;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.Map;

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
    private String itinerary;
    private String budget_breakdown;
    private String supplier_snapshots;
    private BigDecimal budget_total;
    private BigDecimal budget_per_person;
    private Integer duration_days;
    private String departure_city;
    private String destination;
    private String status;
    private Instant confirmed_time;
    private Instant deleted_at;
    private Instant archived_at;

    public static PlanPO fromMap(Map<String, Object> m) {
        PlanPO po = new PlanPO();
        po.plan_id = (String) m.getOrDefault("plan_id", IdGenerator.newId("plan"));
        po.plan_type = (String) m.getOrDefault("plan_type", "standard");
        po.plan_name = (String) m.getOrDefault("plan_name", "");
        po.summary = (String) m.getOrDefault("summary", "");
        po.highlights = JsonHelper.safeJson(m.get("highlights"));
        po.itinerary = JsonHelper.safeJson(m.get("itinerary"));
        po.budget_breakdown = JsonHelper.safeJson(m.get("budget_breakdown"));
        po.supplier_snapshots = JsonHelper.safeJson(m.get("supplier_snapshots"));
        po.budget_total = JsonHelper.safeDecimal(m.get("budget_total"));
        po.budget_per_person = JsonHelper.safeDecimal(m.get("budget_per_person"));
        po.duration_days = JsonHelper.safeInt(m.get("duration_days"));
        po.departure_city = (String) m.getOrDefault("departure_city", "");
        po.destination = (String) m.getOrDefault("destination", "");
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

    public String getItinerary() { return itinerary; }
    public void setItinerary(String v) { this.itinerary = v; }

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

    public Instant getDeletedAt() { return deleted_at; }
    public void setDeletedAt(Instant v) { this.deleted_at = v; }

    public Instant getArchivedAt() { return archived_at; }
    public void setArchivedAt(Instant v) { this.archived_at = v; }
}

