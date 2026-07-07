#!/usr/bin/env bash
# Verify EstateGuard services are reachable
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -f .env ]; then set -a; source .env; set +a; fi

EG_WEB_PORT="${EG_WEB_PORT:-19000}"
EG_API_PORT="${EG_API_PORT:-19001}"
EG_POSTGRES_PORT="${EG_POSTGRES_PORT:-19002}"
EG_REDIS_PORT="${EG_REDIS_PORT:-19003}"

ok=0
fail=0

check() {
  local name=$1 url=$2
  if curl -sf --max-time 3 "$url" >/dev/null 2>&1; then
    echo "✓ $name — $url"
    ok=$((ok + 1))
  else
    echo "✗ $name — $url (not reachable)"
    fail=$((fail + 1))
  fi
}

echo "EstateGuard health check"
check "Web" "http://localhost:${EG_WEB_PORT}"
check "API" "http://localhost:${EG_API_PORT}/v1/health"

if command -v pg_isready >/dev/null 2>&1; then
  if pg_isready -h localhost -p "$EG_POSTGRES_PORT" -U estateguard >/dev/null 2>&1; then
    echo "✓ Postgres — localhost:${EG_POSTGRES_PORT}"
    ok=$((ok + 1))
  else
    echo "✗ Postgres — localhost:${EG_POSTGRES_PORT}"
    fail=$((fail + 1))
  fi
fi

if [ "$fail" -gt 0 ]; then
  echo ""
  echo "Some services are down. Run:  make dev"
  echo "Or:  make up && make api  (terminal 1)  &&  make web  (terminal 2)"
  exit 1
fi
echo ""
echo "All services OK (${ok} checks passed)"
