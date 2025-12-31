#!/usr/bin/env bash
#
# TeamVenture 后端 API 全覆盖回归脚本（基于 QA 一步一步测试计划）
#
# 功能：
# 1) 选择环境（--env-file），启动 docker compose
# 2) 等待 Java/Python 健康检查可用
# 3) 通过网关调用 API：登录 → 生成（异步）→ 轮询直到 3 套方案落库 → 列表/详情 → 确认(幂等) → 供应商查询/详情 → 记录联系
# 4) 输出 MQ 队列 consumers/messages 作为进度与定位线索
# 5) 失败时自动打印关键容器日志尾部，便于快速提 bug/修复
#
# 依赖：
# - bash 4+
# - docker / docker compose
# - curl
# - python3（用于 JSON 解析/断言；避免依赖 jq）
#
# 注意：
# - base URL 默认 http://api.teamVenture.com，需要 QA 机器 /etc/hosts 配置：127.0.0.1 api.teamVenture.com
# - 真实大模型调用：请在 env-file（默认 apps/teamVenture/src/.env.local）中配置 OPENAI_API_KEY
#
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../../../../.." && pwd)"

COMPOSE_FILE_DEFAULT="${REPO_ROOT}/apps/teamVenture/src/docker-compose.yml"
ENV_FILE_DEFAULT="${REPO_ROOT}/apps/teamVenture/src/.env.local"

BASE_URL_DEFAULT="http://api.teamVenture.com"
JAVA_DIRECT_URL_DEFAULT="http://localhost:8080"

COMPOSE_FILE="${COMPOSE_FILE_DEFAULT}"
ENV_FILE="${ENV_FILE_DEFAULT}"
BASE_URL="${BASE_URL_DEFAULT}"
JAVA_DIRECT_URL="${JAVA_DIRECT_URL_DEFAULT}"

LOGIN_CODE="qa-code-001"
POLL_MAX_ATTEMPTS=30
POLL_INTERVAL_SEC=1

usage() {
  cat <<'EOF'
Usage:
  run_backend_api_full_coverage.sh [--env-file PATH] [--compose-file PATH] [--base-url URL] [--java-direct-url URL]
                                  [--login-code CODE] [--poll-max N] [--poll-interval-sec N]

Examples:
  # 本地（默认 .env.local），网关用 api.teamVenture.com（需要 /etc/hosts）
  ./apps/teamVenture/docs/qa/scripts/run_backend_api_full_coverage.sh

  # 指定 dev 环境文件
  ./apps/teamVenture/docs/qa/scripts/run_backend_api_full_coverage.sh --env-file apps/teamVenture/src/.env.dev

Notes:
  - --base-url 默认 http://api.teamVenture.com（走 Nginx 网关）；如果你只想直连 Java，可改成 http://localhost:8080
  - internal 回写接口未通过 Nginx 暴露；需要直连 Java（--java-direct-url，默认 http://localhost:8080）
EOF
}

die() {
  echo "ERROR: $*" >&2
  exit 1
}

log() {
  # 统一时间戳，便于对齐容器日志
  printf '[%s] %s\n' "$(date '+%F %T')" "$*" >&2
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing command: $1"
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --compose-file) COMPOSE_FILE="$2"; shift 2 ;;
      --env-file) ENV_FILE="$2"; shift 2 ;;
      --base-url) BASE_URL="$2"; shift 2 ;;
      --java-direct-url) JAVA_DIRECT_URL="$2"; shift 2 ;;
      --login-code) LOGIN_CODE="$2"; shift 2 ;;
      --poll-max) POLL_MAX_ATTEMPTS="$2"; shift 2 ;;
      --poll-interval-sec) POLL_INTERVAL_SEC="$2"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      *) die "unknown arg: $1" ;;
    esac
  done
}

# curl 工具函数：返回 "status|body"，由调用方拆分
curl_json() {
  local method="$1"; shift
  local url="$1"; shift
  local data="${1:-}"

  local headers=()
  headers+=(-H "Accept: application/json")
  # 额外 header 通过环境变量 CURL_EXTRA_HEADERS 传入（多行，每行一个 -H 'k:v'）
  if [[ -n "${CURL_EXTRA_HEADERS:-}" ]]; then
    while IFS= read -r h; do
      [[ -z "$h" ]] && continue
      headers+=(-H "$h")
    done <<<"${CURL_EXTRA_HEADERS}"
  fi

  local args=(-sS -m 30 -X "$method" "${headers[@]}" -w "\n|||STATUS:%{http_code}|||" "$url")
  if [[ -n "$data" ]]; then
    args+=(-H "Content-Type: application/json" --data "$data")
  fi

  curl "${args[@]}"
}

