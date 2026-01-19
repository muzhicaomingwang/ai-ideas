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
}

