#!/usr/bin/env bash
# EstateGuard — start full stack via Docker Compose
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# Load environment
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

EG_WEB_PORT="${EG_WEB_PORT:-19000}"
EG_API_PORT="${EG_API_PORT:-19001}"
EG_POSTGRES_PORT="${EG_POSTGRES_PORT:-19002}"
EG_REDIS_PORT="${EG_REDIS_PORT:-19003}"
NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:${EG_API_PORT}}"
CORS_ORIGINS="${CORS_ORIGINS:-http://localhost:${EG_WEB_PORT}}"

export EG_WEB_PORT EG_API_PORT EG_POSTGRES_PORT EG_REDIS_PORT
export NEXT_PUBLIC_API_URL CORS_ORIGINS

log() { echo "==> $*"; }
die() { echo "ERROR: $*" >&2; exit 1; }

command -v docker >/dev/null 2>&1 || die "Docker is not installed"
docker compose version >/dev/null 2>&1 || die "Docker Compose is not available"

free_port() {
  local port=$1 name=$2
  if command -v fuser >/dev/null 2>&1; then
    if fuser "${port}/tcp" >/dev/null 2>&1; then
      log "Freeing port ${port} (${name})..."
      fuser -k "${port}/tcp" >/dev/null 2>&1 || true
      sleep 1
    fi
  fi
}

wait_http() {
  local name=$1 url=$2 max=${3:-60}
  local i=1
  while [ "$i" -le "$max" ]; do
    if curl -sf --max-time 2 "$url" >/dev/null 2>&1; then
      log "${name} ready — ${url}"
      return 0
    fi
    sleep 1
    i=$((i + 1))
  done
  die "${name} did not become ready at ${url}"
}

log "EstateGuard Docker startup"
log "Ports: web=${EG_WEB_PORT} api=${EG_API_PORT} postgres=${EG_POSTGRES_PORT} redis=${EG_REDIS_PORT}"

# Free host ports so Docker can bind (avoids conflict with local make dev)
free_port "$EG_WEB_PORT" "web"
free_port "$EG_API_PORT" "api"
free_port "$EG_POSTGRES_PORT" "postgres"
free_port "$EG_REDIS_PORT" "redis"

log "Building and starting containers..."
docker compose up --build -d

log "Waiting for Postgres..."
for i in $(seq 1 60); do
  if docker compose exec -T postgres pg_isready -U estateguard >/dev/null 2>&1; then
    log "Postgres ready"
    break
  fi
  if [ "$i" -eq 60 ]; then die "Postgres failed to start"; fi
  sleep 1
done

log "Waiting for API..."
wait_http "API" "http://127.0.0.1:${EG_API_PORT}/v1/health" 90

log "Seeding demo data (idempotent)..."
docker compose exec -T api sh -c "cd /app && PYTHONPATH=. python scripts/seed.py" || log "Seed skipped or already applied"

log "Waiting for Web..."
wait_http "Web" "http://127.0.0.1:${EG_WEB_PORT}" 120

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  EstateGuard is running (Docker)                     ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Web:         http://localhost:${EG_WEB_PORT}              ║"
echo "║  Dashboard:   http://localhost:${EG_WEB_PORT}/dashboard    ║"
echo "║  Engagements:  http://localhost:${EG_WEB_PORT}/dashboard/engagements"
echo "║  API docs:     http://localhost:${EG_API_PORT}/docs         ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Stop:   ./stop.sh  or  docker compose down          ║"
echo "║  Logs:   docker compose logs -f                        ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
