"""TeamVenture系统健康度监控

每小时执行，收集Prometheus监控指标，分析系统健康状况并通过飞书发送报告。

监控范围：
1. 服务状态（Java/Python服务、MySQL、Redis、RabbitMQ）
2. HTTP性能指标（请求量、错误率、响应时间）
3. LLM使用情况（请求数、Token消耗、成本估算）
4. MySQL健康度（连接数、慢查询、QPS）
5. JVM健康度（堆内存、GC次数）
6. 容器资源（CPU、内存使用率）
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import httpx

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tasks.config import config
from src.feishu_bot import get_feishu_bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class TeamVentureHealthMonitor:
    """TeamVenture健康度监控器"""

    def __init__(self, prometheus_url: str = "http://localhost:9090"):
        """
        Args:
            prometheus_url: Prometheus服务地址
        """
        self.prometheus_url = prometheus_url
        self.timestamp = datetime.now()
        self.time_str = self.timestamp.strftime("%Y-%m-%d %H:%M")

    async def query_prometheus(self, query: str) -> Optional[Dict]:
        """执行PromQL查询

        Args:
            query: PromQL查询语句

        Returns:
            查询结果，失败返回None
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.prometheus_url}/api/v1/query",
                    params={"query": query},
                )
                data = response.json()

                if data.get("status") != "success":
                    logger.error(f"Prometheus查询失败: {data}")
                    return None

                return data.get("data", {})

        except Exception as e:
            logger.error(f"Prometheus查询异常 [{query}]: {e}")
            return None

    async def collect_service_status(self) -> Dict[str, Any]:
        """收集服务状态"""
        status_map = {}

        # 查询所有服务的up状态
        result = await self.query_prometheus('up')

        if result and result.get("result"):
            for item in result["result"]:
                job = item["metric"].get("job", "unknown")
                value = int(item["value"][1])
                status_map[job] = "✅ UP" if value == 1 else "❌ DOWN"

        return status_map

    async def collect_http_metrics(self) -> Dict[str, Any]:
        """收集HTTP性能指标"""
        metrics = {}

        # 请求速率（最近5分钟）
        result = await self.query_prometheus(
            'sum(rate(http_requests_total[5m])) by (service)'
        )
        if result and result.get("result"):
            metrics["request_rate"] = {
                item["metric"].get("service", "unknown"): f"{float(item['value'][1]):.2f} req/s"
                for item in result["result"]
            }

        # 错误率（最近5分钟）
        result = await self.query_prometheus(
            'sum(rate(http_requests_total{status=~"5.."}[5m])) by (service) / '
            'sum(rate(http_requests_total[5m])) by (service) * 100'
        )
        if result and result.get("result"):
            metrics["error_rate"] = {
                item["metric"].get("service", "unknown"): f"{float(item['value'][1]):.2f}%"
                for item in result["result"]
            }

        # P95响应时间（最近5分钟）
        result = await self.query_prometheus(
            'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (service, le)) * 1000'
        )
        if result and result.get("result"):
            metrics["p95_latency"] = {
                item["metric"].get("service", "unknown"): f"{float(item['value'][1]):.0f}ms"
                for item in result["result"]
            }

        return metrics

    async def collect_llm_metrics(self) -> Dict[str, Any]:
        """收集LLM使用指标"""
        metrics = {}

        # 请求总数（最近1小时）
        result = await self.query_prometheus(
            'increase(llm_requests_total[1h])'
        )
        if result and result.get("result"):
            total = sum(float(item["value"][1]) for item in result["result"])
            metrics["requests"] = f"{int(total)} 次"

        # Token消耗（最近1小时）
        result = await self.query_prometheus(
            'increase(llm_tokens_total[1h])'
        )
        if result and result.get("result"):
            prompt_tokens = 0
            completion_tokens = 0
            for item in result["result"]:
                token_type = item["metric"].get("type", "")
                value = float(item["value"][1])
                if token_type == "prompt":
                    prompt_tokens += value
                elif token_type == "completion":
                    completion_tokens += value
            metrics["tokens"] = f"输入: {int(prompt_tokens):,} / 输出: {int(completion_tokens):,}"

        # 成本估算（最近1小时）
        result = await self.query_prometheus(
            'increase(llm_estimated_cost_usd[1h])'
        )
        if result and result.get("result"):
            total_cost = sum(float(item["value"][1]) for item in result["result"])
            metrics["cost"] = f"${total_cost:.2f}"

        return metrics

    async def collect_mysql_metrics(self) -> Dict[str, Any]:
        """收集MySQL健康指标"""
        metrics = {}

        # 连接数
        result = await self.query_prometheus(
            'mysql_global_status_threads_connected'
        )
        if result and result.get("result"):
            for item in result["result"]:
                instance = item["metric"].get("instance", "unknown")
                value = int(float(item["value"][1]))
                metrics[f"connections_{instance}"] = f"{value} 个"

        # 慢查询（最近1小时）
        result = await self.query_prometheus(
            'increase(mysql_global_status_slow_queries[1h])'
        )
        if result and result.get("result"):
            for item in result["result"]:
                instance = item["metric"].get("instance", "unknown")
                value = int(float(item["value"][1]))
                metrics[f"slow_queries_{instance}"] = f"{value} 次"

        # QPS（最近5分钟平均）
        result = await self.query_prometheus(
            'rate(mysql_global_status_queries[5m])'
        )
        if result and result.get("result"):
            for item in result["result"]:
                instance = item["metric"].get("instance", "unknown")
                value = float(item["value"][1])
                metrics[f"qps_{instance}"] = f"{value:.2f} q/s"

        return metrics

    async def collect_jvm_metrics(self) -> Dict[str, Any]:
        """收集JVM健康指标"""
        metrics = {}

        # 堆内存使用率
        result = await self.query_prometheus(
            'jvm_memory_used_bytes{area="heap"} / jvm_memory_max_bytes{area="heap"} * 100'
        )
        if result and result.get("result"):
            for item in result["result"]:
                value = float(item["value"][1])
                metrics["heap_usage"] = f"{value:.1f}%"

        # GC次数（最近1小时）
        result = await self.query_prometheus(
            'increase(jvm_gc_pause_seconds_count[1h])'
        )
        if result and result.get("result"):
            total_gc = sum(float(item["value"][1]) for item in result["result"])
            metrics["gc_count"] = f"{int(total_gc)} 次"

        return metrics

    async def collect_container_metrics(self) -> Dict[str, Any]:
        """收集容器资源使用情况"""
        metrics = {}

        # 容器CPU使用率（最近5分钟平均）
        result = await self.query_prometheus(
            'rate(container_cpu_usage_seconds_total{name=~"teamventure.*"}[5m]) * 100'
        )
        if result and result.get("result"):
            for item in result["result"]:
                name = item["metric"].get("name", "unknown")
                value = float(item["value"][1])
                metrics[f"cpu_{name}"] = f"{value:.1f}%"

        # 容器内存使用率
        result = await self.query_prometheus(
            'container_memory_usage_bytes{name=~"teamventure.*"} / '
            'container_spec_memory_limit_bytes{name=~"teamventure.*"} * 100'
        )
        if result and result.get("result"):
            for item in result["result"]:
                name = item["metric"].get("name", "unknown")
                value = float(item["value"][1])
                metrics[f"memory_{name}"] = f"{value:.1f}%"

        return metrics

    def determine_health_status(
        self,
        service_status: Dict,
        http_metrics: Dict,
        llm_metrics: Dict,
        mysql_metrics: Dict,
    ) -> tuple[str, List[str]]:
        """分析指标，判定健康状态

        Returns:
            (状态, 告警列表): 状态为 healthy/degraded/critical
        """
        alerts = []

        # 检查服务状态
        down_services = [
            name for name, status in service_status.items()
            if "DOWN" in status
        ]
        if down_services:
            alerts.append(f"服务宕机: {', '.join(down_services)}")

        # 检查错误率
        error_rates = http_metrics.get("error_rate", {})
        for service, rate_str in error_rates.items():
            rate = float(rate_str.rstrip("%"))
            if rate > 5.0:
                alerts.append(f"{service} 错误率过高: {rate_str}")

        # 检查响应时间
        latencies = http_metrics.get("p95_latency", {})
        for service, latency_str in latencies.items():
            latency = float(latency_str.rstrip("ms"))
            if latency > 1000:
                alerts.append(f"{service} 响应时间过长: {latency_str}")

        # 检查MySQL慢查询
        for key, value in mysql_metrics.items():
            if "slow_queries" in key:
                count = int(value.split()[0])
                if count > 100:
                    alerts.append(f"MySQL慢查询较多: {value}")

        # 判定总体状态
        if down_services or any("错误率过高" in a for a in alerts):
            return "critical", alerts
        elif alerts:
            return "degraded", alerts
        else:
            return "healthy", []

    def generate_report(
        self,
        service_status: Dict,
        http_metrics: Dict,
        llm_metrics: Dict,
        mysql_metrics: Dict,
        jvm_metrics: Dict,
        container_metrics: Dict,
        health_status: str,
        alerts: List[str],
    ) -> str:
        """生成健康度报告（Markdown格式）"""

        # 状态图标
        status_icon = {
            "healthy": "✅",
            "degraded": "⚠️",
            "critical": "🚨",
        }.get(health_status, "❓")

        lines = [
            f"## {status_icon} 系统健康度: {health_status.upper()}",
            "",
            f"**时间**: {self.time_str}",
            "",
        ]

        # 告警信息
        if alerts:
            lines.extend([
                "### 🔔 告警",
                "",
            ])
            for alert in alerts:
                lines.append(f"- {alert}")
            lines.append("")

        # 服务状态
        if service_status:
            lines.extend([
                "### 📊 服务状态",
                "",
            ])
            for service, status in service_status.items():
                lines.append(f"- **{service}**: {status}")
            lines.append("")

        # HTTP性能
        if http_metrics:
            lines.extend([
                "### 🌐 HTTP性能",
                "",
            ])

            if "request_rate" in http_metrics:
                lines.append("**请求速率（5分钟）**:")
                for service, rate in http_metrics["request_rate"].items():
                    lines.append(f"- {service}: {rate}")
                lines.append("")

            if "error_rate" in http_metrics:
                lines.append("**错误率（5分钟）**:")
                for service, rate in http_metrics["error_rate"].items():
                    lines.append(f"- {service}: {rate}")
                lines.append("")

            if "p95_latency" in http_metrics:
                lines.append("**P95响应时间（5分钟）**:")
                for service, latency in http_metrics["p95_latency"].items():
                    lines.append(f"- {service}: {latency}")
                lines.append("")

        # LLM使用情况
        if llm_metrics:
            lines.extend([
                "### 🤖 LLM使用（1小时）",
                "",
            ])
            if "requests" in llm_metrics:
                lines.append(f"- **请求数**: {llm_metrics['requests']}")
            if "tokens" in llm_metrics:
                lines.append(f"- **Token消耗**: {llm_metrics['tokens']}")
            if "cost" in llm_metrics:
                lines.append(f"- **成本估算**: {llm_metrics['cost']}")
            lines.append("")

        # MySQL健康度
        if mysql_metrics:
            lines.extend([
                "### 🗄️ MySQL",
                "",
            ])
            for key, value in mysql_metrics.items():
                label = key.replace("_", " ").title()
                lines.append(f"- **{label}**: {value}")
            lines.append("")

        # JVM健康度
        if jvm_metrics:
            lines.extend([
                "### ☕ JVM",
                "",
            ])
            for key, value in jvm_metrics.items():
                label = key.replace("_", " ").title()
                lines.append(f"- **{label}**: {value}")
            lines.append("")

        # 容器资源
        if container_metrics:
            lines.extend([
                "### 🐳 容器资源",
                "",
            ])
            # 按容器分组显示
            containers = set(
                k.split("_", 1)[1] for k in container_metrics.keys()
            )
            for container in sorted(containers):
                cpu_key = f"cpu_{container}"
                mem_key = f"memory_{container}"
                lines.append(f"**{container}**:")
                if cpu_key in container_metrics:
                    lines.append(f"- CPU: {container_metrics[cpu_key]}")
                if mem_key in container_metrics:
                    lines.append(f"- 内存: {container_metrics[mem_key]}")
                lines.append("")

        return "\n".join(lines)

    async def send_to_feishu(self, report: str, health_status: str):
        """发送报告到飞书

        Args:
            report: 报告内容（Markdown）
            health_status: 健康状态（healthy/degraded/critical）
        """
        try:
            bot = get_feishu_bot()

            # 根据健康状态选择卡片颜色
            template_map = {
                "healthy": "green",
                "degraded": "yellow",
                "critical": "red",
            }
            template = template_map.get(health_status, "blue")

            # 发送卡片消息
            result = await bot.send_card(
                receive_id=config.FEISHU_RECIPIENT_OPEN_ID,
                title="TeamVenture 系统健康度报告",
                content=report,
                template=template,
            )

            logger.info(f"飞书消息发送结果: {result}")

        except Exception as e:
            logger.error(f"发送飞书消息失败: {e}")
            raise

    async def run(self) -> bool:
        """执行健康度检查和报告"""
        logger.info(f"开始执行 TeamVenture 健康度检查 - {self.time_str}")

        try:
            # 并行收集所有指标
            service_status, http_metrics, llm_metrics, mysql_metrics, jvm_metrics, container_metrics = await asyncio.gather(
                self.collect_service_status(),
                self.collect_http_metrics(),
                self.collect_llm_metrics(),
                self.collect_mysql_metrics(),
                self.collect_jvm_metrics(),
                self.collect_container_metrics(),
            )

            logger.info("指标收集完成")

            # 分析健康状态
            health_status, alerts = self.determine_health_status(
                service_status,
                http_metrics,
                llm_metrics,
                mysql_metrics,
            )

            logger.info(f"健康状态: {health_status}, 告警数: {len(alerts)}")

            # 生成报告
            report = self.generate_report(
                service_status,
                http_metrics,
                llm_metrics,
                mysql_metrics,
                jvm_metrics,
                container_metrics,
                health_status,
                alerts,
            )

            # 发送到飞书
            await self.send_to_feishu(report, health_status)

            logger.info("健康度报告发送成功")
            return True

        except Exception as e:
            logger.error(f"健康度检查失败: {e}", exc_info=True)
            return False


