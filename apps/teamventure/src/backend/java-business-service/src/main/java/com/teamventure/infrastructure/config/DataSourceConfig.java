package com.teamventure.infrastructure.config;

import com.alibaba.druid.pool.DruidDataSource;
import java.util.HashMap;
import java.util.Map;
import javax.sql.DataSource;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

@Configuration
public class DataSourceConfig {

    @Bean
    @ConfigurationProperties(prefix = "spring.datasource.druid.master")
    public DataSource masterDataSource() {
        return new DruidDataSource();
    }

    @Bean
    @ConfigurationProperties(prefix = "spring.datasource.druid.slave")
    public DataSource slaveDataSource() {
        return new DruidDataSource();
    }

    @Bean
    @Primary
    public DataSource dataSource(DataSource masterDataSource, DataSource slaveDataSource) {
        RoutingDataSource routing = new RoutingDataSource();
        Map<Object, Object> targets = new HashMap<>();
        targets.put(DataSourceKey.MASTER, masterDataSource);
        targets.put(DataSourceKey.SLAVE, slaveDataSource);
        routing.setTargetDataSources(targets);
        routing.setDefaultTargetDataSource(masterDataSource);
        routing.afterPropertiesSet();
        return routing;
    }
}
