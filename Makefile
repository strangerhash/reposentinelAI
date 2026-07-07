# Load .env for port configuration
ifneq (,$(wildcard .env))
  include .env
  export
endif

EG_WEB_PORT ?= 19000
EG_API_PORT ?= 19001
EG_POSTGRES_PORT ?= 19002
EG_REDIS_PORT ?= 19003

.PHONY: start stop up down install seed dev check ports logs docker-up

# Primary: run full stack via Docker
start:
	@chmod +x start.sh stop.sh
	@./start.sh

stop:
	@chmod +x stop.sh
	@./stop.sh

logs:
	docker compose logs -f

docker-up: start

ports:
	@echo "EstateGuard ports (host):"
	@echo "  Web:      http://localhost:$(EG_WEB_PORT)"
	@echo "  API:      http://localhost:$(EG_API_PORT)"
	@echo "  Postgres: localhost:$(EG_POSTGRES_PORT)"
	@echo "  Redis:    localhost:$(EG_REDIS_PORT)"

up:
	@chmod +x start.sh
	@./start.sh

down: stop

check:
	@chmod +x scripts/check.sh
	@bash scripts/check.sh

install:
	cd services/api && pip install -r requirements.txt
	cd apps/web && npm install

seed:
	docker compose exec -T api sh -c "cd /app && PYTHONPATH=. python scripts/seed.py"

dev:
	@chmod +x scripts/dev-local.sh
	@bash scripts/dev-local.sh

test-api:
	cd services/api && python3 -c "from app.scanners.engine import scan_files; f=scan_files({'package.json': '{\"dependencies\":{\"lodash\":\"4.17.20\"}}'}); print(len(f), 'findings')"
