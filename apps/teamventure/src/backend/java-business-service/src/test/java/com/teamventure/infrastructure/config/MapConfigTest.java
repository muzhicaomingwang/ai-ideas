package com.teamventure.infrastructure.config;

import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.net.ConnectException;
import java.net.SocketTimeoutException;
import java.time.Duration;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/**
 * MapConfig 单元测试
 *
 * 测试熔断器配置和重试策略
 *
 * @author TeamVenture
 * @since 2026-01-14
 */
class MapConfigTest {

    private MapConfig mapConfig;
    private CircuitBreaker circuitBreaker;

    @BeforeEach
    void setUp() {
        mapConfig = new MapConfig();
        circuitBreaker = mapConfig.mapCircuitBreaker();
    }

    /**
     * 测试1: 熔断器配置参数正确性
     *
     * 场景：验证熔断器的各项阈值配置
     */
    @Test
    @DisplayName("验证熔断器配置参数正确")
    void testCircuitBreakerConfig_ThresholdsCorrect() {
        CircuitBreakerConfig config = circuitBreaker.getCircuitBreakerConfig();

        // 验证失败率阈值
        assertThat(config.getFailureRateThreshold()).isEqualTo(50.0f);

        // 验证熔断等待时间（使用正确的API方法名）
        assertThat(config.getWaitIntervalFunctionInOpenState()).isNotNull();

        // 验证滑动窗口大小
        assertThat(config.getSlidingWindowSize()).isEqualTo(10);

        // 验证最小调用数
        assertThat(config.getMinimumNumberOfCalls()).isEqualTo(5);

        // 验证半开状态允许调用数
        assertThat(config.getPermittedNumberOfCallsInHalfOpenState()).isEqualTo(3);

        // 验证自动转换为半开状态
        assertThat(config.isAutomaticTransitionFromOpenToHalfOpenEnabled()).isTrue();

        // 验证熔断器名称
        assertThat(circuitBreaker.getName()).isEqualTo("amap-static-api");
    }

    /**
     * 测试2: 异常记录策略验证
     *
     * 场景：验证哪些异常会被记录为失败，哪些会被忽略
     */
    @Test
    @DisplayName("验证异常记录策略")
    void testCircuitBreakerConfig_ExceptionHandling() {
        CircuitBreakerConfig config = circuitBreaker.getCircuitBreakerConfig();

        // 这些异常应该被记录为失败
        assertThat(config.getRecordExceptionPredicate().test(new SocketTimeoutException())).isTrue();
        assertThat(config.getRecordExceptionPredicate().test(new ConnectException())).isTrue();
        assertThat(config.getRecordExceptionPredicate().test(new IOException())).isTrue();

        // IllegalArgumentException应该被忽略（参数错误不是服务故障）
        assertThat(config.getIgnoreExceptionPredicate().test(new IllegalArgumentException())).isTrue();
    }

    /**
     * 测试3: 熔断器状态转换
     *
     * 场景：模拟失败率超过50%时熔断器打开
     */
    @Test
    @DisplayName("失败率超过50%时熔断器应打开")
    void testCircuitBreaker_OpensOnHighFailureRate() {
        // 初始状态应该是CLOSED
        assertThat(circuitBreaker.getState()).isEqualTo(CircuitBreaker.State.CLOSED);

        // 模拟10次调用，6次失败（60%失败率）
        for (int i = 0; i < 10; i++) {
            final int attempt = i;
            try {
                circuitBreaker.executeSupplier(() -> {
                    if (attempt < 6) {
                        throw new RuntimeException(new SocketTimeoutException("Simulated timeout"));
                    }
                    return "success";
                });
            } catch (Exception e) {
                // 预期的失败，继续下一次调用
            }
        }

        // 验证熔断器打开
        assertThat(circuitBreaker.getState()).isEqualTo(CircuitBreaker.State.OPEN);
    }

    /**
     * 测试4: 未达到最小调用数时不熔断
     *
     * 场景：少于5次调用时，即使失败率100%也不熔断
     */
    @Test
    @DisplayName("未达到最小调用数时不熔断")
    void testCircuitBreaker_RequiresMinimumCalls() {
        // 初始状态
        assertThat(circuitBreaker.getState()).isEqualTo(CircuitBreaker.State.CLOSED);

        // 4次调用全部失败
        for (int i = 0; i < 4; i++) {
            try {
                circuitBreaker.executeSupplier(() -> {
                    throw new RuntimeException(new SocketTimeoutException("Simulated timeout"));
                });
            } catch (Exception e) {
                // 预期的失败，继续下一次调用
            }
        }

        // 应该仍然是CLOSED状态（未达到最小调用数5次）
        assertThat(circuitBreaker.getState()).isEqualTo(CircuitBreaker.State.CLOSED);
    }

    /**
     * 测试5: 参数错误不计入失败率
     *
     * 场景：IllegalArgumentException被忽略，不影响熔断器
     */
    @Test
    @DisplayName("参数错误异常应被忽略")
    void testCircuitBreaker_IgnoresIllegalArgumentException() {
        // 10次调用，全部抛出IllegalArgumentException
        for (int i = 0; i < 10; i++) {
            assertThatThrownBy(() ->
                circuitBreaker.executeSupplier(() -> {
                    throw new IllegalArgumentException("Invalid parameter");
                })
            ).isInstanceOf(IllegalArgumentException.class);
        }

        // 熔断器应该仍然是CLOSED（参数错误被忽略）
        assertThat(circuitBreaker.getState()).isEqualTo(CircuitBreaker.State.CLOSED);
    }

    /**
     * 测试6: 熔断器注册表Bean存在
     *
     * 场景：验证CircuitBreakerRegistry bean可用
     */
    @Test
    @DisplayName("验证熔断器注册表Bean创建成功")
    void testCircuitBreakerRegistry_BeanCreated() {
        var registry = mapConfig.circuitBreakerRegistry();

        assertThat(registry).isNotNull();
        assertThat(registry.getDefaultConfig()).isNotNull();
    }
}
