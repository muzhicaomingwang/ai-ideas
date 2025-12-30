package com.teamventure.app.support;

public class BizException extends RuntimeException {
    private final String code;

    public BizException(String code, String message) {
        super(message);
        this.code = code;
    }

    public BizException(String code) {
        this(code, code);
    }

    public String getCode() {
        return code;
    }
}

