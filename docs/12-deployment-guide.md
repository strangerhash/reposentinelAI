# Deployment Guide

Infrastructure and deployment options for RepoSentinel AI — SaaS, VPC self-hosted, and local development.

---

## Deployment Options

| Option | Target Customer | Management |
|--------|----------------|-----------|
| SaaS Multi-Tenant | Startups, mid-market | Xenqube managed |
| VPC Self-Hosted | Banks, gov, crypto | Customer managed (Helm) |
| Local Dev | Engineers | Docker Compose |

---

## SaaS Architecture (AWS)

### Infrastructure Diagram

```
Route 53
  └── CloudFront (CDN + WAF)
        └── ALB (TLS 1.3)
              └── EKS Cluster
                    ├── web (Next.js) — 2-10 pods HPA
                    ├── api-gateway (Node.js) — 2-10 pods
                    ├── connector-github — 2 pods
                    ├── connector-gitlab — 2 pods
                    ├── connector-bitbucket — 2 pods
                    ├── scanner-orchestrator — 2-20 pods HPA
                    ├── scanner-* workers — 2-20 pods HPA
                    ├── agent-orchestrator — 2-10 pods
                    ├── flag-service — 2 pods
                    ├── knowledge-service — 2 pods
                    ├── posture-service — 1 pod (cron)
                    ├── compliance-service — 2 pods
                    ├── notification-service — 2 pods
                    └── mcp-server (SSE) — 2 pods

MSK (Kafka)
  ├── topic.changes
  ├── topic.findings
  ├── topic.agent-jobs
  └── topic.notifications

Aurora PostgreSQL (Multi-AZ)
  └── pgvector extension

ElastiCache Valkey
  └── Celery broker + cache

S3
  ├── diffs/ (24h TTL lifecycle)
  ├── reports/
  └── evidence-exports/

EC2 GPU Pool (vLLM)
  └── Tier 0/1 inference

Secrets Manager
CloudWatch + OpenTelemetry → Datadog
```

### Environment Matrix

| Environment | Purpose | URL |
|-------------|---------|-----|
| dev | Feature development | dev.reposentinel.ai |
| staging | Pre-production testing | staging.reposentinel.ai |
| production | Customer-facing | app.reposentinel.ai |
| mcp | MCP SSE endpoint | mcp.reposentinel.ai |

---

## VPC Self-Hosted (Helm Chart)

### Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Kubernetes | 1.28+ | 1.30+ |
| Nodes | 3 × 4 vCPU / 16 GB | 5 × 8 vCPU / 32 GB |
| Storage | 100 GB SSD | 500 GB SSD |
| GPU (optional) | 1 × T4 (vLLM) | 2 × A10G |
| PostgreSQL | 14+ with pgvector | Aurora-compatible |

### Install

```bash
# Add Helm repo
helm repo add reposentinel https://charts.reposentinel.ai
helm repo update

# Create namespace
kubectl create namespace reposentinel

# Create secrets
kubectl create secret generic reposentinel-secrets \
  --namespace reposentinel \
  --from-literal=database-url="postgresql://..." \
  --from-literal=jwt-secret="..." \
  --from-literal=encryption-key="..."

# Install
helm install reposentinel reposentinel/reposentinel \
  --namespace reposentinel \
  --values values.production.yaml \
  --set global.domain="security.company.com" \
  --set vllm.enabled=true \
  --set vllm.gpuCount=1
```

### values.production.yaml

```yaml
global:
  domain: security.company.com
  tls:
    enabled: true
    issuer: letsencrypt-prod

replicaCount:
  web: 2
  api: 2
  scanners: 3
  agents: 2

postgresql:
  enabled: true  # or external: true + external.host
  auth:
    database: reposentinel
  primary:
    persistence:
      size: 100Gi

kafka:
  enabled: true  # or external Redpanda/MSK

redis:
  enabled: true

vllm:
  enabled: true
  model: "meta-llama/Llama-3.1-8B-Instruct"
  gpuCount: 1
  resources:
    limits:
      nvidia.com/gpu: 1

frontierLLM:
  enabled: true  # Tier 2 escalation only
  provider: anthropic  # or openai
  # API key from secret

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod

monitoring:
  enabled: true
  prometheus: true
  grafana: true
```

### Self-Hosted vs SaaS Feature Parity

| Feature | SaaS | Self-Hosted |
|---------|------|-------------|
| All scanners | ✓ | ✓ |
| All agents | ✓ | ✓ |
| MCP server | ✓ | ✓ |
| Posture score | ✓ | ✓ |
| Compliance export | ✓ | ✓ |
| Peer benchmarking | ✓ | ✗ (no cross-customer data) |
| White-label | ✓ | ✓ |
| Auto-updates | ✓ | Manual Helm upgrade |
| Tier 2 frontier LLM | ✓ | Optional egress |

---

