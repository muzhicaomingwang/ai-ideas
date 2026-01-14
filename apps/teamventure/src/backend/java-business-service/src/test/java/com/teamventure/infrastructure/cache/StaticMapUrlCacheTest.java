package com.teamventure.infrastructure.cache;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.teamventure.domain.valueobject.MapRequest;
import com.teamventure.domain.valueobject.MapRequest.Point;
import com.teamventure.domain.valueobject.MapSizePreset;
import com.teamventure.infrastructure.persistence.mapper.StaticMapUrlMapper;
import com.teamventure.infrastructure.persistence.po.StaticMapUrlPO;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.ValueOperations;

import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * StaticMapUrlCache单元测试
 *
 * @author TeamVenture
 * @since 2026-01-14
 */
@ExtendWith(MockitoExtension.class)
class StaticMapUrlCacheTest {

    @Mock
    private RedisTemplate<String, String> redisTemplate;

    @Mock
    private ValueOperations<String, String> valueOperations;

    @Mock
    private StaticMapUrlMapper mapper;

    private StaticMapUrlCache cache;

    @BeforeEach
    void setUp() {
        when(redisTemplate.opsForValue()).thenReturn(valueOperations);

        cache = new StaticMapUrlCache(
            1000,  // memorySize
            7,     // memoryTtlDays
            redisTemplate,
            mapper
        );
    }

