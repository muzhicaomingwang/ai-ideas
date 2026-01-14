package com.teamventure.infrastructure.map;

import com.teamventure.domain.valueobject.MapRequest.Point;
import com.teamventure.infrastructure.map.MarkerStyleConfig.MarkerStyle;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * MarkerStyleConfig 单元测试
 *
 * 测试地图标注样式生成的各种场景
 *
 * @author TeamVenture
 * @since 2026-01-14
 */
class MarkerStyleConfigTest {

    private MarkerStyleConfig config;

    @BeforeEach
    void setUp() {
        config = new MarkerStyleConfig();

        // 使用反射设置配置值（模拟Spring注入）
        try {
            setField("startColor", "0x00FF00");
            setField("endColor", "0xFF0000");
            setField("waypointColor", "0x1890FF");
        } catch (Exception e) {
            throw new RuntimeException("Failed to set config fields", e);
        }
    }

    /**
     * 测试1: 起点+终点+途经点完整路线
     *
     * 场景：3个点（起点→途经点→终点）
     */
    @Test
    @DisplayName("生成起点+终点+途经点的标注参数")
    void testGenerateMarkers_StartEndWaypoint() {
        List<Point> points = List.of(
            Point.of(116.397428, 39.90923),   // 天安门（起点）
            Point.of(116.404269, 39.915119),  // 故宫（途经点）
            Point.of(116.386839, 39.915119)   // 景山公园（终点）
        );

        String result = config.generateMarkersParam(points);

        assertThat(result).isNotEmpty();
        assertThat(result).contains("large,0x00FF00,S:");  // 起点：绿色大标，标签S
        assertThat(result).contains("mid,0x1890FF,:");     // 途经点：蓝色中标，无标签
        assertThat(result).contains("large,0xFF0000,E:");  // 终点：红色大标，标签E

        // 验证坐标格式（6位小数）
        assertThat(result).contains("116.397428,39.909230");
        assertThat(result).contains("116.404269,39.915119");
        assertThat(result).contains("116.386839,39.915119");

        // 验证分隔符
        assertThat(result.split("\\|")).hasSize(3);
    }

    /**
     * 测试2: 仅起点和终点（2个点）
     *
     * 场景：最简单的路线，只有起点和终点
     */
    @Test
    @DisplayName("生成仅起点和终点的标注参数")
    void testGenerateMarkers_OnlyStartEnd() {
        List<Point> points = List.of(
            Point.of(116.397428, 39.90923),   // 起点
            Point.of(116.404269, 39.915119)   // 终点
        );

        String result = config.generateMarkersParam(points);

        assertThat(result).isNotEmpty();
        assertThat(result).contains("large,0x00FF00,S:");  // 起点
        assertThat(result).contains("large,0xFF0000,E:");  // 终点
        assertThat(result.split("\\|")).hasSize(2);

        // 不应包含途经点样式
        assertThat(result).doesNotContain("mid,0x1890FF");
    }

    /**
     * 测试3: 单个点（无路线）
     *
     * 场景：只有一个点，应该同时作为起点和终点
     */
    @Test
    @DisplayName("单个点应作为起点处理")
    void testGenerateMarkers_SinglePoint() {
        List<Point> points = List.of(
            Point.of(116.397428, 39.90923)   // 单点
        );

        String result = config.generateMarkersParam(points);

        assertThat(result).isNotEmpty();
        assertThat(result).contains("large,0x00FF00,S:");  // 起点样式
        assertThat(result).doesNotContain("E:");            // 不应有终点标签

        // 应只有1个标注
        assertThat(result.split("\\|")).hasSize(1);
    }

    /**
     * 测试4: 空列表和null处理
     *
     * 场景：边界条件测试
     */
    @Test
    @DisplayName("空列表或null应返回空字符串")
    void testGenerateMarkers_Empty() {
        assertThat(config.generateMarkersParam(null)).isEmpty();
        assertThat(config.generateMarkersParam(new ArrayList<>())).isEmpty();
    }

    /**
     * 测试5: 供应商标注生成
     *
     * 场景：为供应商POI生成橙色小标
     */
    @Test
    @DisplayName("生成供应商标注（橙色小标）")
    void testGenerateMarkers_WithSuppliers() {
        Point supplierPoint = Point.of(116.397, 39.909);

        String result = config.generateSupplierMarker(supplierPoint);

        assertThat(result).isNotEmpty();
        assertThat(result).contains("small,0xFFA500,$:");  // 橙色小标，标签$
        assertThat(result).contains("116.397000,39.909000");
    }

