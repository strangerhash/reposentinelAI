#!/bin/sh
set -e
echo "==> API entrypoint: waiting for database..."
python - <<'PY'
import asyncio
import os
import sys
import time

import asyncpg

url = os.environ.get("DATABASE_URL", "").replace("postgresql+asyncpg://", "postgresql://")
for i in range(60):
    try:
        asyncio.run(asyncpg.connect(url))
        print("==> Database connection OK")
        sys.exit(0)
    except Exception as e:
        if i == 59:
            print(f"==> Database connection failed: {e}", file=sys.stderr)
            sys.exit(1)
        time.sleep(1)
PY

echo "==> Creating tables if needed..."
python - <<'PY'
import asyncio
from app.database import engine, Base

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init())
print("==> Schema ready")
PY

exec "$@"
