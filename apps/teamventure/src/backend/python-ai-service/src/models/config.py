"""
应用配置模块

使用 pydantic-settings 管理配置，支持：
- 环境变量
- .env 文件
- 默认值
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # 应用配置
    app_name: str = "teamventure-ai-service"
    version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # OpenAI配置
    openai_api_key: str = "sk-xxxxxxxxxxxxx"
    openai_model: str = "gpt-4-0125-preview"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 4000

    # Redis配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = "redis123456"
    redis_db: int = 0

    # RabbitMQ配置
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "admin"
    rabbitmq_password: str = "admin123456"
    rabbitmq_vhost: str = "/"

    # MQ Exchange/Queue配置
    mq_exchange: str = "plan.generation.topic"
    mq_queue: str = "ai.gen.req.queue"
    mq_routing_key: str = "plan.request.#"

    # Java服务回调配置
    java_callback_url: str = "http://localhost:8080/internal/plans/batch"
    java_internal_secret: str = "change-this-in-production"

    # 日志配置
    log_level: str = "INFO"


# 全局配置实例
settings = Settings()
