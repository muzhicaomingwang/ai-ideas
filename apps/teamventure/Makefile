# TeamVenture 项目管理 Makefile
# 使用方法：make [命令]

.PHONY: help init up down restart logs build clean ps exec-java exec-python exec-mysql exec-redis test

# 默认环境（可通过 make ENV=dev up 来指定）
ENV ?= local

# Docker Compose 文件路径
COMPOSE_FILE = src/docker-compose.yml
COMPOSE = docker compose -f $(COMPOSE_FILE)

# 环境变量文件
ENV_FILE = src/.env.$(ENV)

##@ 帮助命令

help: ## 显示帮助信息
	@echo "TeamVenture 项目管理命令"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "\033[36m使用方法:\033[0m\n  make \033[36m<命令>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""
	@echo "环境变量："
	@echo "  ENV=local|dev|beta|prod (默认: local)"
	@echo ""
	@echo "示例："
	@echo "  make up              # 使用 local 环境启动"
	@echo "  make ENV=dev up      # 使用 dev 环境启动"
	@echo "  make logs SERVICE=java-business-service  # 查看指定服务日志"

##@ 初始化命令

init: ## 初始化项目环境
	@echo "初始化 TeamVenture 项目..."
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "错误: 环境配置文件 $(ENV_FILE) 不存在"; \
		exit 1; \
	fi
	@echo "使用环境配置: $(ENV_FILE)"
	@echo "创建必要的目录..."
	@mkdir -p src/database/schema
	@echo "检查 Docker 和 Docker Compose..."
	@docker --version
	@docker compose version
	@echo "✓ 初始化完成"

check-env: ## 检查环境配置
	@echo "当前环境: $(ENV)"
	@echo "配置文件: $(ENV_FILE)"
	@if [ -f $(ENV_FILE) ]; then \
		echo "✓ 配置文件存在"; \
		cat $(ENV_FILE); \
	else \
		echo "✗ 配置文件不存在"; \
		exit 1; \
	fi

##@ Docker 服务管理

up: init ## 启动所有服务
	@echo "启动 TeamVenture 服务 (环境: $(ENV))..."
	$(COMPOSE) --env-file $(ENV_FILE) up -d
	@echo "✓ 服务启动完成"
	@echo ""
	@make ps

down: ## 停止并删除所有服务
	@echo "停止 TeamVenture 服务..."
	$(COMPOSE) down
	@echo "✓ 服务已停止"

stop: ## 停止所有服务（不删除容器）
	@echo "停止 TeamVenture 服务..."
	$(COMPOSE) stop
	@echo "✓ 服务已停止"

start: ## 启动已停止的服务
	@echo "启动 TeamVenture 服务..."
	$(COMPOSE) start
	@echo "✓ 服务已启动"

restart: ## 重启所有服务
	@echo "重启 TeamVenture 服务..."
	$(COMPOSE) restart
	@echo "✓ 服务已重启"

ps: ## 查看服务状态
	@echo "TeamVenture 服务状态："
	@$(COMPOSE) ps

##@ 构建命令

build: ## 构建所有服务镜像
	@echo "构建 TeamVenture 服务镜像..."
	$(COMPOSE) build --no-cache
	@echo "✓ 构建完成"

build-java: ## 构建 Java 服务镜像
	@echo "构建 Java 业务服务镜像..."
	$(COMPOSE) build --no-cache java-business-service
	@echo "✓ Java 服务构建完成"

build-python: ## 构建 Python 服务镜像
	@echo "构建 Python AI 服务镜像..."
	$(COMPOSE) build --no-cache python-ai-service
	@echo "✓ Python 服务构建完成"

rebuild: down build up ## 完全重建并启动服务

##@ 日志查看

logs: ## 查看所有服务日志 (可选: SERVICE=服务名)
	@if [ -z "$(SERVICE)" ]; then \
		$(COMPOSE) logs -f; \
	else \
		$(COMPOSE) logs -f $(SERVICE); \
	fi

logs-java: ## 查看 Java 服务日志
	@$(COMPOSE) logs -f java-business-service

logs-python: ## 查看 Python 服务日志
	@$(COMPOSE) logs -f python-ai-service

logs-nginx: ## 查看 Nginx 日志
	@$(COMPOSE) logs -f nginx

logs-mysql: ## 查看 MySQL 日志
	@$(COMPOSE) logs -f mysql-master

logs-redis: ## 查看 Redis 日志
	@$(COMPOSE) logs -f redis

logs-rabbitmq: ## 查看 RabbitMQ 日志
	@$(COMPOSE) logs -f rabbitmq

##@ 容器操作

exec-java: ## 进入 Java 服务容器
	@$(COMPOSE) exec java-business-service /bin/sh

exec-python: ## 进入 Python 服务容器
	@$(COMPOSE) exec python-ai-service /bin/sh

