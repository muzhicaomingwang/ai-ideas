package com.teamventure.app.service;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class XiaohongshuImportServiceTest {

    @Test
    void extractJsonStringField_shouldHandleEscapes() {
        XiaohongshuImportService service = new XiaohongshuImportService();

        // Simulate XHS HTML embedding a JSON string with escaped newlines and quotes.
        String html = """
                <html>
                  <head><title>三亚5天4夜行程安排 - 小红书</title></head>
                  <body>
                    <script>
                      window.__INIT__ = {
                        "desc":"D1 抵达三亚\\\\n- 酒店\\\\n- 椰梦长廊\\\\nD2 蜈支洲岛\\\\n- 浮潜\\\\n- 海鲜\\\\nTips：防晒\\\\n",
                        "title":"三亚5天4夜行程安排"
                      };
                    </script>
                  </body>
                </html>
                """;

        String desc = service.extractJsonStringField(html, "desc").orElse("");
        assertTrue(desc.contains("D1"));
        assertTrue(desc.contains("\n"));
        assertTrue(desc.contains("D2"));

        // Ensure extracted content can be returned as-is.
        var resp = service.parse(
                "三亚5天4夜行程安排\n" +
                        desc + "\n" +
                        "交通：高铁往返，尽量早出晚归\n" +
                        "住宿：市区酒店，方便集合\n" +
                        "景点：蜈支洲岛、免税店、椰梦长廊\n" +
                        "注意：防晒、提前预约"
        );
        assertNotNull(resp.generatedMarkdown);
        assertTrue(resp.generatedMarkdown.contains("D1"));
        assertTrue(resp.generatedMarkdown.contains("D2"));
    }

    @Test
    void parse_shouldReject_whenNoDayMarkers_evenIfHasDaysText() {
        XiaohongshuImportService service = new XiaohongshuImportService();

        String shareText = """
                青岛3天2夜攻略｜人均800
                交通：高铁往返
                住宿：市南区酒店
                景点：栈桥、八大关、崂山
                """;

        var resp = service.parse(shareText);
        assertFalse(resp.is_itinerary);
        assertNotNull(resp.generatedMarkdown);
        assertTrue(resp.generatedMarkdown.contains("青岛3天2夜攻略"));
    }

    @Test
    void parse_shouldAccept_whenHasDayMarkersWithContent() {
        XiaohongshuImportService service = new XiaohongshuImportService();

        String shareText = """
                三亚5天4夜行程安排
                D1 抵达三亚｜酒店办理入住｜椰梦长廊散步
                D2 蜈支洲岛一日游｜浮潜｜海鲜大餐
                D3 亚特兰蒂斯水世界｜免税店
                Tips：防晒、提前预约
                """;

        var resp = service.parse(shareText);
        assertNotNull(resp.generatedMarkdown);
        assertTrue(resp.generatedMarkdown.contains("D1 抵达三亚"));
        assertTrue(resp.generatedMarkdown.contains("D2 蜈支洲岛一日游"));
    }

    @Test
    void parse_shouldPreferShareText_whenInputContainsUrlAndFullText() {
        XiaohongshuImportService service = new XiaohongshuImportService();

        String shareText = """
                这是小红书分享口令全文：打开小红书App查看
                https://www.xiaohongshu.com/explore/695bbac4000000001a037a46?xsec_token=abc&xsec_source=pc_search
                三亚5天4夜行程安排
                D1 抵达三亚｜酒店办理入住｜椰梦长廊散步
                D2 蜈支洲岛一日游｜浮潜｜海鲜大餐
                交通：高铁/飞机都可
                """;

        var resp = service.parse(shareText);
        assertNotNull(resp.generatedMarkdown);
        assertTrue(resp.generatedMarkdown.contains("三亚5天4夜行程安排"));
    }

    @Test
    void parse_shouldFetchUrl_whenInputIsShareLinkButNoItineraryText() {
        String url = "https://www.xiaohongshu.com/discovery/item/695bbac4000000001a037a46?source=webshare&xhsshare=pc_web&xsec_token=AB5taFdJiFo4QiSl3j3-TiRMphDxMUG7hy9d6eY4HncwE=&xsec_source=pc_share";
        String input = "78 【上海可以分为4个板块游玩不绕路✔️ - 小红书】 😆 HAGCtqi5iliiuu3 😆 " + url;

        String html = """
                <html>
                  <head><title>上海可以分为4个板块游玩不绕路✔️ - 小红书</title></head>
                  <body>
                    <script>
                      window.__INIT__ = {
                        "desc":"📝三日游精华路线\\\\n🏷️day1:南京路步行街-外滩-陆家嘴\\\\n🏷️day2：愚园路-武康路-武康大楼\\\\n🏷️day3：静安寺-淮海中路-新天地\\\\n交通：地铁为主\\\\n",
                        "title":"上海可以分为4个板块游玩不绕路✔️"
                      };
                    </script>
                  </body>
                </html>
                """;

        XiaohongshuImportService service = new XiaohongshuImportService((u) -> {
            assertEquals(url, u);
            return html;
        });

        var resp = service.parse(input);
        assertTrue(resp.generatedMarkdown.contains("南京路步行街"));
        assertTrue(resp.generatedMarkdown.contains("武康大楼"));
    }

    @Test
    void parse_shouldGenerateItineraryMarkdown_whenUrlFetchReturnsContent() {
        String url = "https://www.xiaohongshu.com/explore/695bbac4000000001a037a46?xsec_token=AB5taFdJiFo4QiSl3j3-TiRMphDxMUG7hy9d6eY4HncwE=&xsec_source=pc_search&source=unknown";

        String html = """
                <html>
                  <head><title>上海2天1夜团建行程 - 小红书</title></head>
                  <body>
                    <script>
                      window.__INIT__ = {
                        "desc":"D1 抵达上海｜集合出发\\\\n- 午餐：本帮菜\\\\n- 景点：外滩打卡\\\\n- 住宿：市中心酒店\\\\nD2 返程\\\\n- 早餐\\\\n- 交通：高铁回程\\\\n注意：提前预约\\\\n",
                        "title":"上海2天1夜团建行程"
                      };
                    </script>
                  </body>
                </html>
                """;

        XiaohongshuImportService service = new XiaohongshuImportService((u) -> {
            assertEquals(url, u);
            return html;
        });

        var resp = service.parse(url);
        assertNotNull(resp.generatedMarkdown);
        assertTrue(resp.generatedMarkdown.contains("D1"));
        assertTrue(resp.generatedMarkdown.contains("D2"));
        assertTrue(resp.generatedMarkdown.contains("外滩打卡"));
    }

    @Test
    void parse_shouldAccept_whenDayMarkersUseDayWordAndEmojiPrefix() {
        XiaohongshuImportService service = new XiaohongshuImportService();

        String shareText = """
                上海可以分为4个板块游玩不绕路✔️
                #上海citywalk
                精心划分四大板块，串联热门景点，不走回头路、不绕路
                📝三日游精华路线
                🏷️day1:南京路步行街-上海邮政博物馆-外白渡桥-乍浦路桥-和平饭店-外滩-陆家嘴-东方明珠
                🏷️day2：愚园路-安福路-乌鲁木齐路-五原路-武康路-武康大楼
                🏷️day3：静安寺-马勒别墅-淮海中路-思南公馆-上海新天地-上海博物馆
                🚇 上海交通指南
                1️⃣飞机：上海浦东国际机场/上海虹桥国际机场
                2️⃣高铁：上海虹桥站
                """;

        var resp = service.parse(shareText);
        assertTrue(resp.generatedMarkdown.contains("南京路步行街"));
        assertTrue(resp.generatedMarkdown.contains("武康大楼"));
    }
}
