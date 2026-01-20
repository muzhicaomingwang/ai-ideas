package com.teamventure.app.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.teamventure.app.support.ItineraryMarkdownValidationResult;
import com.teamventure.app.support.ItineraryMarkdownSanitizer;
import com.teamventure.app.support.ItineraryMarkdownValidator;
import com.teamventure.app.support.BizException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class MarkdownOptimizeService {
    private static final Logger log = LoggerFactory.getLogger(MarkdownOptimizeService.class);

    private final HttpClient http;
    private final ObjectMapper objectMapper = new ObjectMapper();

    private static final int MAX_AUTO_FIX_ATTEMPTS = 5;
    private static final Pattern DAY_MARKER = Pattern.compile("(?i)(?:^|\\s)(?:D\\s*\\d+|day\\s*\\d+|第\\s*\\d+\\s*天)(?:\\b|\\s|:|：)");

    @Value("${teamventure.ai-service.url:}")
    private String aiServiceUrl;

    @Value("${teamventure.ai-service.normalize-model:gpt-5.2}")
    private String optimizeModel;

    public MarkdownOptimizeService() {
        this.http = HttpClient.newBuilder()
                .followRedirects(HttpClient.Redirect.NORMAL)
                .connectTimeout(Duration.ofSeconds(10))
                .version(HttpClient.Version.HTTP_1_1)
                .build();
    }

    public String convertFromParsed(String parsedContent) {
        String input = parsedContent == null ? "" : parsedContent.trim();
        if (input.isEmpty()) throw new BizException("VALIDATION_ERROR", "parsed_content is empty");
        if (aiServiceUrl == null || aiServiceUrl.isBlank()) {
            // Even without AI service, still enforce v2 itinerary markdown so the miniapp validator passes.
            return ensureValidItineraryMarkdown(input, input);
        }

        String endpoint = aiServiceUrl.endsWith("/")
                ? (aiServiceUrl.substring(0, aiServiceUrl.length() - 1) + "/api/v1/markdown/convert")
                : (aiServiceUrl + "/api/v1/markdown/convert");

        try {
            String body = objectMapper.createObjectNode()
                    .put("parsed_content", input)
                    .put("model", optimizeModel == null ? "" : optimizeModel)
                    .toString();
            byte[] payload = body.getBytes(StandardCharsets.UTF_8);
            log.debug("markdown convert request prepared: endpoint={} bytes={}", endpoint, payload.length);

            HttpRequest req = HttpRequest.newBuilder(URI.create(endpoint))
                    .timeout(Duration.ofSeconds(45))
                    .header("Content-Type", "application/json")
                    .header("Accept", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofByteArray(payload))
                    .build();

            HttpResponse<byte[]> res = http.send(req, HttpResponse.BodyHandlers.ofByteArray());
            if (res.statusCode() < 200 || res.statusCode() >= 300) {
                String details = safeSnippet(res.body());
                log.warn("markdown convert via AI failed: status={} details={}", res.statusCode(), details);
                return ensureValidItineraryMarkdown(input, input);
            }

            JsonNode root = objectMapper.readTree(res.body());
            String content = root.path("markdown_content").asText("").trim();
            String candidate = content.isBlank() ? input : content;
            return ensureValidItineraryMarkdown(input, candidate);
        } catch (Exception e) {
            log.warn("markdown convert via AI failed, fallback to input", e);
            return ensureValidItineraryMarkdown(input, input);
        }
    }

    /**
     * Closed-loop: template -> validate -> fix/retry (max 5).
     * Ensures the output passes the shared v2 itinerary markdown validator.
     */
    private String ensureValidItineraryMarkdown(String parsedText, String initialMarkdown) {
        String candidate = ItineraryMarkdownSanitizer.sanitizeDraftItineraryMarkdown(initialMarkdown);
        String lastCandidate = "";
        String lastSignature = "";

        for (int attempt = 1; attempt <= MAX_AUTO_FIX_ATTEMPTS; attempt++) {
            ItineraryMarkdownValidationResult check = ItineraryMarkdownValidator.validate(candidate);
            if (check.valid) return candidate;

            String signature = String.join("|", check.errors);
            if (attempt >= MAX_AUTO_FIX_ATTEMPTS) {
                throw new BizException("VALIDATION_ERROR",
                        "解析错误已经识别，请自行进行修改后再次进行尝试（自动修复已尝试 " + MAX_AUTO_FIX_ATTEMPTS + " 次）：\n"
                                + String.join("\n", head(check.errors, 10)));
            }

            if (candidate.equals(lastCandidate) && signature.equals(lastSignature)) {
                throw new BizException("VALIDATION_ERROR",
                        "解析错误已经识别，请自行进行修改后再次进行尝试（自动修复无进展）：\n"
                                + String.join("\n", head(check.errors, 10)));
            }

            lastCandidate = candidate;
            lastSignature = signature;

            // Fix by regenerating a valid v2 template, then (optionally) let AI refine the phrasing.
            String fixed = toValidItineraryTemplate(parsedText, candidate, check.errors, attempt);
            fixed = ItineraryMarkdownSanitizer.sanitizeDraftItineraryMarkdown(fixed);
            ItineraryMarkdownValidationResult fixedCheck = ItineraryMarkdownValidator.validate(fixed);
            if (fixedCheck.valid) return fixed;

            // If still invalid, try AI optimize once per attempt as a best-effort refinement.
            // IMPORTANT: avoid calling optimize() here (it enforces validation and would recurse).
            String optimizedOnce = optimizeOnce(fixed);
            candidate = ItineraryMarkdownSanitizer.sanitizeDraftItineraryMarkdown(optimizedOnce);
        }

        // unreachable
        return candidate;
    }

    public String optimize(String markdownContent) {
        String input = markdownContent == null ? "" : markdownContent.trim();
        if (input.isEmpty()) throw new BizException("VALIDATION_ERROR", "markdown_content is empty");
        // Always enforce the shared v2 itinerary validator so "AI optimize & save" can't regress to invalid output.
        // 1) sanitize the draft markdown (remove Day dates, drop "- -" rows, remove confusing version marker)
        // 2) if already valid, only accept AI output if it stays valid after re-sanitization
        // 3) otherwise fall back to the deterministic fix loop (max 5)
        String base = ItineraryMarkdownSanitizer.sanitizeDraftItineraryMarkdown(input);
        ItineraryMarkdownValidationResult baseCheck = ItineraryMarkdownValidator.validate(base);
        if (baseCheck.valid) {
            String optimized = optimizeOnce(base);
            String sanitizedOptimized = ItineraryMarkdownSanitizer.sanitizeDraftItineraryMarkdown(optimized);
            if (ItineraryMarkdownValidator.validate(sanitizedOptimized).valid) {
                return sanitizedOptimized;
            }
            return base;
        }

        String candidate = optimizeOnce(base);
        return ensureValidItineraryMarkdown(base, candidate);
    }

    private String optimizeOnce(String markdownContent) {
        String input = markdownContent == null ? "" : markdownContent.trim();
        if (input.isEmpty()) return "";
        if (aiServiceUrl == null || aiServiceUrl.isBlank()) return input;

        String endpoint = aiServiceUrl.endsWith("/")
                ? (aiServiceUrl.substring(0, aiServiceUrl.length() - 1) + "/api/v1/markdown/optimize")
                : (aiServiceUrl + "/api/v1/markdown/optimize");
        try {
            String body = objectMapper.createObjectNode()
                    .put("markdown_content", input)
                    .put("model", optimizeModel == null ? "" : optimizeModel)
                    .toString();
            byte[] payload = body.getBytes(StandardCharsets.UTF_8);

            HttpRequest req = HttpRequest.newBuilder(URI.create(endpoint))
                    .timeout(Duration.ofSeconds(45))
                    .header("Content-Type", "application/json")
                    .header("Accept", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofByteArray(payload))
                    .build();

            HttpResponse<byte[]> res = http.send(req, HttpResponse.BodyHandlers.ofByteArray());
            if (res.statusCode() < 200 || res.statusCode() >= 300) {
                String details = safeSnippet(res.body());
                log.warn("markdown optimize via AI failed: status={} details={}", res.statusCode(), details);
                return input;
            }

            JsonNode root = objectMapper.readTree(res.body());
            String content = root.path("markdown_content").asText("").trim();
            return content.isBlank() ? input : content;
        } catch (Exception e) {
            log.warn("markdown optimize via AI failed, fallback to input", e);
            return input;
        }
    }

    private String safeSnippet(byte[] body) {
        if (body == null || body.length == 0) return "";
        try {
            String s = new String(body, StandardCharsets.UTF_8).trim();
            if (s.length() > 240) s = s.substring(0, 240) + "...";
            return s;
        } catch (Exception ignore) {
            return "";
        }
    }

    private List<String> head(List<String> list, int n) {
        if (list == null || list.isEmpty()) return List.of();
        if (n <= 0) return List.of();
        return list.subList(0, Math.min(n, list.size()));
    }

    private String toValidItineraryTemplate(String parsedText, String lastMarkdown, List<String> errors, int attempt) {
        String source = (parsedText == null ? "" : parsedText.trim());
        if (source.isBlank()) source = (lastMarkdown == null ? "" : lastMarkdown.trim());
        if (source.isBlank()) source = "（内容为空）";

        List<String> lines = extractActivityLines(source);
        if (lines.isEmpty()) lines = List.of("自由活动/根据现场调整");

        int days = inferDays(source, lines);
        days = Math.max(1, Math.min(days, 5)); // keep compact to reduce validator risk

        int maxItemsPerDay = 8;
        List<List<String>> perDay = splitIntoDays(lines, days, maxItemsPerDay);

        String title = guessTitle(source);
        StringBuilder sb = new StringBuilder(4096);
        sb.append("# ").append(title).append("\n");
        sb.append("\n");

        int hour = 9;
        for (int d = 1; d <= perDay.size(); d++) {
            sb.append("## Day ").append(d).append("\n");
            List<String> items = perDay.get(d - 1);
            if (items.isEmpty()) items = List.of("自由活动/机动安排");
            int localHour = hour;
            for (String act : items) {
                String activity = sanitizeActivity(act);
                String start = pad2(localHour) + ":00";
                String end = pad2(Math.min(localHour + 1, 23)) + ":00";
                sb.append("- ").append(start).append(" - ").append(end).append(" | ").append(activity).append("\n");
                localHour = Math.min(localHour + 1, 22);
            }
            sb.append("\n");
            hour = Math.min(hour + 1, 12);
        }

        // Preserve original text as reference (ignored by validator).
        sb.append("> 原始内容（仅供参考）\n");
        List<String> rawLines = List.of(source.replace("\r", "").split("\n", -1));
        for (String raw : head(rawLines, 24)) {
            String t = raw == null ? "" : raw.trim();
            if (t.isEmpty()) continue;
            if (t.length() > 200) t = t.substring(0, 200) + "...";
            sb.append("> ").append(t.replace("\t", " ")).append("\n");
        }

        return sb.toString().trim() + "\n";
    }

    private List<String> extractActivityLines(String text) {
        String s = text == null ? "" : text.replace("\r", "");
        String[] raw = s.split("\n");
        List<String> out = new ArrayList<>();
        for (String line : raw) {
            String t = line == null ? "" : line.trim();
            if (t.isEmpty()) continue;
            if (t.startsWith("#") || t.startsWith(">")) continue;
            if (t.matches("^\\-\\s*\\-\\s*\\|.*$")) continue;
            if (t.startsWith("-")) {
                t = t.replaceFirst("^\\-+\\s*", "").trim();
                // If it's already a structured itinerary item "time | activity | location | ...",
                // keep only the meaningful parts and drop the time so we don't duplicate it later.
                String[] parts = t.split("\\|", -1);
                if (parts.length >= 2) {
                    String activity = parts[1].trim();
                    String location = parts.length >= 3 ? parts[2].trim() : "";
                    if (!location.isBlank()) {
                        t = (activity + "（" + location + "）").trim();
                    } else {
                        t = activity;
                    }
                }
            }
            if (t.startsWith("http")) continue;
            if (t.length() < 2) continue;
            out.add(t);
            if (out.size() >= 32) break;
        }

        // If single-line blob, split by punctuation/arrows.
        if (out.size() <= 1) {
            String compact = s.replaceAll("\\s+", " ").trim();
            String[] parts = compact.split("[。！!？?；;]|→|->|➡️|➜|—|–");
            for (String p : parts) {
                String t = p == null ? "" : p.trim();
                if (t.length() < 3) continue;
                out.add(t);
                if (out.size() >= 32) break;
            }
        }

        return out;
    }

    private int inferDays(String source, List<String> lines) {
        if (source == null) return 1;
        int markers = 0;
        var m = DAY_MARKER.matcher(source);
        while (m.find()) markers++;
        if (markers >= 2) return Math.min(markers, 5);
        if (lines.size() >= 16) return 3;
        if (lines.size() >= 10) return 2;
        return 1;
    }

    private List<List<String>> splitIntoDays(List<String> lines, int days, int maxItemsPerDay) {
        List<List<String>> out = new ArrayList<>();
        for (int i = 0; i < days; i++) out.add(new ArrayList<>());
        if (lines == null || lines.isEmpty()) return out;

        int idx = 0;
        for (String line : lines) {
            out.get(Math.min(idx / maxItemsPerDay, days - 1)).add(line);
            idx++;
            if (idx >= days * maxItemsPerDay) break;
        }
        return out;
    }

    private String guessTitle(String source) {
        String s = source == null ? "" : source.trim().replace("\r", "");
        if (s.isBlank()) return "行程安排";
        String firstLine = s.split("\n", -1)[0].trim();
        firstLine = firstLine.replaceFirst("^#+\\s*", "").trim();
        if (firstLine.length() >= 3 && firstLine.length() <= 50 && !firstLine.startsWith("http")) {
            return firstLine.replaceAll("\\s+", " ").trim();
        }
        return "行程安排";
    }

    private String sanitizeActivity(String activity) {
        String s = activity == null ? "" : activity.trim();
        s = s.replace("|", " - ");
        s = s.replaceAll("\\s+", " ");
        if (s.isBlank()) s = "自由活动/机动安排";
        if (s.length() > 80) s = s.substring(0, 80) + "...";
        return s;
    }

    private String pad2(int n) {
        int v = Math.max(0, Math.min(n, 99));
        return (v < 10 ? ("0" + v) : String.valueOf(v));
    }
}
