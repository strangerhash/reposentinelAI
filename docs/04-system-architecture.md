# System Architecture

High-level architecture for RepoSentinel AI — four layers with a hard enforcement boundary between deterministic execution and LLM reasoning.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                                │
│  Next.js Dashboard │ REST/GraphQL API │ Webhooks Out │ MCP Server       │
│  Landing Page      │ Slack/Jira Bots  │ Email Digests│ Cursor/VS Code   │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────────┐
│                     AGENTIC REASONING LAYER                              │
│  Orchestrator (LangGraph adapter) │ State Store (Postgres)               │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ ┌─────────────┐  │
│  │ Triage  │ │Correlate │ │ Explainer│ │ Remediate  │ │ KB Curator  │  │
│  └─────────┘ └──────────┘ └──────────┘ └────────────┘ └─────────────┘  │
│  ┌─────────┐                                                            │
│  │ Query   │  ← Tier 0/1 (vLLM) ──escalate──▶ Tier 2 (frontier API)    │
│  └─────────┘                                                            │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │ reads findings + diffs only
┌──────────────────────────────────▼──────────────────────────────────────┐
│                   DETERMINISTIC ANALYSIS LAYER                           │
│  ┌────────┐ ┌──────┐ ┌─────┐ ┌─────┐ ┌────────┐ ┌────────────────────┐  │
│  │Secrets │ │ SAST │ │ SCA │ │ IaC │ │License │ │ Architecture Drift│  │
│  └────────┘ └──────┘ └─────┘ └─────┘ └────────┘ └────────────────────┘  │
│  Severity Engine (rule-based) │ SBOM Builder │ Call Graph Engine         │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────────┐
│                        INGESTION LAYER                                   │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐                              │
│  │ GitHub   │  │ GitLab   │  │ Bitbucket │  Connectors (registry-driven)│
│  │ Connector│  │ Connector│  │ Connector │                              │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘                              │
│       └─────────────┼──────────────┘                                    │
│                     ▼                                                    │
│           Canonical Event Bus (Kafka / SQS)                              │
│           Raw Event Store (S3 / Postgres)                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Layer 1 — Ingestion

### Responsibilities
- Receive webhooks and poll APIs from GitHub, GitLab, Bitbucket
- Normalize to canonical `Change` event schema
- Deduplicate, order, and publish to event bus
- Handle OAuth token refresh and rate limiting per platform

### Canonical Event Schema

```json
{
  "event_id": "uuid",
  "event_type": "push|pull_request|merge_request|pipeline|branch_delete",
  "platform": "github|gitlab|bitbucket",
  "org_id": "org_xyz",
  "repository": {
    "id": "repo_abc",
    "name": "payment-service",
    "url": "https://github.com/acme/payment-service",
    "default_branch": "main",
    "criticality_tier": "critical|high|medium|low"
  },
  "change": {
    "sha": "abc123",
    "ref": "refs/heads/feature/auth",
    "author": "dev@acme.com",
    "timestamp": "2026-07-07T10:00:00Z",
    "diff_url": "...",
    "files_changed": ["src/auth.ts", "package.json"],
    "is_pr": true,
    "pr_number": 42
  },
  "metadata": {
    "connector_version": "1.2.0",
    "received_at": "2026-07-07T10:00:01Z"
  }
}
```

### Connector Registry Pattern

Connectors register as capabilities in the Tool Hub registry:

```yaml
connector:
  id: github
  version: 1.0.0
  events: [push, pull_request, release, workflow_run]
  auth: oauth2 | github_app
  rate_limit: 5000/hour
```

---

## Layer 2 — Deterministic Analysis

### Scanner Pipeline

```
Change Event → Diff Extractor → Scanner Router → Finding Emitter
                     │
                     ├── secrets_scanner
                     ├── sast_scanner (per language)
                     ├── sca_scanner (SBOM + CVE feed)
                     ├── iac_scanner (Terraform/K8s/CloudFormation)
                     ├── license_scanner
                     └── drift_scanner (call graph diff)
```

### Enforcement Boundary

```
┌─────────────────────────────────────────────┐
│  DETERMINISTIC (agents CANNOT override)      │
│  • Severity score computation               │
│  • Flag open/close decisions                │
│  • Merge approval / block                   │
│  • Compliance control pass/fail             │
└─────────────────────────────────────────────┘
         ▲ agents may SUGGEST, never SET
┌─────────────────────────────────────────────┐
│  AGENTIC (agents MAY produce)               │
│  • Triage classification (advisory)         │
│  • Human-readable explanations              │
│  • Remediation draft PRs (human approves)   │
│  • Knowledge base entries                   │
│  • Query answers with citations             │
└─────────────────────────────────────────────┘
```

### Severity Rule Engine

```python
severity = f(cvss_score, exploitability, exposure, asset_criticality_tier)
# Output: critical | high | medium | low | info
# NEVER assigned by LLM — rule version logged with every flag
```