exec-mysql: ## 进入 MySQL 主库容器
	@$(COMPOSE) exec mysql-master mysql -uroot -proot123456

exec-redis: ## 进入 Redis 容器
	@$(COMPOSE) exec redis redis-cli -a redis123456

exec-rabbitmq: ## 进入 RabbitMQ 容器
	@$(COMPOSE) exec rabbitmq /bin/bash

exec-nginx: ## 进入 Nginx 容器
	@$(COMPOSE) exec nginx /bin/sh

##@ 数据库操作

db-init: ## 初始化数据库
	@echo "初始化数据库..."
	@$(COMPOSE) exec mysql-master mysql -uroot -proot123456 -e "SHOW DATABASES;"
	@echo "✓ 数据库初始化完成"

db-backup: ## 备份数据库
	@echo "备份数据库..."
	@mkdir -p backup
	@$(COMPOSE) exec -T mysql-master mysqldump -uroot -proot123456 --all-databases > backup/teamventure_backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✓ 数据库备份完成"

db-restore: ## 恢复数据库 (使用: make db-restore FILE=backup.sql)
	@if [ -z "$(FILE)" ]; then \
		echo "错误: 请指定备份文件，例如: make db-restore FILE=backup/xxx.sql"; \
		exit 1; \
	fi
	@echo "恢复数据库从 $(FILE)..."
	@$(COMPOSE) exec -T mysql-master mysql -uroot -proot123456 < $(FILE)
	@echo "✓ 数据库恢复完成"

##@ 清理命令

clean: down ## 停止服务并清理所有容器、网络
	@echo "清理 Docker 资源..."
	$(COMPOSE) down -v --remove-orphans
	@echo "✓ 清理完成"

clean-volumes: ## 清理所有数据卷（危险操作，会删除所有数据）
	@echo "警告: 这将删除所有数据卷，包括数据库数据！"
	@read -p "确认继续？(yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		$(COMPOSE) down -v; \
		echo "✓ 数据卷已清理"; \
	else \
		echo "操作已取消"; \
	fi

clean-images: ## 清理构建的镜像
	@echo "清理 TeamVenture 镜像..."
	@docker images | grep teamventure | awk '{print $$3}' | xargs -r docker rmi -f
	@echo "✓ 镜像清理完成"

##@ 测试命令

test: ## 运行所有测试
	@echo "运行测试..."
	@echo "Java 服务测试:"
	@cd src/backend/java-business-service && mvn test
	@echo "Python 服务测试:"
	@cd src/backend/python-ai-service && poetry run pytest
	@echo "✓ 测试完成"

test-java: ## 运行 Java 服务测试
	@echo "运行 Java 服务测试..."
	@cd src/backend/java-business-service && mvn test

test-python: ## 运行 Python 服务测试
	@echo "运行 Python 服务测试..."
	@cd src/backend/python-ai-service && poetry run pytest

##@ 健康检查

health: ## 检查所有服务健康状态
	@echo "检查服务健康状态..."
	@echo ""
	@echo "Nginx (HTTP):"
	@curl -f http://localhost:80/health || echo "✗ 不健康"
	@echo ""
	@echo "Java 服务:"
	@curl -f http://localhost:8080/actuator/health || echo "✗ 不健康"
	@echo ""
	@echo "Python 服务:"
	@curl -f http://localhost:8000/health || echo "✗ 不健康"
	@echo ""
	@echo "MySQL:"
	@$(COMPOSE) exec mysql-master mysqladmin ping -uroot -proot123456 || echo "✗ 不健康"
	@echo ""
	@echo "Redis:"
	@$(COMPOSE) exec redis redis-cli -a redis123456 ping || echo "✗ 不健康"
	@echo ""
	@echo "RabbitMQ:"
	@curl -f http://localhost:15672/api/health/checks/alarms -u admin:admin123456 || echo "✗ 不健康"

##@ 开发辅助

dev: ## 开发模式（启动服务并查看日志）
	@make ENV=dev up
	@make logs

shell-java: ## 在 Java 服务中运行 Maven 命令
	@echo "进入 Java 服务 shell..."
	@cd src/backend/java-business-service && /bin/bash

shell-python: ## 在 Python 服务中运行 Poetry 命令
	@echo "进入 Python 服务 shell..."
	@cd src/backend/python-ai-service && /bin/bash

format-java: ## 格式化 Java 代码
	@echo "格式化 Java 代码..."
	@cd src/backend/java-business-service && mvn spotless:apply

format-python: ## 格式化 Python 代码
	@echo "格式化 Python 代码..."
	@cd src/backend/python-ai-service && poetry run black . && poetry run isort .

##@ 监控命令

stats: ## 查看容器资源使用情况
	@docker stats $$($(COMPOSE) ps -q)

top: ## 查看容器进程
	@$(COMPOSE) top
