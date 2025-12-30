package com.teamventure.infrastructure.persistence.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.teamventure.infrastructure.persistence.po.PlanRequestPO;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface PlanRequestMapper extends BaseMapper<PlanRequestPO> {}

