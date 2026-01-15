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

    # AI Mock模式（开发测试时减少token消耗）
    enable_ai_mock: bool = False  # True=强制使用mock数据，False=优先真实AI

    # Redis配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = "redis123456"
    redis_db: int = 0

    # AI缓存配置
    ai_cache_enabled: bool = True  # 启用AI响应缓存
    ai_cache_ttl_seconds: int = 86400  # 缓存24小时

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

    # Amap (高德地图) WebService enrichment
    amap_enabled: bool = False
    amap_api_key: str = ""
    amap_base_url: str = "https://restapi.amap.com"
    amap_timeout_seconds: float = 5.0
    amap_cache_ttl_seconds: int = 3600
    amap_cache_max_size: int = 256
    amap_max_pois_per_category: int = 6

    # 日志配置
    log_level: str = "INFO"

    # 每日创意生成配置
    daily_idea_enabled: bool = True
    daily_idea_cron_hour: int = 10
    daily_idea_cron_minute: int = 0

    # Notion 集成（可选）
    notion_page_id: str = ""

    # 飞书集成（可选）
    feishu_doc_token: str = ""
    feishu_chat_id: str = ""


# 全局配置实例
settings = Settings()
