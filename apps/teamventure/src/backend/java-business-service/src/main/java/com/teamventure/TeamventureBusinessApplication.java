package com.teamventure;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.teamventure.infrastructure.persistence.mapper")
public class TeamventureBusinessApplication {
    public static void main(String[] args) {
        SpringApplication.run(TeamventureBusinessApplication.class, args);
    }
}

