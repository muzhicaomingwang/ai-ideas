package com.teamventure.infrastructure.persistence.po;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

@TableName("supplier_contact_logs")
public class SupplierContactLogPO {
    @TableId
    private String contact_id;
    private String plan_id;
    private String supplier_id;
    private String user_id;
    private String channel;
    private String notes;

    public String getContactId() { return contact_id; }
    public void setContactId(String v) { this.contact_id = v; }
    public String getPlanId() { return plan_id; }
    public void setPlanId(String v) { this.plan_id = v; }
    public String getSupplierId() { return supplier_id; }
    public void setSupplierId(String v) { this.supplier_id = v; }
    public String getUserId() { return user_id; }
    public void setUserId(String v) { this.user_id = v; }
    public String getChannel() { return channel; }
    public void setChannel(String v) { this.channel = v; }
    public String getNotes() { return notes; }
    public void setNotes(String v) { this.notes = v; }
}

