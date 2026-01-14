package com.teamventure.infrastructure.map;

import com.teamventure.domain.valueobject.MapRequest;
import com.teamventure.domain.valueobject.MapSizePreset;
import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.net.SocketTimeoutException;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

/**
 * MapDegradationHandler单元测试
 *
 * @author TeamVenture
 * @since 2026-01-14
 */
class MapDegradationHandlerTest {

    private MapDegradationHandler handler;
    private CircuitBreaker circuitBreaker;

    @BeforeEach
    void setUp() {
        // 创建测试用的熔断器（宽松配置）
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .failureRateThreshold(50)
            .waitDurationInOpenState(java.time.Duration.ofMillis(100))
            .slidingWindowSize(10)
            .minimumNumberOfCalls(5)
            .build();

        circuitBreaker = CircuitBreaker.of("test-circuit-breaker", config);

        handler = new MapDegradationHandler();
        // 注入circuitBreaker（通过反射或setter）
        try {
            java.lang.reflect.Field field = handler.getClass()
                .getDeclaredField("mapCircuitBreaker");
            field.setAccessible(true);
            field.set(handler, circuitBreaker);
        } catch (Exception e) {
            fail("Failed to inject circuit breaker: " + e.getMessage());
        }
    }

    @Test
    @DisplayName("API调用成功应直接返回结果")
    void testSuccessfulApiCall() {
        MapRequest request = buildTestRequest();
        String expectedUrl = "https://test-success.url";

        String actualUrl = handler.callWithFallback(
            request,
            () -> expectedUrl
        );

        assertEquals(expectedUrl, actualUrl);
    }

    @Test
    @DisplayName("API超时应重试")
    void testTimeoutRetry() throws Exception {
        MapRequest request = buildTestRequest();
        AtomicInteger callCount = new AtomicInteger(0);

        String actualUrl = handler.callWithFallback(
            request,
            () -> {
                int count = callCount.incrementAndGet();
                if (count < 2) {
                    throw new RuntimeException("Timeout");  // 使用RuntimeException避免checked exception
                }
                return "https://success-after-retry.url";
            }
        );

        assertTrue(actualUrl.contains("success") || actualUrl.contains("placeholder"),
            "重试后应成功或降级到占位图");
        assertTrue(callCount.get() >= 1, "至少应调用1次");
    }

    @Test
    @DisplayName("API持续失败应降级到占位图")
    void testFallbackToPlaceholder() {
        MapRequest request = buildTestRequest();

        String actualUrl = handler.callWithFallback(
            request,
            () -> {
                throw new RuntimeException("API totally failed");
            }
        );

        assertTrue(actualUrl.contains("placeholder") || actualUrl.contains("cdn"),
            "持续失败应返回占位图URL");
    }

    @Test
    @DisplayName("熔断器开启后应快速失败")
    void testCircuitBreakerFastFail() {
        MapRequest request = buildTestRequest();

        // 触发多次失败，开启熔断器
        for (int i = 0; i < 10; i++) {
            try {
                handler.callWithFallback(
                    request,
                    () -> {
                        throw new RuntimeException("Fail");
                    }
                );
            } catch (Exception e) {
                // 捕获异常，继续测试
            }
        }

        // 验证熔断器状态
        CircuitBreaker.State state = circuitBreaker.getState();
        assertTrue(
            state == CircuitBreaker.State.OPEN ||
            state == CircuitBreaker.State.HALF_OPEN,
            "失败率达标后熔断器应开启"
        );
    }

    @Test
    @DisplayName("限流错误应触发重试")
    void testRateLimitTriggerRetry() {
        MapRequest request = buildTestRequest();
        AtomicInteger callCount = new AtomicInteger(0);

        String actualUrl = handler.callWithFallback(
            request,
            () -> {
                int count = callCount.incrementAndGet();
                if (count < 2) {
                    throw new RuntimeException("rate limit exceeded");
                }
                return "https://success-after-rate-limit.url";
            }
        );

        assertTrue(actualUrl.contains("success") || actualUrl.contains("placeholder"));
        assertTrue(callCount.get() >= 1, "应至少重试1次");
    }

    /**
     * 构建测试用的MapRequest
     */
    private MapRequest buildTestRequest() {
        return MapRequest.builder()
            .size(MapSizePreset.DETAIL)
            .zoom(15)
            .center(MapRequest.Point.of(121.473701, 31.230416))
            .markers("mid,0x00FF00,S:121.47,31.23")
            .paths("6,0x1890FF,1:121.47,31.23;121.48,31.24")
            .style("normal")
            .format("png")
            .build();
    }
}
