package com.teamventure.app.support;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class ItineraryMarkdownSanitizerTest {

    @Test
    void sanitizeDraftItineraryMarkdown_shouldStripDayDates_andDropPlaceholderTimeRows() {
        String input = """
                # 行程安排
                > 版本: v1

                ## Day 1（2023-10-01）
                - 09:00 - 10:00 | 抵达 | 嘉兴站 |
                - - | 嘉兴站 |  |
                - — | 月河历史街区 |  |
                - - - | 天主堂 |  |
                """;

        String out = ItineraryMarkdownSanitizer.sanitizeDraftItineraryMarkdown(input);
        assertFalse(out.contains("> 版本:"));
        assertFalse(out.contains("（2023-10-01）"));
        assertFalse(out.contains("- - | 嘉兴站"));
        assertFalse(out.contains("- — | 月河历史街区"));
        assertFalse(out.contains("- - - | 天主堂"));
        assertTrue(out.contains("## Day 1"));
        assertTrue(out.contains("- 09:00 - 10:00"));
    }

    @Test
    void sanitizeDraftItineraryMarkdown_shouldApplyToAllDays() {
        String input = """
                # 行程安排
                > 版本: v1

                ## Day 1（2023-12-01）
                - 09:00 - 10:00 | 抵达并办理入住 | 海花岛·欧堡酒店 |
                - 10:00 - 12:00 | 自由活动/休整 | 欧堡酒店/海花岛 |
                - 13:00 - 17:30 | 水上王国游玩 | 海花岛·水上王国 |
                - 18:00 - 19:30 | 晚餐 | 风情饮食街 |
                - 19:45 - 20:00 | 灯光秀观赏 | 婚礼庄园 |
                - - | 海花岛·欧堡酒店 |  |
                - - | 欧堡酒店/海花岛 |  |
                - - | 海花岛·水上王国 |  |
                - - | 风情饮食街 |  |
                - - | 婚礼庄园 |  |

                ## Day 2（2023-12-02）
                - 09:00 - 10:00 | 酒店自助早餐 | 欧堡酒店 |
                - 10:00 - 17:00 | 海洋乐园全日游 | 海花岛·海洋乐园 |
                - 18:00 - 20:00 | 温泉放松 | 五国温泉城 |
                - - | 欧堡酒店 |  |
                - - | 海花岛·海洋乐园 |  |
                - - | 五国温泉城 |  |

                ## Day 3（2023-12-03）
                - 09:00 - 10:00 | 早餐（睡到自然醒后） | 欧堡酒店 |
                - 10:00 - 12:00 | 拍照打卡四大城堡 | 欧堡酒店 |
                - 12:00 - 12:30 | 退房准备 | 欧堡酒店 |
                - 13:00 - 15:00 | 参观（可选） | 博物馆群 |
                - 15:00 - 17:00 | 返程 | 海花岛 |
                - 17:00 - 18:00 | 欧堡酒店 |  |
                - 18:00 - 19:00 | 博物馆群 |  |
                - 19:00 - 20:00 | 海花岛 |  |
                """;

        String out = ItineraryMarkdownSanitizer.sanitizeDraftItineraryMarkdown(input);
        // Dates stripped for every day heading.
        assertTrue(out.contains("## Day 1\n"));
        assertTrue(out.contains("## Day 2\n"));
        assertTrue(out.contains("## Day 3\n"));
        assertFalse(out.contains("（2023-12-01）"));
        assertFalse(out.contains("（2023-12-02）"));
        assertFalse(out.contains("（2023-12-03）"));

        // Placeholder time rows dropped for every day.
        assertFalse(out.contains("- - | 海花岛·欧堡酒店"));
        assertFalse(out.contains("- - | 婚礼庄园"));
        assertFalse(out.contains("- - | 欧堡酒店 |"));
        assertFalse(out.contains("- - | 五国温泉城"));
        assertFalse(out.contains("- - | 海花岛·海洋乐园"));

        // Keep rows that still have a valid time range (even if details are sparse).
        assertTrue(out.contains("- 17:00 - 18:00 | 欧堡酒店"));
        assertTrue(out.contains("- 18:00 - 19:00 | 博物馆群"));
        assertTrue(out.contains("- 19:00 - 20:00 | 海花岛"));
    }
}
