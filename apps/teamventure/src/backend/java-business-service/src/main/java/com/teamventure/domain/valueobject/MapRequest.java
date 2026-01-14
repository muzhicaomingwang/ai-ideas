package com.teamventure.domain.valueobject;

import lombok.Builder;
import lombok.Data;
import org.apache.commons.codec.digest.DigestUtils;

/**
 * 静态地图请求参数值对象
 *
 * 封装生成高德静态地图所需的全部参数
 *
 * @author TeamVenture
 * @since 2026-01-14
 */
@Data
@Builder
public class MapRequest {
    /**
     * 无参构造函数（用于手动builder）
     */
    public MapRequest() {}

    /**
     * 地图尺寸预设
     */
    private MapSizePreset size;

    /**
     * 缩放级别（3-18）
     * - 3: 跨省视图
     * - 8: 跨市视图
     * - 12: 同城视图
     * - 15: 街区视图
     * - 17: 建筑视图
     */
    private Integer zoom;

    /**
     * 地图中心点坐标
     */
    private Point center;

    /**
     * 标注参数（高德API格式）
     * 格式：size,color,label:lng,lat|size,color,label:lng,lat|...
     * 示例：mid,0x00FF00,A:121.47,31.23|mid,0xFF0000,B:121.48,31.24
     */
    private String markers;

    /**
     * 路径参数（高德API格式）
     * 格式：weight,color,transparency:lng1,lat1;lng2,lat2;...
     * 示例：6,0x1890FF,1:121.47,31.23;121.48,31.24;121.49,31.25
     */
    private String paths;

    /**
     * 地图风格
     * - normal: 标准地图
     * - satellite: 卫星图
     * - dark: 暗色模式（v5支持）
     */
    @Builder.Default
    private String style = "normal";

    /**
     * 图片格式
     * - png: PNG格式（无损，文件较大）
     * - jpg: JPEG格式（有损，文件较小）
     * - webp: WebP格式（v5支持，最优压缩）
     */
    @Builder.Default
    private String format = "png";

    /**
     * 生成缓存Key（MD5哈希）
     *
     * 缓存Key包含所有影响地图生成的参数，确保唯一性
     *
     * @return 32字符MD5字符串
     */
    public String generateCacheKey() {
        String raw = String.join("_",
            size != null ? size.name() : "DETAIL",
            zoom != null ? zoom.toString() : "15",
            center != null ? formatPoint(center) : "0,0",
            markers != null ? markers : "",
            paths != null ? paths : "",
            style != null ? style : "normal",
            format != null ? format : "png"
        );
        return DigestUtils.md5Hex(raw);
    }

    /**
     * 格式化坐标点为字符串
     *
     * @param point 坐标点
     * @return 格式：longitude,latitude（保留6位小数）
     */
    private String formatPoint(Point point) {
        return String.format("%.6f,%.6f",
            point.getLongitude(),
            point.getLatitude()
        );
    }

    /**
     * 校验请求参数合法性
     *
     * @throws IllegalArgumentException 参数不合法时抛出
     */
    public void validate() {
        if (size == null) {
            throw new IllegalArgumentException("MapSizePreset cannot be null");
        }

        if (zoom == null || zoom < 3 || zoom > 18) {
            throw new IllegalArgumentException("Zoom must be between 3 and 18");
        }

        if (center == null) {
            throw new IllegalArgumentException("Center point cannot be null");
        }

        // 校验坐标范围（中国境内）
        double lat = center.getLatitude();
        double lng = center.getLongitude();
        if (lat < 3.86 || lat > 53.55 || lng < 73.66 || lng > 135.05) {
            throw new IllegalArgumentException(
                String.format("Coordinates out of China range: (%f, %f)", lng, lat)
            );
        }
    }

    /**
     * 手动添加getter方法（Lombok编译问题临时方案）
     */
    public MapSizePreset getSize() { return size; }
    public Integer getZoom() { return zoom; }
    public Point getCenter() { return center; }
    public String getMarkers() { return markers; }
    public String getPaths() { return paths; }
    public String getStyle() { return style; }
    public String getFormat() { return format; }

    /**
     * 手动添加builder方法（Lombok编译问题临时方案）
     */
    public static MapRequestBuilder builder() {
        return new MapRequestBuilder();
    }

    public static class MapRequestBuilder {
        private MapSizePreset size;
        private Integer zoom;
        private Point center;
        private String markers;
        private String paths;
        private String style = "normal";
        private String format = "png";

        public MapRequestBuilder size(MapSizePreset size) {
            this.size = size;
            return this;
        }

        public MapRequestBuilder zoom(Integer zoom) {
            this.zoom = zoom;
            return this;
        }

        public MapRequestBuilder center(Point center) {
            this.center = center;
            return this;
        }

        public MapRequestBuilder markers(String markers) {
            this.markers = markers;
            return this;
        }

        public MapRequestBuilder paths(String paths) {
            this.paths = paths;
            return this;
        }

        public MapRequestBuilder style(String style) {
            this.style = style;
            return this;
        }

        public MapRequestBuilder format(String format) {
            this.format = format;
            return this;
        }

        public MapRequest build() {
            MapRequest request = new MapRequest();
            request.size = this.size;
            request.zoom = this.zoom;
            request.center = this.center;
            request.markers = this.markers;
            request.paths = this.paths;
            request.style = this.style;
            request.format = this.format;
            return request;
        }
    }

    /**
     * 坐标点内部类
     */
    @Data
    @Builder
    public static class Point {
        /**
         * 无参构造函数（用于手动builder）
         */
        public Point() {}

        private double longitude;  // 经度（GCJ-02坐标系）
        private double latitude;   // 纬度（GCJ-02坐标系）

        /**
         * 创建坐标点
         *
         * @param longitude 经度
         * @param latitude 纬度
         * @return Point对象
         */
        public static Point of(double longitude, double latitude) {
            return Point.builder()
                .longitude(longitude)
                .latitude(latitude)
                .build();
        }

        /**
         * 手动添加getter方法（Lombok编译问题临时方案）
         */
        public double getLongitude() { return longitude; }
        public double getLatitude() { return latitude; }

        /**
         * 手动添加builder方法（Lombok编译问题临时方案）
         */
        public static PointBuilder builder() {
            return new PointBuilder();
        }

        public static class PointBuilder {
            private double longitude;
            private double latitude;

            public PointBuilder longitude(double longitude) {
                this.longitude = longitude;
                return this;
            }

            public PointBuilder latitude(double latitude) {
                this.latitude = latitude;
                return this;
            }

            public Point build() {
                Point point = new Point();
                point.longitude = this.longitude;
                point.latitude = this.latitude;
                return point;
            }
        }

        @Override
        public String toString() {
            return String.format("(%.6f, %.6f)", longitude, latitude);
        }
    }
}
