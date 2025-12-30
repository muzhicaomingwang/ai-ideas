"""
RabbitMQ 消费者模块

负责：
1. 监听 Java 服务发送的方案生成请求
2. 触发 LangGraph 工作流
3. 回调 Java 服务写入生成结果
"""

import json
import logging
from typing import Any

import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustChannel, AbstractRobustConnection

from src.integrations.java_client import JavaCallbackClient
from src.langgraph.workflow import run_generation_workflow
from src.models.config import settings

logger = logging.getLogger(__name__)

_connection: AbstractRobustConnection | None = None
_channel: AbstractRobustChannel | None = None
_consumer_tag: str | None = None


def _amqp_url() -> str:
    return (
        f"amqp://{settings.rabbitmq_user}:{settings.rabbitmq_password}"
        f"@{settings.rabbitmq_host}:{settings.rabbitmq_port}{settings.rabbitmq_vhost}"
    )


async def start_mq_consumer():
    """启动MQ消费者"""
    logger.info("Starting MQ consumer...")
    global _connection, _channel, _consumer_tag

    if _connection is not None:
        logger.info("MQ consumer already started")
        return

    _connection = await aio_pika.connect_robust(_amqp_url())
    _channel = await _connection.channel()
    await _channel.set_qos(prefetch_count=5)

    exchange = await _channel.declare_exchange(
        settings.mq_exchange,
        aio_pika.ExchangeType.TOPIC,
        durable=True,
    )
    queue = await _channel.declare_queue(settings.mq_queue, durable=True)
    await queue.bind(exchange, routing_key=settings.mq_routing_key)

    async def on_message(message: AbstractIncomingMessage) -> None:
        async with message.process(ignore_processed=True, requeue=False):
            body = message.body.decode("utf-8")
            payload: dict[str, Any] = json.loads(body)
            logger.info("Received plan generation message: %s", payload.get("plan_request_id"))

            state = await run_generation_workflow(payload)
            if state.get("error"):
                logger.error("Plan generation failed: %s", state["error"])
                return

            callback_payload = {
                "plan_request_id": state["plan_request_id"],
                "user_id": state["user_id"],
                "plans": state.get("generated_plans", []),
                "trace_id": payload.get("trace_id"),
            }
            client = JavaCallbackClient()
            await client.post_generated_plans(callback_payload)

    _consumer_tag = await queue.consume(on_message)
    logger.info("MQ consumer ready: exchange=%s queue=%s", settings.mq_exchange, settings.mq_queue)


async def stop_mq_consumer():
    """停止MQ消费者"""
    logger.info("Stopping MQ consumer...")
    global _connection, _channel, _consumer_tag

    try:
        if _channel is not None and _consumer_tag is not None:
            await _channel.basic_cancel(_consumer_tag)
    finally:
        _consumer_tag = None

    try:
        if _channel is not None:
            await _channel.close()
    finally:
        _channel = None

    try:
        if _connection is not None:
            await _connection.close()
    finally:
        _connection = None

    logger.info("MQ consumer stopped")


async def handle_plan_request(message: dict):
    """
    处理方案生成请求

    Args:
        message: 来自Java的请求消息
            {
                "plan_request_id": "plan_req_xxx",
                "user_id": "user_xxx",
                "people_count": 50,
                "budget_min": 25000,
                "budget_max": 35000,
                "start_date": "2026-01-10",
                "end_date": "2026-01-11",
                "departure_city": "北京",
                "preferences": {...}
            }
    """
    logger.info(f"Handling plan request: {message.get('plan_request_id')}")

    state = await run_generation_workflow(message)
    if state.get("error"):
        return {"plan_request_id": message.get("plan_request_id"), "status": "failed", "error": state["error"]}
    return {
        "plan_request_id": state["plan_request_id"],
        "status": "generated",
        "plans": state.get("generated_plans", []),
    }
