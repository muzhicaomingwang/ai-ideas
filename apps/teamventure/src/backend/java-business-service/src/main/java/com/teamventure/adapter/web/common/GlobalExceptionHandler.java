package com.teamventure.adapter.web.common;

import com.teamventure.app.support.BizException;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.ConstraintViolationException;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.env.Environment;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.servlet.resource.NoResourceFoundException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {
    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);
    private final Environment env;

    public GlobalExceptionHandler(Environment env) {
        this.env = env;
    }

    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<ApiResponse<Void>> handleNotReadable(HttpMessageNotReadableException e) {
        // JSON 解析失败 / body 缺失：这是客户端请求问题，应返回 400，而不是 500
        String msg = "Invalid request body";
        if (env != null && env.acceptsProfiles(org.springframework.core.env.Profiles.of("dev", "local"))) {
            Throwable cause = e.getMostSpecificCause();
            String detail = (cause == null ? e.getMessage() : cause.getMessage());
            msg = "HttpMessageNotReadableException: " + (detail == null ? "" : detail);
        }
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(ApiResponse.failure("BAD_REQUEST", msg.trim()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Void>> handleValidation(MethodArgumentNotValidException e) {
        String msg = "Validation failed";
        if (env != null && env.acceptsProfiles(org.springframework.core.env.Profiles.of("dev", "local"))) {
            msg = e.getBindingResult().getFieldErrors().stream()
                    .map(fe -> fe.getField() + ": " + (fe.getDefaultMessage() == null ? "" : fe.getDefaultMessage()))
                    .collect(Collectors.joining("; "));
            if (msg.isBlank()) msg = "Validation failed";
        }
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(ApiResponse.failure("BAD_REQUEST", msg.trim()));
    }

    @ExceptionHandler(ConstraintViolationException.class)
    public ResponseEntity<ApiResponse<Void>> handleConstraintViolation(ConstraintViolationException e) {
        String msg = "Validation failed";
        if (env != null && env.acceptsProfiles(org.springframework.core.env.Profiles.of("dev", "local"))) {
            msg = e.getConstraintViolations().stream()
                    .map(ConstraintViolation::getMessage)
                    .collect(Collectors.joining("; "));
            if (msg.isBlank()) msg = "Validation failed";
        }
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(ApiResponse.failure("BAD_REQUEST", msg.trim()));
    }

    @ExceptionHandler(MissingServletRequestParameterException.class)
    public ResponseEntity<ApiResponse<Void>> handleMissingParam(MissingServletRequestParameterException e) {
        String msg = "Missing request parameter";
        if (env != null && env.acceptsProfiles(org.springframework.core.env.Profiles.of("dev", "local"))) {
            msg = "MissingServletRequestParameterException: " + e.getParameterName();
        }
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(ApiResponse.failure("BAD_REQUEST", msg.trim()));
    }

    @ExceptionHandler(BizException.class)
    public ResponseEntity<ApiResponse<Void>> handleBiz(BizException e) {
        HttpStatus status = HttpStatus.BAD_REQUEST;
        if ("UNAUTHENTICATED".equals(e.getCode())) {
            status = HttpStatus.UNAUTHORIZED;
        }
        return ResponseEntity.status(status).body(ApiResponse.failure(e.getCode(), e.getMessage()));
    }

    @ExceptionHandler(NoResourceFoundException.class)
    public ResponseEntity<ApiResponse<Void>> handleNoResource(NoResourceFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(ApiResponse.failure("NOT_FOUND", e.getMessage()));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleGeneric(Exception e) {
        log.error("unhandled exception", e);
        // 开发环境下透出更多错误信息，便于联调排查；生产环境仍返回统一文案
        if (env != null && env.acceptsProfiles(org.springframework.core.env.Profiles.of("dev", "local"))) {
            String detail = e.getClass().getSimpleName() + ": " + (e.getMessage() == null ? "" : e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ApiResponse.failure("INTERNAL_ERROR", detail.trim()));
        }
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.failure("INTERNAL_ERROR", "Internal server error"));
    }
}
