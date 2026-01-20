package com.teamventure.app.support;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

public class ItineraryMarkdownValidatorTest {

    @Test
    void validate_accepts_common_ime_and_llm_artifacts_after_normalization() {
        String zw = "\u200b";
        String md = """
                # 行程安排
                > 版本: v2

                ## Day 1（今天）
                - %s07：30%s − %s10：30%s ｜ 游览 ｜ 拙政园 ｜ 备注
                - 11：00 – 12：30 ｜ 用餐 ｜ 观前街 ｜ 
                """.formatted(zw, zw, zw, zw);

        ItineraryMarkdownValidationResult res = ItineraryMarkdownValidator.validate(md);
        assertTrue(res.valid, String.join("\n", res.errors));
        assertEquals(1, res.days);
        assertEquals(2, res.items);
    }

    @Test
    void validate_rejects_items_outside_day() {
        String md = """
                # 行程安排
                > 版本: v2
                - 09:00 - 10:00 | 游览 | 某地 |
                """;
        ItineraryMarkdownValidationResult res = ItineraryMarkdownValidator.validate(md);
        assertFalse(res.valid);
        assertTrue(res.errors.stream().anyMatch(s -> s.contains("行项目必须放在某个 Day 标题下方")));
    }
}

