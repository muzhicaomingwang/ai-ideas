package com.teamventure.infrastructure.map;

import com.teamventure.domain.valueobject.MapRequest.Point;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 地图标注样式配置
 *
 * 为不同类型的POI生成统一的标注样式参数
 *
 * @author TeamVenture
 * @since 2026-01-14
 */
@Component
public class MarkerStyleConfig {

    @Value("${teamventure.map.style.marker.start-color:0x00FF00}")
    private String startColor;

    @Value("${teamventure.map.style.marker.end-color:0xFF0000}")
    private String endColor;

    @Value("${teamventure.map.style.marker.waypoint-color:0x1890FF}")
    private String waypointColor;

    /**
     * 标注样式枚举
     */
    public enum MarkerStyle {
        START("S", "0x00FF00", "large"),      // 起点：绿色大标
        END("E", "0xFF0000", "large"),        // 终点：红色大标
        WAYPOINT("", "0x1890FF", "mid"),      // 途经点：蓝色中标
        SUPPLIER("$", "0xFFA500", "small");   // 供应商：橙色小标

        private final String label;
        private final String defaultColor;
        private final String size;

        MarkerStyle(String label, String defaultColor, String size) {
            this.label = label;
            this.defaultColor = defaultColor;
            this.size = size;
        }

        public String getLabel() {
            return label;
        }

        public String getDefaultColor() {
            return defaultColor;
        }

        public String getSize() {
            return size;
        }
    }

    /**
     * 为路线POI列表生成markers参数
     *
     * 格式：size,color,label:lng,lat|size,color,label:lng,lat|...
     * 示例：mid,0x00FF00,S:121.47,31.23|mid,0x1890FF,:121.48,31.24|mid,0xFF0000,E:121.49,31.25
     *
     * @param points POI坐标列表
     * @return 高德API markers参数
     */
    public String generateMarkersParam(List<Point> points) {
        if (points == null || points.isEmpty()) {
            return "";
        }

        List<String> markers = new ArrayList<>();

        for (int i = 0; i < points.size(); i++) {
            Point point = points.get(i);
            MarkerStyle style;
            String color;

            if (i == 0) {
                // 起点
                style = MarkerStyle.START;
                color = startColor;
            } else if (i == points.size() - 1) {
                // 终点
                style = MarkerStyle.END;
                color = endColor;
            } else {
                // 途经点
                style = MarkerStyle.WAYPOINT;
                color = waypointColor;
            }

            markers.add(formatMarker(style, color, point));
        }

        return String.join("|", markers);
    }

    /**
     * 格式化单个标注参数
     *
     * @param style 标注样式
     * @param color 标注颜色（十六进制，如0x00FF00）
     * @param point 坐标点
     * @return 高德API格式：size,color,label:lng,lat
     */
    private String formatMarker(MarkerStyle style, String color, Point point) {
        return String.format("%s,%s,%s:%.6f,%.6f",
            style.getSize(),
            color,
            style.getLabel(),
            point.getLongitude(),
            point.getLatitude()
        );
    }

    /**
     * 为供应商位置生成单个标注
     *
     * @param point 供应商坐标
     * @return markers参数
     */
    public String generateSupplierMarker(Point point) {
        return formatMarker(
            MarkerStyle.SUPPLIER,
            MarkerStyle.SUPPLIER.getDefaultColor(),
            point
        );
    }

    /**
     * 生成带自定义标签的标注
     *
     * @param point 坐标点
     * @param label 自定义标签文本（单个字符）
     * @param color 颜色（十六进制）
     * @return markers参数
     */
    public String generateCustomMarker(Point point, String label, String color) {
        return String.format("mid,%s,%s:%.6f,%.6f",
            color != null ? color : waypointColor,
            label != null ? label : "",
            point.getLongitude(),
            point.getLatitude()
        );
    }
}
