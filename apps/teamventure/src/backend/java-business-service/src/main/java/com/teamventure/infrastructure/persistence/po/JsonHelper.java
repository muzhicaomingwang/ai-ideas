package com.teamventure.infrastructure.persistence.po;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.math.BigDecimal;

public class JsonHelper {
    private static final ObjectMapper MAPPER = new ObjectMapper();

    public static String safeJson(Object v) {
        if (v == null) return "{}";
        if (v instanceof String s) return s;
        try {
            return MAPPER.writeValueAsString(v);
        } catch (JsonProcessingException e) {
            return "{}";
        }
    }

    public static BigDecimal safeDecimal(Object v) {
        if (v == null) return BigDecimal.ZERO;
        if (v instanceof Number n) return BigDecimal.valueOf(n.doubleValue());
        try {
            return new BigDecimal(String.valueOf(v));
        } catch (Exception e) {
            return BigDecimal.ZERO;
        }
    }

    public static Integer safeInt(Object v) {
        if (v == null) return 0;
        if (v instanceof Number n) return n.intValue();
        try {
            return Integer.parseInt(String.valueOf(v));
        } catch (Exception e) {
            return 0;
        }
    }
}

