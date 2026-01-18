package com.teamventure.app.service;

import com.teamventure.adapter.web.imports.XiaohongshuImportController.ParseResponse;
import com.teamventure.app.support.BizException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class XiaohongshuImportService {
    private static final Logger log = LoggerFactory.getLogger(XiaohongshuImportService.class);

    private static final Pattern URL_PATTERN = Pattern.compile("(https?://\\S+)");
    private static final Pattern TITLE_TAG_PATTERN = Pattern.compile("<title>(.*?)</title>", Pattern.CASE_INSENSITIVE | Pattern.DOTALL);
    private static final Pattern DAY_HEADER_LINE_PATTERN =
            Pattern.compile("(?m)^\\s*(?:[\\p{So}\\p{Sk}\\p{Cn}\\p{Punct}\\p{M}]{0,8}\\s*)?(D\\s*\\d+|第[一二三四五六七八九十\\d]+天|day\\s*\\d+)\\s*[:：]?\\s*([^\\n]*)$",
                    Pattern.CASE_INSENSITIVE);

    private static final Pattern DAYS_PATTERN = Pattern.compile("(\\d{1,2})\\s*天");
    private static final Pattern DAY_MARKER_PATTERN =
            Pattern.compile("(?:^|\\n)\\s*(?:[\\p{So}\\p{Sk}\\p{Cn}\\p{Punct}\\p{M}]{0,8}\\s*)?(?:D\\s*\\d+|第[一二三四五六七八九十\\d]+天|day\\s*\\d+)\\b",
                    Pattern.CASE_INSENSITIVE);
    private static final Pattern ITINERARY_KEYWORDS_PATTERN = Pattern.compile("(行程|路线|路书|攻略|安排|出行|旅行|游玩|打卡|景点|酒店|住宿|交通|高铁|航班|车次|集合|出发)", Pattern.CASE_INSENSITIVE);

    private final HttpClient http;
    private final HtmlFetcher htmlFetcher;

    @FunctionalInterface
    interface HtmlFetcher {
        String fetch(String url) throws Exception;
    }

    public XiaohongshuImportService() {
        this.http = HttpClient.newBuilder()
                .followRedirects(HttpClient.Redirect.NORMAL)
                .connectTimeout(Duration.ofSeconds(10))
                .build();
        this.htmlFetcher = this::fetchHtml;
    }

    XiaohongshuImportService(HtmlFetcher htmlFetcher) {
        this.http = HttpClient.newBuilder()
                .followRedirects(HttpClient.Redirect.NORMAL)
                .connectTimeout(Duration.ofSeconds(10))
                .build();
        this.htmlFetcher = htmlFetcher == null ? this::fetchHtml : htmlFetcher;
    }

    public ParseResponse parse(String linkOrText) {
        String input = linkOrText == null ? "" : linkOrText.trim();
        if (input.isEmpty()) {
            throw new BizException("VALIDATION_ERROR", "link is empty");
        }

        Optional<String> extractedUrl = extractUrl(input);
        String sourceUrl = extractedUrl.orElse("");

        String rawContent;
        String title = "";
        String desc = "";
        try {
            // 仅做“内容解析”：
            // - 如果输入包含小红书 URL：优先抓取 URL 内容并提取正文
            // - 如果抓取失败：回退到用户粘贴的文本（可能包含正文）
            // - 不做“是否行程”的业务判断
            if (sourceUrl.startsWith("http")) {
                String html = htmlFetcher.fetch(sourceUrl);
                title = extractTitleFromHtml(html).orElse("");
                desc = extractJsonStringField(html, "desc").orElse("");

                // Some pages only expose JSON title, try field extract fallback
                if (title.isBlank()) {
                    title = extractJsonStringField(html, "title").orElse("");
                }

                rawContent = (desc == null ? "" : desc.trim());
                if (rawContent.isBlank()) rawContent = (title == null ? "" : title.trim());
                if (rawContent.isBlank()) rawContent = "(empty)";
            } else {
                // Treat pasted share text as raw content
                rawContent = input;
                title = firstNonEmptyLine(rawContent).orElse("");
            }
        } catch (Exception e) {
            log.warn("xhs parse failed", e);
            // fallback to user text if available
            if (input.length() >= 20) {
                rawContent = input;
                title = firstNonEmptyLine(rawContent).orElse("");
            } else {
                throw new BizException("PARSE_FAILED", "无法获取或解析内容，请稍后重试（建议粘贴分享口令全文）");
            }
        }

        ParseResponse resp = new ParseResponse();
        resp.is_itinerary = false;
        resp.title = normalizeTitle(title);
        resp.destination = "";
        resp.days = null;
        resp.source_url = sourceUrl;
        resp.raw_content = truncate(rawContent, 20000);
        // Frontend uses this field to fill the document box; keep it as the extracted content.
        resp.generatedMarkdown = resp.raw_content;
        return resp;
    }

    private String buildImportedContentMarkdown(ParseResponse resp, String rawContentForMarkdown) {
        String title = resp.title == null ? "" : resp.title.trim();
        String headerTitle = !title.isBlank() ? title : "小红书导入内容";
        String source = (resp.source_url == null || resp.source_url.isBlank()) ? "（无）" : resp.source_url;
        String raw = rawContentForMarkdown == null ? "" : rawContentForMarkdown.trim();
        if (raw.isBlank()) raw = "（无）";

        return """
                # %s

                ## 导入来源
                - **链接**: %s

                ## 原文内容
                %s
                """.formatted(headerTitle, source, raw).trim() + "\n";
    }

    private boolean hasStrongDayMarkers(String input) {
        if (input == null) return false;
        String normalized = normalizeForDetection(input);
        if (normalized.isBlank()) return false;
        if (countDayMarkers(normalized) < 2) return false;
        return hasDaySectionsWithContent(normalized);
    }

    private boolean looksLikeShareText(String input, String extractedUrl) {
        if (input == null) return false;
        String s = input.trim();
        if (s.isEmpty()) return false;
        if (extractedUrl == null) return false;

        // If there's more than just a URL (multi-line / contains typical share words), treat as share text.
        boolean multiLine = s.contains("\n");
        boolean hasShareKeywords = s.contains("小红书") || s.contains("复制") || s.contains("打开") || s.contains("分享");
        boolean hasExtraContent = s.length() >= extractedUrl.length() + 40;
        return (multiLine && hasExtraContent) || (hasShareKeywords && hasExtraContent);
    }

    private Optional<String> extractUrl(String text) {
        Matcher m = URL_PATTERN.matcher(text);
        if (!m.find()) return Optional.empty();
        return Optional.ofNullable(m.group(1));
    }

    private String fetchHtml(String url) throws IOException, InterruptedException, URISyntaxException {
        URI uri = new URI(url);
        HttpRequest req = HttpRequest.newBuilder(uri)
                .timeout(Duration.ofSeconds(15))
                .header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36")
                .header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
                .GET()
                .build();

        HttpResponse<byte[]> res = http.send(req, HttpResponse.BodyHandlers.ofByteArray());
        if (res.statusCode() < 200 || res.statusCode() >= 300) {
            throw new IOException("unexpected status: " + res.statusCode());
        }
        byte[] body = res.body();
        // XHS typically serves UTF-8
        return new String(body, StandardCharsets.UTF_8);
    }

    private Optional<String> extractTitleFromHtml(String html) {
        Matcher m = TITLE_TAG_PATTERN.matcher(html);
        if (!m.find()) return Optional.empty();
        return Optional.of(stripHtml(m.group(1)));
    }

    /**
     * Extract a JSON string field value from a larger HTML blob.
     * This is a best-effort extractor that respects escaped quotes in string values.
     */
    Optional<String> extractJsonStringField(String html, String fieldName) {
        if (html == null || fieldName == null || fieldName.isBlank()) return Optional.empty();
        String needle = "\"" + fieldName + "\"";
        int idx = html.indexOf(needle);
        if (idx < 0) return Optional.empty();

        // Find ':' after the field name
        int colon = html.indexOf(':', idx + needle.length());
        if (colon < 0) return Optional.empty();

        // Find first quote after colon
        int startQuote = html.indexOf('"', colon + 1);
        if (startQuote < 0) return Optional.empty();

        String raw = extractJsonStringLiteral(html, startQuote);
        if (raw == null) return Optional.empty();
        String unescaped = unescapeJsonStringDeep(raw);
        if (unescaped.isBlank()) return Optional.empty();
        return Optional.of(unescaped);
    }

    /**
     * Given a string and the index of the opening quote, extract the raw JSON string contents
     * (without the surrounding quotes), respecting escape sequences.
     */
    String extractJsonStringLiteral(String s, int openingQuoteIndex) {
        if (s == null) return null;
        if (openingQuoteIndex < 0 || openingQuoteIndex >= s.length()) return null;
        if (s.charAt(openingQuoteIndex) != '"') return null;

        StringBuilder out = new StringBuilder(256);
        boolean escaping = false;
        for (int i = openingQuoteIndex + 1; i < s.length(); i++) {
            char c = s.charAt(i);
            if (escaping) {
                // Keep escapes as-is (e.g. \\n, \\u1234) for later unescapeJsonString()
                out.append('\\').append(c);
                escaping = false;
                continue;
            }
            if (c == '\\') {
                escaping = true;
                continue;
            }
            if (c == '"') {
                return out.toString();
            }
            out.append(c);
        }
        return null;
    }

    private ItinerarySignals detectItinerary(String raw) {
        String normalized = normalizeForDetection(raw);
        int days = -1;

        Matcher mDays = DAYS_PATTERN.matcher(normalized);
        if (mDays.find()) {
            days = safeParseInt(mDays.group(1), -1);
        }

        int dayMarkers = countDayMarkers(normalized);
        boolean hasKeywords = ITINERARY_KEYWORDS_PATTERN.matcher(normalized).find();
        boolean hasStructure = hasDaySectionsWithContent(normalized);

        // 严格模式（先严后松的第一版）：
        // - 必须出现 >=2 个“分天标记”（D1/D2/第X天…）
        // - 且每个分天块后有实际内容（避免仅出现“D1 D2”标题）
        // - 且包含常见行程关键词（降低误判为营销/碎片信息）
        // - 且文本长度达到阈值（降低误判）
        boolean isItinerary =
                dayMarkers >= 2
                        && hasStructure
                        && hasKeywords
                        && normalized.length() >= 80;

        // Best-effort destination guess from title/content
        String destination = guessDestination(normalized);

        if (days == -1 && dayMarkers > 0) {
            // If days not explicitly present, infer from markers (cap 9 for template consistency)
            days = Math.min(dayMarkers, 9);
        }
        if (days == -1) days = DEFAULT_DAYS();

        return new ItinerarySignals(isItinerary, destination, days);
    }

    private int DEFAULT_DAYS() {
        return 3;
    }

    private String normalizeForDetection(String raw) {
        if (raw == null) return "";
        String s = raw.replace("\r\n", "\n").replace("\r", "\n");
        s = s.replace('\u00A0', ' '); // nbsp
        return s.trim();
    }

    private int countDayMarkers(String text) {
        int count = 0;
        Matcher m = DAY_MARKER_PATTERN.matcher(text);
        while (m.find()) {
            count++;
            // still count fully; useful for inferred days
        }
        return count;
    }

    private boolean hasDaySectionsWithContent(String text) {
        // Find each marker position; ensure within next few lines there is meaningful content.
        Matcher m = DAY_MARKER_PATTERN.matcher(text);
        int found = 0;
        int valid = 0;
        while (m.find()) {
            found++;
            int start = m.end();
            String tail = text.substring(Math.min(start, text.length()));
            if (hasMeaningfulLineSoon(tail)) {
                valid++;
            }
            if (found >= 3) break; // only need evidence; keep it cheap
        }
        return found >= 2 && valid >= 2;
    }

    private boolean hasMeaningfulLineSoon(String tail) {
        if (tail == null || tail.isBlank()) return false;
        String[] lines = tail.split("\\n", 8); // look at a small window
        int checked = 0;
        for (String line : lines) {
            if (checked++ >= 6) break;
            String s = line.trim();
            if (s.isEmpty()) continue;
            // ignore another marker immediately
            if (DAY_MARKER_PATTERN.matcher(s).find()) continue;
            // must have some content beyond punctuation
            if (s.length() >= 4) return true;
        }
        return false;
    }

    private String guessDestination(String raw) {
        // Heuristic: pick first 2-6 consecutive CJK chars followed by "攻略/旅行/行程/团建/游"
        Pattern p = Pattern.compile("([\\p{IsHan}]{2,6})(?:\\s*)(?:攻略|旅行|行程|团建|游)");
        Matcher m = p.matcher(raw);
        if (m.find()) return m.group(1);

        // Fallback: if title line contains "·" or "-" split and take first segment
        String firstLine = firstNonEmptyLine(raw).orElse("");
        String cleaned = firstLine.replaceAll("\\s+", " ").trim();
        if (cleaned.contains("·")) return cleaned.split("·")[0].trim();
        if (cleaned.contains("-")) return cleaned.split("-")[0].trim();
        return "";
    }

    private String buildMarkdown(ParseResponse resp, String rawContentForMarkdown) {
        String title = resp.title == null ? "" : resp.title.trim();
        String destination = resp.destination == null ? "" : resp.destination.trim();
        Integer days = resp.days;

        String headerTitle = !title.isBlank() ? title : "团建行程方案（由小红书导入）";
        String d = destination.isBlank() ? "（待确认）" : destination;
        String daysText = days == null ? "（待确认）" : (days + "天" + (days > 1 ? (days - 1) + "夜" : ""));

        String itinerary = buildItineraryMarkdown(rawContentForMarkdown);
        if (itinerary.isBlank()) {
            itinerary = """
                    ## 行程安排
                    > （未能抽取分天行程，请参考下方“原文要点”手动整理）
                    """.trim();
        }

        return """
                # %s

                ## 基本信息
                - **天数**: %s

                ## 行程路线
                - **到达地**: %s

                %s

                ## 导入来源
                - **链接**: %s

                ## 原文要点（供校对）
                %s
                """.formatted(
                headerTitle,
                daysText,
                d,
                itinerary,
                (resp.source_url == null || resp.source_url.isBlank()) ? "（无）" : resp.source_url,
                toBlockQuoteLines(resp.raw_content == null ? "" : resp.raw_content)
        ).trim() + "\n";
    }

    private String buildItineraryMarkdown(String raw) {
        String text = normalizeForDetection(raw);
        if (text.isBlank()) return "";

        Matcher m = DAY_HEADER_LINE_PATTERN.matcher(text);
        int count = 0;
        int[] starts = new int[16];
        int[] headerEnds = new int[16];
        String[] headerMarkers = new String[16];
        String[] headerRests = new String[16];

        while (m.find()) {
            if (count >= starts.length) break;
            starts[count] = m.start();
            headerEnds[count] = m.end();
            headerMarkers[count] = m.group(1);
            headerRests[count] = m.group(2);
            count++;
        }

        if (count < 2) return "";

        StringBuilder sb = new StringBuilder();
        sb.append("## 行程安排\n");

        for (int i = 0; i < count; i++) {
            int sectionStart = headerEnds[i];
            int sectionEnd = (i + 1 < count) ? starts[i + 1] : text.length();
            String sectionBody = text.substring(Math.min(sectionStart, text.length()), Math.min(sectionEnd, text.length()));

            String marker = normalizeDayMarker(headerMarkers[i]);
            String rest = headerRests[i] == null ? "" : headerRests[i].trim();
            String[] restParts = splitDayRest(rest);

            String heading = marker;
            StringBuilder composite = new StringBuilder();
            if (restParts.length > 0) {
                heading = marker + " " + restParts[0];
                for (int r = 1; r < restParts.length; r++) {
                    composite.append(restParts[r]).append("\n");
                }
            }
            composite.append(sectionBody);

            sb.append("\n### ").append(heading.trim()).append("\n");
            String bullets = toBullets(composite.toString());
            if (bullets.isBlank()) {
                sb.append("- （无）\n");
            } else {
                sb.append(bullets).append("\n");
            }
        }

        return sb.toString().trim();
    }

    private String normalizeDayMarker(String marker) {
        String m = marker == null ? "" : marker.trim();
        if (!m.isBlank() && m.matches("(?i)^D\\s*\\d+\\b.*")) {
            m = m.toUpperCase().replaceAll("\\s+", "");
        } else if (!m.isBlank() && m.toLowerCase().startsWith("day")) {
            String digits = m.replaceAll("(?i)day", "").replaceAll("\\s+", "");
            m = digits.isBlank() ? "Day1" : ("Day" + digits);
        }
        return m.isBlank() ? "D1" : m;
    }

    private String[] splitDayRest(String rest) {
        if (rest == null) return new String[0];
        String s = rest.trim();
        if (s.isBlank()) return new String[0];
        // Common separators inside a day line: "｜" / "|" / "·"
        String normalized = s.replace('｜', '|');
        String[] parts = normalized.split("\\|");
        int nonEmpty = 0;
        for (String p : parts) {
            if (p != null && !p.trim().isEmpty()) nonEmpty++;
        }
        if (nonEmpty <= 1) return new String[] { s };

        String[] out = new String[nonEmpty];
        int idx = 0;
        for (String p : parts) {
            if (p == null) continue;
            String t = p.trim();
            if (t.isEmpty()) continue;
            out[idx++] = t;
        }
        return out;
    }

    private String toBullets(String sectionBody) {
        if (sectionBody == null) return "";
        String[] lines = sectionBody.split("\\R");
        StringBuilder sb = new StringBuilder();
        int added = 0;
        for (String line : lines) {
            String s = line == null ? "" : line.trim();
            if (s.isEmpty()) continue;
            // skip typical share guidance noise
            if (s.contains("打开小红书")) continue;
            if (s.contains("复制") && s.contains("小红书")) continue;
            String bullet = normalizeToBullet(s);
            if (bullet.isBlank()) continue;
            sb.append(bullet).append("\n");
            if (++added >= 30) break;
        }
        return sb.toString().trim();
    }

    private String normalizeToBullet(String line) {
        String s = line.trim();
        // avoid treating a new day marker line as a bullet
        if (DAY_HEADER_LINE_PATTERN.matcher(s).find() || DAY_MARKER_PATTERN.matcher("\n" + s).find()) return "";
        if (s.startsWith("-")) return s.startsWith("- ") ? s : "- " + s.substring(1).trim();
        if (s.startsWith("*")) return "- " + s.substring(1).trim();
        if (s.startsWith("•") || s.startsWith("·")) return "- " + s.substring(1).trim();
        if (s.matches("^\\d+\\s*[\\.|、】【、].+")) return "- " + s;
        return "- " + s;
    }

    private String toBlockQuoteLines(String text) {
        String t = text == null ? "" : text.trim();
        if (t.isBlank()) return "> （无）";
        String[] lines = t.split("\\R");
        StringBuilder sb = new StringBuilder();
        for (String line : lines) {
            String s = line.trim();
            if (s.isEmpty()) continue;
            sb.append("> ").append(truncate(s, 200)).append("\n");
        }
        if (sb.length() == 0) return "> （无）";
        return sb.toString().trim();
    }

    private Optional<String> firstNonEmptyLine(String text) {
        if (text == null) return Optional.empty();
        for (String line : text.split("\\R")) {
            String s = line.trim();
            if (!s.isEmpty()) return Optional.of(s);
        }
        return Optional.empty();
    }

    private String stripHtml(String s) {
        if (s == null) return "";
        return s.replaceAll("<[^>]+>", "").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").trim();
    }

    private String unescapeJsonString(String s) {
        if (s == null) return "";
        StringBuilder out = new StringBuilder(s.length());
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c != '\\') {
                out.append(c);
                continue;
            }
            if (i + 1 >= s.length()) break;
            char n = s.charAt(++i);
            switch (n) {
                case '"': out.append('"'); break;
                case '\\': out.append('\\'); break;
                case '/': out.append('/'); break;
                case 'b': out.append('\b'); break;
                case 'f': out.append('\f'); break;
                case 'n': out.append('\n'); break;
                case 'r': out.append('\r'); break;
                case 't': out.append('\t'); break;
                case 'u':
                    if (i + 4 < s.length()) {
                        String hex = s.substring(i + 1, i + 5);
                        try {
                            int code = Integer.parseInt(hex, 16);
                            out.append((char) code);
                            i += 4;
                        } catch (NumberFormatException e) {
                            out.append("\\u").append(hex);
                            i += 4;
                        }
                    } else {
                        out.append("\\u");
                    }
                    break;
                default:
                    out.append(n);
            }
        }
        return out.toString().trim();
    }

    private String unescapeJsonStringDeep(String s) {
        String once = unescapeJsonString(s);
        // Some pages embed JSON inside another JSON/JS string, leading to double-escaped sequences (e.g. "\\n").
        if (once.contains("\\n") || once.contains("\\r") || once.contains("\\t") || once.contains("\\u")) {
            return unescapeJsonString(once);
        }
        return once;
    }

    private int safeParseInt(String s, int fallback) {
        try {
            return Integer.parseInt(s);
        } catch (Exception e) {
            return fallback;
        }
    }

    private String normalizeTitle(String title) {
        if (title == null) return "";
        String t = title.trim();
        t = t.replaceAll("\\s+", " ");
        // Some <title> include suffixes like "_小红书"
        t = t.replaceAll("[-_ ]*小红书\\s*$", "");
        return t.trim();
    }

    private String truncate(String s, int max) {
        if (s == null) return "";
        if (s.length() <= max) return s;
        return s.substring(0, max) + "...";
    }

    private static class ItinerarySignals {
        final boolean isItinerary;
        final String destination;
        final Integer days;

        ItinerarySignals(boolean isItinerary, String destination, Integer days) {
            this.isItinerary = isItinerary;
            this.destination = destination == null ? "" : destination;
            this.days = days;
        }
    }
}
