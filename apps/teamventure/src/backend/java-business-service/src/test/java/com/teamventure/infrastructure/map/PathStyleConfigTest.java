package com.teamventure.infrastructure.map;

import com.teamventure.domain.valueobject.MapRequest.Point;
import com.teamventure.infrastructure.map.PathStyleConfig.PathSegment;
import com.teamventure.infrastructure.map.PathStyleConfig.PathStyle;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * PathStyleConfig 单元测试
 *
 * 测试路径样式生成、路径简化算法等
 *
 * @author TeamVenture
 * @since 2026-01-14
 */
class PathStyleConfigTest {

    private PathStyleConfig config;

    @BeforeEach
    void setUp() {
        config = new PathStyleConfig();

        // 使用反射设置配置值（模拟Spring注入）
        try {
            setField("defaultColor", "0x1890FF");
            setField("defaultWidth", 6);
            setField("defaultTransparency", 1.0);
        } catch (Exception e) {
            throw new RuntimeException("Failed to set config fields", e);
        }
    }

    /**
     * 测试1: 驾车路径样式
     *
     * 场景：生成蓝色粗线（驾车）
     */
    @Test
    @DisplayName("生成驾车路径样式（蓝色粗线）")
    void testGeneratePath_Driving() {
        List<Point> points = List.of(
            Point.of(116.397428, 39.90923),
            Point.of(116.404269, 39.915119),
            Point.of(116.386839, 39.915119)
        );

        String result = config.generatePathsParam(points, PathStyle.DRIVING);

        assertThat(result).isNotEmpty();
        assertThat(result).startsWith("6,0x1890FF,1.0:");  // 宽度6，蓝色，透明度1.0
        assertThat(result).contains("116.397428,39.909230");
        assertThat(result).contains(";");  // 坐标用分号分隔
    }

    /**
     * 测试2: 步行路径样式
     *
     * 场景：生成绿色中线（步行）
     */
    @Test
    @DisplayName("生成步行路径样式（绿色中线）")
    void testGeneratePath_Walking() {
        List<Point> points = List.of(
            Point.of(116.397, 39.909),
            Point.of(116.404, 39.915)
        );

        String result = config.generatePathsParam(points, PathStyle.WALKING);

        assertThat(result).isNotEmpty();
        assertThat(result).startsWith("4,0x52C41A,0.8:");  // 宽度4，绿色，透明度0.8
    }

    /**
     * 测试3: 骑行路径样式
     *
     * 场景：生成橙色中线（骑行）
     */
    @Test
    @DisplayName("生成骑行路径样式（橙色中线）")
    void testGeneratePath_Cycling() {
        List<Point> points = List.of(
            Point.of(121.473, 31.230),
            Point.of(121.480, 31.235)
        );

        String result = config.generatePathsParam(points, PathStyle.CYCLING);

        assertThat(result).isNotEmpty();
        assertThat(result).startsWith("5,0xFFA500,0.9:");  // 宽度5，橙色，透明度0.9
    }

    /**
     * 测试4: 公交路径样式
     *
     * 场景：生成紫色中线（公交）
     */
    @Test
    @DisplayName("生成公交路径样式（紫色中线）")
    void testGeneratePath_Transit() {
        List<Point> points = List.of(
            Point.of(116.397, 39.909),
            Point.of(116.404, 39.915)
        );

        String result = config.generatePathsParam(points, PathStyle.TRANSIT);

        assertThat(result).isNotEmpty();
        assertThat(result).startsWith("5,0x722ED1,0.9:");  // 宽度5，紫色，透明度0.9
    }

    /**
     * 测试5: 长路径简化（>50个点）
     *
     * 场景：100个点应简化到50个点以内
     */
    @Test
    @DisplayName("超过50点的路径应简化")
    void testSimplifyPolyline_LongPath() {
        // 生成100个测试点
        List<Point> points = IntStream.range(0, 100)
            .mapToObj(i -> Point.of(116.397 + i * 0.001, 39.909 + i * 0.001))
            .collect(Collectors.toList());

        String result = config.generatePathsParam(points, PathStyle.DRIVING);

        assertThat(result).isNotEmpty();

        // 提取坐标部分（去掉样式前缀）
        String coordsPart = result.split(":")[1];
        String[] coords = coordsPart.split(";");

        // 应简化到50个点以内（+1因为包含终点）
        assertThat(coords.length).isLessThanOrEqualTo(51);

        // 验证起点被保留
        assertThat(coords[0]).contains("116.397000,39.909000");

        // 验证终点被保留（100个点，索引99，坐标为116.397 + 99*0.001 = 116.496, 39.909 + 99*0.001 = 40.008）
        assertThat(coords[coords.length - 1]).contains("116.496000,40.008000");
    }

