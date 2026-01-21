package com.teamventure.infrastructure.persistence;

import java.sql.Connection;
import java.sql.PreparedStatement;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class DbSchemaMigrator implements CommandLineRunner {
    private static final Logger log = LoggerFactory.getLogger(DbSchemaMigrator.class);

    private final DataSource dataSource;

    public DbSchemaMigrator(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Override
    public void run(String... args) {
        // 当前项目使用 MySQL init 脚本初始化（仅首次生效）。为了让迭代字段在既有数据卷也可用，这里做轻量级幂等迁移。
        ensureColumnExists(
                "plans",
                "logo_url",
                "ALTER TABLE `plans` ADD COLUMN `logo_url` VARCHAR(512) NULL COMMENT '方案Logo图片URL（可选）' AFTER `highlights`"
        );
        ensureColumnExists(
                "plans",
                "logo_storage",
                "ALTER TABLE `plans` ADD COLUMN `logo_storage` VARCHAR(512) NULL COMMENT '方案Logo对象引用（minio://bucket/key，可选）' AFTER `logo_url`"
        );
    }

    private void ensureColumnExists(String table, String column, String alterSql) {
        try (Connection conn = dataSource.getConnection()) {
            if (columnExists(conn, table, column)) {
                return;
            }
            try (PreparedStatement ps = conn.prepareStatement(alterSql)) {
                ps.execute();
            }
            log.info("db schema migrated: add {}.{} ok", table, column);
        } catch (Exception e) {
            // Avoid hard fail on startup; runtime APIs will surface issues if schema is truly incompatible.
            log.warn("db schema migration failed for {}.{}: {}", table, column, e.getMessage());
        }
    }

    private boolean columnExists(Connection conn, String table, String column) throws Exception {
        String sql = """
                SELECT COUNT(*) AS cnt
                FROM information_schema.COLUMNS
                WHERE table_schema = DATABASE()
                  AND table_name = ?
                  AND column_name = ?
                """;
        try (PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, table);
            ps.setString(2, column);
            try (var rs = ps.executeQuery()) {
                if (!rs.next()) return false;
                return rs.getLong(1) > 0;
            }
        }
    }
}
