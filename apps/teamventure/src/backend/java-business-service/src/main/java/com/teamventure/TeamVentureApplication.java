package com.teamventure;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * TeamVenture 团建助手主应用
 *
 * <p>技术架构：
 * <ul>
 *   <li>SpringBoot 3.2+</li>
 *   <li>COLA 4层架构（写操作）</li>
 *   <li>传统3层架构（读操作）</li>
 *   <li>MySQL 8.0 主从分离</li>
 *   <li>Redis 缓存与Session管理</li>
 *   <li>RabbitMQ 异步通信</li>
 * </ul>
 *
 * @author TeamVenture Team
 * @version 1.0.0
 * @since 2025-12-30
 */
@SpringBootApplication
@MapperScan("com.teamventure.infrastructure.persistence.mapper")
public class TeamVentureApplication {

    public static void main(String[] args) {
        SpringApplication.run(TeamVentureApplication.class, args);
        System.out.println("""

            ========================================
            🎉 TeamVenture Business Service Started
            ========================================
            📚 API Docs: http://localhost:8080/doc.html
            💚 Health Check: http://localhost:8080/actuator/health
            📊 Metrics: http://localhost:8080/actuator/metrics
            ========================================
            """);
    }
}
