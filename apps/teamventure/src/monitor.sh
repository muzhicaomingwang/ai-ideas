#!/bin/bash
# TeamVenture 终端监控脚本
# 用法: ./monitor.sh [command]

PROM_HOST="http://localhost:9090"
export PATH="$HOME/go/bin:$PATH"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

case "$1" in
    status|s)
        header "服务状态 (up)"
        promql-cli --host $PROM_HOST 'up'
        ;;

    http|h)
        header "HTTP 请求统计 (5分钟)"
        echo -e "${GREEN}请求速率 (req/s):${NC}"
        promql-cli --host $PROM_HOST 'sum(rate(http_server_requests_seconds_count[5m])) by (uri)'
        echo -e "\n${GREEN}错误率 (%):${NC}"
        promql-cli --host $PROM_HOST 'sum(rate(http_server_requests_seconds_count{status=~"5.."}[5m])) / sum(rate(http_server_requests_seconds_count[5m])) * 100'
        echo -e "\n${GREEN}P95 延迟 (ms):${NC}"
        promql-cli --host $PROM_HOST 'histogram_quantile(0.95, sum(rate(http_server_requests_seconds_bucket[5m])) by (le)) * 1000'
        ;;

    llm|l)
        header "LLM/AI 服务指标"
        echo -e "${GREEN}LLM 调用次数:${NC}"
        promql-cli --host $PROM_HOST 'llm_requests_total'
        echo -e "\n${GREEN}Token 使用量:${NC}"
        promql-cli --host $PROM_HOST 'llm_tokens_total'
        echo -e "\n${GREEN}累计成本 (USD):${NC}"
        promql-cli --host $PROM_HOST 'llm_estimated_cost_usd'
        ;;

    mysql|m)
        header "MySQL 数据库指标"
        echo -e "${GREEN}连接数:${NC}"
        promql-cli --host $PROM_HOST 'mysql_global_status_threads_connected'
        echo -e "\n${GREEN}连接使用率 (%):${NC}"
        promql-cli --host $PROM_HOST 'mysql_global_status_threads_connected / mysql_global_variables_max_connections * 100'
        echo -e "\n${GREEN}慢查询总数:${NC}"
        promql-cli --host $PROM_HOST 'mysql_global_status_slow_queries'
        echo -e "\n${GREEN}QPS (5m):${NC}"
        promql-cli --host $PROM_HOST 'rate(mysql_global_status_queries[5m])'
        echo -e "\n${GREEN}Buffer Pool 使用 (MB):${NC}"
        promql-cli --host $PROM_HOST 'mysql_global_status_buffer_pool_pages{state="data"} * 16384 / 1024 / 1024'
        ;;

    jvm|j)
        header "JVM 指标"
        echo -e "${GREEN}Heap 使用率 (%):${NC}"
        promql-cli --host $PROM_HOST 'sum(jvm_memory_used_bytes{area="heap"}) / sum(jvm_memory_max_bytes{area="heap"}) * 100'
        echo -e "\n${GREEN}Heap 使用量 (MB):${NC}"
        promql-cli --host $PROM_HOST 'sum(jvm_memory_used_bytes{area="heap"}) / 1024 / 1024'
        echo -e "\n${GREEN}GC 次数:${NC}"
        promql-cli --host $PROM_HOST 'jvm_gc_pause_seconds_count'
        echo -e "\n${GREEN}线程数:${NC}"
        promql-cli --host $PROM_HOST 'jvm_threads_live_threads'
        ;;

    container|c)
        header "容器资源"
        echo -e "${GREEN}CPU 使用率 (%):${NC}"
        promql-cli --host $PROM_HOST 'sum(rate(container_cpu_usage_seconds_total{name=~"teamventure.*"}[5m])) by (name) * 100'
        echo -e "\n${GREEN}内存使用 (MB):${NC}"
        promql-cli --host $PROM_HOST 'sum(container_memory_usage_bytes{name=~"teamventure.*"}) by (name) / 1024 / 1024'
        ;;

    alerts|a)
        header "告警状态"
        curl -s "$PROM_HOST/api/v1/alerts" | python3 -c "
import json, sys
data = json.load(sys.stdin)
alerts = data.get('data', {}).get('alerts', [])
if not alerts:
    print('  ✅ 无活跃告警')
else:
    for a in alerts:
        state = a.get('state', 'unknown')
        name = a.get('labels', {}).get('alertname', 'unknown')
        severity = a.get('labels', {}).get('severity', 'unknown')
        emoji = '🔴' if state == 'firing' else '🟡'
        print(f'  {emoji} [{severity}] {name}: {state}')
"
        ;;

    all)
        $0 status
        $0 http
        $0 llm
        $0 mysql
        $0 jvm
        $0 alerts
        ;;

    watch|w)
        # 实时监控模式 (每5秒刷新)
        watch -n 5 -c "$0 status"
        ;;

    *)
        echo -e "${YELLOW}TeamVenture 终端监控${NC}"
        echo ""
        echo "用法: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  status, s     服务状态 (up/down)"
        echo "  http, h       HTTP 请求统计"
        echo "  llm, l        LLM/AI 服务指标"
        echo "  mysql, m      MySQL 数据库指标"
        echo "  jvm, j        JVM 内存/GC/线程"
        echo "  container, c  容器 CPU/内存"
        echo "  alerts, a     告警状态"
        echo "  all           显示所有指标"
        echo "  watch, w      实时监控 (5秒刷新)"
        echo ""
        echo "示例:"
        echo "  $0 status     # 查看服务状态"
        echo "  $0 mysql      # 查看 MySQL 指标"
        echo "  $0 all        # 查看所有指标"
        ;;
esac
