package com.teamventure.app.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.teamventure.app.support.BizException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class MarkdownOptimizeService {
    private static final Logger log = LoggerFactory.getLogger(MarkdownOptimizeService.class);

    private final HttpClient http;
    private final ObjectMapper objectMapper = new ObjectMapper();

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
        if (aiServiceUrl == null || aiServiceUrl.isBlank()) return input;

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
                return input;
            }

            JsonNode root = objectMapper.readTree(res.body());
            String content = root.path("markdown_content").asText("").trim();
            return content.isBlank() ? input : content;
        } catch (Exception e) {
            log.warn("markdown convert via AI failed, fallback to input", e);
            return input;
        }
    }

    public String optimize(String markdownContent) {
        String input = markdownContent == null ? "" : markdownContent.trim();
        if (input.isEmpty()) throw new BizException("VALIDATION_ERROR", "markdown_content is empty");
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
}
