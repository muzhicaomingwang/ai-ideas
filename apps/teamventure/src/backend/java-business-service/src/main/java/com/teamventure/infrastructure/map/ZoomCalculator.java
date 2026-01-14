package com.teamventure.infrastructure.map;

import com.teamventure.domain.valueobject.MapRequest.Point;
import com.teamventure.domain.valueobject.MapSizePreset;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * 地图缩放级别智能计算器
 *
 * 根据POI分布自动计算最佳zoom级别，确保所有标注点都在可视范围内
 *
 * 算法原理：
 * 1. 计算所有POI的地理包围盒（BoundingBox）
 * 2. 根据包围盒的宽度和高度映射到zoom级别
 * 3. 针对不同地图尺寸进行微调
 *
 * @author TeamVenture
 * @since 2026-01-14
 */
@Component
public class ZoomCalculator {

    /**
     * 计算最佳zoom级别
     *
     * @param points POI坐标列表
     * @param size 地图尺寸预设
     * @return zoom级别（3-18）
     */
    public int calculateOptimalZoom(List<Point> points, MapSizePreset size) {
        if (points == null || points.isEmpty()) {
            return getDefaultZoom(size);
        }

        if (points.size() == 1) {
            // 单点地图：根据场景返回合适的zoom
            return getSinglePointZoom(size);
        }

        // 1. 计算包围盒
        BoundingBox bbox = calculateBoundingBox(points);

        // 2. 计算跨度（取宽高中的较大值，并留20%边距）
        double maxSpan = Math.max(bbox.getWidth(), bbox.getHeight()) * 1.2;

        // 3. 跨度到zoom级别映射
        int zoom = mapSpanToZoom(maxSpan);

        // 4. 根据地图尺寸微调
        zoom = adjustZoomBySize(zoom, size);

        // 5. 限制在有效范围内
        return Math.max(3, Math.min(18, zoom));
    }

    /**
     * 跨度到zoom级别映射
     *
     * 高德地图zoom与经纬度跨度的对应关系：
     * - zoom=3:  全球视图   (~180度)
     * - zoom=8:  省级视图   (~10度)
     * - zoom=12: 城市视图   (~0.3度 ≈ 30km)
     * - zoom=15: 街区视图   (~0.01度 ≈ 1km)
     * - zoom=17: 建筑视图   (~0.003度 ≈ 300m)
     *
     * @param maxSpan 最大跨度（度）
     * @return zoom级别
     */
    private int mapSpanToZoom(double maxSpan) {
        if (maxSpan > 10.0) {
            return 3;   // 跨省/跨国
        } else if (maxSpan > 1.0) {
            return 8;   // 跨市
        } else if (maxSpan > 0.1) {
            return 12;  // 同城
        } else if (maxSpan > 0.01) {
            return 15;  // 街区
        } else {
            return 17;  // 相邻建筑
        }
    }

    /**
     * 根据地图尺寸微调zoom
     *
     * 原则：
     * - 缩略图（小尺寸）：降低zoom，显示更大范围
     * - 分享图（大尺寸）：提高zoom，显示更多细节
     *
     * @param baseZoom 基础zoom级别
     * @param size 地图尺寸
     * @return 调整后的zoom
     */
    private int adjustZoomBySize(int baseZoom, MapSizePreset size) {
        switch (size) {
            case THUMBNAIL:
                // 缩略图：降低1级zoom（显示更大范围，避免拥挤）
                return Math.max(3, baseZoom - 1);

            case SHARE:
                // 分享图：提高1级zoom（显示更多细节）
                return Math.min(18, baseZoom + 1);

            case DETAIL:
            case SUPPLIER:
            default:
                // 详情页和供应商位置：使用基础zoom
                return baseZoom;
        }
    }

    /**
     * 获取单点地图的默认zoom
     *
     * @param size 地图尺寸
     * @return zoom级别
     */
    private int getSinglePointZoom(MapSizePreset size) {
        switch (size) {
            case THUMBNAIL:
                return 13;  // 缩略图：稍远视角
            case SHARE:
                return 16;  // 分享图：清晰展示周边
            case SUPPLIER:
                return 15;  // 供应商：街区级别
            case DETAIL:
            default:
                return 15;  // 详情页：街区级别
        }
    }

    /**
     * 获取默认zoom（无POI时）
     *
     * @param size 地图尺寸
     * @return zoom级别
     */
    private int getDefaultZoom(MapSizePreset size) {
        return 12;  // 默认城市级别视图
    }

    /**
     * 计算地理包围盒
     *
     * @param points POI坐标列表
     * @return 包围盒对象
     */
    private BoundingBox calculateBoundingBox(List<Point> points) {
        double minLat = points.stream()
            .mapToDouble(Point::getLatitude)
            .min()
            .orElse(0);

        double maxLat = points.stream()
            .mapToDouble(Point::getLatitude)
            .max()
            .orElse(0);

        double minLng = points.stream()
            .mapToDouble(Point::getLongitude)
            .min()
            .orElse(0);

        double maxLng = points.stream()
            .mapToDouble(Point::getLongitude)
            .max()
            .orElse(0);

        return new BoundingBox(minLat, maxLat, minLng, maxLng);
    }

    /**
     * 地理包围盒内部类
     */
    private static class BoundingBox {
        private final double minLat;
        private final double maxLat;
        private final double minLng;
        private final double maxLng;

        BoundingBox(double minLat, double maxLat, double minLng, double maxLng) {
            this.minLat = minLat;
            this.maxLat = maxLat;
            this.minLng = minLng;
            this.maxLng = maxLng;
        }

        /**
         * 获取纬度跨度（度）
         */
        double getHeight() {
            return maxLat - minLat;
        }

        /**
         * 获取经度跨度（度）
         */
        double getWidth() {
            return maxLng - minLng;
        }

        /**
         * 获取中心点
         */
        Point getCenter() {
            return Point.builder()
                .latitude((minLat + maxLat) / 2.0)
                .longitude((minLng + maxLng) / 2.0)
                .build();
        }

        @Override
        public String toString() {
            return String.format("BBox[lat:%.4f~%.4f, lng:%.4f~%.4f, span:%.4f°×%.4f°]",
                minLat, maxLat, minLng, maxLng, getHeight(), getWidth());
        }
    }
}
