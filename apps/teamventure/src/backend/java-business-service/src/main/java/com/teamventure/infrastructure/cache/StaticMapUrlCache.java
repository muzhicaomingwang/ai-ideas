package com.teamventure.infrastructure.cache;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import com.github.benmanes.caffeine.cache.stats.CacheStats;
import com.teamventure.domain.valueobject.MapRequest;
import com.teamventure.infrastructure.persistence.mapper.StaticMapUrlMapper;
import com.teamventure.infrastructure.persistence.po.StaticMapUrlPO;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;

/**
 * 静态地图URL三级缓存管理器
 *
 * 缓存架构：
 * - L1: Caffeine内存缓存（1000条，7天TTL，LRU淘汰）
 * - L2: Redis缓存（30天TTL）
 * - L3: MySQL数据库（永久存储，防缓存穿透）
 *
 * 查询顺序：L1 → L2 → L3 → 生成新URL
 * 回填策略：L3 → L2 → L1
 *
 * @author TeamVenture
 * @since 2026-01-14
 */
@Component
public class StaticMapUrlCache {

    private static final Logger log = LoggerFactory.getLogger(StaticMapUrlCache.class);

    private final Cache<String, String> memoryCache;  // L1缓存
    private final RedisTemplate<String, String> redisTemplate;  // L2缓存
    private final StaticMapUrlMapper mapper;  // L3缓存

    @Value("${teamventure.map.cache.enabled:true}")
    private boolean cacheEnabled;

    @Value("${teamventure.map.cache.redis-ttl-days:30}")
    private int redisTtlDays;

    private static final String REDIS_KEY_PREFIX = "map:static:";

    @Autowired
    public StaticMapUrlCache(
        @Value("${teamventure.map.cache.memory-size:1000}") int memorySize,
        @Value("${teamventure.map.cache.memory-ttl-days:7}") int memoryTtlDays,
        RedisTemplate<String, String> redisTemplate,
        StaticMapUrlMapper mapper
    ) {
        // 初始化L1缓存（Caffeine）
        this.memoryCache = Caffeine.newBuilder()
            .maximumSize(memorySize)
            .expireAfterWrite(memoryTtlDays, TimeUnit.DAYS)
            .recordStats()  // 记录缓存统计信息
            .build();

        this.redisTemplate = redisTemplate;
        this.mapper = mapper;

        log.info("StaticMapUrlCache initialized: L1 size={}, L1 TTL={}days, L2 TTL={}days",
            memorySize, memoryTtlDays, redisTtlDays);
    }

    /**
     * 获取或生成静态地图URL
     *
     * @param request 地图请求参数
     * @param urlGenerator URL生成器（缓存未命中时调用）
     * @return 静态地图URL
     */
    public String getOrGenerate(MapRequest request, Supplier<String> urlGenerator) {
        if (!cacheEnabled) {
            return urlGenerator.get();
        }

        String cacheKey = request.generateCacheKey();

        // L1: 内存缓存
        String url = memoryCache.getIfPresent(cacheKey);
        if (url != null) {
            log.debug("L1 cache hit: {}", cacheKey);
            return url;
        }

        // L2: Redis缓存
        url = getFromRedis(cacheKey);
        if (url != null) {
            log.debug("L2 cache hit: {}", cacheKey);
            memoryCache.put(cacheKey, url);  // 回填L1
            return url;
        }

        // L3: 数据库缓存
        url = getFromDatabase(cacheKey);
        if (url != null) {
            log.debug("L3 cache hit: {}", cacheKey);
            putToRedis(cacheKey, url);       // 回填L2
            memoryCache.put(cacheKey, url);  // 回填L1
            return url;
        }

        // 缓存未命中：生成新URL
        log.info("Cache miss, generating new URL: {}", cacheKey);
        url = urlGenerator.get();

        // 写入所有缓存层
        saveToAllLayers(cacheKey, url, request);

        return url;
    }

    /**
     * 从Redis获取缓存
     */
    private String getFromRedis(String cacheKey) {
        try {
            return redisTemplate.opsForValue().get(REDIS_KEY_PREFIX + cacheKey);
        } catch (Exception e) {
            log.warn("Redis get failed: {}", e.getMessage());
            return null;
        }
    }

    /**
     * 写入Redis缓存
     */
    private void putToRedis(String cacheKey, String url) {
        try {
            redisTemplate.opsForValue().set(
                REDIS_KEY_PREFIX + cacheKey,
                url,
                redisTtlDays,
                TimeUnit.DAYS
            );
        } catch (Exception e) {
            log.warn("Redis put failed: {}", e.getMessage());
        }
    }

    /**
     * 从数据库获取缓存
     */
    private String getFromDatabase(String cacheKey) {
        try {
            QueryWrapper<StaticMapUrlPO> query = new QueryWrapper<>();
            query.eq("cache_key", cacheKey);
            StaticMapUrlPO po = mapper.selectOne(query);

            if (po != null) {
                // 异步更新命中次数
                CompletableFuture.runAsync(() -> {
                    try {
                        mapper.incrementHitCount(cacheKey);
                    } catch (Exception e) {
                        log.warn("Update hit count failed: {}", e.getMessage());
                    }
                });
                return po.getUrl();
            }
        } catch (Exception e) {
            log.warn("Database get failed: {}", e.getMessage());
        }
        return null;
    }

    /**
     * 保存到所有缓存层
     */
    private void saveToAllLayers(String cacheKey, String url, MapRequest request) {
        // L1: 内存缓存（同步）
        memoryCache.put(cacheKey, url);

        // L2: Redis缓存（同步）
        putToRedis(cacheKey, url);

        // L3: 数据库缓存（异步）
        CompletableFuture.runAsync(() -> {
            try {
                StaticMapUrlPO po = new StaticMapUrlPO();
                po.setCacheKey(cacheKey);
                po.setUrl(url);
                po.setRequest(serializeRequest(request));
                po.setHitCount(0);
                po.setCreatedAt(LocalDateTime.now());

                mapper.insert(po);
                log.debug("Saved to database: {}", cacheKey);
            } catch (Exception e) {
                log.error("Database save failed: {}", e.getMessage());
            }
        });
    }

    /**
     * 序列化请求参数为JSON（用于调试）
     */
    private String serializeRequest(MapRequest request) {
        try {
            return String.format(
                "{\"size\":\"%s\",\"zoom\":%d,\"center\":\"%s\",\"style\":\"%s\"}",
                request.getSize().name(),
                request.getZoom(),
                request.getCenter(),
                request.getStyle()
            );
        } catch (Exception e) {
            return "{}";
        }
    }

    /**
     * 获取缓存统计信息（监控用）
     *
     * @return L1缓存统计
     */
    public CacheStats getStats() {
        return memoryCache.stats();
    }

    /**
     * 清空L1内存缓存（仅用于测试）
     */
    public void clearMemoryCache() {
        memoryCache.invalidateAll();
        log.warn("L1 memory cache cleared");
    }

    /**
     * 预热缓存（批量加载热门地图）
     *
     * @param requests 需要预热的请求列表
     * @param urlGenerator URL生成器
     */
    public void warmUp(List<MapRequest> requests, Supplier<String> urlGenerator) {
        log.info("Starting cache warm-up: {} requests", requests.size());

        requests.forEach(request -> {
            String cacheKey = request.generateCacheKey();
            String url = memoryCache.getIfPresent(cacheKey);

            if (url == null) {
                // 缓存未命中，生成并缓存
                url = urlGenerator.get();
                memoryCache.put(cacheKey, url);
                putToRedis(cacheKey, url);
            }
        });

        log.info("Cache warm-up completed");
    }
}
