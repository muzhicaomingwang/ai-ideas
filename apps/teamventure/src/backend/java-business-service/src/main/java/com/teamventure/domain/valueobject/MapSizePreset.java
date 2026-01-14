package com.teamventure.domain.valueobject;

/**
 * 地图尺寸预设枚举
 *
 * 定义不同使用场景下的标准地图尺寸规格
 *
 * @author TeamVenture
 * @since 2026-01-14
 */
public enum MapSizePreset {
    /**
     * 详情页主地图
     * 用于方案详情页展示完整路线
     */
    DETAIL(750, 520, "detail"),

    /**
     * 列表缩略图
     * 用于方案列表页快速预览
     */
    THUMBNAIL(375, 200, "thumbnail"),

    /**
     * 分享图
     * 用于生成社交媒体分享图片（适配微信朋友圈）
     */
    SHARE(1200, 800, "share"),

    /**
     * 供应商位置图
     * 用于供应商详情页展示位置
     */
    SUPPLIER(600, 400, "supplier");

    private final int width;
    private final int height;
    private final String sceneName;

    MapSizePreset(int width, int height, String sceneName) {
        this.width = width;
        this.height = height;
        this.sceneName = sceneName;
    }

    /**
     * 获取地图宽度（像素）
     */
    public int getWidth() {
        return width;
    }

    /**
     * 获取地图高度（像素）
     */
    public int getHeight() {
        return height;
    }

    /**
     * 获取场景名称
     */
    public String getSceneName() {
        return sceneName;
    }

    /**
     * 转换为高德地图API的size参数格式
     *
     * @return 格式：widthxheight（例如：750x520）
     */
    public String toApiParam() {
        return width + "x" + height;
    }

    /**
     * 校验尺寸是否在API允许范围内
     * 高德地图v3最大支持1024x1024，v5支持2048x2048
     *
     * @param apiVersion API版本（v3或v5）
     * @return true表示尺寸合法
     */
    public boolean isValid(String apiVersion) {
        int maxSize = "v5".equals(apiVersion) ? 2048 : 1024;
        return width <= maxSize && height <= maxSize;
    }

    /**
     * 根据场景名称查找对应的尺寸预设
     *
     * @param sceneName 场景名称（detail/thumbnail/share/supplier）
     * @return MapSizePreset枚举值
     * @throws IllegalArgumentException 如果场景名称不存在
     */
    public static MapSizePreset fromSceneName(String sceneName) {
        for (MapSizePreset preset : values()) {
            if (preset.sceneName.equalsIgnoreCase(sceneName)) {
                return preset;
            }
        }
        throw new IllegalArgumentException("Unknown scene name: " + sceneName);
    }

    /**
     * 估算该尺寸地图的文件大小（PNG格式）
     *
     * @return 估算文件大小（KB）
     */
    public int estimatedSizeKB() {
        // 经验值：PNG格式约0.3KB/像素（包含标注和路径）
        int pixels = width * height;
        return (int) (pixels * 0.3 / 1024);
    }

    @Override
    public String toString() {
        return String.format("%s(%dx%d, ~%dKB)",
            sceneName, width, height, estimatedSizeKB());
    }
}
