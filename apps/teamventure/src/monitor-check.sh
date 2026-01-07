#!/bin/bash
# TeamVenture 定时健康检查脚本
# 用法:
#   ./monitor-check.sh          # 单次检查
#   ./monitor-check.sh daemon   # 后台持续运行 (每2小时)

PROM_HOST="http://localhost:9090"
LOG_FILE="/tmp/teamventure-monitor.log"
export PATH="$HOME/go/bin:$PATH"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_health() {
    log "========== 健康检查开始 =========="

    ISSUES=0

    # 1. 检查服务状态
    log "检查服务状态..."
    DOWN_SERVICES=$(curl -s "$PROM_HOST/api/v1/query?query=up==0" | python3 -c "
import json,sys
d=json.load(sys.stdin)
results=d.get('data',{}).get('result',[])
for r in results:
    print(r.get('metric',{}).get('job','unknown'))
" 2>/dev/null)

    if [ -n "$DOWN_SERVICES" ]; then
        log "❌ 服务宕机: $DOWN_SERVICES"
        ((ISSUES++))
    else
        log "✅ 所有服务正常"
    fi

    # 2. 检查错误率
    log "检查错误率..."
    ERROR_RATE=$(curl -s "$PROM_HOST/api/v1/query?query=sum(rate(http_server_requests_seconds_count{status=~\"5..\"}[5m]))/sum(rate(http_server_requests_seconds_count[5m]))*100" | python3 -c "
import json,sys
d=json.load(sys.stdin)
results=d.get('data',{}).get('result',[])
if results:
    val=float(results[0].get('value',[0,0])[1])
    if val > 5:
        print(f'{val:.2f}')
" 2>/dev/null)

    if [ -n "$ERROR_RATE" ]; then
        log "⚠️  错误率过高: ${ERROR_RATE}%"
        ((ISSUES++))
    else
        log "✅ 错误率正常"
    fi

    # 3. 检查 MySQL 连接
    log "检查 MySQL 连接..."
    MYSQL_CONN=$(curl -s "$PROM_HOST/api/v1/query?query=mysql_global_status_threads_connected/mysql_global_variables_max_connections*100" | python3 -c "
import json,sys
d=json.load(sys.stdin)
results=d.get('data',{}).get('result',[])
if results:
    val=float(results[0].get('value',[0,0])[1])
    if val > 80:
        print(f'{val:.2f}')
" 2>/dev/null)

    if [ -n "$MYSQL_CONN" ]; then
        log "⚠️  MySQL 连接使用率过高: ${MYSQL_CONN}%"
        ((ISSUES++))
    else
        log "✅ MySQL 连接正常"
    fi

    # 4. 检查 JVM 堆内存
    log "检查 JVM 堆内存..."
    JVM_HEAP=$(curl -s "$PROM_HOST/api/v1/query?query=sum(jvm_memory_used_bytes{area=\"heap\"})/sum(jvm_memory_max_bytes{area=\"heap\"})*100" | python3 -c "
import json,sys
d=json.load(sys.stdin)
results=d.get('data',{}).get('result',[])
if results:
    val=float(results[0].get('value',[0,0])[1])
    if val > 85:
        print(f'{val:.2f}')
" 2>/dev/null)

    if [ -n "$JVM_HEAP" ]; then
        log "⚠️  JVM 堆内存过高: ${JVM_HEAP}%"
        ((ISSUES++))
    else
        log "✅ JVM 堆内存正常"
    fi

    # 5. 检查 Prometheus 告警
    log "检查活跃告警..."
    ALERTS=$(curl -s "$PROM_HOST/api/v1/alerts" | python3 -c "
import json,sys
d=json.load(sys.stdin)
alerts=d.get('data',{}).get('alerts',[])
firing=[a for a in alerts if a.get('state')=='firing']
if firing:
    for a in firing:
        print(a.get('labels',{}).get('alertname','unknown'))
" 2>/dev/null)

    if [ -n "$ALERTS" ]; then
        log "🔴 活跃告警: $ALERTS"
        ((ISSUES++))
    else
        log "✅ 无活跃告警"
    fi

    # 汇总
    log "========== 检查完成 =========="
    if [ $ISSUES -eq 0 ]; then
        log "🟢 系统健康，无异常"
    else
        log "🔴 发现 $ISSUES 个问题，请检查!"
    fi
    echo ""

    return $ISSUES
}

case "$1" in
    daemon)
        log "启动后台监控 (每2小时检查一次)"
        log "日志文件: $LOG_FILE"
        log "停止: kill $(echo $$)"

        while true; do
            check_health
            sleep 7200  # 2小时 = 7200秒
        done
        ;;
    *)
        check_health
        ;;
esac
