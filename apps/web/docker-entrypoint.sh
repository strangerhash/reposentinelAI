#!/bin/sh
set -e
echo "==> Web: installing dependencies..."
npm install --silent
echo "==> Web: starting Next.js on port ${EG_WEB_PORT:-19000}..."
exec npm run dev -- --port "${EG_WEB_PORT:-19000}" --hostname 0.0.0.0
