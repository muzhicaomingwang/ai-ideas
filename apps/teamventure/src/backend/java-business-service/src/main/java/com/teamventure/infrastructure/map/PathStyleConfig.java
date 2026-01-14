package com.teamventure.infrastructure.map;

import com.teamventure.domain.valueobject.MapRequest.Point;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 地图路径样式配置
 *
 * 为不同交通方式的路线生成统一的路径样式参数
 *
 * @author TeamVenture
 * @since 2026-01-14
 */
@Component
public class PathStyleConfig {

    @Value("${teamventure.map.style.path.color:0x1890FF}")
    private String defaultColor;

    @Value("${teamventure.map.style.path.width:6}")
    private int defaultWidth;

    @Value("${teamventure.map.style.path.transparency:1.0}")
    private double defaultTransparency;

    /**
     * 路径样式枚举（按交通方式区分）
     */
    public enum PathStyle {
        DRIVING("0x1890FF", 6, 1.0, "驾车"),      // 蓝色粗线
        WALKING("0x52C41A", 4, 0.8, "步行"),      // 绿色中线
        CYCLING("0xFFA500", 5, 0.9, "骑行"),      // 橙色中线
        TRANSIT("0x722ED1", 5, 0.9, "公交");      // 紫色中线

        private final String color;
        private final int weight;
        private final double transparency;
        private final String description;

        PathStyle(String color, int weight, double transparency, String description) {
            this.color = color;
            this.weight = weight;
            this.transparency = transparency;
            this.description = description;
        }

        public String getColor() {
            return color;
        }

        public int getWeight() {
            return weight;
        }

        public double getTransparency() {
            return transparency;
        }

        public String getDescription() {
            return description;
        }
    }

    /**
     * 为路线坐标列表生成paths参数
     *
     * 格式：weight,color,transparency:lng1,lat1;lng2,lat2;...
     * 示例：6,0x1890FF,1:121.47,31.23;121.48,31.24;121.49,31.25
     *
     * @param points 路线坐标列表
     * @return 高德API paths参数
     */
    public String generatePathsParam(List<Point> points) {
        return generatePathsParam(points, PathStyle.DRIVING);
    }

    /**
     * 为路线坐标列表生成paths参数（指定交通方式）
     *
     * @param points 路线坐标列表
     * @param style 路径样式
     * @return 高德API paths参数
     */
    public String generatePathsParam(List<Point> points, PathStyle style) {
        if (points == null || points.size() < 2) {
            return "";  // 至少需要2个点才能画路径
        }

        // 简化路径点（避免URL过长）
        List<Point> simplified = simplifyPath(points, 50);

        // 生成坐标串
        String coords = simplified.stream()
            .map(p -> String.format("%.6f,%.6f",
                p.getLongitude(),
                p.getLatitude()
            ))
            .collect(Collectors.joining(";"));

        // 拼接样式参数
        return String.format("%d,%s,%.1f:%s",
            style.getWeight(),
            style.getColor(),
            style.getTransparency(),
            coords
        );
    }

    /**
     * 使用配置的默认样式生成paths参数
     *
     * @param points 路线坐标列表
     * @return 高德API paths参数
     */
    public String generateDefaultPathsParam(List<Point> points) {
        if (points == null || points.size() < 2) {
            return "";
        }

        List<Point> simplified = simplifyPath(points, 50);

        String coords = simplified.stream()
            .map(p -> String.format("%.6f,%.6f",
                p.getLongitude(),
                p.getLatitude()
            ))
            .collect(Collectors.joining(";"));

        return String.format("%d,%s,%.1f:%s",
            defaultWidth,
            defaultColor,
            defaultTransparency,
            coords
        );
    }

    /**
     * 简化路径点（Douglas-Peucker算法）
     *
     * 减少路径点数量，避免URL过长，同时保持路径形状
     *
     * @param points 原始路径点列表
     * @param maxPoints 最大保留点数
     * @return 简化后的路径点列表
     */
    private List<Point> simplifyPath(List<Point> points, int maxPoints) {
        if (points.size() <= maxPoints) {
            return points;
        }

        // 简单实现：等间隔采样（生产环境可用Douglas-Peucker算法）
        int step = points.size() / (maxPoints - 1);
        List<Point> simplified = new ArrayList<>();

        for (int i = 0; i < points.size(); i += step) {
            simplified.add(points.get(i));
        }

        // 确保终点被包含
        Point lastPoint = points.get(points.size() - 1);
        if (!simplified.get(simplified.size() - 1).equals(lastPoint)) {
            simplified.add(lastPoint);
        }

        return simplified;
    }

    /**
     * 生成多段路径（不同颜色）
     *
     * 用于复杂路线，每段使用不同颜色区分
     *
     * @param segments 路径分段列表
     * @return paths参数（用|连接多段）
     */
    public String generateMultiSegmentPaths(List<PathSegment> segments) {
        if (segments == null || segments.isEmpty()) {
            return "";
        }

        return segments.stream()
            .map(seg -> generatePathsParam(seg.getPoints(), seg.getStyle()))
            .collect(Collectors.joining("|"));
    }

    /**
     * 路径分段数据结构
     */
    @lombok.Data
    @lombok.Builder
    public static class PathSegment {
        private List<Point> points;
        private PathStyle style;
    }
}
