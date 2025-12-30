package com.teamventure.adapter.web.common;

public class ApiError {
    private String code;
    private String message;

    public ApiError() {}

    public ApiError(String code, String message) {
        this.code = code;
        this.message = message;
    }

    public String getCode() {
        return code;
    }

    public String getMessage() {
        return message;
    }
}

