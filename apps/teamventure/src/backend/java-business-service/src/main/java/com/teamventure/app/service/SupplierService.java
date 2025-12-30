package com.teamventure.app.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.teamventure.app.support.BizException;
import com.teamventure.infrastructure.persistence.mapper.SupplierMapper;
import com.teamventure.infrastructure.persistence.po.SupplierPO;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class SupplierService {
    private final SupplierMapper supplierMapper;

    public SupplierService(SupplierMapper supplierMapper) {
        this.supplierMapper = supplierMapper;
    }

    public List<SupplierPO> search(String city, String category) {
        QueryWrapper<SupplierPO> q = new QueryWrapper<>();
        if (city != null && !city.isBlank()) {
            q.eq("city", city);
        }
        if (category != null && !category.isBlank()) {
            q.eq("category", category);
        }
        q.eq("status", "active").orderByDesc("rating");
        return supplierMapper.selectList(q);
    }

    public SupplierPO getById(String supplierId) {
        SupplierPO po = supplierMapper.selectById(supplierId);
        if (po == null) {
            throw new BizException("NOT_FOUND", "supplier not found");
        }
        return po;
    }
}

