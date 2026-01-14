package com.teamventure.infrastructure.persistence.po;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import java.time.LocalDateTime;

/**
 * 静态地图URL缓存表PO对象
 *
 * @author TeamVenture
 * @since 2026-01-14
 */
@TableName("static_map_url_cache")
public class StaticMapUrlPO {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** MD5缓存键（32字符） */
    private String cache_key;

    /** 静态地图URL */
    private String url;

    /** 原始请求参数（JSON格式，用于调试） */
    private String request;

    /** 缓存命中次数 */
    private Integer hit_count;

    /** 创建时间 */
    private LocalDateTime created_at;

    /** 最后命中时间 */
    private LocalDateTime last_hit_at;

    // Getter/Setter
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getCacheKey() {
        return cache_key;
    }

    public void setCacheKey(String cache_key) {
        this.cache_key = cache_key;
    }

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public String getRequest() {
        return request;
    }

    public void setRequest(String request) {
        this.request = request;
    }

    public Integer getHitCount() {
        return hit_count;
    }

    public void setHitCount(Integer hit_count) {
        this.hit_count = hit_count;
    }

    public LocalDateTime getCreatedAt() {
        return created_at;
    }

    public void setCreatedAt(LocalDateTime created_at) {
        this.created_at = created_at;
    }

    public LocalDateTime getLastHitAt() {
        return last_hit_at;
    }

    public void setLastHitAt(LocalDateTime last_hit_at) {
        this.last_hit_at = last_hit_at;
    }

    /**
     * 增加命中次数
     */
    public void incrementHitCount() {
        if (this.hit_count == null) {
            this.hit_count = 0;
        }
        this.hit_count++;
        this.last_hit_at = LocalDateTime.now();
    }
}