    /**
     * 测试6: 短路径不简化（<50个点）
     *
     * 场景：20个点应全部保留
     */
    @Test
    @DisplayName("少于50点的路径不简化")
    void testSimplifyPolyline_ShortPath() {
        // 生成20个测试点
        List<Point> points = IntStream.range(0, 20)
            .mapToObj(i -> Point.of(116.397 + i * 0.001, 39.909 + i * 0.001))
            .collect(Collectors.toList());

        String result = config.generatePathsParam(points, PathStyle.DRIVING);

        // 提取坐标部分
        String coordsPart = result.split(":")[1];
        String[] coords = coordsPart.split(";");

        // 应保留所有20个点
        assertThat(coords).hasSize(20);
    }

    /**
     * 测试7: URL编码正确性
     *
     * 场景：生成的参数应符合URL编码规范
     */
    @Test
    @DisplayName("路径参数应符合URL编码规范")
    void testPathFormat_UrlEncoding() {
        List<Point> points = List.of(
            Point.of(116.397, 39.909),
            Point.of(116.404, 39.915)
        );

        String result = config.generatePathsParam(points, PathStyle.DRIVING);

        // 验证不包含URL不安全字符
        assertThat(result).doesNotContain(" ");    // 无空格
        assertThat(result).doesNotContain("\n");   // 无换行
        assertThat(result).doesNotContain("\t");   // 无tab

        // 验证包含正确的分隔符
        assertThat(result).contains(":");  // 样式和坐标用冒号分隔
        assertThat(result).contains(";");  // 坐标用分号分隔
        assertThat(result).contains(",");  // 经纬度用逗号分隔
    }

    /**
     * 测试8: 空列表和少于2个点的处理
     *
     * 场景：边界条件测试
     */
    @Test
    @DisplayName("少于2个点应返回空字符串")
    void testGeneratePath_InsufficientPoints() {
        assertThat(config.generatePathsParam(null, PathStyle.DRIVING)).isEmpty();
        assertThat(config.generatePathsParam(new ArrayList<>(), PathStyle.DRIVING)).isEmpty();
        assertThat(config.generatePathsParam(List.of(Point.of(116.397, 39.909)), PathStyle.DRIVING)).isEmpty();
    }

    /**
     * 测试9: 默认样式参数
     *
     * 场景：使用配置的默认样式生成路径
     */
    @Test
    @DisplayName("使用默认样式生成路径")
    void testGenerateDefaultPathsParam() {
        List<Point> points = List.of(
            Point.of(116.397, 39.909),
            Point.of(116.404, 39.915)
        );

        String result = config.generateDefaultPathsParam(points);

        assertThat(result).isNotEmpty();
        assertThat(result).startsWith("6,0x1890FF,1.0:");  // 使用配置的默认值
    }

    /**
     * 测试10: 多段路径生成（不同颜色）
     *
     * 场景：复杂路线包含多段，每段使用不同样式
     */
    @Test
    @DisplayName("生成多段不同样式的路径")
    void testGenerateMultiSegmentPaths() {
        // 第一段：驾车（蓝色）
        PathSegment segment1 = PathSegment.builder()
            .points(List.of(
                Point.of(116.397, 39.909),
                Point.of(116.400, 39.912)
            ))
            .style(PathStyle.DRIVING)
            .build();

        // 第二段：步行（绿色）
        PathSegment segment2 = PathSegment.builder()
            .points(List.of(
                Point.of(116.400, 39.912),
                Point.of(116.404, 39.915)
            ))
            .style(PathStyle.WALKING)
            .build();

        String result = config.generateMultiSegmentPaths(List.of(segment1, segment2));

        assertThat(result).isNotEmpty();
        assertThat(result).contains("|");  // 多段路径用|分隔

        String[] segments = result.split("\\|");
        assertThat(segments).hasSize(2);

        // 验证第一段是驾车样式
        assertThat(segments[0]).startsWith("6,0x1890FF,1.0:");

        // 验证第二段是步行样式
        assertThat(segments[1]).startsWith("4,0x52C41A,0.8:");
    }

    /**
     * 测试11: 路径简化算法保证终点
     *
     * 场景：无论如何简化，终点必须被保留
     */
    @Test
    @DisplayName("路径简化必须保留终点")
    void testSimplifyPath_PreservesEndpoint() {
        // 生成80个点
        List<Point> points = IntStream.range(0, 80)
            .mapToObj(i -> Point.of(116.397 + i * 0.001, 39.909 + i * 0.001))
            .collect(Collectors.toList());

        Point lastPoint = points.get(points.size() - 1);

        String result = config.generatePathsParam(points, PathStyle.DRIVING);

        // 验证终点坐标在结果中
        String lastCoord = String.format("%.6f,%.6f",
            lastPoint.getLongitude(),
            lastPoint.getLatitude()
        );
        assertThat(result).endsWith(lastCoord);
    }

    // ==================== 辅助方法 ====================

    /**
     * 通过反射设置private字段（模拟Spring @Value注入）
     */
    private void setField(String fieldName, Object value) throws Exception {
        java.lang.reflect.Field field = PathStyleConfig.class.getDeclaredField(fieldName);
        field.setAccessible(true);
        field.set(config, value);
    }
}
