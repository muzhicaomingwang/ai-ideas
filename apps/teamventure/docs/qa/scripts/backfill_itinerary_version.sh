#!/usr/bin/env bash
#
# Backfill plans.itinerary_version to 1 when missing/NULL to prevent CAS permanent conflicts.
#
# Default target: docker compose service "mysql-master" (from apps/teamventure/src/docker-compose.yml).
#
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../../../../.." && pwd)"

SQL_FILE_DEFAULT="${REPO_ROOT}/apps/teamventure/src/database/schema/V1.0.9__backfill_itinerary_version.sql"
COMPOSE_FILE_DEFAULT="${REPO_ROOT}/apps/teamventure/src/docker-compose.yml"
ENV_FILE_DEFAULT="${REPO_ROOT}/apps/teamventure/src/.env.local"
SERVICE_DEFAULT="mysql-master"

SQL_FILE="$SQL_FILE_DEFAULT"
COMPOSE_FILE="$COMPOSE_FILE_DEFAULT"
ENV_FILE="$ENV_FILE_DEFAULT"
SERVICE="$SERVICE_DEFAULT"

usage() {
  cat <<'EOF'
Usage:
  backfill_itinerary_version.sh [--sql-file PATH] [--compose-file PATH] [--env-file PATH] [--service NAME]

Examples:
  # 默认：对 docker compose 服务 mysql-master 执行回填
  bash apps/teamventure/docs/qa/scripts/backfill_itinerary_version.sh

  # 指定 compose 文件 / env 文件（如果你改过路径）
  bash apps/teamventure/docs/qa/scripts/backfill_itinerary_version.sh --compose-file apps/teamventure/src/docker-compose.yml --env-file apps/teamventure/src/.env.local

  # 指定服务名（如果你改过 compose service）
  bash apps/teamventure/docs/qa/scripts/backfill_itinerary_version.sh --service mysql-master
EOF
}

die() {
  echo "ERROR: $*" >&2
  exit 1
}

log() {
  printf '[%s] %s\n' "$(date '+%F %T')" "$*" >&2
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing command: $1"
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --sql-file) SQL_FILE="$2"; shift 2 ;;
      --compose-file) COMPOSE_FILE="$2"; shift 2 ;;
      --env-file) ENV_FILE="$2"; shift 2 ;;
      --service) SERVICE="$2"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      *) die "unknown arg: $1" ;;
    esac
  done
}

mysql_exec() {
  local sql="$1"
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T "$SERVICE" sh -lc \
    'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "${MYSQL_DATABASE:-teamventure_main}" -Nse "$1"' -- "$sql"
}

main() {
  parse_args "$@"
  require_cmd docker

  [[ -f "$SQL_FILE" ]] || die "sql file not found: $SQL_FILE"
  [[ -f "$COMPOSE_FILE" ]] || die "compose file not found: $COMPOSE_FILE"
  [[ -f "$ENV_FILE" ]] || die "env file not found: $ENV_FILE"

  local cid
  cid="$(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps -q "$SERVICE" 2>/dev/null || true)"
  [[ -n "$cid" ]] || die "service not running: $SERVICE (hint: docker compose --env-file \"$ENV_FILE\" -f \"$COMPOSE_FILE\" up -d $SERVICE)"

  log "compose_file=$COMPOSE_FILE"
  log "env_file=$ENV_FILE"
  log "service=$SERVICE"
  log "sql_file=$SQL_FILE"

  log "apply backfill sql..."
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T "$SERVICE" sh -lc \
    'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "${MYSQL_DATABASE:-teamventure_main}"' <"$SQL_FILE"

  log "verify: itinerary_version NULL count"
  local null_cnt
  null_cnt="$(mysql_exec "SELECT COUNT(*) FROM plans WHERE itinerary_version IS NULL;")"
  log "plans.itinerary_version null_cnt=$null_cnt"
  [[ "$null_cnt" == "0" ]] || die "backfill incomplete: null_cnt=$null_cnt"

  log "verify: column definition"
  mysql_exec "SHOW COLUMNS FROM plans LIKE 'itinerary_version';" | sed 's/^/  /' >&2 || true

  log "done"
}

main "$@"
