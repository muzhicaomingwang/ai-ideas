package com.teamventure.app.service;

import com.teamventure.app.support.ItineraryMarkdownValidator;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class MarkdownOptimizeServiceTest {

    @Test
    void convertFromParsed_shouldAlwaysReturnValidV2Markdown_evenWithoutAiService() {
        MarkdownOptimizeService service = new MarkdownOptimizeService();
        String parsed = """
                去过6次！嘉兴一日游citywalk，不走回头路
                嘉兴站→月河历史街区→天主堂→子城遗址公园→南湖旅游区
                会景园码头乘船：20元/往返
                南湖天地购物中心：餐厅多
                """;

        String md = service.convertFromParsed(parsed);
        var res = ItineraryMarkdownValidator.validate(md);
        assertTrue(res.valid, String.join("\n", res.errors));
        assertTrue(md.contains("## Day 1"));
        assertTrue(md.contains("- 09:00 - 10:00 |"));
        assertFalse(md.contains("> 版本:"));
    }

    @Test
    void convertFromParsed_shouldDropPlaceOnlyItems_withoutTimeRange() {
        MarkdownOptimizeService service = new MarkdownOptimizeService();
        String parsed = """
                # 行程安排
                > 版本: v1

                ## Day 1（2026-01-20）
                - 09:00 - 09:30 | 抵达/出发 | 嘉兴站 |
                - 09:30 - 11:30 | 逛街区/拍照打卡 | 月河历史街区 |
                - - | 嘉兴站 |  |
                - - - | 月河历史街区 |  |
                - - | 月河历史街区 |  |
                """;

        String md = service.convertFromParsed(parsed);
        assertFalse(md.contains("（2026-01-20）"));
        assertFalse(md.contains("- - | 嘉兴站"));
        assertFalse(md.contains("- - - | 月河历史街区"));
        assertFalse(md.contains("- - | 月河历史街区"));
        var res = ItineraryMarkdownValidator.validate(md);
        assertTrue(res.valid, String.join("\n", res.errors));
    }

    @Test
    void optimize_shouldAlsoEnforceValidV2Markdown_andSanitize() {
        MarkdownOptimizeService service = new MarkdownOptimizeService();
        String mdV1ish = """
                # 行程安排
                > 版本: v1

                ## Day 1（2023-10-01）
                - 09:00 - 10:00 | 抵达/出站 | 嘉兴站 |
                - - | 嘉兴站 |  |
                """;

        String out = service.optimize(mdV1ish);
        assertFalse(out.contains("> 版本:"));
        assertFalse(out.contains("（2023-10-01）"));
        assertFalse(out.contains("- - | 嘉兴站"));
        assertFalse(out.contains("# # 行程安排"));
        assertFalse(out.contains("原始内容（仅供参考）"));
        var res = ItineraryMarkdownValidator.validate(out);
        assertTrue(res.valid, String.join("\n", res.errors));
    }
}