# 解析 curl_json 输出，设置全局变量 CURL_STATUS 和 CURL_BODY
parse_curl_response() {
  local response="$1"
  CURL_BODY="$(echo "$response" | sed 's/|||STATUS:[0-9]*|||$//')"
  CURL_STATUS="$(echo "$response" | grep -o '|||STATUS:[0-9]*|||$' | sed 's/|||STATUS://;s/|||$//')"
}

py_assert() {
  local expr="$1"
  local json_input
  json_input="$(cat)"
  JSON_INPUT="$json_input" PY_EXPR="$expr" python3 <<'PY'
import json, os
data = json.loads(os.environ.get('JSON_INPUT', '{}'))
PY_EXPR = os.environ.get('PY_EXPR', 'True')
assert eval(PY_EXPR), f"assertion failed: {PY_EXPR}"
print("OK")
PY
}

py_get() {
  local expr="$1"
  local json_input
  json_input="$(cat)"
  JSON_INPUT="$json_input" PY_EXPR="$expr" python3 <<'PY'
import json, os
data = json.loads(os.environ.get('JSON_INPUT', '{}'))
val = eval(os.environ.get('PY_EXPR', 'None'))
if val is None:
  print("")
else:
  print(val)
PY
}

dump_debug_logs() {
  log "=== debug: docker ps ==="
  docker ps --filter name=teamventure- --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' || true

  log "=== debug: rabbitmq queues ==="
  docker exec teamventure-rabbitmq rabbitmqctl list_queues name messages consumers 2>/dev/null | sed -n '1,60p' || true

  log "=== debug: nginx logs (tail) ==="
  docker logs --tail=120 teamventure-nginx 2>/dev/null || true

  log "=== debug: java logs (tail) ==="
  docker logs --tail=200 teamventure-java 2>/dev/null || true

  log "=== debug: python logs (tail) ==="
  docker logs --tail=200 teamventure-python 2>/dev/null || true
}