---

## Layer 3 — Agentic Reasoning

### Orchestration

- **Engine:** LangGraph as thin adapter over Postgres-backed state machine
- **State:** All run state, budgets, checkpoints in Aurora PostgreSQL
- **Queue:** Celery workers on Valkey/Redis for async agent runs

### Agent Roster

| Agent | Trigger | Input | Output | Model Tier |
|-------|---------|-------|--------|------------|
| Triage | Per-change | New findings | Signal/noise classification | Tier 0 |
| Correlation | Scheduled batch | Cross-repo findings | Merged flags | Tier 0 |
| Explainer | Per-flag | Findings + diff | Summary + remediation steps | Tier 1 |
| Remediation | Per-actionable-flag | Finding + diff | Draft PR branch | Tier 1 |
| Knowledge-Curator | Post-merge batch | Merged PRs, closed flags | KnowledgeUnit drafts | Tier 1 |
| Query | On-demand | User question | Answer + citations | Tier 0→2 |

### Token Budget Per Agent

| Agent | Max Input Tokens | Max Output Tokens | Hard Timeout |
|-------|-----------------|-------------------|--------------|
| Triage | 8,000 | 500 | 30s |
| Correlation | 16,000 | 1,000 | 120s |
| Explainer | 12,000 | 2,000 | 60s |
| Remediation | 16,000 | 4,000 | 180s |
| Knowledge-Curator | 20,000 | 3,000 | 300s |
| Query | 8,000 | 2,000 | 45s |

---

## Layer 4 — Presentation

### Dashboard Modules

| Module | API Namespace | Primary Users |
|--------|--------------|---------------|
| Posture Dashboard | `/api/v1/posture` | CISO, Security Lead |
| Risk Register | `/api/v1/flags` | Security Lead, Developers |
| Architecture Map | `/api/v1/architecture` | Platform, Architects |
| Knowledge Copilot | `/api/v1/knowledge/query` | All engineers |
| Compliance Center | `/api/v1/compliance` | Compliance Officer |
| Due Diligence | `/api/v1/engagements` | Consultancy |
| Settings & Admin | `/api/v1/admin` | Org Admin |
| Cost Dashboard | `/api/v1/ops/cost` | Org Owner, Admin |

### External Interfaces

| Interface | Protocol | Consumers |
|-----------|----------|-----------|
| REST API | HTTPS + JSON | Dashboard, CI/CD, integrations |
| GraphQL API | HTTPS | Dashboard (complex queries) |
| WebSocket | WSS | Real-time flag updates |
| MCP Server | MCP over stdio/SSE | Cursor, VS Code, custom agents |
| Webhooks Out | HTTPS POST | Slack, Jira, PagerDuty, custom |
| GitHub App | Webhooks In | GitHub repos |

---

## Deployment Topologies

### SaaS Multi-Tenant (Default)

```
Route 53 → CloudFront → ALB → EKS (Next.js + FastAPI pods)
                              → MSK (Kafka)
                              → Aurora PostgreSQL (tenant_id RLS)
                              → ElastiCache Valkey
                              → S3 (artifacts, reports)
                              → vLLM on GPU nodes (Tier 0/1)
```

### VPC / Self-Hosted (Enterprise)

```
Customer VPC:
  ├── RepoSentinel Helm chart
  ├── Postgres + pgvector
  ├── Kafka (or Redpanda)
  ├── vLLM (customer GPU or CPU)
  └── Optional: frontier API egress for Tier 2 only
```

### MSP White-Label

```
Consultancy Control Plane
  ├── Tenant A (client branding, isolated DB schema)
  ├── Tenant B
  └── Tenant N
Shared: scanner workers, agent orchestrator (tenant-scoped jobs)
```

---

## Cross-Cutting Concerns

| Concern | Implementation |
|---------|---------------|
| Multi-tenancy | `tenant_id` on every row + Postgres RLS |
| Auth | JWT (short-lived) + refresh tokens; API keys scoped |
| Secrets | AWS Secrets Manager / Vault; never in env files |
| Observability | OpenTelemetry → Datadog/Grafana |
| Rate limiting | Per-org, per-repo, per-agent token budgets |
| Data residency | Region-pinned tenants (EU, US, APAC) |

---

## Technology Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, shadcn/ui, Tailwind, Tremor, React Flow |
| API Gateway | Node.js (BFF) + FastAPI (core services) |
| Event Bus | Kafka (MSK) or SQS |
| Database | Aurora PostgreSQL + pgvector |
| Cache/Queue | Valkey/Redis + Celery |
| Object Storage | S3 |
| LLM Inference | vLLM (self-hosted) + Anthropic/OpenAI (Tier 2) |
| Agent Orchestration | LangGraph (adapter) + custom state in Postgres |
| IaC | Terraform + Helm (self-hosted) |
| CI/CD | GitHub Actions |
