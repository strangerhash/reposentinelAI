#!/usr/bin/env bash
# Start EstateGuard locally (API + Web). Requires: make up && make install
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -f .env ]; then set -a; source .env; set +a; fi
EG_WEB_PORT="${EG_WEB_PORT:-19000}"
EG_API_PORT="${EG_API_PORT:-19001}"
DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://estateguard:estateguard@localhost:19002/estateguard}"
NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:${EG_API_PORT}}"
CORS_ORIGINS="${CORS_ORIGINS:-http://localhost:${EG_WEB_PORT}}"

check_port() {
  local port=$1 name=$2
  if ss -tln 2>/dev/null | grep -q ":${port} "; then
    echo "WARNING: port ${port} (${name}) already in use."
    return 1
  fi
  return 0
}

echo "==> EstateGuard dev (web :${EG_WEB_PORT}, api :${EG_API_PORT})"
check_port "$EG_API_PORT" "API" || true
check_port "$EG_WEB_PORT" "Web" || true

# Ensure infra
if ! docker compose ps postgres 2>/dev/null | grep -q "Up"; then
  echo "==> Starting postgres + redis..."
  docker compose up -d postgres redis
  sleep 3
fi

cleanup() {
  echo ""
  echo "==> Stopping dev processes..."
  kill "$API_PID" 2>/dev/null || true
  kill "$WEB_PID" 2>/dev/null || true
  wait "$API_PID" 2>/dev/null || true
  wait "$WEB_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "==> Starting API on :${EG_API_PORT}..."
(
  cd services/api
  export DATABASE_URL CORS_ORIGINS
  exec uvicorn app.main:app --host 0.0.0.0 --port "$EG_API_PORT" --reload
) &
API_PID=$!

for i in $(seq 1 30); do
  if curl -sf "http://127.0.0.1:${EG_API_PORT}/v1/health" >/dev/null 2>&1; then
    echo "    API ready"
    break
  fi
  sleep 0.5
done

echo "==> Starting Web on :${EG_WEB_PORT}..."
(
  cd apps/web
  export NEXT_PUBLIC_API_URL
  exec npm run dev -- --port "$EG_WEB_PORT" --hostname 0.0.0.0
) &
WEB_PID=$!

for i in $(seq 1 60); do
  if curl -sf "http://127.0.0.1:${EG_WEB_PORT}" >/dev/null 2>&1; then
    echo ""
    echo "✓ EstateGuard running"
    echo "  Web:  http://localhost:${EG_WEB_PORT}"
    echo "  API:  http://localhost:${EG_API_PORT}/docs"
    break
  fi
  sleep 0.5
done

wait "$WEB_PID"
