package com.teamventure.app.support;

import com.github.f4b6a3.ulid.UlidCreator;

public class IdGenerator {
    public static String newId(String prefix) {
        return prefix + "_" + UlidCreator.getUlid().toString().toLowerCase();
    }
}

