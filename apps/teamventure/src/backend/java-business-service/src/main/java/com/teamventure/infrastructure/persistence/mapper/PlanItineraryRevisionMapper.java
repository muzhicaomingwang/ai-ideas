package com.teamventure.infrastructure.persistence.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.teamventure.infrastructure.persistence.po.PlanItineraryRevisionPO;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface PlanItineraryRevisionMapper extends BaseMapper<PlanItineraryRevisionPO> {}

