package com.teamventure.infrastructure.persistence.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.teamventure.infrastructure.persistence.po.StaticMapUrlPO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Update;

/**
 * 静态地图URL缓存Mapper
 *
 * @author TeamVenture
 * @since 2026-01-14
 */
@Mapper
public interface StaticMapUrlMapper extends BaseMapper<StaticMapUrlPO> {

    /**
     * 增加命中次数（原子操作）
     *
     * @param cacheKey 缓存键
     * @return 影响行数
     */
    @Update("UPDATE static_map_url_cache " +
            "SET hit_count = hit_count + 1, last_hit_at = NOW() " +
            "WHERE cache_key = #{cacheKey}")
    int incrementHitCount(@Param("cacheKey") String cacheKey);
}