async def main_async():
    """异步主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="TeamVenture系统健康度监控")
    parser.add_argument(
        "--prometheus-url",
        type=str,
        default="http://localhost:9090",
        help="Prometheus服务地址",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅生成报告，不发送飞书消息",
    )

    args = parser.parse_args()

    # 创建监控器
    monitor = TeamVentureHealthMonitor(prometheus_url=args.prometheus_url)

    if args.dry_run:
        # 收集指标并打印报告
        service_status, http_metrics, llm_metrics, mysql_metrics, jvm_metrics, container_metrics = await asyncio.gather(
            monitor.collect_service_status(),
            monitor.collect_http_metrics(),
            monitor.collect_llm_metrics(),
            monitor.collect_mysql_metrics(),
            monitor.collect_jvm_metrics(),
            monitor.collect_container_metrics(),
        )

        health_status, alerts = monitor.determine_health_status(
            service_status,
            http_metrics,
            llm_metrics,
            mysql_metrics,
        )

        report = monitor.generate_report(
            service_status,
            http_metrics,
            llm_metrics,
            mysql_metrics,
            jvm_metrics,
            container_metrics,
            health_status,
            alerts,
        )

        print(report)
    else:
        # 执行完整流程
        success = await monitor.run()
        sys.exit(0 if success else 1)


def main():
    """同步主入口（用于launchd调度）"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