main() {
  parse_args "$@"

  require_cmd docker
  require_cmd curl
  require_cmd python3

  [[ -f "$COMPOSE_FILE" ]] || die "compose file not found: $COMPOSE_FILE"
  [[ -f "$ENV_FILE" ]] || die "env file not found: $ENV_FILE"

  log "compose_file=$COMPOSE_FILE"
  log "env_file=$ENV_FILE"
  log "base_url=$BASE_URL"
  log "java_direct_url=$JAVA_DIRECT_URL"

  # 0) 启动环境
  log "Step 0: docker compose up -d"
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d

  # 1) 等待健康检查
  log "Step 1: wait for Java health (/actuator/health) and Python health (/ai/health)"

  local java_health_url="${BASE_URL%/}/actuator/health"
  local python_health_url="${BASE_URL%/}/ai/health"

  local i
  for i in {1..60}; do
    if curl -sS -m 3 "$java_health_url" >/dev/null 2>&1 && curl -sS -m 3 "$python_health_url" >/dev/null 2>&1; then
      log "health endpoints reachable"
      break
    fi
    sleep 1
  done
  if ! curl -sS -m 3 "$java_health_url" >/dev/null 2>&1; then
    dump_debug_logs
    die "java health not reachable: $java_health_url"
  fi
  if ! curl -sS -m 3 "$python_health_url" >/dev/null 2>&1; then
    dump_debug_logs
    die "python health not reachable: $python_health_url"
  fi

  # 2) 登录拿 token
  log "Step 2: login to get session_token"
  local login_body
  login_body="$(printf '{"code":"%s"}' "$LOGIN_CODE")"
  CURL_EXTRA_HEADERS=""
  local login_raw
  login_raw="$(curl_json POST "${BASE_URL%/}/api/v1/auth/wechat/login" "$login_body")" || {
    dump_debug_logs
    die "login request failed"
  }
  parse_curl_response "$login_raw"
  [[ "$CURL_STATUS" == "200" ]] || { echo "$CURL_BODY"; dump_debug_logs; die "login http status=$CURL_STATUS"; }
  echo "$CURL_BODY" | py_assert "data.get('success') is True"
  local session_token user_id
  session_token="$(echo "$CURL_BODY" | py_get "data['data']['session_token']")"
  user_id="$(echo "$CURL_BODY" | py_get "data['data']['user_id']")"
  [[ -n "$session_token" ]] || { dump_debug_logs; die "missing session_token in login response"; }
  log "login OK user_id=$user_id"

  # 3) 供应商查询（拿一个 supplierId）
  log "Step 3: suppliers search"
  CURL_EXTRA_HEADERS=$'Authorization: Bearer '"$session_token"
  local sup_list_raw
  sup_list_raw="$(curl_json GET "${BASE_URL%/}/api/v1/suppliers")" || {
    dump_debug_logs
    die "suppliers search failed"
  }
  [[ "$CURL_STATUS" == "200" ]] || { echo "$CURL_BODY"; dump_debug_logs; die "suppliers search http status=$CURL_STATUS"; }
  parse_curl_response "$sup_list_raw"
  echo "$CURL_BODY" | py_assert "data.get('success') is True"
  local supplier_id
  supplier_id="$(echo "$CURL_BODY" | py_get "(data.get('data') or [{}])[0].get('supplierId') or (data.get('data') or [{}])[0].get('supplier_id')")"
  if [[ -z "$supplier_id" ]]; then
    log "WARN: supplier list empty; ensure DB seed applied (V1.0.1__seed_suppliers.sql)"
  else
    log "supplier_id=$supplier_id"
  fi

  # 4) 发起生成（异步）
  log "Step 4: plans generate (async)"
  local gen_body
  gen_body="$(cat <<JSON
{
  "people_count": 50,
  "budget_min": 25000,
  "budget_max": 35000,
  "start_date": "2026-01-10",
  "end_date": "2026-01-11",
  "departure_city": "北京",
  "preferences": { "qa_run_at": "$(date -Iseconds)" }
}
JSON
)"
  local gen_resp
  gen_raw="$(curl_json POST "${BASE_URL%/}/api/v1/plans/generate" "$gen_body")" || {
    dump_debug_logs
    die "plans generate failed"
  }
  [[ "$CURL_STATUS" == "200" ]] || { echo "$CURL_BODY"; dump_debug_logs; die "plans generate http status=$CURL_STATUS"; }
  parse_curl_response "$gen_raw"
  echo "$CURL_BODY" | py_assert "data.get('success') is True"
  local plan_request_id
  plan_request_id="$(echo "$CURL_BODY" | py_get "data['data']['plan_request_id']")"
  [[ -n "$plan_request_id" ]] || { dump_debug_logs; die "missing plan_request_id"; }
  log "plan_request_id=$plan_request_id"

  # 5) MQ 观测：队列消费者/积压
  log "Step 5: MQ queue check (consumers/messages)"
  docker exec teamventure-rabbitmq rabbitmqctl list_queues name messages consumers | sed -n '1,60p' || true

  # 6) 轮询 plans 列表，直到 records >= 3
  log "Step 6: poll plans list until >= 3 records (max=${POLL_MAX_ATTEMPTS}, interval=${POLL_INTERVAL_SEC}s)"
  local attempt=0
  local list_raw=""
  local list_resp_body=""
  local record_count=0
  while [[ $attempt -lt $POLL_MAX_ATTEMPTS ]]; do
    attempt=$((attempt + 1))
    list_raw="$(curl_json GET "${BASE_URL%/}/api/v1/plans?page=1&pageSize=10")" || {
      dump_debug_logs
      die "plans list failed during polling"
    }
    parse_curl_response "$list_raw"
    list_resp_body="$CURL_BODY"
    if [[ "$CURL_STATUS" != "200" ]]; then
      echo "$CURL_BODY"
      dump_debug_logs
      die "plans list http status=$CURL_STATUS"
    fi
    echo "$CURL_BODY" | py_assert "data.get('success') is True"
    record_count="$(echo "$CURL_BODY" | py_get "len((((data or {}).get('data') or {}).get('records')) or [])")"
    log "poll attempt=${attempt}: records=${record_count}"
    if [[ "$record_count" -ge 3 ]]; then
      break
    fi
    sleep "$POLL_INTERVAL_SEC"
  done
  if [[ "$record_count" -lt 3 ]]; then
    log "polling did not reach 3 plans in time"
    dump_debug_logs
    die "plans not generated within polling window"
  fi

  # 7) 取一个 planId，调详情
  log "Step 7: plan detail"
  local plan_id
  plan_id="$(echo "$CURL_BODY" | python3 - <<'PY'
