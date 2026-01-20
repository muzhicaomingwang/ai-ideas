package com.teamventure.app.support;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Sanitizes itinerary markdown for the "draft/unscheduled" phase:
 * - Removes concrete dates in Day headings (e.g. "## Day 1（2023-10-01）" -> "## Day 1")
 * - Drops placeholder rows that have no time (e.g. "- - | 北戴河 |  |")
 */
public final class ItineraryMarkdownSanitizer {
    private ItineraryMarkdownSanitizer() {}

    private static final Pattern DAY_HEADING_WITH_PAREN =
            Pattern.compile("^(##\\s*Day\\s*\\d+)\\s*[（(][^）)]*[）)]\\s*$");
    private static final Pattern VERSION_LINE =
            Pattern.compile("^>\\s*版本\\s*:\\s*.*$", Pattern.CASE_INSENSITIVE);
    private static final Pattern DAY_HEADING =
            Pattern.compile("^##\\s*Day\\b", Pattern.CASE_INSENSITIVE);
    private static final Pattern TIME_START =
            Pattern.compile("^(\\d{1,2}[:：]\\d{2})\\b");

    public static String sanitizeDraftItineraryMarkdown(String text) {
        if (text == null || text.isBlank()) return text == null ? "" : text;

        String s = ItineraryMarkdownValidator.normalizeMarkdown(text);
        String[] lines = s.replace("\r", "").split("\n", -1);
        StringBuilder sb = new StringBuilder(s.length());

        for (String line : lines) {
            String raw = line == null ? "" : line;
            String trimmed = raw.trim();

            if (VERSION_LINE.matcher(trimmed).matches()) {
                // Avoid confusion: itinerary schema version is not the validator version.
                continue;
            }

            Matcher m = DAY_HEADING_WITH_PAREN.matcher(trimmed);
            if (m.matches()) {
                sb.append(m.group(1)).append("\n");
                continue;
            }

            if (trimmed.startsWith("- ")) {
                String body = trimmed.substring(2);
                String[] parts = body.split("\\|", -1);
                if (parts.length >= 2) {
                    String time = parts[0].trim();
                    if (isPlaceholderTimeRange(time)) {
                        continue;
                    }
                }
            }

            sb.append(raw).append("\n");
        }

        return sb.toString().trim() + "\n";
    }

    /**
     * Line-based "validation" cleanup:
     * - Split by '\n' (折行算一行)
     * - Keep only lines whose trimmed form starts with:
     *   1) "##Day"/"## Day"
     *   2) a time (optionally prefixed by "- " / "* ")
     * - Delete all other lines.
     *
     * If a time line has no list marker, prefix "- " so it remains parsable by v2 validator/parser.
     */
    public static String filterDayAndTimeLines(String text) {
        if (text == null || text.isBlank()) return text == null ? "" : text.trim() + "\n";
        String s = ItineraryMarkdownValidator.normalizeMarkdown(text).replace("\r", "");
        String[] lines = s.split("\n", -1);
        StringBuilder sb = new StringBuilder(s.length());

        for (String line : lines) {
            String raw = line == null ? "" : line;
            String trimmed = ItineraryMarkdownValidator.normalizeMarkdown(raw).trim();
            if (trimmed.isBlank()) continue;

            if (DAY_HEADING.matcher(trimmed).find()) {
                sb.append(trimmed).append("\n");
                continue;
            }

            String withoutBullet = trimmed.replaceFirst("^[\\-*]\\s*", "");
            if (TIME_START.matcher(withoutBullet).find()) {
                if (trimmed.startsWith("- ")) {
                    sb.append(trimmed).append("\n");
                } else if (trimmed.startsWith("* ")) {
                    sb.append("- ").append(trimmed.substring(2).trim()).append("\n");
                } else {
                    sb.append("- ").append(withoutBullet).append("\n");
                }
            }
        }

        return sb.toString().trim() + "\n";
    }

    private static boolean isPlaceholderTimeRange(String time) {
        if (time == null) return true;
        String s = time.trim();
        if (s.isBlank()) return true;

        s = s.replace('：', ':');
        // Normalize dash variants to "-"
        s = s.replaceAll("[—–－‐‑‒―−~〜～﹣]", "-");
        // Remove whitespace
        s = s.replaceAll("\\s+", "");
        // If only hyphens remain, treat as placeholder (e.g. "-", "--", "- - -")
        String withoutHyphens = s.replace("-", "");
        return withoutHyphens.isBlank();
    }
}