    @Test
    @DisplayName("首次请求应调用URL生成器并缓存")
    void testCacheMissGeneratesUrl() {
        // 准备测试数据
        MapRequest request = buildTestRequest();
        String expectedUrl = "https://restapi.amap.com/v3/staticmap?key=test&...";

        // Mock Redis和数据库均未命中
        when(valueOperations.get(anyString())).thenReturn(null);
        when(mapper.selectOne(any(QueryWrapper.class))).thenReturn(null);

        // 执行测试
        String actualUrl = cache.getOrGenerate(request, () -> expectedUrl);

        // 验证结果
        assertEquals(expectedUrl, actualUrl);

        // 验证Redis写入
        verify(valueOperations).set(
            anyString(),
            eq(expectedUrl),
            eq(30L),
            eq(TimeUnit.DAYS)
        );

        // 验证数据库写入（异步，使用sleep等待）
        try {
            Thread.sleep(500);  // 等待异步操作完成
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        verify(mapper, atLeastOnce()).insert(any(StaticMapUrlPO.class));
    }

    @Test
    @DisplayName("L1缓存命中应不调用Redis和数据库")
    void testL1CacheHit() {
        MapRequest request = buildTestRequest();
        String expectedUrl = "https://test.url";

        // 第一次调用（缓存未命中）
        when(valueOperations.get(anyString())).thenReturn(null);
        when(mapper.selectOne(any(QueryWrapper.class))).thenReturn(null);

        cache.getOrGenerate(request, () -> expectedUrl);

        // 重置mock计数器
        clearInvocations(valueOperations, mapper);

        // 第二次调用（L1缓存命中）
        String secondCall = cache.getOrGenerate(request, () -> "should-not-be-called");

        assertEquals(expectedUrl, secondCall);

        // 验证没有调用Redis和数据库
        verify(valueOperations, never()).get(anyString());
        verify(mapper, never()).selectOne(any());
    }

    @Test
    @DisplayName("L2 Redis缓存命中应回填L1")
    void testL2CacheHitFillsL1() {
        MapRequest request = buildTestRequest();
        String expectedUrl = "https://from-redis.url";

        // Mock Redis命中
        when(valueOperations.get(anyString())).thenReturn(expectedUrl);

        // 执行测试
        String actualUrl = cache.getOrGenerate(request, () -> "should-not-be-called");

        assertEquals(expectedUrl, actualUrl);

        // 验证数据库未被调用
        verify(mapper, never()).selectOne(any());

        // 验证L1缓存被回填（第二次调用不应访问Redis）
        clearInvocations(valueOperations);
        String secondCall = cache.getOrGenerate(request, () -> "should-not-be-called");
        assertEquals(expectedUrl, secondCall);
        verify(valueOperations, never()).get(anyString());
    }

    @Test
    @DisplayName("L3数据库缓存命中应回填L1和L2")
    void testL3CacheHitFillsL1AndL2() {
        MapRequest request = buildTestRequest();
        String expectedUrl = "https://from-database.url";

        // Mock Redis未命中
        when(valueOperations.get(anyString())).thenReturn(null);

        // Mock数据库命中
        StaticMapUrlPO po = new StaticMapUrlPO();
        po.setCacheKey(request.generateCacheKey());
        po.setUrl(expectedUrl);
        when(mapper.selectOne(any(QueryWrapper.class))).thenReturn(po);

        // 执行测试
        String actualUrl = cache.getOrGenerate(request, () -> "should-not-be-called");

        assertEquals(expectedUrl, actualUrl);

        // 验证Redis被回填
        verify(valueOperations).set(
            anyString(),
            eq(expectedUrl),
            eq(30L),
            eq(TimeUnit.DAYS)
        );

        // 验证命中次数被更新（异步）
        try {
            Thread.sleep(500);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        verify(mapper, atLeastOnce()).incrementHitCount(anyString());
    }

    @Test
    @DisplayName("缓存禁用时应直接调用生成器")
    void testCacheDisabled() {
        // 重新创建缓存对象（禁用缓存）
        cache = new StaticMapUrlCache(0, 0, redisTemplate, mapper);

        MapRequest request = buildTestRequest();
        String expectedUrl = "https://generated.url";

        String actualUrl = cache.getOrGenerate(request, () -> expectedUrl);

        assertEquals(expectedUrl, actualUrl);

        // 验证没有缓存操作
        verify(valueOperations, never()).get(anyString());
        verify(valueOperations, never()).set(anyString(), anyString(), anyLong(), any());
        verify(mapper, never()).selectOne(any());
    }

    @Test
    @DisplayName("缓存Key应根据请求参数生成唯一MD5")
    void testCacheKeyUniqueness() {
        MapRequest request1 = MapRequest.builder()
            .size(MapSizePreset.DETAIL)
            .zoom(15)
            .center(Point.of(121.47, 31.23))
            .markers("mid,0x00FF00,A:121.47,31.23")
            .paths("6,0x1890FF,1:121.47,31.23;121.48,31.24")
            .style("normal")
            .build();

        MapRequest request2 = MapRequest.builder()
            .size(MapSizePreset.DETAIL)
            .zoom(15)
            .center(Point.of(121.47, 31.23))
            .markers("mid,0x00FF00,A:121.47,31.23")
            .paths("6,0x1890FF,1:121.47,31.23;121.48,31.24")
            .style("normal")
            .build();

        MapRequest request3 = MapRequest.builder()
            .size(MapSizePreset.THUMBNAIL)  // 不同的size
            .zoom(15)
            .center(Point.of(121.47, 31.23))
            .markers("mid,0x00FF00,A:121.47,31.23")
            .paths("6,0x1890FF,1:121.47,31.23;121.48,31.24")
            .style("normal")
            .build();

        String key1 = request1.generateCacheKey();
        String key2 = request2.generateCacheKey();
        String key3 = request3.generateCacheKey();

        // 相同参数应生成相同key
        assertEquals(key1, key2);

        // 不同参数应生成不同key
        assertNotEquals(key1, key3);

        // key应该是32字符MD5
        assertEquals(32, key1.length());
        assertTrue(key1.matches("[0-9a-f]{32}"));
    }

    /**
     * 构建测试用的MapRequest
     */
    private MapRequest buildTestRequest() {
        return MapRequest.builder()
            .size(MapSizePreset.DETAIL)
            .zoom(15)
            .center(Point.of(121.473701, 31.230416))
            .markers("mid,0x00FF00,S:121.47,31.23")
            .paths("6,0x1890FF,1:121.47,31.23;121.48,31.24")
            .style("normal")
            .format("png")
            .build();
    }
}
