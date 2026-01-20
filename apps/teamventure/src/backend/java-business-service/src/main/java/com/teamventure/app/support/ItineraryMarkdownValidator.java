package com.teamventure.app.support;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Backend mirror of miniapp utils/itinerary-markdown.js validation logic.
 * Normalizes common model/IME artifacts (fullwidth pipes, invisible chars, dash variants)
 * and validates the v2 markdown structure.
 */
public final class ItineraryMarkdownValidator {
    private ItineraryMarkdownValidator() {}

    private static final Pattern DAY_HEADING = Pattern.compile("^##\\s*Day\\s*(\\d+)\\s*(?:（(.*)）)?\\s*$");
    private static final Pattern TIME_RANGE = Pattern.compile("^(\\d{1,2}:\\d{2})\\s*-\\s*(\\d{0,2}:?\\d{0,2})\\s*$");

    public static String normalizeMarkdown(String markdown) {
        if (markdown == null) return "";
        String s = markdown.replace("\r", "");
        s = normalizePipes(s);
        s = stripInvisible(s);
        return s;
    }

    public static ItineraryMarkdownValidationResult validate(String markdown) {
        String normalized = normalizeMarkdown(markdown);
        String[] rawLines = normalized.split("\n", -1);

        List<String> errors = new ArrayList<>();

        int days = 0;
        int totalItems = 0;

        boolean inDay = false;
        boolean currentDayHasItem = false;
        Integer currentDayNumber = null;

        for (int i = 0; i < rawLines.length; i++) {
            String line = normalizeLine(rawLines[i]);
            if (line.isEmpty()) continue;

            if (line.startsWith("# ")) continue;
            if (line.startsWith(">")) continue;

            Matcher day = DAY_HEADING.matcher(line);
            if (day.matches()) {
                // finalize previous day
                if (inDay && !currentDayHasItem && currentDayNumber != null) {
                    errors.add("Day " + currentDayNumber + " 下未找到任何行项目（以 \"-\" 开头）");
                }
                inDay = true;
                currentDayHasItem = false;
                currentDayNumber = safeParseInt(day.group(1));
                days++;
                continue;
            }

            if (line.startsWith("- ")) {
                if (!inDay || currentDayNumber == null) {
                    errors.add("第 " + (i + 1) + " 行：行项目必须放在某个 Day 标题下方");
                    continue;
                }
                String err = validateItemLine(line);
                if (err != null) {
                    errors.add("第 " + (i + 1) + " 行：" + err);
                    continue;
                }
                currentDayHasItem = true;
                totalItems++;
                continue;
            }

            errors.add("第 " + (i + 1) + " 行：无法识别的内容（请使用 Day 标题或 \"-\" 行项目）");
        }

        if (days == 0) {
            errors.add("未找到任何 Day 标题（例如：## Day 1（日期））");
        } else if (inDay && !currentDayHasItem && currentDayNumber != null) {
            errors.add("Day " + currentDayNumber + " 下未找到任何行项目（以 \"-\" 开头）");
        }

        return new ItineraryMarkdownValidationResult(errors.isEmpty(), errors, days, totalItems);
    }

    private static String validateItemLine(String line) {
        String trimmed = normalizePipes(line).replaceFirst("^\\-\\s*", "");
        String[] parts = trimmed.split("\\|", -1);
        if (parts.length < 2) return "行项目格式错误：需要至少包含「时间 | 活动」";

        String timeRange = normalizeTimeRange(parts[0].trim());
        String activity = stripInvisible(parts[1]).trim();
        if (activity.isEmpty()) return "活动不能为空";

        Matcher m = TIME_RANGE.matcher(timeRange);
        if (!m.matches()) return "时间格式错误：应为「HH:MM - HH:MM」（结束时间可留空）";

        return null;
    }

    private static String normalizeLine(String line) {
        return stripInvisible(String.valueOf(line == null ? "" : line)).trim();
    }

    private static String normalizePipes(String s) {
        return String.valueOf(s == null ? "" : s).replace('｜', '|');
    }

    private static String normalizeTimeRange(String timeRange) {
        if (timeRange == null) return "";
        String s = stripInvisible(timeRange);
        s = s.replace('：', ':');
        // Common dash variants: em/en/minus/fullwidth, plus tildes.
        s = s.replaceAll("[—–－‐‑‒―−~〜～﹣]", "-");
        s = s.replaceAll("\\s+", " ").trim();
        return s;
    }

    private static String stripInvisible(String s) {
        if (s == null) return "";
        // Remove common invisible characters that can break regex matching.
        return s.replaceAll("[\\u200B-\\u200F\\u202A-\\u202E\\u2060\\uFEFF]", "");
    }

    private static Integer safeParseInt(String s) {
        try {
            return Integer.parseInt(String.valueOf(s));
        } catch (Exception ignore) {
            return null;
        }
    }
}