import json, sys
j = json.loads(sys.stdin.read() or "{}")
records = (((j or {}).get("data") or {}).get("records")) or []
first = records[0] if records else {}
print(first.get("planId") or first.get("plan_id") or "")
PY
)"
  [[ -n "$plan_id" ]] || { dump_debug_logs; die "missing plan_id from list"; }
  local detail_resp
  detail_raw="$(curl_json GET "${BASE_URL%/}/api/v1/plans/${plan_id}")" || {
    dump_debug_logs
    die "plan detail failed"
  }
  [[ "$CURL_STATUS" == "200" ]] || { echo "$CURL_BODY"; dump_debug_logs; die "plan detail http status=$CURL_STATUS"; }
  parse_curl_response "$detail_raw"
  echo "$CURL_BODY" | py_assert "data.get('success') is True"

  # 8) confirm 幂等（调用两次都应成功）
  log "Step 8: confirm plan (idempotent) - twice"
  local confirm_raw_1 confirm_raw_2
  confirm_raw_1="$(curl_json POST "${BASE_URL%/}/api/v1/plans/${plan_id}/confirm" "")" || {
    dump_debug_logs
    die "plan confirm #1 failed"
  }
  parse_curl_response "$confirm_raw_1"
  [[ "$CURL_STATUS" == "200" ]] || { echo "$CURL_BODY"; dump_debug_logs; die "plan confirm #1 http status=$CURL_STATUS"; }
  echo "$CURL_BODY" | py_assert "data.get('success') is True"

  confirm_raw_2="$(curl_json POST "${BASE_URL%/}/api/v1/plans/${plan_id}/confirm" "")" || {
    dump_debug_logs
    die "plan confirm #2 failed"
  }
  parse_curl_response "$confirm_raw_2"
  [[ "$CURL_STATUS" == "200" ]] || { echo "$CURL_BODY"; dump_debug_logs; die "plan confirm #2 http status=$CURL_STATUS"; }
  echo "$CURL_BODY" | py_assert "data.get('success') is True"

  # 9) 供应商详情（如果有 supplier_id）
  if [[ -n "$supplier_id" ]]; then
    log "Step 9: supplier detail"
    local sup_detail_resp
    sup_detail_raw="$(curl_json GET "${BASE_URL%/}/api/v1/suppliers/${supplier_id}")" || {
      dump_debug_logs
      die "supplier detail failed"
    }
    [[ "$CURL_STATUS" == "200" ]] || { echo "$CURL_BODY"; dump_debug_logs; die "supplier detail http status=$CURL_STATUS"; }
  parse_curl_response "$sup_detail_raw"
    echo "$CURL_BODY" | py_assert "data.get('success') is True"
  else
    log "Step 9: skip supplier detail (no supplier_id)"
  fi

  # 10) 记录联系供应商（如果有 supplier_id）
  if [[ -n "$supplier_id" ]]; then
    log "Step 10: record supplier contact"
    local contact_body
    contact_body="$(printf '{"supplier_id":"%s","channel":"PHONE","notes":"qa-run %s"}' "$supplier_id" "$(date -Iseconds)")"
    local contact_resp
    contact_resp="$(curl_json POST "${BASE_URL%/}/api/v1/plans/${plan_id}/supplier-contacts" "$contact_body")" || {
      dump_debug_logs
      die "supplier contact failed"
    }
    [[ "$CURL_STATUS" == "200" ]] || { echo "$CURL_BODY"; dump_debug_logs; die "supplier contact http status=$CURL_STATUS"; }
    echo "$CURL_BODY" | py_assert "data.get('success') is True"
  else
    log "Step 10: skip supplier contact (no supplier_id)"
  fi

  # 11) Internal callback 安全性（密钥错误应拒绝）
  # 注意：该接口未走 Nginx；这里直连 Java（默认 http://localhost:8080）
  log "Step 11: internal callback security (wrong secret should be rejected)"
  CURL_EXTRA_HEADERS="X-Internal-Secret: wrong"
  local internal_body
  internal_body="$(printf '{"plan_request_id":"%s","user_id":"%s","plans":[],"trace_id":"trace_qa"}' "$plan_request_id" "$user_id")"
  local internal_resp
  internal_resp="$(curl_json POST "${JAVA_DIRECT_URL%/}/internal/plans/batch" "$internal_body")" || {
    dump_debug_logs
    die "internal callback request failed"
  }
  [[ "$CURL_STATUS" == "200" ]] || { echo "$CURL_BODY"; dump_debug_logs; die "internal callback http status=$CURL_STATUS"; }
  echo "$CURL_BODY" | py_assert "data.get('success') is False and (data.get('error') or {}).get('code') == 'UNAUTHORIZED'"

  log "ALL PASSED"
}

trap 'dump_debug_logs' ERR
main "$@"

