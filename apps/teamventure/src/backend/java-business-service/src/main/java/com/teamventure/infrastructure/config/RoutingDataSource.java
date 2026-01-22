package com.teamventure.infrastructure.config;

import org.springframework.jdbc.datasource.lookup.AbstractRoutingDataSource;
import org.springframework.transaction.support.TransactionSynchronizationManager;

public class RoutingDataSource extends AbstractRoutingDataSource {
    @Override
    protected Object determineCurrentLookupKey() {
        if (TransactionSynchronizationManager.isActualTransactionActive()
                && TransactionSynchronizationManager.isCurrentTransactionReadOnly()) {
            return DataSourceKey.SLAVE;
        }
        return DataSourceKey.MASTER;
    }
}

