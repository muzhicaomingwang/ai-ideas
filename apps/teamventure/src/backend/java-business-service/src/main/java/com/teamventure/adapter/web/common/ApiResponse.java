package com.teamventure.adapter.web.common;

public class ApiResponse<T> {
    private boolean success;
    private T data;
    private ApiError error;

    public static <T> ApiResponse<T> success(T data) {
        ApiResponse<T> resp = new ApiResponse<>();
        resp.success = true;
        resp.data = data;
        return resp;
    }

    public static ApiResponse<Void> success() {
        return success(null);
    }

    public static ApiResponse<Void> failure(String code, String message) {
        ApiResponse<Void> resp = new ApiResponse<>();
        resp.success = false;
        resp.error = new ApiError(code, message);
        return resp;
    }

    public static <T> ApiResponse<T> failure(String code, String message, T data) {
        ApiResponse<T> resp = new ApiResponse<>();
        resp.success = false;
        resp.error = new ApiError(code, message);
        resp.data = data;
        return resp;
    }

    public boolean isSuccess() {
        return success;
    }

    public T getData() {
        return data;
    }

    public ApiError getError() {
        return error;
    }
}