    /**
     * 测试6: 所有标注类型的格式验证
     *
     * 场景：验证每种标注类型的size、color、label格式正确
     */
    @Test
    @DisplayName("验证所有标注类型格式正确性")
    void testFormatMarker_AllTypes() {
        // 验证枚举值
        assertThat(MarkerStyle.START.getLabel()).isEqualTo("S");
        assertThat(MarkerStyle.START.getDefaultColor()).isEqualTo("0x00FF00");
        assertThat(MarkerStyle.START.getSize()).isEqualTo("large");

        assertThat(MarkerStyle.END.getLabel()).isEqualTo("E");
        assertThat(MarkerStyle.END.getDefaultColor()).isEqualTo("0xFF0000");
        assertThat(MarkerStyle.END.getSize()).isEqualTo("large");

        assertThat(MarkerStyle.WAYPOINT.getLabel()).isEmpty();
        assertThat(MarkerStyle.WAYPOINT.getDefaultColor()).isEqualTo("0x1890FF");
        assertThat(MarkerStyle.WAYPOINT.getSize()).isEqualTo("mid");

        assertThat(MarkerStyle.SUPPLIER.getLabel()).isEqualTo("$");
        assertThat(MarkerStyle.SUPPLIER.getDefaultColor()).isEqualTo("0xFFA500");
        assertThat(MarkerStyle.SUPPLIER.getSize()).isEqualTo("small");
    }

    /**
     * 测试7: 颜色格式验证（十六进制）
     *
     * 场景：验证颜色值是否符合高德API要求的0xRRGGBB格式
     */
    @Test
    @DisplayName("颜色格式应为0xRRGGBB")
    void testColorFormat_HexValidation() {
        List<Point> points = List.of(
            Point.of(116.397, 39.909),
            Point.of(116.404, 39.915)
        );

        String result = config.generateMarkersParam(points);

        // 验证颜色格式（0x + 6位十六进制）
        assertThat(result).containsPattern("0x[0-9A-F]{6}");

        // 验证不包含非法颜色格式
        assertThat(result).doesNotContain("#");      // 不是CSS格式
        assertThat(result).doesNotContain("rgb(");   // 不是rgb格式
    }

    /**
     * 测试8: 自定义标签标注
     *
     * 场景：生成带自定义标签和颜色的标注
     */
    @Test
    @DisplayName("生成带自定义标签的标注")
    void testGenerateCustomMarker() {
        Point point = Point.of(121.473701, 31.230416);

        String result = config.generateCustomMarker(point, "A", "0xFF00FF");

        assertThat(result).isNotEmpty();
        assertThat(result).contains("mid,0xFF00FF,A:");
        assertThat(result).contains("121.473701,31.230416");

        // 测试null参数（应使用默认值）
        String resultWithDefaults = config.generateCustomMarker(point, null, null);
        assertThat(resultWithDefaults).contains("mid,0x1890FF,:");  // 默认颜色和空标签
    }

    /**
     * 测试9: 多途经点路线
     *
     * 场景：起点 + 5个途经点 + 终点
     */
    @Test
    @DisplayName("多途经点路线标注生成")
    void testGenerateMarkers_MultipleWaypoints() {
        List<Point> points = new ArrayList<>();
        points.add(Point.of(116.397, 39.909));  // 起点

        // 添加5个途经点
        for (int i = 1; i <= 5; i++) {
            points.add(Point.of(116.397 + i * 0.01, 39.909 + i * 0.01));
        }

        points.add(Point.of(116.450, 39.960));  // 终点

        String result = config.generateMarkersParam(points);

        String[] markers = result.split("\\|");
        assertThat(markers).hasSize(7);

        // 验证第一个是起点
        assertThat(markers[0]).contains("S:");

        // 验证中间都是途经点
        for (int i = 1; i < markers.length - 1; i++) {
            assertThat(markers[i]).contains("mid,0x1890FF,:");
        }

        // 验证最后一个是终点
        assertThat(markers[markers.length - 1]).contains("E:");
    }

    // ==================== 辅助方法 ====================

    /**
     * 通过反射设置private字段（模拟Spring @Value注入）
     */
    private void setField(String fieldName, Object value) throws Exception {
        java.lang.reflect.Field field = MarkerStyleConfig.class.getDeclaredField(fieldName);
        field.setAccessible(true);
        field.set(config, value);
    }
}
