package com.teamventure.infrastructure.persistence.po;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.math.BigDecimal;

@TableName("suppliers")
public class SupplierPO {
    @TableId
    private String supplier_id;
    private String name;
    private String category;
    private String city;
    private BigDecimal rating;
    private String contact_phone;
    private String contact_wechat;
    private String status;

    public String getSupplierId() { return supplier_id; }
    public void setSupplierId(String v) { this.supplier_id = v; }
    public BigDecimal getRating() { return rating; }
    public void setRating(BigDecimal v) { this.rating = v; }
}

