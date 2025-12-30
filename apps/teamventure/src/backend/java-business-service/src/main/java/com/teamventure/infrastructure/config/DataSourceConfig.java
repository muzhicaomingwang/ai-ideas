package com.teamventure.infrastructure.config;

import com.alibaba.druid.pool.DruidDataSource;
import javax.sql.DataSource;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

@Configuration
public class DataSourceConfig {

    @Bean
    @Primary
    @ConfigurationProperties(prefix = "spring.datasource.druid.master")
    public DataSource dataSource() {
        return new DruidDataSource();
    }
}