## Local Development

### Local Development (Docker — recommended)

```bash
./start.sh
```

`start.sh` will:
1. Load ports from `.env` (defaults 19000–19003)
2. Free any conflicting local processes on those ports
3. `docker compose up --build -d` for postgres, redis, api, web
4. Wait for health checks
5. Seed demo data
6. Print URLs

```bash
./stop.sh           # stop all containers
docker compose logs -f   # tail logs
make check          # verify web + API
```

### docker-compose.yml (core services)

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    ports: ["5432:5432"]
    environment:
      POSTGRES_DB: reposentinel
      POSTGRES_USER: reposentinel
      POSTGRES_PASSWORD: dev

  redis:
    image: valkey/valkey:8
    ports: ["6379:6379"]

  kafka:
    image: redpandadata/redpanda:latest
    ports: ["9092:9092"]

  api:
    build: ./services/api
    ports: ["8000:8000"]
    depends_on: [postgres, redis, kafka]
    env_file: .env

  web:
    build: ./apps/web
    ports: ["3000:3000"]
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000

  scanner-orchestrator:
    build: ./services/scanner-orchestrator
    depends_on: [kafka, postgres]

  agent-orchestrator:
    build: ./services/agent-orchestrator
    depends_on: [redis, postgres]
    environment:
      LLM_PROVIDER: openai  # dev uses hosted API
      OPENAI_API_KEY: ${OPENAI_API_KEY}
```

### Dev URLs

| Service | Default URL | Port env var |
|---------|-------------|--------------|
| Dashboard | http://localhost:19000 | `EG_WEB_PORT` |
| API | http://localhost:19001 | `EG_API_PORT` |
| API Docs | http://localhost:19001/docs | — |
| Postgres (host) | localhost:19002 | `EG_POSTGRES_PORT` |
| Redis (host) | localhost:19003 | `EG_REDIS_PORT` |

Defaults use **19000–19003** to avoid conflicts with common dev ports (3000, 5432, 6379, 8000). Override in `.env`.

---

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
name: Deploy Production
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm test
      - run: pip install -r requirements.txt && pytest

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: |
            ${{ secrets.ECR_REGISTRY }}/reposentinel-web:${{ github.sha }}
            ${{ secrets.ECR_REGISTRY }}/reposentinel-api:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: |
          aws eks update-kubeconfig --name reposentinel-prod
          helm upgrade reposentinel ./infra/helm/reposentinel \
            --set image.tag=${{ github.sha }} \
            --namespace production
```

---

## Database Migrations

```bash
# Using Alembic (Python services)
cd services/api
alembic upgrade head

# Generate new migration
alembic revision --autogenerate -m "add mcp_servers table"
```

Migrations run as Kubernetes init container before API pods start.

---

## Monitoring & Alerting

### Key Dashboards

| Dashboard | Metrics |
|-----------|---------|
| Platform Health | Pod restarts, error rates, latency p95 |
| Ingestion | Webhook rate, Kafka lag, connector errors |
| Scanners | Scan duration, findings rate, failures |
| Agents | Token usage, budget exceeded, run duration |
| Business | Active orgs, flags opened/resolved, posture scores |

### Alert Rules

```yaml
- alert: HighKafkaLag
  expr: kafka_consumer_lag > 1000
  for: 5m
  severity: warning

- alert: AgentBudgetExceeded
  expr: rate(agent_budget_exceeded_total[5m]) > 0.05
  severity: warning

- alert: APIErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
  severity: critical
```

---

## Backup & Disaster Recovery

| Component | Backup | RPO | RTO |
|-----------|--------|-----|-----|
| Aurora PostgreSQL | Continuous + daily snapshot | 5 min | 30 min |
| S3 reports | Cross-region replication | 1 hour | 1 hour |
| Kafka | MSK multi-AZ | 0 | 5 min |
| Secrets Manager | Automatic versioning | 0 | Immediate |

### DR Runbook

1. Detect failure (automated health checks)
2. Failover Aurora to standby (automatic, < 30s)
3. Scale EKS pods in secondary AZ
4. Verify Kafka consumer groups rebalanced
5. Smoke test: webhook → flag → dashboard
6. Customer communication if > 5 min downtime

---

## Scaling Runbook

### When to Scale

| Signal | Action |
|--------|--------|
| Kafka lag > 500 for 10 min | Scale scanner workers +2 |
| API p95 > 500ms | Scale API pods +2 |
| Celery queue > 100 jobs | Scale agent workers +2 |
| vLLM queue > 50 requests | Scale GPU nodes +1 |
| Aurora CPU > 80% | Upgrade instance class |

### Cost Optimization

- Spot instances for scanner workers (fault-tolerant)
- vLLM request batching (max batch size 32)
- S3 lifecycle: diffs deleted after 24h
- Reserved instances for Aurora and baseline EKS nodes
