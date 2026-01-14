package com.teamventure.infrastructure.map;

import com.teamventure.domain.valueobject.MapRequest.Point;
import com.teamventure.domain.valueobject.MapSizePreset;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * ZoomCalculator单元测试
 *
 * @author TeamVenture
 * @since 2026-01-14
 */
class ZoomCalculatorTest {

    private ZoomCalculator calculator;

    @BeforeEach
    void setUp() {
        calculator = new ZoomCalculator();
    }

    @Test
    @DisplayName("单点地图应返回默认zoom=15")
    void testSinglePoint() {
        List<Point> points = Collections.singletonList(
            Point.of(121.473701, 31.230416)  // 上海人民广场
        );

        int zoom = calculator.calculateOptimalZoom(points, MapSizePreset.DETAIL);

        assertEquals(15, zoom, "单点地图应返回街区级别zoom");
    }

    @Test
    @DisplayName("相邻建筑（<100m，跨度<0.001度）应返回zoom=17")
    void testVeryClosePoints() {
        List<Point> points = Arrays.asList(
            Point.of(121.473701, 31.230416),  // 人民广场
            Point.of(121.473801, 31.230516)   // 100米外
        );

        int zoom = calculator.calculateOptimalZoom(points, MapSizePreset.DETAIL);

        assertEquals(17, zoom, "相邻建筑应返回最高zoom级别");
    }

    @Test
    @DisplayName("街区级别（1-3km，跨度0.01-0.03度）应返回zoom=15")
    void testStreetLevel() {
        List<Point> points = Arrays.asList(
            Point.of(121.473701, 31.230416),  // 人民广场
            Point.of(121.483701, 31.240416)   // 约1.5km外
        );

        int zoom = calculator.calculateOptimalZoom(points, MapSizePreset.DETAIL);

        assertEquals(15, zoom, "街区级别应返回zoom=15");
    }

    @Test
    @DisplayName("同城路线（10km，跨度0.1度）应返回zoom=12")
    void testCityLevel() {
        List<Point> points = Arrays.asList(
            Point.of(121.473701, 31.230416),  // 上海人民广场
            Point.of(121.573701, 31.230416)   // 约10km外
        );

        int zoom = calculator.calculateOptimalZoom(points, MapSizePreset.DETAIL);

        assertEquals(12, zoom, "同城路线应返回zoom=12");
    }

    @Test
    @DisplayName("跨市路线（100km，跨度1度）应返回zoom=8")
    void testProvinceLevel() {
        List<Point> points = Arrays.asList(
            Point.of(121.473701, 31.230416),  // 上海
            Point.of(120.153576, 30.287459)   // 杭州（约150km）
        );

        int zoom = calculator.calculateOptimalZoom(points, MapSizePreset.DETAIL);

        assertEquals(8, zoom, "跨市路线应返回zoom=8");
    }

    @Test
    @DisplayName("跨省路线（>1000km，跨度>10度）应返回zoom=3")
    void testCountryLevel() {
        List<Point> points = Arrays.asList(
            Point.of(121.473701, 31.230416),  // 上海
            Point.of(113.264385, 23.129110)   // 广州（约1200km）
        );

        int zoom = calculator.calculateOptimalZoom(points, MapSizePreset.DETAIL);

        assertEquals(3, zoom, "跨省路线应返回最低zoom级别");
    }

    @Test
    @DisplayName("缩略图应降低1级zoom")
    void testThumbnailSizeAdjustment() {
        List<Point> points = Arrays.asList(
            Point.of(121.473701, 31.230416),
            Point.of(121.483701, 31.240416)   // 约1.5km
        );

        // 详情页zoom应该是15
        int detailZoom = calculator.calculateOptimalZoom(points, MapSizePreset.DETAIL);
        assertEquals(15, detailZoom);

        // 缩略图zoom应该是14（降低1级）
        int thumbnailZoom = calculator.calculateOptimalZoom(points, MapSizePreset.THUMBNAIL);
        assertEquals(14, thumbnailZoom, "缩略图应降低1级zoom");
    }

    @Test
    @DisplayName("分享图应提高1级zoom")
    void testShareSizeAdjustment() {
        List<Point> points = Arrays.asList(
            Point.of(121.473701, 31.230416),
            Point.of(121.483701, 31.240416)   // 约1.5km
        );

        // 详情页zoom应该是15
        int detailZoom = calculator.calculateOptimalZoom(points, MapSizePreset.DETAIL);
        assertEquals(15, detailZoom);

        // 分享图zoom应该是16（提高1级）
        int shareZoom = calculator.calculateOptimalZoom(points, MapSizePreset.SHARE);
        assertEquals(16, shareZoom, "分享图应提高1级zoom");
    }

    @Test
    @DisplayName("空列表应返回默认zoom=12")
    void testEmptyPoints() {
        List<Point> points = Collections.emptyList();

        int zoom = calculator.calculateOptimalZoom(points, MapSizePreset.DETAIL);

        assertEquals(12, zoom, "空列表应返回默认zoom");
    }

    @Test
    @DisplayName("null列表应返回默认zoom=12")
    void testNullPoints() {
        int zoom = calculator.calculateOptimalZoom(null, MapSizePreset.DETAIL);

        assertEquals(12, zoom, "null列表应返回默认zoom");
    }

    @Test
    @DisplayName("zoom应限制在3-18范围内")
    void testZoomBoundary() {
        // 极端近距离（理论zoom可能>18）
        List<Point> veryClose = Arrays.asList(
            Point.of(121.473701, 31.230416),
            Point.of(121.473702, 31.230417)   // 约10米
        );

        int zoom = calculator.calculateOptimalZoom(veryClose, MapSizePreset.SHARE);
        assertTrue(zoom >= 3 && zoom <= 18, "zoom应在3-18范围内");
    }

    @Test
    @DisplayName("多点路线应计算正确的包围盒和zoom")
    void testMultiplePoints() {
        List<Point> points = Arrays.asList(
            Point.of(121.473701, 31.230416),  // 上海人民广场
            Point.of(121.523701, 31.280416),  // 东北5km
            Point.of(121.423701, 31.180416),  // 西南5km
            Point.of(121.473701, 31.230416)   // 回到起点
        );

        int zoom = calculator.calculateOptimalZoom(points, MapSizePreset.DETAIL);

        // 包围盒约0.1度x0.1度，应该是zoom=12（同城级别）
        assertEquals(12, zoom, "多点路线应根据最大跨度计算zoom");
    }
}
