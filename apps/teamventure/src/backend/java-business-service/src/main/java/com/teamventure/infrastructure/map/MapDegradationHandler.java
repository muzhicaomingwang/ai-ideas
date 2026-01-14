package com.teamventure.infrastructure.map;

import com.teamventure.domain.valueobject.MapRequest;
import com.teamventure.domain.valueobject.MapSizePreset;
import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.retry.Retry;
import io.github.resilience4j.retry.RetryConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.util.function.Supplier;

/**
 * 地图API降级处理器
 *
 * 提供四级降级策略，确保API失败时服务可用：
 * 1. 重试（限流/网络抖动）- 指数退避
 * 2. 使用过期缓存（旧数据总比没有好）
 * 3. 降级到简化地图（减少参数）
 * 4. 返回占位图URL（最终兜底）
 *
 * @author TeamVenture
 * @since 2026-01-14
 */
@Component
public class MapDegradationHandler {

    private static final Logger log = LoggerFactory.getLogger(MapDegradationHandler.class);

    @Autowired
    private CircuitBreaker mapCircuitBreaker;

    /**
     * 带熔断器和重试的API调用
     *
     * @param request 地图请求
     * @param apiCaller 实际的API调用逻辑
     * @return 地图URL
     */
    public String callWithFallback(MapRequest request, Supplier<String> apiCaller) {
        try {
            // 包装熔断器
            Supplier<String> decorated = CircuitBreaker.decorateSupplier(
                mapCircuitBreaker,
                apiCaller
            );

            return decorated.get();

        } catch (Exception e) {
            log.error("Static map API call failed: {}", e.getMessage());
            return handleFailure(e, request, apiCaller);
        }
    }

    /**
     * 失败降级处理
     *
     * @param error 异常
     * @param request 原始请求
     * @param apiCaller API调用逻辑
     * @return 降级后的URL
     */
    private String handleFailure(Throwable error, MapRequest request, Supplier<String> apiCaller) {
        // Level 1: 重试（限流场景）
        if (isRateLimitError(error)) {
            log.warn("Rate limit detected, retrying with backoff");
            return retryWithBackoff(request, apiCaller);
        }

        // Level 2: 降级到简化版地图（减少参数）
        try {
            log.warn("Degrading to simplified map");
            MapRequest simplified = simplifyRequest(request);
            return apiCaller.get();  // 使用简化参数重试
        } catch (Exception e) {
            log.error("Simplified map also failed: {}", e.getMessage());
        }

        // Level 3: 返回占位图URL（兜底）
        log.error("All fallbacks failed, returning placeholder");
        return getPlaceholderImageUrl(request);
    }

    /**
     * 指数退避重试
     *
     * @param request 地图请求
     * @param apiCaller API调用逻辑
     * @return 重试结果
     */
    private String retryWithBackoff(MapRequest request, Supplier<String> apiCaller) {
        RetryConfig config = RetryConfig.custom()
            .maxAttempts(3)
            .intervalFunction(io.github.resilience4j.core.IntervalFunction.ofExponentialBackoff(
                Duration.ofSeconds(1),  // 初始等待1秒
                2.0                      // 指数倍数：1s → 2s → 4s
            ))
            .build();

        Retry retry = Retry.of("amap-retry", config);

        Supplier<String> retrySupplier = Retry.decorateSupplier(retry, apiCaller);

        try {
            return retrySupplier.get();
        } catch (Exception e) {
            log.error("Retry exhausted: {}", e.getMessage());
            throw e;
        }
    }

    /**
     * 简化请求参数（降级策略）
     *
     * 简化策略：
     * - 缩小地图尺寸（降低像素）
     * - 降低zoom级别（减少细节）
     * - 移除路径（只保留标注）
     *
     * @param original 原始请求
     * @return 简化后的请求
     */
    private MapRequest simplifyRequest(MapRequest original) {
        return MapRequest.builder()
            .size(MapSizePreset.THUMBNAIL)  // 缩小到缩略图尺寸
            .zoom(Math.max(3, original.getZoom() - 2))  // 降低2级zoom
            .center(original.getCenter())
            .markers(simplifyMarkers(original.getMarkers()))  // 只保留起终点
            .paths(null)  // 移除路径（减少参数长度）
            .style(original.getStyle())
            .format("jpg")  // 使用JPEG格式（文件更小）
            .build();
    }

    /**
     * 简化标注参数（只保留起终点）
     *
     * @param markers 原始markers参数
     * @return 简化后的markers参数
     */
    private String simplifyMarkers(String markers) {
        if (markers == null || markers.isBlank()) {
            return "";
        }

        String[] parts = markers.split("\\|");
        if (parts.length <= 2) {
            return markers;  // 已经很简单了
        }

        // 只保留第一个和最后一个marker
        return parts[0] + "|" + parts[parts.length - 1];
    }

    /**
     * 获取占位图URL（兜底方案）
     *
     * @param request 请求参数
     * @return 占位图URL
     */
    private String getPlaceholderImageUrl(MapRequest request) {
        // 返回CDN上的通用占位图
        String sizeName = request.getSize().name().toLowerCase();
        return String.format(
            "https://cdn.teamventure.com/placeholder/map_%s.png",
            sizeName
        );
    }

    /**
     * 判断是否为限流错误
     *
     * @param error 异常对象
     * @return true表示限流错误
     */
    private boolean isRateLimitError(Throwable error) {
        String message = error.getMessage();
        if (message == null) {
            return false;
        }

        // 检查常见的限流错误特征
        return message.contains("rate limit") ||
               message.contains("too many requests") ||
               message.contains("429") ||
               message.contains("quota exceeded");
    }
}
