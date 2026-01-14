package com.teamventure.infrastructure.map;

import org.springframework.stereotype.Component;

import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 城市名称提取工具
 *
 * 从地址文本中提取城市名称，用于判断跨城/周边游路线
 *
 * 支持格式：
 * - 标准格式："浙江省杭州市西湖区" → "杭州市"
 * - 无省份："杭州市西湖区" → "杭州市"
 * - 直辖市："上海市黄浦区" → "上海市"
 * - 自治区："新疆维吾尔自治区乌鲁木齐市" → "乌鲁木齐市"
 * - 自治州："云南省西双版纳傣族自治州" → "西双版纳傣族自治州"
 *
 * @author TeamVenture
 * @since 2026-01-14
 */
@Component
public class CityNameExtractor {

    /**
     * 城市名称匹配正则
     *
     * 匹配规则：
     * - XX市（如"杭州市"、"乌鲁木齐市"）
     * - XX自治州（如"西双版纳傣族自治州"）
     * - XX地区（如"阿里地区"）
     * - XX盟（如"锡林郭勒盟"）
     */
    private static final Pattern CITY_PATTERN = Pattern.compile(
        "([\\u4e00-\\u9fa5]+?(?:市|自治州|地区|盟))"
    );

    /**
     * 省份前缀匹配正则（用于规范化）
     *
     * 匹配：XX省、XX自治区、XX特别行政区
     */
    private static final Pattern PROVINCE_PREFIX_PATTERN = Pattern.compile(
        "^(.+?(?:省|自治区|特别行政区))"
    );

    /**
     * 从地址文本中提取城市名
     *
     * 示例：
     * - "浙江省杭州市西湖区莫干山路" → "杭州市"
     * - "上海市黄浦区人民广场" → "上海市"
     * - "新疆维吾尔自治区乌鲁木齐市" → "乌鲁木齐市"
     * - "莫干山风景区" → Optional.empty()
     *
     * @param address 地址文本
     * @return 城市名（如"杭州市"），未提取到则返回Optional.empty()
     */
    public static Optional<String> extractCityFromAddress(String address) {
        if (address == null || address.isBlank()) {
            return Optional.empty();
        }

        // 先去除省份前缀，再提取城市名
        String normalized = PROVINCE_PREFIX_PATTERN.matcher(address)
            .replaceFirst("")
            .trim();

        Matcher matcher = CITY_PATTERN.matcher(normalized);
        if (matcher.find()) {
            return Optional.of(matcher.group(1));
        }

        return Optional.empty();
    }

    /**
     * 规范化城市名（去除省份前缀）
     *
     * 示例：
     * - "浙江省杭州市" → "杭州市"
     * - "杭州市" → "杭州市"（无变化）
     *
     * @param cityName 可能包含省份前缀的城市名
     * @return 规范化后的城市名
     */
    public static String normalizeCityName(String cityName) {
        if (cityName == null || cityName.isBlank()) {
            return cityName;
        }

        return PROVINCE_PREFIX_PATTERN.matcher(cityName)
            .replaceFirst("")
            .trim();
    }

    /**
     * 批量提取城市名（去重）
     *
     * 从多个地址中提取唯一的城市集合
     *
     * @param addresses 地址列表
     * @return 城市名集合
     */
    public static java.util.Set<String> extractCities(java.util.List<String> addresses) {
        if (addresses == null || addresses.isEmpty()) {
            return java.util.Set.of();
        }

        return addresses.stream()
            .map(CityNameExtractor::extractCityFromAddress)
            .filter(Optional::isPresent)
            .map(Optional::get)
            .map(CityNameExtractor::normalizeCityName)
            .collect(java.util.stream.Collectors.toSet());
    }

    /**
     * 判断两个地址是否属于同一城市
     *
     * @param address1 地址1
     * @param address2 地址2
     * @return true表示同城
     */
    public static boolean isSameCity(String address1, String address2) {
        Optional<String> city1 = extractCityFromAddress(address1);
        Optional<String> city2 = extractCityFromAddress(address2);

        if (city1.isEmpty() || city2.isEmpty()) {
            return false;
        }

        String normalizedCity1 = normalizeCityName(city1.get());
        String normalizedCity2 = normalizeCityName(city2.get());

        return normalizedCity1.equals(normalizedCity2);
    }

    /**
     * 验证城市名是否合法
     *
     * 合法标准：
     * - 长度2-10个汉字
     * - 以"市"、"自治州"、"地区"、"盟"结尾
     *
     * @param cityName 城市名
     * @return true表示合法
     */
    public static boolean isValidCityName(String cityName) {
        if (cityName == null || cityName.isBlank()) {
            return false;
        }

        // 长度检查
        if (cityName.length() < 2 || cityName.length() > 10) {
            return false;
        }

        // 格式检查
        return cityName.matches("[\\u4e00-\\u9fa5]+?(?:市|自治州|地区|盟)");
    }
}
