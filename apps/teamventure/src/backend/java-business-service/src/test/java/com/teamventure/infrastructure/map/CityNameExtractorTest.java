package com.teamventure.infrastructure.map;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Optional;
import java.util.Set;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * CityNameExtractor 单元测试
 *
 * 测试城市名提取的各种地址格式
 *
 * @author TeamVenture
 * @since 2026-01-14
 */
class CityNameExtractorTest {

    /**
     * 测试1: 标准格式（省份+城市+区县）
     */
    @Test
    @DisplayName("标准格式应正确提取城市名")
    void testExtractCity_StandardFormat() {
        Optional<String> result = CityNameExtractor.extractCityFromAddress("浙江省杭州市西湖区莫干山路");

        assertThat(result).isPresent();
        assertThat(result.get()).isEqualTo("杭州市");
    }

    /**
     * 测试2: 无省份前缀
     */
    @Test
    @DisplayName("无省份前缀应正确提取城市名")
    void testExtractCity_NoProvince() {
        Optional<String> result = CityNameExtractor.extractCityFromAddress("杭州市西湖区文二路");

        assertThat(result).isPresent();
        assertThat(result.get()).isEqualTo("杭州市");
    }

    /**
     * 测试3: 直辖市
     */
    @Test
    @DisplayName("直辖市应正确提取")
    void testExtractCity_Municipality() {
        assertThat(CityNameExtractor.extractCityFromAddress("上海市黄浦区人民广场").get())
            .isEqualTo("上海市");

        assertThat(CityNameExtractor.extractCityFromAddress("北京市朝阳区国贸").get())
            .isEqualTo("北京市");

        assertThat(CityNameExtractor.extractCityFromAddress("重庆市渝中区解放碑").get())
            .isEqualTo("重庆市");

        assertThat(CityNameExtractor.extractCityFromAddress("天津市和平区").get())
            .isEqualTo("天津市");
    }

    /**
     * 测试4: 自治区
     */
    @Test
    @DisplayName("自治区城市应正确提取")
    void testExtractCity_AutonomousRegion() {
        Optional<String> result = CityNameExtractor.extractCityFromAddress(
            "新疆维吾尔自治区乌鲁木齐市天山区"
        );

        assertThat(result).isPresent();
        assertThat(result.get()).isEqualTo("乌鲁木齐市");
    }

    /**
     * 测试5: 自治州
     */
    @Test
    @DisplayName("自治州应正确提取")
    void testExtractCity_AutonomousPrefecture() {
        Optional<String> result = CityNameExtractor.extractCityFromAddress(
            "云南省西双版纳傣族自治州景洪市"
        );

        assertThat(result).isPresent();
        assertThat(result.get()).isEqualTo("西双版纳傣族自治州");
    }

    /**
     * 测试6: 地区/盟
     */
    @Test
    @DisplayName("地区和盟应正确提取")
    void testExtractCity_Prefecture() {
        assertThat(CityNameExtractor.extractCityFromAddress("西藏自治区阿里地区").get())
            .isEqualTo("阿里地区");

        assertThat(CityNameExtractor.extractCityFromAddress("内蒙古自治区锡林郭勒盟").get())
            .isEqualTo("锡林郭勒盟");
    }

    /**
     * 测试7: 只有景点名（无城市信息）
     */
    @Test
    @DisplayName("无城市信息应返回empty")
    void testExtractCity_NoCity() {
        assertThat(CityNameExtractor.extractCityFromAddress("莫干山风景区")).isEmpty();
        assertThat(CityNameExtractor.extractCityFromAddress("西湖")).isEmpty();
        assertThat(CityNameExtractor.extractCityFromAddress("灵隐寺")).isEmpty();
    }

    /**
     * 测试8: 空字符串和null处理
     */
    @Test
    @DisplayName("空字符串和null应返回empty")
    void testExtractCity_EmptyOrNull() {
        assertThat(CityNameExtractor.extractCityFromAddress(null)).isEmpty();
        assertThat(CityNameExtractor.extractCityFromAddress("")).isEmpty();
        assertThat(CityNameExtractor.extractCityFromAddress("   ")).isEmpty();
    }

    /**
     * 测试9: 规范化城市名（去除省份前缀）
     */
    @Test
    @DisplayName("规范化应去除省份前缀")
    void testNormalizeCityName() {
        assertThat(CityNameExtractor.normalizeCityName("浙江省杭州市"))
            .isEqualTo("杭州市");

        assertThat(CityNameExtractor.normalizeCityName("新疆维吾尔自治区乌鲁木齐市"))
            .isEqualTo("乌鲁木齐市");

        assertThat(CityNameExtractor.normalizeCityName("杭州市"))
            .isEqualTo("杭州市");  // 无省份前缀，保持不变

        assertThat(CityNameExtractor.normalizeCityName(""))
            .isEqualTo("");
    }

    /**
     * 测试10: 批量提取城市名（去重）
     */
    @Test
    @DisplayName("批量提取应去重并规范化")
    void testExtractCities_Batch() {
        List<String> addresses = List.of(
            "浙江省杭州市西湖区",
            "杭州市上城区",      // 重复城市
            "浙江省宁波市海曙区",
            "莫干山风景区",      // 无城市信息
            "上海市黄浦区"
        );

        Set<String> cities = CityNameExtractor.extractCities(addresses);

        assertThat(cities).hasSize(3);
        assertThat(cities).containsExactlyInAnyOrder("杭州市", "宁波市", "上海市");
    }

    /**
     * 测试11: 判断同城
     */
    @Test
    @DisplayName("同城判断应正确")
    void testIsSameCity() {
        assertThat(CityNameExtractor.isSameCity(
            "浙江省杭州市西湖区",
            "杭州市上城区"
        )).isTrue();

        assertThat(CityNameExtractor.isSameCity(
            "浙江省杭州市西湖区",
            "浙江省宁波市海曙区"
        )).isFalse();

        assertThat(CityNameExtractor.isSameCity(
            "莫干山风景区",
            "西湖"
        )).isFalse();  // 两者都无城市信息
    }

    /**
     * 测试12: 验证城市名合法性
     */
    @Test
    @DisplayName("城市名验证应符合规则")
    void testIsValidCityName() {
        assertThat(CityNameExtractor.isValidCityName("杭州市")).isTrue();
        assertThat(CityNameExtractor.isValidCityName("西双版纳傣族自治州")).isTrue();
        assertThat(CityNameExtractor.isValidCityName("阿里地区")).isTrue();

        assertThat(CityNameExtractor.isValidCityName("")).isFalse();
        assertThat(CityNameExtractor.isValidCityName("杭州")).isFalse();  // 无"市"后缀
        assertThat(CityNameExtractor.isValidCityName("x市")).isFalse();   // 太短
    }
}
