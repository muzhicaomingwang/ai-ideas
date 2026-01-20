package com.teamventure.app.service;

import com.teamventure.app.support.BizException;
import java.util.Optional;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class XiaohongshuImportServiceTest {

    @Test
    void parse_shouldUseRapidApi_whenNoteIdPresent() {
        String url = "https://www.xiaohongshu.com/discovery/item/686f89fa000000002400f18a?source=webshare";
        String input = "share " + url;

        XiaohongshuImportService service = new XiaohongshuImportService(
                null,
                (noteId) -> {
                    assertEquals("686f89fa000000002400f18a", noteId);
                    return Optional.of(new XiaohongshuImportService.ScrapedNote("t", "real content from rapid"));
                }
        );

        var resp = service.parse(input);
        assertNotNull(resp.generatedMarkdown);
        assertTrue(resp.generatedMarkdown.contains("real content from rapid"));
    }

    @Test
    void parse_shouldResolveNoteId_fromXhsShortLink() {
        String input = """
                63 小红书APP 复制链接打开
                https://xhslink.com/AbCdEf
                """.trim();

        XiaohongshuImportService service = new XiaohongshuImportService(
                null,
                (noteId) -> {
                    assertEquals("686f89fa000000002400f18a", noteId);
                    return Optional.of(new XiaohongshuImportService.ScrapedNote("t", "content"));
                },
                (shortLink) -> Optional.of("https://www.xiaohongshu.com/explore/686f89fa000000002400f18a?x=1")
        );

        var resp = service.parse(input);
        assertEquals("686f89fa000000002400f18a", resp.note_id);
        assertTrue(resp.source_url.contains("/explore/686f89fa000000002400f18a"));
    }

    @Test
    void parse_shouldFail_whenNoNoteId() {
        String url = "https://www.xiaohongshu.com/some/other/path?x=1";
        XiaohongshuImportService service = new XiaohongshuImportService(null, (id) -> Optional.empty());

        BizException ex = assertThrows(BizException.class, () -> service.parse(url));
        assertEquals("PARSE_FAILED", ex.getCode());
    }

    @Test
    void parse_shouldFail_whenRapidApiReturnsEmpty() {
        String url = "https://www.xiaohongshu.com/explore/686f89fa000000002400f18a";
        XiaohongshuImportService service = new XiaohongshuImportService(null, (id) -> Optional.empty());

        BizException ex = assertThrows(BizException.class, () -> service.parse(url));
        assertEquals("PARSE_FAILED", ex.getCode());
    }

    @Test
    void parse_shouldFallbackToMetaDescription_whenRapidApiUnavailable() {
        String url = "https://www.xiaohongshu.com/discovery/item/686f89fa000000002400f18a?xsec_token=abc";
        String html = """
                <html>
                  <head>
                    <title>测试标题 - 小红书</title>
                    <meta name="description" content="这是兜底的 meta description 正文内容">
                  </head>
                  <body>...</body>
                </html>
                """;

        XiaohongshuImportService service = new XiaohongshuImportService(
                (u) -> html,
                (id) -> Optional.empty()
        );

        var resp = service.parse(url);
        assertEquals("686f89fa000000002400f18a", resp.note_id);
        assertTrue(resp.generatedMarkdown.contains("meta description"));
    }

    @Test
    void resolveNoteId_shouldReturnNoteId_andResolvedUrl() {
        XiaohongshuImportService service = new XiaohongshuImportService(
                null,
                (id) -> Optional.empty(),
                (shortLink) -> Optional.of("https://www.xiaohongshu.com/discovery/item/686f89fa000000002400f18a")
        );

        var result = service.resolveNoteId("https://xhslink.com/AbCdEf");
        assertEquals("686f89fa000000002400f18a", result.noteId);
        assertTrue(result.resolvedUrl.contains("/discovery/item/686f89fa000000002400f18a"));
    }

    @Test
    void parse_shouldDropPlaceholderTimeRows_andStripDayDates_inImportedMarkdown() {
        String url = "https://www.xiaohongshu.com/discovery/item/686f89fa000000002400f18a?xsec_token=abc";
        String content = """
                # 行程安排
                > 版本: v1

                ## Day 1（2026-01-20）
                - 09:00 - 10:00 | 抵达/出站 | 嘉兴站 |
                - - | 嘉兴站 |  |
                """;

        XiaohongshuImportService service = new XiaohongshuImportService(
                null,
                (noteId) -> Optional.of(new XiaohongshuImportService.ScrapedNote("t", content))
        );

        var resp = service.parse(url);
        assertFalse(resp.generatedMarkdown.contains("（2026-01-20）"));
        assertFalse(resp.generatedMarkdown.contains("- - | 嘉兴站"));
        assertTrue(resp.generatedMarkdown.contains("## Day 1"));
        assertTrue(resp.generatedMarkdown.contains("- 09:00 - 10:00"));
    }
}
