package com.teamventure.infrastructure.config;

import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.io.IOException;
import java.net.ConnectException;
import java.net.SocketTimeoutException;
import java.time.Duration;

/**
 * 地图服务配置类
 *
 * 配置熔断器、重试等resilience组件
 *
 * @author TeamVenture
 * @since 2026-01-14
 */
@Configuration
public class MapConfig {

    /**
     * 配置高德地图API的熔断器
     *
     * 熔断策略：
     * - 失败率达到50%时开启熔断
     * - 熔断后等待30秒再尝试半开状态
     * - 滑动窗口10次请求
     * - 至少5次调用后才开始计算失败率
     *
     * @return CircuitBreaker实例
     */
    @Bean
    public CircuitBreaker mapCircuitBreaker() {
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .failureRateThreshold(50)  // 失败率阈值50%
            .waitDurationInOpenState(Duration.ofSeconds(30))  // 熔断后等待30秒
            .slidingWindowSize(10)  // 滑动窗口大小10次请求
            .minimumNumberOfCalls(5)  // 至少5次调用才计算失败率
            .permittedNumberOfCallsInHalfOpenState(3)  // 半开状态允许3次调用
            .automaticTransitionFromOpenToHalfOpenEnabled(true)  // 自动从开启转半开
            .recordException(MapConfig::shouldRecord)
            .ignoreExceptions(IllegalArgumentException.class)  // 参数错误不计入失败率
            .build();

        CircuitBreaker circuitBreaker = CircuitBreaker.of("amap-static-api", config);

        // 注册事件监听（用于监控和告警）
        circuitBreaker.getEventPublisher()
            .onStateTransition(event -> {
                // 熔断状态变化时记录日志
                org.slf4j.LoggerFactory.getLogger(MapConfig.class)
                    .warn("CircuitBreaker state changed: {} -> {}",
                        event.getStateTransition().getFromState(),
                        event.getStateTransition().getToState()
                    );
            })
            .onFailureRateExceeded(event -> {
                // 失败率超过阈值时告警
                org.slf4j.LoggerFactory.getLogger(MapConfig.class)
                    .error("CircuitBreaker failure rate exceeded: {}%",
                        event.getFailureRate()
                    );
            });

        return circuitBreaker;
    }

    private static boolean shouldRecord(Throwable t) {
        Throwable cur = t;
        for (int i = 0; i < 8 && cur != null; i++) {
            if (cur instanceof SocketTimeoutException) return true;
            if (cur instanceof ConnectException) return true;
            if (cur instanceof IOException) return true;
            cur = cur.getCause();
        }
        return false;
    }

    /**
     * 配置熔断器注册表（用于管理多个熔断器）
     *
     * @return CircuitBreakerRegistry
     */
    @Bean
    public CircuitBreakerRegistry circuitBreakerRegistry() {
        return CircuitBreakerRegistry.of(
            CircuitBreakerConfig.ofDefaults()
        );
    }
}
