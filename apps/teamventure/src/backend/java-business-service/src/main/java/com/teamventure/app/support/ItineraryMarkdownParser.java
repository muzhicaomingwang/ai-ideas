package com.teamventure.app.support;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Parse itinerary markdown v2 into structured itinerary JSON ({days:[{day,items:[...]}]}).
 *
 * This is intentionally strict and pairs with {@link ItineraryMarkdownValidator}.
 */
public final class ItineraryMarkdownParser {
    private ItineraryMarkdownParser() {}

    private static final Pattern DAY_HEADING = Pattern.compile("^##\\s*Day\\s*(\\d+)\\s*(?:（(.*)）)?\\s*$");
    private static final Pattern TIME_RANGE = Pattern.compile("^(\\d{1,2}:\\d{2})\\s*-\\s*(\\d{0,2}:?\\d{0,2})\\s*$");

    public static Map<String, Object> parseToItinerary(String markdown) {
        String normalized = ItineraryMarkdownValidator.normalizeMarkdown(markdown);
        String[] rawLines = normalized.split("\n", -1);

        List<Map<String, Object>> days = new ArrayList<>();

        Integer currentDay = null;
        List<Map<String, Object>> currentItems = null;

        for (String raw : rawLines) {
            String line = raw == null ? "" : raw.trim();
            if (line.isEmpty()) continue;
            if (line.startsWith("# ")) continue;
            if (line.startsWith(">")) continue;

            Matcher day = DAY_HEADING.matcher(line);
            if (day.matches()) {
                currentDay = safeParseInt(day.group(1));
                currentItems = new ArrayList<>();
                Map<String, Object> dayObj = new LinkedHashMap<>();
                dayObj.put("day", currentDay == null ? (days.size() + 1) : currentDay);
                dayObj.put("items", currentItems);
                days.add(dayObj);
                continue;
            }

            if (line.startsWith("- ")) {
                if (currentDay == null || currentItems == null) continue;
                Map<String, Object> item = parseItemLine(line);
                if (item != null) currentItems.add(item);
            }
        }

        Map<String, Object> itinerary = new LinkedHashMap<>();
        itinerary.put("days", days);
        return itinerary;
    }

    private static Map<String, Object> parseItemLine(String line) {
        String trimmed = ItineraryMarkdownValidator.normalizeMarkdown(line).replaceFirst("^\\-\\s*", "");
        String[] parts = trimmed.split("\\|", -1);
        if (parts.length < 2) return null;

        String timeRange = parts[0].trim();
        String activity = strip(parts[1]);
        if (activity.isEmpty()) return null;

        String location = parts.length >= 3 ? strip(parts[2]) : "";
        String note = parts.length >= 4 ? strip(parts[3]) : "";

        String normalizedTime = normalizeTimeRange(timeRange);
        Matcher m = TIME_RANGE.matcher(normalizedTime);
        if (!m.matches()) return null;

        String timeStart = m.group(1);
        String timeEnd = m.group(2) == null ? "" : m.group(2);

        Map<String, Object> item = new LinkedHashMap<>();
        item.put("time_start", timeStart);
        if (!timeEnd.isBlank()) item.put("time_end", timeEnd);
        item.put("activity", activity);
        if (!location.isBlank()) item.put("location", location);
        if (!note.isBlank()) item.put("note", note);
        return item;
    }

    private static String strip(String s) {
        return ItineraryMarkdownValidator.normalizeMarkdown(s == null ? "" : s).trim();
    }

    private static String normalizeTimeRange(String timeRange) {
        if (timeRange == null) return "";
        String s = ItineraryMarkdownValidator.normalizeMarkdown(timeRange);
        s = s.replace('：', ':');
        s = s.replaceAll("[—–－‐‑‒―−~〜～﹣]", "-");
        s = s.replaceAll("\\s+", " ").trim();
        return s;
    }

    private static Integer safeParseInt(String s) {
        try {
            return Integer.parseInt(String.valueOf(s));
        } catch (Exception ignore) {
            return null;
        }
    }
}

