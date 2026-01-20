package com.teamventure.app.support;

import java.util.List;

public class ItineraryMarkdownValidationResult {
    public final boolean valid;
    public final List<String> errors;
    public final int days;
    public final int items;

    public ItineraryMarkdownValidationResult(boolean valid, List<String> errors, int days, int items) {
        this.valid = valid;
        this.errors = errors;
        this.days = days;
        this.items = items;
    }
}

