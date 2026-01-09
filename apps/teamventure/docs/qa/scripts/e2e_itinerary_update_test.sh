#!/usr/bin/env bash
#
# E2E: update itinerary via Nginx gateway (no direct Java URL).
#
set -euo pipefail

BASE_URL_DEFAULT="http://api.teamventure.com"
LOGIN_CODE_DEFAULT="qa-code-001"

BASE_URL="$BASE_URL_DEFAULT"
LOGIN_CODE="$LOGIN_CODE_DEFAULT"
PLAN_ID="${PLAN_ID:-}"

usage() {
  cat <<'EOF'
Usage:
  e2e_itinerary_update_test.sh [--base-url URL] [--login-code CODE] [--plan-id PLAN_ID]

Examples:
  # 默认：走网关（需要 /etc/hosts: 127.0.0.1 api.teamventure.com）
  bash apps/teamventure/docs/qa/scripts/e2e_itinerary_update_test.sh

  # 指定 plan_id（避免随机挑一个）
  bash apps/teamventure/docs/qa/scripts/e2e_itinerary_update_test.sh --plan-id plan_xxx
EOF
}

die() { echo "ERROR: $*" >&2; exit 1; }
log() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" >&2; }

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing command: $1"
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --base-url) BASE_URL="$2"; shift 2 ;;
      --login-code) LOGIN_CODE="$2"; shift 2 ;;
      --plan-id) PLAN_ID="$2"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      *) die "unknown arg: $1" ;;
    esac
  done
}

json_get() {
  local path="$1"
  python3 -c '
import json,sys
path=sys.argv[1]
j=json.load(sys.stdin)
cur=j
for part in path.split("."):
  if part.endswith("]") and "[" in part:
    k,idx=part[:-1].split("[", 1)
    if k:
      cur=cur[k]
    cur=cur[int(idx)]
  else:
    cur=cur[part]
print(cur)
' "$path"
}

main() {
  parse_args "$@"
  require_cmd curl
  require_cmd python3

  log "base_url=$BASE_URL"

  local tmp_resp
  tmp_resp="$(mktemp -t tv_itin_put_resp.XXXXXX)"
  trap 'rm -f "'"$tmp_resp"'"' EXIT

  # 0) health
  curl -sS -m 5 "${BASE_URL%/}/actuator/health" >/dev/null 2>&1 || die "gateway health not reachable: ${BASE_URL%/}/actuator/health"
  log "health OK"

  # 1) login
  local login_json token
  login_json="$(curl -sS -m 10 -H 'Content-Type: application/json' -d "{\"code\":\"${LOGIN_CODE}\"}" "${BASE_URL%/}/api/v1/auth/wechat/login")"
  token="$(echo "$login_json" | json_get 'data.sessionToken')"
  [[ -n "$token" ]] || { echo "$login_json"; die "missing sessionToken in login response"; }
  log "login OK"

  # 2) choose plan
  if [[ -z "${PLAN_ID}" ]]; then
    local list_json
    list_json="$(curl -sS -m 10 -H "Authorization: Bearer $token" "${BASE_URL%/}/api/v1/plans?page=1&pageSize=1")"
    PLAN_ID="$(echo "$list_json" | json_get 'data.plans[0].plan_id')"
  fi
  [[ -n "$PLAN_ID" ]] || die "missing plan_id (no plans?)"
  log "plan_id=$PLAN_ID"

  # 3) fetch detail and base_version
  local detail_json base_ver
  detail_json="$(curl -sS -m 10 -H "Authorization: Bearer $token" "${BASE_URL%/}/api/v1/plans/${PLAN_ID}")"
  base_ver="$(echo "$detail_json" | python3 -c 'import json,sys; j=json.load(sys.stdin); print(int((j.get("data") or {}).get("itinerary_version") or 1))')"
  log "base_version=$base_ver"

  # 4) put itinerary (should 200)
  local payload resp1 new_ver
  payload="$(python3 - <<PY
import json,time
itinerary={"days":[{"day":1,"title":"Day 1","items":[{"time":"09:00","title":"Smoke Test","desc":f"updated {int(time.time())}"}]}]}
print(json.dumps({"itinerary":itinerary,"base_version":int($base_ver)}))
PY
)"
  resp1="$(curl -sS -m 10 -X PUT -H "Authorization: Bearer $token" -H 'Content-Type: application/json' --data "$payload" "${BASE_URL%/}/api/v1/plans/${PLAN_ID}/itinerary")"
  new_ver="$(echo "$resp1" | python3 -c 'import json,sys; j=json.load(sys.stdin); assert j.get("success") is True, j; print(int(j["data"]["itinerary_version"]))')"
  [[ "$new_ver" -eq $((base_ver + 1)) ]] || { echo "$resp1"; die "unexpected itinerary_version=$new_ver (expected $((base_ver+1)))"; }
  log "PUT OK itinerary_version=$new_ver"

  # 5) stale put should 409 CAS_CONFLICT
  local status resp2
  status="$(curl -sS -m 10 -o "$tmp_resp" -w "%{http_code}" -X PUT \
    -H "Authorization: Bearer $token" -H 'Content-Type: application/json' --data "$payload" \
    "${BASE_URL%/}/api/v1/plans/${PLAN_ID}/itinerary" || true)"
  resp2="$(cat "$tmp_resp" 2>/dev/null || true)"
  [[ "$status" == "409" ]] || { echo "$resp2"; die "expected 409 for stale put, got $status"; }
  echo "$resp2" | python3 -c 'import json,sys; j=json.load(sys.stdin); assert j.get("success") is False, j; assert (j.get("error") or {}).get("code") == "CAS_CONFLICT", j'
  log "stale PUT => 409 CAS_CONFLICT OK"

  log "done"
}

main "$@"
