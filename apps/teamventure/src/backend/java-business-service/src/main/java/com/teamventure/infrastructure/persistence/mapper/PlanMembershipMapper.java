package com.teamventure.infrastructure.persistence.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.teamventure.infrastructure.persistence.po.PlanMembershipPO;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface PlanMembershipMapper extends BaseMapper<PlanMembershipPO> {}

