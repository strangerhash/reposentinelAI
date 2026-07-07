#!/usr/bin/env bash
# Stop EstateGuard Docker stack
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
echo "==> Stopping EstateGuard containers..."
docker compose down
echo "==> Stopped."
