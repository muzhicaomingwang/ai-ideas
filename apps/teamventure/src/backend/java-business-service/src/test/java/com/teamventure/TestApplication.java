package com.teamventure;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 测试用Spring Boot应用入口
 *
 * 用途: 为集成测试提供完整的Spring应用上下文
 *
 * 使用方法:
 *   @SpringBootTest(classes = TestApplication.class)
 *   class SomeIntegrationTest { ... }
 */
@SpringBootApplication
public class TestApplication {
    public static void main(String[] args) {
        SpringApplication.run(TestApplication.class, args);
    }
}
